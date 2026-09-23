"""Run the in-basket triage demo end to end and write results.json.

  jev      One Jev request per message: 26 questions over one copy of the message (urgency, category, owner Choices;
           16 snippet Nouls; 7 flag Nouls). Probabilities come back for every question.
  opus     Claude Opus 5 (effort low) with structured output: the same labels + self-reported confidence, one call per message.
  haiku    Claude Haiku 4.5, same prompt and schema.
  draft    Claude Opus 5 drafts a reply for every message the routing policy allows, with ONLY the snippets Jev selected.
           count_tokens records what the same draft prompt would cost with all 16 snippets loaded.
"""
import json, os, sys, time, urllib.request, concurrent.futures as cf
import anthropic
from data import *

JEV_URL, JEV_MODEL = "https://api.typesafe.ai/v1/systemone", "jev-1.13.0"
def _jev_key():
    k = os.environ.get("TYPESAFE_API_KEY")
    if k: return k.strip()
    p = os.path.expanduser("~/.typesafe_api_key")
    if os.path.exists(p): return open(p).read().strip()
    sys.exit("Set TYPESAFE_API_KEY or put your key in ~/.typesafe_api_key (get one at https://console.typesafe.ai)")
JEV_KEY = _jev_key()
CL = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY
SNIP_T = 0.5; FLAG_T = 0.5

