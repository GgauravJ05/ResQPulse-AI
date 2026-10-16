"""ML2: incident classifier interface (SCHEMA §5).

    from src.models.classifier import classify
    result = classify("Fire near FC road petrol pump, 3 people stuck inside")
    result.incident_type, result.probs, result.severity, result.attention

The model is loaded ONCE, when this module is imported. Folder (SCHEMA §9):
    models/classifier/   (override with env var RESQPULSE_CLASSIFIER_DIR)
If loading fails, the module still imports; classify() then raises ModelNotReady,
which the API maps to MODEL_NOT_READY (HTTP 503). Use is_ready() for /health.

Attention heatmap = attention rollout (Abnar & Zuidema, 2020):
  1. average each layer's attention over its heads
  2. add the identity (residual connection) and re-normalise rows
  3. multiply the layers together (layer 1 -> layer 6)
  4. take the [CLS] row = how much the final [CLS] vector draws on each token
  5. drop [CLS]/[SEP], merge word pieces into words (max over pieces), scale so max = 1
"""
import os
from pathlib import Path
from typing import Literal

import torch
from pydantic import BaseModel
from transformers import AutoTokenizer

from src.models.two_head import LABELS, TwoHeadClassifier, unit_to_sev

IncidentType = Literal["FIRE", "FLOOD", "STORM_CYCLONE", "EARTHQUAKE_COLLAPSE",
                       "TRANSPORT_ACCIDENT", "MEDICAL", "VIOLENCE_CRIME", "NON_EMERGENCY"]

MAX_LEN = 128                      # SCHEMA §9
REPO_ROOT = Path(__file__).resolve().parents[2]
_raw_dir = os.environ.get("RESQPULSE_CLASSIFIER_DIR") or os.environ.get("CLASSIFIER_DIR") or "models/classifier"
MODEL_DIR = Path(_raw_dir) if Path(_raw_dir).is_absolute() else REPO_ROOT / _raw_dir
MODEL_VERSION = "distilbert-v1"


class ClassifyResult(BaseModel):
    incident_type: IncidentType
    probs: dict[str, float]                     # all 8 types, sums to 1
    severity: float                             # 1.0-5.0, clipped
    attention: list[tuple[str, float]]          # (word, score), in text order, scores 0-1 (max = 1)


class ModelNotReady(RuntimeError):
    pass


# ---------------------------------------------------------------- load once at import
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_model = _tokenizer = None
_load_error = None
try:
    _tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    _model = TwoHeadClassifier.load(MODEL_DIR, device=_device, attn_implementation="eager")
except Exception as e:  # keep the API importable; report via is_ready()/classify()
    _load_error = f"{type(e).__name__}: {e}"


def is_ready() -> bool:
    return _model is not None


# ---------------------------------------------------------------- attention rollout
def attention_rollout(attentions):
    """attentions: tuple of (1, heads, T, T) per layer -> (T,) importance of each token for [CLS]."""
    result = None
    for layer in attentions:
        a = layer[0].float().mean(0)                                   # (T, T), mean over heads
        a = a + torch.eye(a.size(0), device=a.device)                  # residual connection
        a = a / a.sum(-1, keepdim=True)
        result = a if result is None else a @ result
    return result[0]                                                    # [CLS] row


def words_with_scores(text, enc, token_scores):
    """Merge word pieces into words using the tokenizer's word ids + character offsets.
    Words are cut from the original text, so casing is preserved. Punctuation-only words are skipped."""
    word_ids = enc.word_ids(0)
    offsets = enc["offset_mapping"][0].tolist()
    spans, scores = {}, {}
    for i, w in enumerate(word_ids):
        if w is None:                                                   # [CLS], [SEP]
            continue
        s, e = offsets[i]
        if w not in spans:
            spans[w], scores[w] = [s, e], token_scores[i]
        else:
            spans[w][1] = e
            scores[w] = max(scores[w], token_scores[i])
    out = []
    for w in sorted(spans):
        word = text[spans[w][0]:spans[w][1]]
        if any(ch.isalnum() for ch in word):
            out.append((word, scores[w]))
    top = max((s for _, s in out), default=0.0)
    return [(w, round(s / top, 4) if top > 0 else 0.0) for w, s in out]


# ---------------------------------------------------------------- public API
@torch.no_grad()
def classify(text: str) -> ClassifyResult:
    if not is_ready():
        raise ModelNotReady(f"classifier not loaded from {MODEL_DIR}: {_load_error}")
    if not text or not text.strip():
        raise ValueError("EMPTY_INPUT")
    enc = _tokenizer(text, truncation=True, max_length=MAX_LEN, return_offsets_mapping=True, return_tensors="pt")
    logits, sev_unit, attentions = _model(enc["input_ids"].to(_device), enc["attention_mask"].to(_device),
                                          output_attentions=True)
    probs = torch.softmax(logits[0].float(), -1).cpu().tolist()
    incident_type = LABELS[max(range(len(LABELS)), key=lambda i: probs[i])]
    severity = 1.0 if incident_type == "NON_EMERGENCY" else round(float(unit_to_sev(sev_unit[0].float().item())), 2)
    token_scores = attention_rollout(attentions).cpu().tolist()
    return ClassifyResult(
        incident_type=incident_type,
        probs={lab: float(p) for lab, p in zip(LABELS, probs)},
        severity=severity,
        attention=words_with_scores(text, enc, token_scores),
    )
