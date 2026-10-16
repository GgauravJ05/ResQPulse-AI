"""Build the public-data splits (v0) from HumAID, CrisisLexT26 and Kaggle Disaster Tweets.

Reads  data/raw/{events_set1, CrisisLexT26, kaggle_disaster}
Writes data/processed/public_{train,val,test}.csv  (schema: docs/SCHEMA.md §2)

Run from the repo root:  .venv/bin/python scripts/build_public.py
"""
import csv
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.clean import clean_text  # noqa: E402
from src.data.labels import (  # noqa: E402
    CRISISLEX_EVENT_TYPE,
    CRISISLEX_TEST_CRISES,
    HUMAID_EVENT_TYPE,
    HUMAID_KEEP,
)

SEED = 42
TRAIN_CAP = 3000          # max training rows per incident type, so STORM_CYCLONE doesn't dominate
MIN_WORDS = 4
RAW = Path("data/raw")
OUT = Path("data/processed")
COLUMNS = ["id", "text", "incident_type", "severity", "fields_json",
           "data_source", "split", "style", "event", "humanitarian_label"]
SPLIT_NAME = {"train": "train", "dev": "val", "test": "test"}


def load_humaid() -> pd.DataFrame:
    rows = []
    for path in sorted((RAW / "events_set1").rglob("*.tsv")):
        m = re.match(r"(.+)_(train|dev|test)\.tsv$", path.name)
        if not m or m.group(1) not in HUMAID_EVENT_TYPE:
            continue
        event, part = m.group(1), m.group(2)  # event comes from the file name: two events sit in the wrong folder
        df = pd.read_csv(path, sep="\t", quoting=csv.QUOTE_NONE, dtype=str, keep_default_na=False)
        df = df[df["class_label"].isin(HUMAID_KEEP)]
        rows.append(pd.DataFrame({
            "id": "humaid-" + df["tweet_id"],
            "text": df["tweet_text"],
            "incident_type": HUMAID_EVENT_TYPE[event],
            "data_source": "humaid",
            "split": SPLIT_NAME[part],
            "event": event,
            "humanitarian_label": df["class_label"],
        }))
    return pd.concat(rows, ignore_index=True)


def load_crisislex(rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for path in sorted((RAW / "CrisisLexT26").glob("*/*-tweets_labeled.csv")):
        crisis = path.parent.name
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        df.columns = [c.strip() for c in df.columns]   # header has leading spaces
        info = df["Informativeness"].str.strip()
        etype = CRISISLEX_EVENT_TYPE.get(crisis)
        incident = pd.Series(np.nan, index=df.index, dtype=object)
        if etype:
            incident[info == "Related and informative"] = etype
        incident[info == "Not related"] = "NON_EMERGENCY"
        keep = incident.notna()
        df, incident = df[keep], incident[keep]
        if crisis in CRISISLEX_TEST_CRISES:
            split = pd.Series("test", index=df.index)
        else:
            split = pd.Series(np.where(rng.random(len(df)) < 0.1, "val", "train"), index=df.index)
        rows.append(pd.DataFrame({
            "id": "crisislex-" + df["Tweet ID"].str.strip(),
            "text": df["Tweet Text"],
            "incident_type": incident,
            "data_source": "crisislex",
            "split": split,
            "event": crisis,
            "humanitarian_label": df["Information Type"].str.strip(),
        }))
    return pd.concat(rows, ignore_index=True)


def load_kaggle(rng: np.random.Generator) -> pd.DataFrame:
    df = pd.read_csv(RAW / "kaggle_disaster" / "train.csv", dtype=str, keep_default_na=False)
    df = df[df["target"] == "0"]   # tweets that use disaster words without a real emergency
    r = rng.random(len(df))
    return pd.DataFrame({
        "id": "kaggle_disaster-" + df["id"],
        "text": df["text"],
        "incident_type": "NON_EMERGENCY",
        "data_source": "kaggle_disaster",
        "split": np.where(r < 0.70, "train", np.where(r < 0.85, "val", "test")),
        "event": "",
        "humanitarian_label": "",
    })


def main() -> None:
    rng = np.random.default_rng(SEED)
    df = pd.concat([load_humaid(), load_crisislex(rng), load_kaggle(rng)], ignore_index=True)
    print(f"loaded: {len(df):,} rows")

    df["text"] = df["text"].map(clean_text)
    df = df[df["text"].str.split().str.len() >= MIN_WORDS]

    # Drop exact duplicates (retweets, copies). Sort so the train copy is kept: no train/test leakage.
    df["_key"] = df["text"].str.lower()
    df["_order"] = df["split"].map({"train": 0, "val": 1, "test": 2})
    before = len(df)
    df = df.sort_values("_order", kind="stable").drop_duplicates("_key", keep="first")
    print(f"dropped {before - len(df):,} duplicates / too-short rows -> {len(df):,}")

    # Cap training rows per class
    parts = []
    for _, g in df.groupby("incident_type"):
        tr, rest = g[g["split"] == "train"], g[g["split"] != "train"]
        if len(tr) > TRAIN_CAP:
            tr = tr.sample(TRAIN_CAP, random_state=SEED)
        parts.append(pd.concat([tr, rest]))
    df = pd.concat(parts, ignore_index=True)

    df["severity"] = ""      # real tweets have no severity: the loss is masked for them
    df["fields_json"] = ""
    df["style"] = ""
    df = df[COLUMNS].sample(frac=1, random_state=SEED).reset_index(drop=True)

    OUT.mkdir(parents=True, exist_ok=True)
    for split in ["train", "val", "test"]:
        part = df[df["split"] == split]
        part.to_csv(OUT / f"public_{split}.csv", index=False, quoting=csv.QUOTE_NONNUMERIC)
        print(f"wrote public_{split}.csv: {len(part):,} rows")

    print("\nrows per incident_type x split:")
    print(pd.crosstab(df["incident_type"], df["split"]).assign(total=lambda t: t.sum(axis=1)))
    print("\nrows per data_source x split:")
    print(pd.crosstab(df["data_source"], df["split"]))


if __name__ == "__main__":
    main()
