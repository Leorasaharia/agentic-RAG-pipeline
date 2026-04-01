from typing import List, Dict, Generator
from openai import OpenAI
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class RefinerAgent:
    """Takes verified chunks and generates the final coherent answer. Supports streaming."""

    def __init__(self):
        self._client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def run(self, query: str, context_chunks: List[Dict], stream: bool = False):
        logger.info(f"[RefinerAgent] Refining answer from {len(context_chunks)} chunks.")

        if not context_chunks:
            fallback_msg = "I could not find relevant information in the uploaded documents to answer your query."
            if stream:
                def fallback_stream():
                    yield fallback_msg
                    yield "[DONE]"
                return fallback_stream()
            return fallback_msg

        context_text = "\n\n---\n\n".join(
            [f"Document chunk: {c['text']}" for c in context_chunks]
        )

        system_prompt = (
            "You are a helpful and intelligent AI assistant analyzing uploaded documents.\n"
            "Answer the user's query gracefully using ONLY the provided document chunks.\n"
            "If the chunks do not contain the answer, say so explicitly.\n"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context_text}\n\nQuery: {query}"}
        ]

        try:
            response = self._client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=1024,
                stream=stream,
            )

            if stream:
                def generate_stream() -> Generator[str, None, None]:
                    for chunk in response:
                        if chunk.choices[0].delta.content is not None:
                            yield chunk.choices[0].delta.content
                    yield "[DONE]"

                return generate_stream()
            else:
                return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"[RefinerAgent] Text generation failed: {e}")
            msg = "An error occurred while generating the response."
            if stream:
                def err_stream():
                    yield msg
                    yield "[DONE]"
                return err_stream()
            return msg
