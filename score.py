"""Score results.json against the seed labels. Imported by build.py; run directly for a console summary."""
import json
PRICE = {"jev": (0.042, 0.0), "opus": (5, 25), "haiku": (1, 5)}   # USD per 1M tokens (in, out)

def top(x): return max(x["p"].values())
def arm_view(r, arm):
    """Normalize one arm's answers to {urgency,category,owner: (value, conf)}, snippets set, flags dict."""
    a = r[arm]
    if arm == "jev":
        lab = {k: (a[k]["choice"], top(a[k])) for k in ("urgency", "category", "owner")}
        return lab, {k for k, v in a["snippets"].items() if v >= 0.5}, {k: v >= 0.5 for k, v in a["flags"].items()}
    lab = {k: (a[k]["value"], a[k]["confidence"]) for k in ("urgency", "category", "owner")}
    return lab, set(a["snippets"]), a["flags"]

def score(rows):
    out = {}
    for arm in ("jev", "opus", "haiku"):
        s = {"n": len(rows)}; tp = fp = fn = 0; fl_ok = fl_n = 0; saf_miss = 0; conf = []
        for k in ("urgency", "category", "owner"): s[k] = 0
        for r in rows:
            lab, sn, fl = arm_view(r, arm); seed = r["seed"]
            for k in ("urgency", "category", "owner"):
                ok = lab[k][0] == seed[k]; s[k] += ok; conf.append((lab[k][1], ok))
            g = set(seed["snippets"]); tp += len(sn & g); fp += len(sn - g); fn += len(g - sn)
            for k, v in fl.items(): fl_ok += (v == seed[k]); fl_n += 1
            if seed["safety"] and not fl["safety"]: saf_miss += 1
        for k in ("urgency", "category", "owner"): s[k] = s[k] / len(rows)
        s["snip_precision"] = tp / (tp + fp) if tp + fp else 0; s["snip_recall"] = tp / (tp + fn)
        s["flags"] = fl_ok / fl_n; s["safety_missed"] = saf_miss
        # Brier on the three Choice labels using the reported confidence of the chosen answer
        s["brier"] = sum((c - ok) ** 2 for c, ok in conf) / len(conf); s["conf_pairs"] = conf
        tin = sum(r[arm]["usage"]["input"] for r in rows); tout = sum(r[arm]["usage"]["output"] for r in rows)
        pi, po = PRICE[arm]; s["tokens_in"], s["tokens_out"] = tin, tout
        s["cost_per_msg"] = (tin * pi + tout * po) / 1e6 / len(rows)
        s["latency_mean"] = sum(r[arm]["latency_s"] for r in rows) / len(rows)
        out[arm] = s
    return out

if __name__ == "__main__":
    d = json.load(open("results.json")); S = score(d["messages"])
    for arm, s in S.items():
        print(f"{arm:6} urg {s['urgency']:.2f} cat {s['category']:.2f} own {s['owner']:.2f} | snip P {s['snip_precision']:.2f} R {s['snip_recall']:.2f} | flags {s['flags']:.2f} safety_missed {s['safety_missed']} | brier {s['brier']:.3f} | ${s['cost_per_msg']:.5f}/msg {s['latency_mean']:.1f}s")
    for r in d["messages"]:
        sd = r["seed"]; line = []
        for arm in ("jev", "opus", "haiku"):
            lab, sn, fl = arm_view(r, arm)
            miss = [f"{k}={lab[k][0]}({lab[k][1]:.2f})" for k in ("urgency", "category", "owner") if lab[k][0] != sd[k]]
            fmiss = [k for k, v in fl.items() if v != sd[k]]
            line.append(f"{arm}: {' '.join(miss + ['F:' + x for x in fmiss]) or 'ok'}")
        print(r["id"], f"seed {sd['urgency']}/{sd['category']}/{sd['owner']}", " | ".join(line))
    dr = [r["draft"] for r in d["messages"] if r["draft"]]
    print(f"\ndrafts {len(dr)}: mean input selected {sum(x['usage']['input'] for x in dr)/len(dr):.0f} vs all-snippets {sum(x['all_snippets_input'] for x in dr)/len(dr):.0f}")
    from clock import clock_errors
    print("\nresponse clocks vs reference urgency (too loose = a later clock than the reference warrants)")
    rows = [("argmax label", dict(pick=lambda r: r["jev"]["urgency"]["choice"]))] + [(f"P(at least) >= {t:.2f}", dict(t=t)) for t in (0.5, 0.4, 0.3, 0.2)]
    for name, kw in rows:
        lo, ti, now = clock_errors(d["messages"], **kw)
        print(f"  {name:20} too loose {len(lo)} {' '.join(lo) or '-':14} too tight {len(ti)} {' '.join(ti) or '-'}")
    print(f"  no clock (Call Now, or no reply needed): {' '.join(now)}")
