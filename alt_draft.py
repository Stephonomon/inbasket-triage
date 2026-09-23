"""Re-draft M18 with the snippet threshold lowered to 0.3 (loads insurance_billing at p=0.37) and store it as draft_alt."""
import json
from triage import run_draft
d = json.load(open("results.json"))
for r in d["messages"]:
    if r["id"] == "M18":
        snips = [k for k, v in r["jev"]["snippets"].items() if v >= 0.3]
        r["draft_alt"] = {**run_draft({**r, "_owner": r["jev"]["owner"]["choice"]}, snips), "threshold": 0.3}
        print(snips); print(r["draft_alt"]["text"])
json.dump(d, open("results.json", "w"), indent=1)
