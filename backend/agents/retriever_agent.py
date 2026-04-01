from typing import List, Dict
from backend.rag.embeddings import generate_single_embedding
from backend.rag.vector_store import get_vector_store
from backend.rag.hybrid_search import hybrid_search
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class RetrieverAgent:
    """Fetches top-k relevant chunks using hybrid search."""

    def run(self, query: str) -> List[Dict]:
        logger.info(f"[RetrieverAgent] Retrieving for: {query[:80]}")
        store = get_vector_store()

        # Vector search
        query_vector = generate_single_embedding(query)
        candidates = store.search(query_vector, top_k=settings.TOP_K_RETRIEVAL * 3)

        if not candidates:
            logger.warning("[RetrieverAgent] No candidates found in vector store")
            return []

        # Hybrid re-rank
        results = hybrid_search(query, query_vector, candidates, top_k=settings.TOP_K_RETRIEVAL)
        logger.info(f"[RetrieverAgent] Returned {len(results)} chunks")
        return results
