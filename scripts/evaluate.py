"""Score the teammates' prediction CSVs and write every reported number in one place.

Inputs (all optional: whatever is missing is skipped with a message)
  predictions/<model>_<set>.csv       model: ml2 | baseline | ml3     set: test_synth | test_public | gold
                                      ML3 uses  ml3_test_flan.csv  and  ml3_gold.csv
  data/processed/{test_synth,test_public}.csv, data/gold/gold.csv    (the labels, never shared with the models)

Outputs
  reports/metrics.json          SCHEMA §8, read by the Streamlit metrics page
  reports/results.md            tables to paste into the slides
  reports/error_analysis.md     the most confident mistakes, worst severity errors, worst extractions
  reports/confusion_matrix_<set>_<model>.png

Run from the repo root:  .venv/bin/python scripts/evaluate.py [--pred-dir predictions] [--out reports]
"""
import argparse
import csv
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.flan import parse_target  # noqa: E402
from src.data.labels import INCIDENT_TYPES  # noqa: E402
from src.eval.metrics import (  # noqa: E402
    classification_metrics, confusion_counts, critical_recall, extraction_metrics, severity_metrics,
)

MODEL_NAMES = {"baseline": "baseline_tfidf_lr", "ml2": "distilbert", "ml3": "flan_t5"}
SETS = ["test_synth", "test_public", "gold"]
CLS_COLS = ["id", "pred_type"]
SEV_SETS = {"test_synth", "gold"}   # sets whose labels include severity and fields
IST = timezone(timedelta(hours=5, minutes=30))
warnings: list = []


def warn(msg: str) -> None:
    warnings.append(msg)
    print("WARNING:", msg)


# ---------------------------------------------------------------- loading

def load_labels(data_dir: Path) -> dict:
    paths = {"test_synth": data_dir / "processed" / "test_synth.csv",
             "test_public": data_dir / "processed" / "test_public.csv",
             "gold": data_dir / "gold" / "gold.csv"}
    out = {}
    for name, path in paths.items():
        if not path.exists():
            warn(f"labels not found for {name}: {path}")
            continue
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        df["severity_f"] = pd.to_numeric(df["severity"], errors="coerce")
        out[name] = df.set_index("id", drop=False)
    return out


def read_pred(path: Path, labels: pd.DataFrame, required: list):
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing_cols = [c for c in required if c not in df.columns]
    if missing_cols:
        warn(f"{path.name}: missing columns {missing_cols}, skipped")
        return None
    if df["id"].duplicated().any():
        warn(f"{path.name}: {int(df['id'].duplicated().sum())} duplicate ids, keeping the first")
        df = df.drop_duplicates("id")
    missing = set(labels.index) - set(df["id"])
    extra = set(df["id"]) - set(labels.index)
    if missing:
        warn(f"{path.name}: {len(missing)} of {len(labels)} ids have no prediction; scoring the {len(labels) - len(missing)} that do")
    if extra:
        warn(f"{path.name}: {len(extra)} unknown ids ignored")
    return df[df["id"].isin(labels.index)].set_index("id", drop=False)


# ---------------------------------------------------------------- scoring

def score_classification(model: str, set_name: str, labels: pd.DataFrame, pred: pd.DataFrame) -> dict:
    ids = [i for i in labels.index if i in pred.index]
    y_true, y_pred = labels.loc[ids, "incident_type"], pred.loc[ids, "pred_type"]
    bad = ~y_pred.isin(INCIDENT_TYPES)
    if bad.any():
        warn(f"{model}/{set_name}: {int(bad.sum())} predictions are not one of the 8 type names (counted as wrong)")
    m = classification_metrics(y_true, y_pred)
    m["confusion_matrix"] = confusion_counts(y_true, y_pred)
    if set_name in SEV_SETS:
        m["critical_recall"] = critical_recall(y_true, y_pred, labels.loc[ids, "severity_f"])
    if set_name == "test_public":
        m["per_source"] = {}
        for src in sorted(labels["data_source"].unique()):
            sub = [i for i in ids if labels.loc[i, "data_source"] == src]
            m["per_source"][src] = {"n": len(sub), "accuracy": float(np.mean(
                [labels.loc[i, "incident_type"] == pred.loc[i, "pred_type"] for i in sub]))}
    return m