def jev(state, questions):
    body = json.dumps({"model": JEV_MODEL, "state": state, "questions": questions}).encode()
    req = urllib.request.Request(JEV_URL, data=body, headers={"Authorization": f"Bearer {JEV_KEY}", "Content-Type": "application/json", "User-Agent": "inbasket-triage-demo/1.0"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as r: return json.load(r)
        except Exception:
            if attempt == 2: raise
            time.sleep(2)

def header(m):
    p = PATIENTS[m["patient"]]
    return (f"Patient: {p['age']} {p['sex']}. Problems: {'; '.join(p['problems']) or 'none'}. Meds: {'; '.join(p['meds']) or 'none'}.\n"
            f"Sender: {m['sender']}")

def choice(instr, opts): return {"type": "choice", "instructions": instr, "criteria": {k: {"what": v} for k, v in opts.items()}}
def noul(instr, t, f): return {"type": "noul", "instructions": instr, "criteria": {"true": t, "false": f}}

QUESTIONS = {
  "urgency":  choice("How quickly must a human act on this pediatric patient-portal `message`? Judge the clinical content, not the sender's tone.", URGENCY),
  "category": choice("What is the primary request in this patient-portal `message`? If there are several, pick the one that drives who must handle it.", CATEGORIES),
  "owner":    choice("Which pool in the practice should own this `message`? Pick the least-credentialed pool that can fully resolve it safely; route to the physician only when medical judgment beyond a nursing protocol is needed.", OWNERS),
  **{f"snip_{k}": noul(f"To draft an accurate reply to this `message`, the drafter needs this chart/practice context: {v}.",
                       "The reply would be wrong, incomplete, or unsafe without this context.",
                       "The reply can be written well without this context; it is irrelevant to what was asked.") for k, v in SNIPPETS.items()},
  **{f"flag_{k}": noul(f"About this patient-portal `message`: {t}", t, f) for k, (t, f) in FLAGS.items()},
}

def run_jev(m):
    t0 = time.time(); r = jev({"practice": PRACTICE, "context": header(m), "message": m["text"]}, QUESTIONS); lat = time.time() - t0
    a = r["answers"]; out = {}
    for k in ("urgency", "category", "owner"):
        out[k] = {"choice": a[k]["choice"], "confidence": round(a[k].get("confidence", a[k]["probabilities"][a[k]["choice"]]), 3),
                  "p": {o: round(v, 3) for o, v in a[k]["probabilities"].items()}}
    out["snippets"] = {k: round(a[f"snip_{k}"]["noul"], 3) for k in SNIPPETS}
    out["flags"] = {k: round(a[f"flag_{k}"]["noul"], 3) for k in FLAGS}
    out["usage"] = {"input": r["usage"]["input_tokens"], "output": r["usage"]["output_tokens"]}; out["latency_s"] = round(lat, 2)
    return out

# ---------- Claude baselines ----------
def _enum_desc(d): return "\n".join(f"  - {k}: {v}" for k, v in d.items())
CL_SYSTEM = f"""You triage patient-portal messages for {PRACTICE}. All data is FABRICATED for a benchmark.
Return JSON only. Definitions:
urgency:
{_enum_desc(URGENCY)}
category (primary request; if several, the one that drives who must handle it):
{_enum_desc(CATEGORIES)}
owner (least-credentialed pool that can fully resolve it safely; physician only when medical judgment beyond a nursing protocol is needed):
{_enum_desc(OWNERS)}
snippets: every chart/practice context block the drafter NEEDS to write an accurate reply (omit irrelevant ones):
{_enum_desc(SNIPPETS)}
flags (true/false):
{chr(10).join(f'  - {k}: true = {t}' for k, (t, f) in FLAGS.items())}
For urgency, category and owner also give your probability (0-1) that your answer is correct."""
def _lab(enum): return {"type": "object", "properties": {"value": {"type": "string", "enum": list(enum)}, "confidence": {"type": "number"}}, "required": ["value", "confidence"], "additionalProperties": False}
CL_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["urgency", "category", "owner", "snippets", "flags"], "properties": {
  "urgency": _lab(URGENCY), "category": _lab(CATEGORIES), "owner": _lab(OWNERS),
  "snippets": {"type": "array", "items": {"type": "string", "enum": list(SNIPPETS)}},
  "flags": {"type": "object", "additionalProperties": False, "required": list(FLAGS), "properties": {k: {"type": "boolean"} for k in FLAGS}}}}

def run_claude(m, model):
    t0 = time.time()
    kw = dict(model=model, max_tokens=2000, system=CL_SYSTEM, messages=[{"role": "user", "content": f"{header(m)}\n\nMessage:\n{m['text']}"}])
    if model == "claude-opus-5":
        r = CL.beta.messages.create(**kw, output_config={"effort": "low", "format": {"type": "json_schema", "schema": CL_SCHEMA}},
                                    betas=["server-side-fallback-2026-07-01"], fallbacks="default")
    else:
        r = CL.messages.create(**kw, output_config={"format": {"type": "json_schema", "schema": CL_SCHEMA}})
    d = json.loads(next(b.text for b in r.content if b.type == "text"))
    return {"urgency": d["urgency"], "category": d["category"], "owner": d["owner"], "snippets": sorted(d["snippets"]), "flags": d["flags"],
            "usage": {"input": r.usage.input_tokens, "output": r.usage.output_tokens}, "latency_s": round(time.time() - t0, 2)}

# ---------- Routing policy (code, not model) + drafting ----------
def render(snip, p):
    if snip in PRACTICE_SNIPPETS: return PRACTICE_SNIPPETS[snip]
    lst = lambda xs, empty: "\n".join(f"- {x}" for x in xs) if xs else empty
    wt = p["weight_kg"]
    return {
      "med_list": lst(p["meds"], "No active medications."),
      "allergies": lst(p["allergies"], "NKDA"),
      "recent_labs": lst(p["labs"], "No resulted labs in the last 12 months."),
      "pending_results": lst(p["pending"], "No pending orders."),
      "problem_list": lst(p["problems"], "No active problems."),
      "last_visit": p["last_visit"] or "No visits on file.",
      "upcoming_appts": lst(p["appts"], "No upcoming appointments."),
      "immunizations": p["imms"],
      "forms_status": p["forms"] or "No forms on file.",
      "weight_dosing": f"Weight {wt} kg ({wt*2.2:.0f} lb). Acetaminophen 15 mg/kg = {15*wt:.0f} mg every 4-6 h, max 5 doses/24 h "
                       f"(160 mg/5 mL liquid: {15*wt/32:.1f} mL). Ibuprofen 10 mg/kg = {10*wt:.0f} mg every 6-8 h if >= 6 months "
                       f"(100 mg/5 mL liquid: {10*wt/20:.1f} mL).",
      "referral_status": lst(p["referrals"], "No open referrals."),
    }[snip]

def policy(j):
    f = j["flags"]
    if f["safety"] >= FLAG_T: return "phone_now"          # never a portal draft; RN calls the family and documents
    if f["needs_reply"] < FLAG_T: return "file_fyi"        # thank-you / FYI: route to PCP to read, no draft
    return "draft"

DRAFT_SYSTEM = f"""You draft patient-portal replies for {PRACTICE}. All data is FABRICATED for a demo.
The draft will be reviewed and edited by the clinician or staff member in the pool named below before it is sent.
- Use ONLY the chart and practice context provided. If something you would need is missing, say the care team will follow up; never invent values.
- Warm, plain language at a 6th-grade reading level, 60-150 words. No diagnosis beyond what the context supports.
- Follow the triage protocol if one is provided. Reply in the language the sender wrote in.
- If the sender is an adolescent writing from a confidential account, address only them.
- Sign as "Proctor Pediatrics care team"."""

def draft_prompt(m, snips):
    p = PATIENTS[m["patient"]]
    ctx = "\n\n".join(f"<{s}>\n{render(s, p)}\n</{s}>" for s in snips)
    return (f"Routed to: {m['_owner']} pool. Sender: {m['sender']}. Patient: {p['name']}, {p['age']}.\n\n"
            f"Chart and practice context:\n{ctx or '(none loaded)'}\n\nMessage:\n{m['text']}\n\nWrite the draft reply only.")

def run_draft(m, snips):
    msgs = lambda s: [{"role": "user", "content": draft_prompt(m, s)}]
    full = CL.messages.count_tokens(model="claude-opus-5", system=DRAFT_SYSTEM, messages=msgs(list(SNIPPETS))).input_tokens
    t0 = time.time()
    r = CL.beta.messages.create(model="claude-opus-5", max_tokens=1500, system=DRAFT_SYSTEM, messages=msgs(snips),
                                output_config={"effort": "low"}, betas=["server-side-fallback-2026-07-01"], fallbacks="default")
    text = "".join(b.text for b in r.content if b.type == "text").strip()
    return {"text": text, "snippets_loaded": snips, "usage": {"input": r.usage.input_tokens, "output": r.usage.output_tokens},
            "all_snippets_input": full, "latency_s": round(time.time() - t0, 2)}

def one(m):
    j = run_jev(m)
    with cf.ThreadPoolExecutor(2) as ex:
        fo, fh = ex.submit(run_claude, m, "claude-opus-5"), ex.submit(run_claude, m, "claude-haiku-4-5")
        opus, haiku = fo.result(), fh.result()
    action = policy(j); m = {**m, "_owner": j["owner"]["choice"]}
    snips = [k for k, v in j["snippets"].items() if v >= SNIP_T]
    draft = run_draft(m, snips) if action == "draft" else None
    print(f"{m['id']} jev {j['latency_s']:.1f}s  {j['urgency']['choice']}/{j['category']['choice']}/{j['owner']['choice']}  {action}", flush=True)
    return {k: v for k, v in m.items() if not k.startswith("_")} | {"jev": j, "opus": opus, "haiku": haiku, "action": action, "draft": draft}

if __name__ == "__main__":
    only = sys.argv[1:]
    msgs = [m for m in MESSAGES if not only or m["id"] in only]
    t0 = time.time()
    with cf.ThreadPoolExecutor(6) as ex: rows = list(ex.map(one, msgs))
    out = {"run_at": time.strftime("%Y-%m-%d %H:%M"), "jev_model": JEV_MODEL, "wall_s": round(time.time() - t0, 1), "snip_threshold": SNIP_T,
           "urgency": URGENCY, "categories": CATEGORIES, "owners": OWNERS, "snippets": SNIPPETS, "flags": {k: v[0] for k, v in FLAGS.items()},
           "patients": PATIENTS, "n_questions": len(QUESTIONS), "messages": rows}
    json.dump(out, open("results.json" if not only else "results_partial.json", "w"), indent=1)
    print(f"done in {out['wall_s']}s")
