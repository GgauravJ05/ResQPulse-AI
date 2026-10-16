"""Gold set in two steps.

  prelabel  merge candidates + Claude's pre-labels into a spreadsheet for human review
            reads  data/gold/gold_candidates.csv, data/gold/gold_prelabels.jsonl
            writes data/gold/gold_review.csv
  finalize  read the reviewed spreadsheet and write the gold set in the SCHEMA §2 format
            reads  data/gold/gold_review.csv   (after humans fill `verified` and, if needed, `correction_*`)
            writes data/gold/gold.csv

Review rules (give these to the reviewers):
  * incident_type: the type of incident the TEXT reports. Donations, jokes, ads, commentary, rumours about
    media, or relief logistics are NON_EMERGENCY, even if they mention a disaster.
  * severity: 1-5 using the rubric in docs/SCHEMA.md §1.2. News about a past event or a follow-up is low (2-3).
  * location / injuries / hazards must be copied word for word from the text.
  * If a row is correct, write 1 in `verified`. If you changed anything, edit the cell and write 2.
    If the row is unusable (not English, unreadable), write 0 and it is dropped.

Run from the repo root:  .venv/bin/python scripts/build_gold.py prelabel   (then, after review)  finalize
"""
import csv
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.labels import INCIDENT_TYPES  # noqa: E402

GOLD = Path("data/gold")
LIST_SEP = " ; "


def in_text(item: str, text: str) -> bool:
    return bool(item) and item.lower() in text.lower()


def prelabel() -> None:
    cand = pd.read_csv(GOLD / "gold_candidates.csv", dtype=str, keep_default_na=False)
    labels = {}
    for line in (GOLD / "gold_prelabels.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            labels[r["i"]] = r

    rows, problems = [], []
    for i, c in cand.iterrows():
        lab = labels.get(i)
        if lab is None or "drop" in lab:
            continue
        text = c["text"]
        assert lab["t"] in INCIDENT_TYPES, (i, lab["t"])
        loc = lab["loc"] if lab["loc"] and in_text(lab["loc"], text) else None
        if lab["loc"] and loc is None:
            problems.append(f"row {i}: location not in text: {lab['loc']!r}")
        inj = [x for x in lab["inj"] if in_text(x, text)]
        haz = [x for x in lab["haz"] if in_text(x, text)]
        problems += [f"row {i}: injury not in text: {x!r}" for x in lab["inj"] if x not in inj]
        problems += [f"row {i}: hazard not in text: {x!r}" for x in lab["haz"] if x not in haz]
        rows.append({
            "id": c["id"], "text": text, "mapped_type": c["incident_type"], "incident_type": lab["t"],
            "severity": lab["s"], "location": loc or "", "people_affected": "" if lab["p"] is None else lab["p"],
            "injuries": LIST_SEP.join(inj), "hazards": LIST_SEP.join(haz), "summary": lab["sum"],
            "data_source": c["data_source"], "event": c["event"], "verified": "", "notes": "",
        })
    out = pd.DataFrame(rows)
    out.to_csv(GOLD / "gold_review.csv", index=False, quoting=csv.QUOTE_NONNUMERIC)
    print(f"wrote data/gold/gold_review.csv: {len(out)} rows ({len(cand) - len(out)} dropped)")
    print("type changed from the event-based mapping:", int((out["incident_type"] != out["mapped_type"]).sum()))
    print(out["incident_type"].value_counts().to_string())
    for p in problems:
        print("WARNING", p)


def finalize() -> None:
    df = pd.read_csv(GOLD / "gold_review.csv", dtype=str, keep_default_na=False)
    df = df[df["verified"].str.strip().isin(["1", "2"])]
    out = []
    for _, r in df.iterrows():
        text = r["text"]
        assert r["incident_type"] in INCIDENT_TYPES, (r["id"], r["incident_type"])
        split = lambda v: [x.strip() for x in v.split(";") if x.strip()]
        fields = {
            "location": r["location"] or None,
            "people_affected": int(r["people_affected"]) if r["people_affected"].strip().isdigit() else None,
            "injuries": [x for x in split(r["injuries"]) if in_text(x, text)],
            "hazards": [x for x in split(r["hazards"]) if in_text(x, text)],
            "summary": r["summary"],
        }
        if fields["location"] and not in_text(fields["location"], text):
            fields["location"] = None
        out.append({
            "id": r["id"], "text": text, "incident_type": r["incident_type"], "severity": float(r["severity"]),
            "fields_json": json.dumps(fields, ensure_ascii=False), "data_source": r["data_source"],
            "split": "gold", "style": "", "event": r["event"], "humanitarian_label": "",
        })
    gold = pd.DataFrame(out)
    gold.to_csv(GOLD / "gold.csv", index=False, quoting=csv.QUOTE_NONNUMERIC)
    print(f"wrote data/gold/gold.csv: {len(gold)} verified rows")
    print(gold["incident_type"].value_counts().to_string())


if __name__ == "__main__":
    {"prelabel": prelabel, "finalize": finalize}[sys.argv[1] if len(sys.argv) > 1 else "prelabel"]()
