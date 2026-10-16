"""Sample gold-set candidates: real reports the models never train on, balanced by incident type.

Reads  data/processed/test_public.csv   (HumAID test split + held-out CrisisLex crises)
Writes data/gold/gold_candidates.csv    (id, text, incident_type (mapped), data_source, event)

Run from the repo root:  .venv/bin/python scripts/sample_gold.py
"""
import csv
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

SEED = 42
PER_TYPE = 22
SRC = Path("data/processed/test_public.csv")
OUT = Path("data/gold/gold_candidates.csv")


def mostly_english(text: str) -> bool:
    return sum(c.isascii() for c in text) / max(len(text), 1) > 0.97


def main() -> None:
    df = pd.read_csv(SRC, dtype=str, keep_default_na=False)
    words = df["text"].str.split().str.len()
    df = df[(words >= 8) & (words <= 60) & df["text"].map(mostly_english)]
    df = df[~df["text"].str.contains(r"\b(?:donate|donation|sms|text|call)\b.*\d{4,}", case=False, regex=True)]
    parts = [g.sample(min(PER_TYPE, len(g)), random_state=SEED) for _, g in df.groupby("incident_type")]
    out = pd.concat(parts).sample(frac=1, random_state=SEED).reset_index(drop=True)
    out = out[["id", "text", "incident_type", "data_source", "event"]]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False, quoting=csv.QUOTE_NONNUMERIC)
    print(out["incident_type"].value_counts().to_string())
    print(f"wrote {OUT}: {len(out)} rows")


if __name__ == "__main__":
    main()
