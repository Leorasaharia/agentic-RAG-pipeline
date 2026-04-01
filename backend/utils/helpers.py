import uuid
from datetime import datetime


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.utcnow()


def chunk_list(lst: list, n: int) -> list:
    """Split list into chunks of size n."""
    return [lst[i : i + n] for i in range(0, len(lst), n)]


def sanitize_filename(filename: str) -> str:
    import re
    return re.sub(r"[^\w\-.]", "_", filename)
