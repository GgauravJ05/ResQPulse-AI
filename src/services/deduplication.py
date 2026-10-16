"""Duplicate-report detection (BE2): a new report whose embedding is > 0.85 similar to an earlier alert gets duplicate_of set.

Optional feature. It needs `sentence-transformers` and a one-time download of all-MiniLM-L6-v2. The model is loaded on
first use, never at import, and if anything is missing the functions return (None, None) so the API keeps working.
"""
from typing import Dict, Optional, Tuple

import numpy as np

THRESHOLD = 0.85

embedding_store: Dict[str, np.ndarray] = {}      # alert_id -> embedding of that alert's text
_embedder = None
_unavailable = False


def _get_embedder():
    global _embedder, _unavailable
    if _embedder is None and not _unavailable:
        try:
            from sentence_transformers import SentenceTransformer
            _embedder = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            _unavailable = True
            print(f"duplicate detection disabled: {type(e).__name__}: {e}")
    return _embedder


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def find_duplicate(new_text: str, alert_store: dict) -> Tuple[Optional[str], Optional[np.ndarray]]:
    """Return (id of the most similar earlier alert if similarity > 0.85 else None, embedding of the new text)."""
    embedder = _get_embedder()
    if embedder is None:
        return None, None
    new_emb = embedder.encode(new_text)
    best_id, best_score = None, -1.0
    for alert_id in alert_store:
        existing = embedding_store.get(alert_id)
        if existing is not None:
            score = cosine_similarity(new_emb, existing)
            if score > best_score:
                best_id, best_score = alert_id, score
    return (best_id if best_score > THRESHOLD else None), new_emb


def register_embedding(alert_id: str, embedding: Optional[np.ndarray]) -> None:
    if embedding is not None:
        embedding_store[alert_id] = embedding
