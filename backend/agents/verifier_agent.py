from typing import List, Dict, Tuple
from openai import OpenAI
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class VerifierAgent:
    """Checks retrieved chunks for relevance and filters out noise."""

    def __init__(self):
        self._client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def run(self, query: str, chunks: List[Dict]) -> Tuple[List[Dict], List[str]]:
        logger.info(f"[VerifierAgent] Verifying {len(chunks)} chunks")
        if not chunks:
            return [], []

        verified = []
        issues = []

        context_preview = "\n---\n".join(
            [f"Chunk {i + 1}: {c['text'][:300]}" for i, c in enumerate(chunks)]
        )
        prompt = (
            f"Given the user query: '{query}'\n\n"
            f"Evaluate each chunk below and respond with a JSON list of booleans "
            f"(true if relevant, false if not). Only respond with the JSON array.\n\n"
            f"{context_preview}"
        )
        try:
            response = self._client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=100,
            )
            import json
            content = response.choices[0].message.content.strip()
            verdicts = json.loads(content)
            for i, (chunk, keep) in enumerate(zip(chunks, verdicts)):
                if keep:
                    verified.append(chunk)
                else:
                    issues.append(f"Chunk {i + 1} filtered as irrelevant")
        except Exception as e:
            logger.warning(f"[VerifierAgent] Verification failed, keeping all: {e}")
            verified = chunks  # Fall back to all chunks on error

        logger.info(f"[VerifierAgent] {len(verified)}/{len(chunks)} chunks passed")
        return verified, issues
