from openai import OpenAI
from typing import List
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)
_client = None


def get_openai_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts (batched)."""
    client = get_openai_client()
    # OpenAI allows up to 2048 items per request; batch defensively
    all_embeddings = []
    for i in range(0, len(texts), 100):
        batch = texts[i : i + 100]
        response = client.embeddings.create(model=settings.EMBEDDING_MODEL, input=batch)
        all_embeddings.extend([item.embedding for item in response.data])
    logger.info(f"Generated {len(all_embeddings)} embeddings")
    return all_embeddings


def generate_single_embedding(text: str) -> List[float]:
    client = get_openai_client()
    response = client.embeddings.create(model=settings.EMBEDDING_MODEL, input=[text])
    return response.data[0].embedding
