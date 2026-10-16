"""Metric functions for ResQPulse (docs/SCHEMA.md §8). Pure functions: no file IO, no printing."""
import re
from collections import Counter
from typing import Optional

import numpy as np
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

from src.data.labels import INCIDENT_TYPES, severity_label

NON = "NON_EMERGENCY"
FLAN_KEYS = ["location: ", "people: ", "injuries: ", "hazards: ", "summary: "]


# ---------------------------------------------------------------- classification

def classification_metrics(y_true, y_pred) -> dict:
    """Precision / recall / F1 per class, plus macro, weighted and the two safety numbers.

    Macro averages only cover classes that actually occur in y_true (the gold set has no MEDICAL,
    and counting that as 0 would punish the model for data that does not exist).
    """
    y_true, y_pred = list(y_true), list(y_pred)
    present = [c for c in INCIDENT_TYPES if c in set(y_true)]
    p, r, f, s = precision_recall_fscore_support(y_true, y_pred, labels=INCIDENT_TYPES, zero_division=0)
    idx = [INCIDENT_TYPES.index(c) for c in present]
    out = {
        "n": len(y_true),
        "accuracy": float(np.mean(np.array(y_true) == np.array(y_pred))),
        "macro_precision": float(np.mean(p[idx])),
        "macro_recall": float(np.mean(r[idx])),
        "macro_f1": float(np.mean(f[idx])),
        "weighted_f1": float(np.average(f[idx], weights=s[idx])),
        "classes_evaluated": present,
        "per_class": {c: {"precision": float(p[i]), "recall": float(r[i]), "f1": float(f[i]), "support": int(s[i])}
                      for i, c in enumerate(INCIDENT_TYPES)},
    }
    is_em = np.array([t != NON for t in y_true])
    pred_em = np.array([t != NON for t in y_pred])
    out["emergency_recall"] = float(pred_em[is_em].mean()) if is_em.any() else None   # real emergencies caught
    out["false_alarm_rate"] = float(pred_em[~is_em].mean()) if (~is_em).any() else None  # non-emergencies flagged
    return out


def critical_recall(y_true, y_pred, severity_true) -> Optional[float]:
    """Of the reports with true severity >= 4, the share NOT dismissed as NON_EMERGENCY (a miss costs most)."""
    mask = np.array([s >= 4.0 for s in severity_true])
    if not mask.any():
        return None
    pred = np.array(list(y_pred))
    return float((pred[mask] != NON).mean())


def confusion_counts(y_true, y_pred) -> list:
    return confusion_matrix(list(y_true), list(y_pred), labels=INCIDENT_TYPES).tolist()


# ---------------------------------------------------------------- severity (regression)

def severity_metrics(y_true, y_pred) -> dict:
    t = np.asarray(list(y_true), dtype=float)
    p = np.clip(np.asarray(list(y_pred), dtype=float), 1.0, 5.0)
    err = p - t
    return {
        "n": int(len(t)),
        "mse": float(np.mean(err ** 2)),
        "rmse": float(np.sqrt(np.mean(err ** 2))),
        "mae": float(np.mean(np.abs(err))),
        "bucket_accuracy": float(np.mean([severity_label(a) == severity_label(b) for a, b in zip(t, p)])),
        "within_one": float(np.mean(np.abs(err) <= 1.0)),
    }


# ---------------------------------------------------------------- extraction (Flan-T5)

def _tokens(text: Optional[str]) -> list:
    return re.findall(r"\w+", (text or "").lower())


def token_f1(a: Optional[str], b: Optional[str]) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    overlap = sum((Counter(ta) & Counter(tb)).values())
    if overlap == 0:
        return 0.0
    prec, rec = overlap / len(tb), overlap / len(ta)
    return 2 * prec * rec / (prec + rec)


def parses_ok(raw: str) -> bool:
    """True if the raw Flan-T5 line contains all five fields in the SCHEMA §4 format."""
    raw = str(raw)
    return all(k in raw for k in FLAN_KEYS)


def set_prf(true_lists, pred_lists, lenient: bool = False) -> dict:
    """Micro precision / recall / F1 over list items. lenient=True counts a pair as a match at token-F1 >= 0.5."""
    tp = fp = fn = 0
    for true, pred in zip(true_lists, pred_lists):
        true = [" ".join(_tokens(x)) for x in true if _tokens(x)]
        pred = [" ".join(_tokens(x)) for x in pred if _tokens(x)]
        if not lenient:
            ts, ps = set(true), set(pred)
            tp += len(ts & ps)
            fp += len(ps - ts)
            fn += len(ts - ps)
            continue
        unmatched = list(true)
        matched = 0
        for item in pred:
            best = max(unmatched, key=lambda t: token_f1(t, item), default=None)
            if best is not None and token_f1(best, item) >= 0.5:
                unmatched.remove(best)
                matched += 1
        tp += matched
        fp += len(pred) - matched
        fn += len(true) - matched
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {"precision": prec, "recall": rec, "f1": f1, "tp": tp, "fp": fp, "fn": fn}


def rouge_l(refs, hyps) -> float:
    from rouge_score import rouge_scorer
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=False)
    scores = [scorer.score(r, h)["rougeL"].fmeasure for r, h in zip(refs, hyps)]
    return float(np.mean(scores)) if scores else 0.0


def extraction_metrics(true_fields: list, pred_fields: list, raw_outputs: Optional[list] = None) -> dict:
    """true_fields / pred_fields: lists of dicts with location, people_affected, injuries, hazards, summary."""
    n = len(true_fields)
    loc_true = [t.get("location") for t in true_fields]
    loc_pred = [p.get("location") for p in pred_fields]
    out = {
        "n": n,
        "location_exact": float(np.mean([" ".join(_tokens(a)) == " ".join(_tokens(b)) for a, b in zip(loc_true, loc_pred)])),
        "location_token_f1": float(np.mean([token_f1(a, b) for a, b in zip(loc_true, loc_pred)])),
        "people_exact_match": float(np.mean([t.get("people_affected") == p.get("people_affected")
                                             for t, p in zip(true_fields, pred_fields)])),
        "injuries": set_prf([t.get("injuries") or [] for t in true_fields], [p.get("injuries") or [] for p in pred_fields]),
        "hazards": set_prf([t.get("hazards") or [] for t in true_fields], [p.get("hazards") or [] for p in pred_fields]),
        "injuries_lenient": set_prf([t.get("injuries") or [] for t in true_fields],
                                    [p.get("injuries") or [] for p in pred_fields], lenient=True),
        "hazards_lenient": set_prf([t.get("hazards") or [] for t in true_fields],
                                   [p.get("hazards") or [] for p in pred_fields], lenient=True),
        "summary_rougeL": rouge_l([t.get("summary") or "" for t in true_fields], [p.get("summary") or "" for p in pred_fields]),
    }
    if raw_outputs is not None:
        out["parse_rate"] = float(np.mean([parses_ok(r) for r in raw_outputs]))
    return out
