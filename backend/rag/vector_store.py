import os
import json
import pickle
import numpy as np
from typing import List, Dict, Optional
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class FAISSVectorStore:
    """FAISS-based vector store with metadata persistence."""

    def __init__(self):
        self.index = None
        self.metadata: List[Dict] = []
        self._dim = settings.EMBEDDING_DIMENSION
        self._index_path = settings.FAISS_INDEX_PATH
        self._meta_path = f"{self._index_path}.meta.json"
        os.makedirs(os.path.dirname(self._index_path) or ".", exist_ok=True)
        self._load()

    def _load(self):
        try:
            import faiss
            if os.path.exists(f"{self._index_path}.faiss"):
                self.index = faiss.read_index(f"{self._index_path}.faiss")
                with open(self._meta_path, "r") as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
                return
        except Exception as e:
            logger.warning(f"Could not load FAISS index: {e}")

        import faiss
        self.index = faiss.IndexFlatIP(self._dim)
        self.metadata = []

    def _save(self):
        import faiss
        faiss.write_index(self.index, f"{self._index_path}.faiss")
        with open(self._meta_path, "w") as f:
            json.dump(self.metadata, f)

    def add_vectors(self, vectors: List[List[float]], metadata: List[Dict]):
        arr = np.array(vectors, dtype="float32")
        # Normalize for cosine similarity via inner product
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        arr = arr / (norms + 1e-10)
        self.index.add(arr)
        self.metadata.extend(metadata)
        self._save()
        logger.info(f"Added {len(vectors)} vectors. Total: {self.index.ntotal}")

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict]:
        arr = np.array([query_vector], dtype="float32")
        arr = arr / (np.linalg.norm(arr) + 1e-10)
        scores, indices = self.index.search(arr, top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            meta = dict(self.metadata[idx])
            meta["score"] = float(score)
            results.append(meta)
        return results

    def delete_by_doc_id(self, doc_id: str):
        """Remove all chunks belonging to a document (rebuild index)."""
        import faiss
        remaining = [(m, i) for i, m in enumerate(self.metadata) if m.get("doc_id") != doc_id]
        if not remaining:
            self.index = faiss.IndexFlatIP(self._dim)
            self.metadata = []
        else:
            metas, old_indices = zip(*remaining)
            self.metadata = list(metas)
            # Reconstruct index
            old_arr = np.zeros((self.index.ntotal, self._dim), dtype="float32")
            for i in range(self.index.ntotal):
                self.index.reconstruct(i, old_arr[i])
            new_arr = old_arr[list(old_indices)]
            self.index = faiss.IndexFlatIP(self._dim)
            self.index.add(new_arr)
        self._save()
        logger.info(f"Deleted vectors for doc_id={doc_id}")


# Singleton instance
_store: Optional[FAISSVectorStore] = None


def get_vector_store() -> FAISSVectorStore:
    global _store
    if _store is None:
        _store = FAISSVectorStore()
    return _store
