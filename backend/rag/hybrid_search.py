from typing import List, Dict
from rank_bm25 import BM25Okapi
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def hybrid_search(
    query: str,
    query_vector: List[float],
    candidate_chunks: List[Dict],
    top_k: int = None,
) -> List[Dict]:
    """
    Combine BM25 keyword scores with FAISS vector scores.
    candidate_chunks: list of dicts with 'text', 'score' (vector score), and metadata.
    """
    top_k = top_k or settings.TOP_K_RETRIEVAL

    if not candidate_chunks:
        return []

    # --- BM25 Scoring ---
    tokenized_corpus = [c["text"].lower().split() for c in candidate_chunks]
    bm25 = BM25Okapi(tokenized_corpus)
    bm25_scores = bm25.get_scores(query.lower().split())

    # --- Normalize both score sets to [0, 1] ---
    vector_scores = [c.get("score", 0.0) for c in candidate_chunks]

    def _normalize(scores):
        mn, mx = min(scores), max(scores)
        if mx == mn:
            return [1.0] * len(scores)
        return [(s - mn) / (mx - mn) for s in scores]

    norm_vector = _normalize(vector_scores)
    norm_bm25 = _normalize(list(bm25_scores))

    # --- Combine ---
    fused = []
    for i, chunk in enumerate(candidate_chunks):
        hybrid_score = (
            settings.VECTOR_WEIGHT * norm_vector[i]
            + settings.BM25_WEIGHT * norm_bm25[i]
        )
        fused.append({**chunk, "hybrid_score": hybrid_score})

    fused.sort(key=lambda x: x["hybrid_score"], reverse=True)
    logger.info(f"Hybrid search returned {min(top_k, len(fused))} results")
    return fused[:top_k]
