"""Run the real extract() (src/models/generator.py) over the test inputs and write prediction CSVs.

Why: the scores on the slides must describe the pipeline that runs in the demo (generation + retry + fallback + people-count
rule), not a separate notebook run. Output formats follow docs/SCHEMA.md §8.1.

Writes <out>/ml3_test_flan.csv and <out>/ml3_gold.csv, and prints how many rows used the fallback.

Run from the repo root:  .venv/bin/python scripts/predict_generator.py --out predictions
"""
import argparse
import csv
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.flan import format_target  # noqa: E402
from src.models import generator  # noqa: E402


def run(texts: list, ids: list, path: Path) -> int:
    rows, fallback = [], 0
    t0 = time.time()
    for n, (i, text) in enumerate(zip(ids, texts), 1):
        r = generator.extract(text)
        fallback += r.extractor == "fallback_rules"
        fields = {"location": r.location, "people_affected": r.people_affected, "injuries": r.injuries,
                  "hazards": r.hazards, "summary": r.summary}
        rows.append({"id": i, "raw_output": format_target(fields), "pred_location": r.location or "",
                     "pred_people": "" if r.people_affected is None else r.people_affected,
                     "pred_injuries": " ; ".join(r.injuries), "pred_hazards": " ; ".join(r.hazards),
                     "pred_summary": r.summary, "extractor": r.extractor})
        if n % 25 == 0:
            print(f"  {path.name}: {n}/{len(texts)} ({time.time() - t0:.0f}s)", flush=True)
    pd.DataFrame(rows).to_csv(path, index=False, quoting=csv.QUOTE_NONNUMERIC)
    return fallback


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if not generator.is_ready():
        print("WARNING: model not loaded, everything will use the fallback:", generator._load_error)

    tf = pd.read_csv("data/processed/test_flan.csv", dtype=str, keep_default_na=False)
    gold = pd.read_csv("data/gold/gold_inputs.csv", dtype=str, keep_default_na=False)
    test_texts = [s.removeprefix("extract alert: ") for s in tf["input"]]
    fb1 = run(test_texts, tf["id"].tolist(), out / "ml3_test_flan.csv")
    fb2 = run(gold["text"].tolist(), gold["id"].tolist(), out / "ml3_gold.csv")
    print(f"done. fallback used: test_flan {fb1}/{len(tf)}, gold {fb2}/{len(gold)}")


if __name__ == "__main__":
    main()