def score_severity(model: str, set_name: str, labels: pd.DataFrame, pred: pd.DataFrame):
    if "pred_severity" not in pred.columns:
        return None
    ids = [i for i in labels.index if i in pred.index]
    p = pd.to_numeric(pred.loc[ids, "pred_severity"], errors="coerce")
    t = labels.loc[ids, "severity_f"]
    ok = p.notna() & t.notna()
    if not ok.any():
        return None
    return severity_metrics(t[ok], p[ok])


def _split_items(value: str) -> list:
    return [x.strip() for x in str(value).split(";") if x.strip()]


def pred_fields_from_row(row) -> dict:
    if "pred_location" in row.index:
        people = str(row.get("pred_people", "")).strip()
        return {"location": str(row["pred_location"]).strip() or None,
                "people_affected": int(float(people)) if people.replace(".", "", 1).isdigit() else None,
                "injuries": _split_items(row.get("pred_injuries", "")), "hazards": _split_items(row.get("pred_hazards", "")),
                "summary": str(row.get("pred_summary", ""))}
    return parse_target(row.get("raw_output", ""))


def score_extraction(set_name: str, labels: pd.DataFrame, pred: pd.DataFrame):
    ids = [i for i in labels.index if i in pred.index]
    true_fields = [json.loads(labels.loc[i, "fields_json"]) for i in ids]
    pred_fields = [pred_fields_from_row(pred.loc[i]) for i in ids]
    raw = pred.loc[ids, "raw_output"].tolist() if "raw_output" in pred.columns else None
    return extraction_metrics(true_fields, pred_fields, raw), ids, true_fields, pred_fields


# ---------------------------------------------------------------- outputs

def plot_confusion(matrix, title: str, path: Path) -> None:
    cm = np.array(matrix, dtype=float)
    norm = cm / np.maximum(cm.sum(axis=1, keepdims=True), 1)
    fig, ax = plt.subplots(figsize=(8, 6.5))
    ax.imshow(norm, cmap="Blues", vmin=0, vmax=1)
    short = [t.replace("_", "\n") for t in INCIDENT_TYPES]
    ax.set_xticks(range(len(short)), short, fontsize=7)
    ax.set_yticks(range(len(short)), short, fontsize=7)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(title, fontsize=10)
    for i in range(len(short)):
        for j in range(len(short)):
            if cm[i, j]:
                ax.text(j, i, int(cm[i, j]), ha="center", va="center", fontsize=8,
                        color="white" if norm[i, j] > 0.5 else "black")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def f(v, digits=3) -> str:
    return "-" if v is None else f"{v:.{digits}f}"


