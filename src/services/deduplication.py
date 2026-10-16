import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Optional, Tuple, Dict

print("Loading SentenceTransformer for deduplication (all-MiniLM-L6-v2)...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# In-memory store to hold the embeddings of past alerts
# Format: { "RQP-000001": np.ndarray, ... }
embedding_store: Dict[str, np.ndarray] = {}

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculates cosine similarity between two vectors."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def find_duplicate(new_text: str, alert_store: dict) -> Tuple[Optional[str], np.ndarray]:
    """
    Compares the new report text against existing alerts.
    Returns the duplicate alert_id (if > 0.85 similarity) and the new embedding.
    """
    # 1. Compute embedding for the incoming report
    new_emb = embedder.encode(new_text)
    
    best_score = -1.0
    best_id = None
    
    # 2. Compare against all previous alerts in the queue
    for alert_id in alert_store.keys():
        if alert_id in embedding_store:
            existing_emb = embedding_store[alert_id]
            score = cosine_similarity(new_emb, existing_emb)
            
            if score > best_score:
                best_score = score
                best_id = alert_id
                
    # 3. Apply the 0.85 threshold rule
    if best_score > 0.85:
        print(f"Duplicate found! Matched {best_id} with score {best_score:.2f}")
        return best_id, new_emb
        
    return None, new_emb

def register_embedding(alert_id: str, embedding: np.ndarray):
    """Saves the embedding of a new alert for future comparisons."""
    embedding_store[alert_id] = embedding