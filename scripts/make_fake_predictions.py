"""Write FAKE prediction files with realistic noise, to test scripts/evaluate.py before the real ones exist.

The numbers these produce mean nothing about our models. Never copy them into slides.

Run from the repo root:  .venv/bin/python scripts/make_fake_predictions.py --out /tmp/fake_predictions
"""
import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.flan import format_target  # noqa: E402
from src.data.labels import INCIDENT_TYPES  # noqa: E402

rng = np.random.default_rng(0)


def fake_classifier(df: pd.DataFrame, accuracy: float, with_severity: bool) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        true = r["incident_type"]
        pred = true if rng.random() < accuracy else str(rng.choice([t for t in INCIDENT_TYPES if t != true]))
        probs = rng.dirichlet(np.ones(len(INCIDENT_TYPES)) * 0.5)
        top = rng.uniform(0.55, 0.97)
        probs = probs / probs.sum() * (1 - top)
        row = {"id": r["id"], "pred_type": pred}
        for t, p in zip(INCIDENT_TYPES, probs):
            row[f"p_{t}"] = round(float(top if t == pred else p), 4)
        if with_severity:
            sev = float(r["severity"]) if r["severity"] not in ("", None) else 2.5
            row["pred_severity"] = round(float(np.clip(sev + rng.normal(0, 0.8), 0.5, 5.5)), 2)
        rows.append(row)
    return pd.DataFrame(rows)


def fake_extractor(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        t = json.loads(r["fields_json"])
        loc = t["location"]
        u = rng.random()
        if loc and u < 0.15:
            loc = None
        elif loc and u < 0.30:
            loc = " ".join(loc.split()[:2])
        people = t["people_affected"] if rng.random() < 0.7 else (None if rng.random() < 0.5 else (t["people_affected"] or 1) + 1)
        keep = lambda items: [i for i in items if rng.random() < 0.8] + (["extra item"] if rng.random() < 0.1 else [])
        pred = {"location": loc, "people_affected": people, "injuries": keep(t["injuries"]),
                "hazards": keep(t["hazards"]), "summary": " ".join(t["summary"].split()[: int(rng.integers(6, 14))])}
        raw = format_target(pred)
        if rng.random() < 0.05:   # unparseable output, so parse_rate < 1
            rows.append({"id": r["id"], "raw_output": "the fire is near the market", "pred_location": "", "pred_people": "",
                         "pred_injuries": "", "pred_hazards": "", "pred_summary": ""})
            continue
        rows.append({"id": r["id"], "raw_output": raw, "pred_location": pred["location"] or "",
                     "pred_people": "" if pred["people_affected"] is None else pred["people_affected"],
                     "pred_injuries": " ; ".join(pred["injuries"]), "pred_hazards": " ; ".join(pred["hazards"]),
                     "pred_summary": pred["summary"]})
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--data-dir", default="data")
    args = ap.parse_args()
    out, data = Path(args.out), Path(args.data_dir)
    out.mkdir(parents=True, exist_ok=True)
    sets = {"test_synth": data / "processed" / "test_synth.csv", "test_public": data / "processed" / "test_public.csv",
            "gold": data / "gold" / "gold.csv"}
    q = dict(index=False, quoting=csv.QUOTE_NONNUMERIC)
    for name, path in sets.items():
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        fake_classifier(df, 0.82 if name != "test_public" else 0.74, True).to_csv(out / f"ml2_{name}.csv", **q)
        fake_classifier(df, 0.62, False).to_csv(out / f"baseline_{name}.csv", **q)
        if name in ("test_synth", "gold"):
            fake_extractor(df).to_csv(out / ("ml3_test_flan.csv" if name == "test_synth" else "ml3_gold.csv"), **q)
    print("wrote fake predictions to", out, "->", sorted(p.name for p in out.iterdir()))


if __name__ == "__main__":
    main()
