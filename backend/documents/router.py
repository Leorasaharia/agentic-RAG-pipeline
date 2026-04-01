from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os

from backend.db.session import get_db
from backend.db.models import User, Document, DocumentStatus
from backend.auth.utils import get_current_user
from backend.documents.s3 import upload_file_to_s3, delete_file_from_s3
from backend.documents.schemas import DocumentOut
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_TYPES = {"pdf", "txt", "docx"}
MAX_FILE_SIZE_MB = 50


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"File type '.{ext}' not supported. Allowed: {ALLOWED_TYPES}")

    # Upload to S3
    try:
        s3_key, s3_url = await upload_file_to_s3(file, str(current_user.id))
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="File upload to S3 failed")

    # Persist document record
    doc = Document(
        user_id=current_user.id,
        filename=file.filename,
        s3_key=s3_key,
        s3_url=s3_url,
        file_type=ext,
        file_size=file.size,
        status=DocumentStatus.PENDING,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # Dispatch async processing task
    from backend.workers.document_tasks import process_document_task
    process_document_task.delay(str(doc.id), s3_key, ext)

    logger.info(f"Document {doc.id} queued for processing")
    return doc


@router.get("/", response_model=List[DocumentOut])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Document).where(Document.user_id == current_user.id).order_by(Document.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{doc_id}", response_model=DocumentOut)
async def get_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.user_id == current_user.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.user_id == current_user.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.s3_key:
        try:
            delete_file_from_s3(doc.s3_key)
        except Exception:
            pass  # Log but don't block deletion

    await db.delete(doc)
    await db.commit()
