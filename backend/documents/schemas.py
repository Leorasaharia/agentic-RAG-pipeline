from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from backend.db.models import DocumentStatus


class DocumentOut(BaseModel):
    id: UUID
    filename: str
    file_type: str
    file_size: Optional[int]
    status: DocumentStatus
    chunk_count: int
    s3_url: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True