def write_results_md(res: dict, path: Path) -> None:
    L = ["# Results (generated by scripts/evaluate.py)", "",
         "Macro averages cover only the classes that occur in each test set (the gold set has no MEDICAL).",
         "Test sets: `test_synth` = call-style synthetic reports; `test_public` = real tweets with event-based labels "
         "(about 16% noisy); `gold` = real reports with checked labels.", ""]
    L += ["## Incident type", "", "| Test set | n | Model | Accuracy | Macro P | Macro R | Macro F1 | Emergency recall | False alarm | Critical recall |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for s in SETS:
        for model, d in res["classification"].items():
            if s in d:
                m = d[s]
                L.append(f"| {s} | {m['n']} | {model} | {f(m['accuracy'])} | {f(m['macro_precision'])} | {f(m['macro_recall'])} | "
                         f"{f(m['macro_f1'])} | {f(m['emergency_recall'])} | {f(m['false_alarm_rate'])} | {f(m.get('critical_recall'))} |")
    if res["severity"]:
        L += ["", "## Severity (regression)", "", "| Test set | n | Model | MSE | RMSE | MAE | Bucket accuracy | Within ±1 |", "|---|---|---|---|---|---|---|---|"]
        for model, d in res["severity"].items():
            for s, m in d.items():
                L.append(f"| {s} | {m['n']} | {model} | {f(m['mse'])} | {f(m['rmse'])} | {f(m['mae'])} | {f(m['bucket_accuracy'])} | {f(m['within_one'])} |")
    if res["extraction"]:
        L += ["", "## Field extraction", "",
              "| Test set | n | Parse rate | Location F1 | Location exact | People exact | Injuries F1 (strict / lenient) | Hazards F1 (strict / lenient) | ROUGE-L |",
              "|---|---|---|---|---|---|---|---|---|"]
        for model, d in res["extraction"].items():
            for s, m in d.items():
                L.append(f"| {s} | {m['n']} | {f(m.get('parse_rate'))} | {f(m['location_token_f1'])} | {f(m['location_exact'])} | "
                         f"{f(m['people_exact_match'])} | {f(m['injuries']['f1'])} / {f(m['injuries_lenient']['f1'])} | "
                         f"{f(m['hazards']['f1'])} / {f(m['hazards_lenient']['f1'])} | {f(m['summary_rougeL'])} |")
    srcs = {(mo, s): d[s]["per_source"] for mo, d in res["classification"].items() for s in d if "per_source" in d[s]}
    if srcs:
        L += ["", "## test_public accuracy by data source", "", "| Model | Source | n | Accuracy |", "|---|---|---|---|"]
        for (mo, _), d in srcs.items():
            for src, v in d.items():
                L.append(f"| {mo} | {src} | {v['n']} | {f(v['accuracy'])} |")
    if warnings:
        L += ["", "## Warnings", ""] + [f"- {w}" for w in warnings]
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def shown_text(df, i) -> str:
    """Synthetic reports are ours and shown in full; real tweets are shown by ID only, because their source
    datasets (HumAID, CrisisLexT26, Kaggle) do not allow redistributing tweet text."""
    return str(df.loc[i, "text"]) if str(i).startswith("synth") else f"tweet {i}"


def clip(text, n=110) -> str:
    text = str(text).replace("\n", " ")
    return text if len(text) <= n else text[: n - 1] + "…"


def write_error_analysis(cls_rows: dict, sev_rows: dict, ext_rows: dict, path: Path, top: int = 6) -> None:
    L = ["# Error analysis (generated by scripts/evaluate.py)", "",
         "Use two or three of these on the slides: what failed and why. Note that on `test_public` some labels are "
         "themselves wrong (event-based mapping), so check the text before blaming the model.", ""]
    for (model, s), rows in cls_rows.items():
        wrong = [r for r in rows if r["true"] != r["pred"]]
        wrong.sort(key=lambda r: -r["conf"])
        L += [f"## {model} on {s}: {len(wrong)} of {len(rows)} wrong, most confident first", "",
              "| True | Predicted | Conf. | Text |", "|---|---|---|---|"]
        L += [f"| {r['true']} | {r['pred']} | {f(r['conf'], 2)} | {clip(r['text'])} |" for r in wrong[:top]]
        L.append("")
    for (model, s), rows in sev_rows.items():
        rows.sort(key=lambda r: -abs(r["pred"] - r["true"]))
        L += [f"## {model} on {s}: largest severity errors", "", "| True | Predicted | Text |", "|---|---|---|"]
        L += [f"| {r['true']:.1f} | {r['pred']:.1f} | {clip(r['text'])} |" for r in rows[:top]]
        L.append("")
    for (model, s), rows in ext_rows.items():
        rows.sort(key=lambda r: -r["gap"])
        L += [f"## {model} on {s}: worst extractions", "", "| Text | Expected injuries / hazards | Predicted |", "|---|---|---|"]
        for r in rows[:top]:
            L.append(f"| {clip(r['text'], 80)} | {clip(r['true'], 60)} | {clip(r['pred'], 60)} |")
        L.append("")
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred-dir", default="predictions")
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--out", default="reports")
    args = ap.parse_args()
    pred_dir, out_dir = Path(args.pred_dir), Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    labels = load_labels(Path(args.data_dir))

    res = {"generated_at": datetime.now(IST).isoformat(timespec="seconds"), "eval_sets": {},
           "classification": {}, "severity": {}, "extraction": {}, "voice": None, "latency_ms": None,
           "confusion_matrix_png": None}
    cls_rows, sev_rows, ext_rows = {}, {}, {}

    for s, df in labels.items():
        res["eval_sets"][s] = {"n": len(df)}

    for model in ["baseline", "ml2"]:
        for s in SETS:
            path = pred_dir / f"{model}_{s}.csv"
            if s not in labels or not path.exists():
                continue
            pred = read_pred(path, labels[s], CLS_COLS)
            if pred is None:
                continue
            name = MODEL_NAMES[model]
            m = score_classification(model, s, labels[s], pred)
            res["classification"].setdefault(name, {})[s] = m
            png = out_dir / f"confusion_matrix_{s}_{model}.png"
            plot_confusion(m["confusion_matrix"], f"{name} on {s} (n={m['n']})", png)
            if model == "ml2" and s == "gold":
                res["confusion_matrix_png"] = str(png)
            sev = score_severity(model, s, labels[s], pred)
            if sev:
                res["severity"].setdefault(name, {})[s] = sev
            ids = [i for i in labels[s].index if i in pred.index]
            pcols = {t: f"p_{t}" for t in INCIDENT_TYPES if f"p_{t}" in pred.columns}
            cls_rows[(name, s)] = [{
                "true": labels[s].loc[i, "incident_type"], "pred": pred.loc[i, "pred_type"], "text": shown_text(labels[s], i),
                "conf": float(pred.loc[i, pcols[pred.loc[i, "pred_type"]]] or 0) if pred.loc[i, "pred_type"] in pcols else 0.0,
            } for i in ids]
            if sev and s in SEV_SETS:
                sev_rows[(name, s)] = [{"true": labels[s].loc[i, "severity_f"], "pred": float(np.clip(float(pred.loc[i, "pred_severity"]), 1, 5)),
                                        "text": shown_text(labels[s], i)} for i in ids if pred.loc[i, "pred_severity"] not in ("", None)]

    for s, fname in [("test_synth", "ml3_test_flan.csv"), ("gold", "ml3_gold.csv")]:
        path = pred_dir / fname
        if s not in labels or not path.exists():
            continue
        pred = read_pred(path, labels[s], ["id", "raw_output"])
        if pred is None:
            continue
        m, ids, true_f, pred_f = score_extraction(s, labels[s], pred)
        res["extraction"].setdefault(MODEL_NAMES["ml3"], {})[s] = m
        ext_rows[(MODEL_NAMES["ml3"], s)] = [{
            "text": shown_text(labels[s], i), "gap": len(set(t["injuries"]) ^ set(p["injuries"])) + len(set(t["hazards"]) ^ set(p["hazards"])),
            "true": f"{t['injuries']} / {t['hazards']}", "pred": f"{p['injuries']} / {p['hazards']}"}
            for i, t, p in zip(ids, true_f, pred_f)]

    if not (res["classification"] or res["extraction"]):
        print(f"No prediction files found in {pred_dir}/. Expected names such as ml2_gold.csv, baseline_test_synth.csv, ml3_gold.csv.")
    res["warnings"] = warnings

    (out_dir / "metrics.json").write_text(json.dumps(res, indent=2, default=float), encoding="utf-8")
    write_results_md(res, out_dir / "results.md")
    write_error_analysis(cls_rows, sev_rows, ext_rows, out_dir / "error_analysis.md")
    print(f"\nwrote {out_dir}/metrics.json, results.md, error_analysis.md and confusion matrices")
    print((out_dir / "results.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
