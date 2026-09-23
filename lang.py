"""Merge results_partial.json (new messages) into results.json, ask Jev one extra Choice per message (language),
and have Claude Opus 5 produce English translations of non-English messages and drafts for staff review."""
import json, concurrent.futures as cf
from triage import jev, CL, PATIENTS

LANGS = {"english": "English", "spanish": "Spanish", "vietnamese": "Vietnamese", "chinese": "Chinese (Mandarin or Cantonese)",
         "arabic": "Arabic", "russian": "Russian", "haitian_creole": "Haitian Creole", "other": "Another language not listed"}
Q = {"language": {"type": "choice", "instructions": "What language is the patient-portal `message` mostly written in?",
                  "criteria": {k: {"what": v} for k, v in LANGS.items()}}}

d = json.load(open("results.json"))
new = json.load(open("results_partial.json"))["messages"]
have = {r["id"] for r in d["messages"]}
d["messages"] += [r for r in new if r["id"] not in have]
d["patients"] = PATIENTS

def lang(r):
    a = jev({"message": r["text"]}, Q)["answers"]["language"]
    r["jev"]["language"] = {"choice": a["choice"], "p": {k: round(v, 3) for k, v in a["probabilities"].items()}}
    if a["choice"] != "english":
        def tr(text):
            m = CL.messages.create(model="claude-opus-5", max_tokens=1500, output_config={"effort": "low"},
                system="Translate the text into plain English for clinic staff. Output only the translation.",
                messages=[{"role": "user", "content": text}])
            return "".join(b.text for b in m.content if b.type == "text").strip()
        r["text_en"] = tr(r["text"])
        if r.get("draft"): r["draft"]["text_en"] = tr(r["draft"]["text"])
    return r["id"], a["choice"], round(max(a["probabilities"].values()), 2)

with cf.ThreadPoolExecutor(6) as ex:
    for x in ex.map(lang, d["messages"]):
        if x[1] != "english": print(x)
json.dump(d, open("results.json", "w"), indent=1)
print(len(d["messages"]), "messages")
