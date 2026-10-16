"""TF-IDF + Logistic Regression baseline for incident_type (SCHEMA §1.1).

Run in a Kaggle notebook (or locally):
    python scripts/baseline_tfidf_lr.py --data /kaggle/input/resqpulse-data --out outputs/baseline

Prints macro precision / recall / F1 on val and test, and writes prediction CSVs in the
same format as the DistilBERT model (id, pred_type, p_<TYPE> x8, pred_severity).
pred_severity is left empty: the baseline does not predict severity.

Macro scores are reported two ways:
  * present  - averaged over classes that appear in that split's gold labels (default, fair on v0
               which has no MEDICAL rows)
  * all8     - averaged over all 8 classes (absent classes count as 0)
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, precision_recall_fscore_support

SEED = 42
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
try:  # single source of truth when run inside the repo
    from src.data.labels import LABEL_MAP
except ImportError:  # identical to SCHEMA §9
    LABEL_MAP = {"FIRE": 0, "FLOOD": 1, "STORM_CYCLONE": 2, "EARTHQUAKE_COLLAPSE": 3,
                 "TRANSPORT_ACCIDENT": 4, "MEDICAL": 5, "VIOLENCE_CRIME": 6, "NON_EMERGENCY": 7}
LABELS = sorted(LABEL_MAP, key=LABEL_MAP.get)          # index order 0..7
IDX = list(range(len(LABELS)))

SPLIT_FILES = {"train": "public_train.csv", "val": "public_val.csv", "test": "public_test.csv"}


def load(data_dir, name):
    df = pd.read_csv(Path(data_dir) / name, dtype={"id": str}, keep_default_na=False)
    unknown = set(df["incident_type"]) - set(LABELS)
    if unknown:
        raise ValueError(f"{name}: labels not in LABEL_MAP: {sorted(unknown)}")
    df["y"] = df["incident_type"].map(LABEL_MAP)
    return df


def macro(y_true, y_pred, labels):
    p, r, f, _ = precision_recall_fscore_support(y_true, y_pred, labels=labels, average="macro", zero_division=0)
    return {"macro_precision": round(p, 4), "macro_recall": round(r, 4), "macro_f1": round(f, 4)}


def evaluate(name, y_true, y_pred):
    present = sorted(set(y_true))
    res = {"n": int(len(y_true)), "accuracy": round(accuracy_score(y_true, y_pred), 4),
           "present": macro(y_true, y_pred, present), "all8": macro(y_true, y_pred, IDX),
           "classes_present": [LABELS[i] for i in present]}
    print(f"\n=== {name} (n={res['n']}) ===")
    print(f"accuracy {res['accuracy']:.4f}")
    print("macro over classes present: P {macro_precision:.4f}  R {macro_recall:.4f}  F1 {macro_f1:.4f}".format(**res["present"]))
    print("macro over all 8 classes:   P {macro_precision:.4f}  R {macro_recall:.4f}  F1 {macro_f1:.4f}".format(**res["all8"]))
    missing = [l for i, l in enumerate(LABELS) if i not in present]
    if missing:
        print(f"(no gold rows for: {', '.join(missing)})")
    print(classification_report(y_true, y_pred, labels=present, target_names=[LABELS[i] for i in present],
                                digits=4, zero_division=0))
    return res


def write_predictions(df, probs, path):
    """probs: (n, 8) in LABEL_MAP order. Classes absent from training get probability 0."""
    out = pd.DataFrame({"id": df["id"], "pred_type": [LABELS[i] for i in probs.argmax(1)]})
    for i, lab in enumerate(LABELS):
        out[f"p_{lab}"] = probs[:, i].round(6)
    out["pred_severity"] = ""  # baseline has no severity head
    out.to_csv(path, index=False)
    print(f"wrote {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="/kaggle/input/resqpulse-data")
    ap.add_argument("--out", default="outputs/baseline")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    dfs = {k: load(args.data, v) for k, v in SPLIT_FILES.items()}
    for k, d in dfs.items():
        print(f"{k}: {len(d)} rows | " + ", ".join(f"{l}={c}" for l, c in d["incident_type"].value_counts().items()))

    word = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, lowercase=True, strip_accents="unicode")
    char = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True, lowercase=True)
    tr_text = dfs["train"]["text"]
    X = {"train": hstack([word.fit_transform(tr_text), char.fit_transform(tr_text)]).tocsr()}
    for k in ("val", "test"):
        X[k] = hstack([word.transform(dfs[k]["text"]), char.transform(dfs[k]["text"])]).tocsr()

    # choose C on val macro-F1 (classes present); test is never used for selection
    best = None
    for C in (0.5, 1.0, 2.0, 4.0, 8.0):
        clf = LogisticRegression(C=C, max_iter=3000, random_state=SEED)
        clf.fit(X["train"], dfs["train"]["y"])
        f1 = macro(dfs["val"]["y"], clf.predict(X["val"]), sorted(set(dfs["val"]["y"])))["macro_f1"]
        print(f"C={C:<4} val macro-F1 {f1:.4f}")
        if best is None or f1 > best[0]:
            best = (f1, C, clf)
    _, C, clf = best
    print(f"selected C={C}")

    results = {"model": "baseline_tfidf_lr", "C": C}
    for k in ("val", "test"):
        p_trained = clf.predict_proba(X[k])                   # columns = clf.classes_ (classes seen in train)
        probs = np.zeros((p_trained.shape[0], len(LABELS)))
        probs[:, clf.classes_] = p_trained
        pred = probs.argmax(1)
        results[k] = evaluate(f"public_{k}", dfs[k]["y"].to_numpy(), pred)
        write_predictions(dfs[k], probs, out / f"baseline_public_{k}_predictions.csv")
    (out / "baseline_metrics.json").write_text(json.dumps(results, indent=2))
    print(f"wrote {out / 'baseline_metrics.json'}")


if __name__ == "__main__":
    main()
