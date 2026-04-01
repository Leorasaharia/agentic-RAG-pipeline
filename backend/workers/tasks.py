from backend.workers.celery_app import celery_app
from backend.utils.logger import get_logger
from backend.rag.chunker import chunk_document
from backend.rag.vector_store import get_vector_store
from backend.rag.embeddings import generate_embeddings
from backend.db.session import SessionLocal
from backend.db.models import Document, Feedback
from sqlalchemy.orm import Session
import os

logger = get_logger(__name__)

@celery_app.task(bind=True, max_retries=3)
def document_processing_task(self, document_id: int):
    """Processes an uploaded document, chunks it, embeds it, and saves to FAISS vector DB synchronously."""
    logger.info(f"Starting chunking and embedding for document {document_id}")
    db: Session = SessionLocal()
    
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            logger.error(f"Document {document_id} not found in DB")
            return "Failed - doc missing"

        # Usually, fetch from S3 logic here using doc.s3_key.
        # Let's mock the document body parsing for brevity:
        # doc_text = fetch_from_s3(doc.s3_key)
        
        # We will assume chunk_document simulates this logic internally
        chunks = chunk_document("Sample mock document content fetched from bucket...")

        logger.info(f"Generated {len(chunks)} chunks.")
        
        store = get_vector_store()
        for idx, chunk in enumerate(chunks):
            vector = generate_embeddings([chunk['text']])[0]
            # Create a simple unique ID and metadata mapping
            chunk_id = f"doc_{document_id}_chk_{idx}"
            metadata = {"document_id": document_id, "text": chunk['text']}
            
            store.add(vectors=[vector], ids=[chunk_id], metadata=[metadata])

        # Commit Vector index
        store.save()
        logger.info(f"Document {document_id} embedded and stored successfully.")

        # Mark Document as processed
        doc.status = "processed"
        db.commit()
        return f"Successfully processed {len(chunks)} chunks."

    except Exception as exc:
        logger.error(f"Error processing doc {document_id}: {exc}")
        db.rollback()
        raise self.retry(exc=exc, countdown=10)
    finally:
        db.close()

@celery_app.task
def feedback_retraining_task(message_id: str, score: int):
    """Simulates retraining logic by adjusting vectors or logging scores."""
    logger.info(f"Activating feedback loop - updating heuristics for Msg {message_id} with score {score}.")
    
    db: Session = SessionLocal()
    try:
        fb = Feedback(message_id=message_id, score=score)
        db.add(fb)
        db.commit()
        logger.info(f"Feedback {score} recorded successfully for {message_id}.")
        return "Feedback Processed"
    except Exception as e:
        logger.error(f"Error updating feedback: {e}")
    finally:
        db.close()
