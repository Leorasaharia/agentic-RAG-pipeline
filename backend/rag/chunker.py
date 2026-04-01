from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict
import io
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def load_text_from_bytes(content: bytes, file_type: str) -> str:
    """Extract raw text from file bytes based on file type."""
    if file_type == "txt":
        return content.decode("utf-8", errors="ignore")

    elif file_type == "pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(content))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            logger.error(f"PDF parse error: {e}")
            return ""

    elif file_type == "docx":
        try:
            import docx
            doc = docx.Document(io.BytesIO(content))
            return "\n".join(para.text for para in doc.paragraphs)
        except Exception as e:
            logger.error(f"DOCX parse error: {e}")
            return ""

    return ""


def chunk_text(text: str) -> List[Dict]:
    """Split text into chunks and return list of {chunk_id, text, token_count}."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    chunks = splitter.split_text(text)
    result = []
    for i, chunk in enumerate(chunks):
        result.append({
            "chunk_id": i,
            "text": chunk.strip(),
            "token_count": len(chunk.split()),
        })
    logger.info(f"Split into {len(result)} chunks")
    return result
