import json
from pathlib import Path
from typing import List, Dict

from .analyzer import get_embedding_vector


# Store JSON file next to this module
DB_FILE = Path(__file__).resolve().parent / "vector_store.json"


def _load_db() -> List[Dict]:
    if DB_FILE.exists():
        return json.loads(DB_FILE.read_text(encoding="utf-8"))
    return []


def _save_db(db: List[Dict]) -> None:
    DB_FILE.write_text(json.dumps(db, indent=2), encoding="utf-8")


def add_embedding(batch_id: int, text: str) -> None:
    """
    Compute an embedding vector for `text` and store it in a simple JSON file.
    """
    db = _load_db()
    vector = get_embedding_vector(text)

    db.append(
        {
            "batch_id": batch_id,
            "text": text,
            "vector": vector,
        }
    )

    _save_db(db)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    from math import sqrt

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sqrt(sum(x * x for x in a)) or 1.0
    norm_b = sqrt(sum(y * y for y in b)) or 1.0
    return dot / (norm_a * norm_b)


def search_embeddings(query: str, top_k: int = 5) -> List[Dict]:
    """
    Return top_k most similar stored items to the query text.
    Each item has: {batch_id, text, vector, score}
    """
    db = _load_db()
    if not db:
        return []

    q_vec = get_embedding_vector(query)

    scored: List[Dict] = []
    for item in db:
        score = _cosine_similarity(q_vec, item["vector"])
        scored.append({**item, "score": float(score)})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]
