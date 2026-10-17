"""Build the public, redistributable release of the ResQPulse dataset (for Kaggle / Hugging Face).

What it contains, and why:
  * synthetic_reports.csv   all 710 call-style reports we generated, with every label (ours to share)
  * train_flan.csv, val_flan.csv, test_flan.csv   text-to-text pairs for the generator (synthetic only)
  * tweet_labels.csv        real tweets as ID + our labels + split, **no text** (the source datasets' terms do not
                            allow redistributing tweet text; rebuild it from HumAID / CrisisLexT26 / Kaggle by ID)
  * gold_labels.csv         the 144-report gold test set, ID + labels, no text
  * gold_audit_labels.csv   the 30-row human audit of the gold set, no text

Run from the repo root after building the data (see README):  python scripts/make_public_dataset.py
Writes dist/kaggle/ (git-ignored).
"""
import shutil
from pathlib import Path

import pandas as pd

PROCESSED = Path("data/processed")
GOLD = Path("data/gold")
OUT = Path("dist/kaggle")
SPLITS = ["train", "val", "test_public", "test_synth"]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    frames = [pd.read_csv(PROCESSED / f"{s}.csv", dtype=str, keep_default_na=False) for s in SPLITS]
    rows = pd.concat(frames, ignore_index=True)

    synth = rows[rows["data_source"] == "synthetic"].drop_duplicates("id")   # training rows are repeated 4x
    synth.to_csv(OUT / "synthetic_reports.csv", index=False, quoting=1)

    tweets = rows[rows["data_source"] != "synthetic"].drop(columns=["text", "severity", "fields_json", "style"])
    tweets.to_csv(OUT / "tweet_labels.csv", index=False, quoting=1)

    for name in ["train_flan", "val_flan", "test_flan"]:
        shutil.copy(PROCESSED / f"{name}.csv", OUT / f"{name}.csv")
    for name in ["gold_labels.csv", "gold_audit_labels.csv"]:
        shutil.copy(GOLD / name, OUT / name)

    assert "text" not in tweets.columns
    print(f"wrote {OUT}/: {len(synth)} synthetic reports, {len(tweets)} tweet labels (no text), "
          f"flan pairs, gold labels")


if __name__ == "__main__":
    main()
