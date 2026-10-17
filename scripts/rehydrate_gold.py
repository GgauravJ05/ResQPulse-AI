"""Rebuild the gold test set's text files from the public source data.

The repository ships only our gold *labels* (data/gold/gold_labels.csv, data/gold/gold_audit_labels.csv): the tweet
text belongs to the source datasets (HumAID, CrisisLexT26, Kaggle Disaster Tweets), whose terms do not allow
redistributing it. Every gold report is a tweet from the held-out test split, so after building the public data
(scripts/build_public.py + scripts/make_splits.py) this script joins the text back on by ID.

Writes data/gold/gold.csv (labels + text, used by scripts/evaluate.py) and data/gold/gold_inputs.csv (id, text,
the unlabelled file the models predict on).

Run from the repo root:  python scripts/rehydrate_gold.py
"""
import sys
from pathlib import Path

import pandas as pd

GOLD = Path("data/gold")
SOURCE = Path("data/processed/test_public.csv")
COLUMNS = ["id", "text", "incident_type", "severity", "fields_json", "data_source", "split", "style", "event",
           "humanitarian_label"]


def main() -> None:
    if not SOURCE.exists():
        sys.exit(f"{SOURCE} not found: run scripts/build_public.py and scripts/make_splits.py first (see README).")
    labels = pd.read_csv(GOLD / "gold_labels.csv", dtype=str, keep_default_na=False)
    text = pd.read_csv(SOURCE, dtype=str, keep_default_na=False)[["id", "text"]]
    gold = labels.merge(text, on="id", how="left")
    missing = gold["text"].isna() | (gold["text"] == "")
    if missing.any():
        sys.exit(f"{int(missing.sum())} gold IDs not found in {SOURCE}; were the splits rebuilt with the same seed?")
    gold[COLUMNS].to_csv(GOLD / "gold.csv", index=False, quoting=1)
    gold[["id", "text"]].to_csv(GOLD / "gold_inputs.csv", index=False, quoting=1)
    print(f"wrote {GOLD/'gold.csv'} and {GOLD/'gold_inputs.csv'} ({len(gold)} rows)")


if __name__ == "__main__":
    main()
