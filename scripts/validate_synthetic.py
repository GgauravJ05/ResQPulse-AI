"""Validate and convert synthetic reports to the SCHEMA §2 CSV format.

Reads  data/raw/synthetic/*.jsonl   (one JSON report per line, keys as in docs/SCHEMA.md §3.2)
Writes data/processed/synthetic_clean.csv   (split column is filled later by make_splits.py)

Checks: enums, severity range, length, word-for-word extraction (location / injuries / hazards must
appear in the text), near-duplicates (TF-IDF cosine > 0.9). Prints what was dropped and why.

Run from the repo root:  .venv/bin/python scripts/validate_synthetic.py
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.labels import INCIDENT_TYPES  # noqa: E402

RAW = Path("data/raw/synthetic")
OUT = Path("data/processed/synthetic_clean.csv")
STYLES = {"panicked_caller", "calm_bystander", "sms_shorthand", "whatsapp_message",
          "elderly_caller", "child_caller", "official_report", "vague_report"}
MIN_WORDS, MAX_WORDS = 5, 90   # short vague reports are realistic, so keep them
DUP_THRESHOLD = 0.9
COLUMNS = ["id", "text", "incident_type", "severity", "fields_json",
           "data_source", "split", "style", "event", "humanitarian_label"]


def in_text(item: str, text: str) -> bool:
    return bool(item) and item.lower() in text.lower()


def main() -> None:
    drops, fixes, rows = Counter(), Counter(), []
    for path in sorted(RAW.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                drops["bad json"] += 1
                continue
            text = " ".join(str(r.get("text", "")).split())
            n_words = len(text.split())
            if r.get("incident_type") not in INCIDENT_TYPES:
                drops["bad incident_type"] += 1
                continue
            if r.get("style") not in STYLES:
                drops["bad style"] += 1
                continue
            if not MIN_WORDS <= n_words <= MAX_WORDS:
                drops["length"] += 1
                continue
            try:
                severity = float(r["severity"])
            except (KeyError, TypeError, ValueError):
                drops["bad severity"] += 1
                continue
            if not 1.0 <= severity <= 5.0:
                drops["severity range"] += 1
                continue
            if r["incident_type"] == "NON_EMERGENCY" and severity != 1.0:
                severity = 1.0
                fixes["non-emergency severity forced to 1"] += 1

            location = r.get("location")
            if location is not None and not in_text(location, text):
                fixes["location not in text -> null"] += 1
                location = None
            injuries = [i for i in r.get("injuries", []) if in_text(i, text)]
            hazards = [h for h in r.get("hazards", []) if in_text(h, text)]
            if len(injuries) != len(r.get("injuries", [])):
                fixes["injury item not in text -> removed"] += 1
            if len(hazards) != len(r.get("hazards", [])):
                fixes["hazard item not in text -> removed"] += 1
            people = r.get("people_affected")
            people = int(people) if isinstance(people, (int, float)) and not isinstance(people, bool) else None
            summary = " ".join(str(r.get("summary", "")).replace("|", ",").split())
            if not summary:
                drops["empty summary"] += 1
                continue

            rows.append({
                "text": text,
                "incident_type": r["incident_type"],
                "severity": severity,
                "fields_json": json.dumps({
                    "location": location, "people_affected": people,
                    "injuries": injuries, "hazards": hazards, "summary": summary,
                }, ensure_ascii=False),
                "style": r["style"],
            })

    df = pd.DataFrame(rows)
    before = len(df)
    if before:
        tfidf = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True).fit_transform(df["text"])
        sim = cosine_similarity(tfidf)
        keep, seen = [], set()
        for i in range(len(df)):
            if any(sim[i, j] > DUP_THRESHOLD for j in keep):
                drops["near-duplicate"] += 1
                continue
            keep.append(i)
        df = df.iloc[keep].reset_index(drop=True)

    df.insert(0, "id", [f"synthetic-{i:06d}" for i in range(len(df))])
    df["data_source"] = "synthetic"
    df["split"] = ""
    df["event"] = ""
    df["humanitarian_label"] = ""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df[COLUMNS].to_csv(OUT, index=False, quoting=csv.QUOTE_NONNUMERIC)

    print(f"kept {len(df)} of {before + sum(v for k, v in drops.items() if k != 'near-duplicate')} reports")
    print("dropped:", dict(drops) or "nothing")
    print("fixed:  ", dict(fixes) or "nothing")
    print("\nper type:")
    print(df["incident_type"].value_counts().to_string())
    print("\nseverity:", df["severity"].describe()[["mean", "min", "max"]].round(2).to_dict())
    print("styles:", df["style"].value_counts().to_dict())
    print(f"mean words: {df['text'].str.split().str.len().mean():.1f}")


if __name__ == "__main__":
    main()
