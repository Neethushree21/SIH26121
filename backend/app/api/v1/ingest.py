import os
import shutil
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.database import get_db, SessionLocal
from app.core.config import settings
from app.models.document import IngestedDocument
from app.models.user import User
from app.core.security import get_optional_current_user
from app.services.ingestion import ingestion_service, INGESTION_TASKS
from app.services.vector_store import vector_store_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class FolderIngestRequest(BaseModel):
    folder_path: str = Field(..., description="Server-side directory path to recursively scan and ingest")

@router.post("/folder")
def trigger_folder_ingestion(
    payload: FolderIngestRequest,
    background_tasks: BackgroundTasks,
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Scans a folder recursively for .pdf, .csv, .xlsx, .txt files,
    preserves metadata hierarchy, and processes them in asynchronous batches of 10.
    """
    clean_path = os.path.normpath(payload.folder_path)
    if not os.path.isabs(clean_path) and not os.path.exists(clean_path):
        # Resolve against workspace root
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        candidate = os.path.normpath(os.path.join(base_dir, clean_path))
        if os.path.exists(candidate):
            clean_path = candidate

    if not os.path.exists(clean_path):
        raise HTTPException(status_code=400, detail=f"Directory '{clean_path}' does not exist on server.")
    if not os.path.isdir(clean_path):
        raise HTTPException(status_code=400, detail=f"Path '{clean_path}' is not a directory.")

    task_id = str(uuid.uuid4())
    INGESTION_TASKS[task_id] = {
        "task_id": task_id,
        "folder_path": clean_path,
        "status": "QUEUED",
        "total_files": 0,
        "processed_files": 0,
        "processed_file_names": [],
        "current_batch": 0,
        "total_batches": 0,
        "indexed_chunks": 0,
        "errors": [],
        "created_at": datetime.utcnow().isoformat()
    }

    background_tasks.add_task(
        ingestion_service.process_folder_batch_async,
        task_id=task_id,
        folder_path=clean_path,
        db_session_factory=SessionLocal
    )

    return {
        "task_id": task_id,
        "status": "QUEUED",
        "folder_path": clean_path,
        "message": "Asynchronous batch folder ingestion initiated. Track progress via /api/v1/ingest/status/{task_id}."
    }

@router.get("/status/{task_id}")
def get_task_status(task_id: str):
    """Returns real-time progress of an asynchronous batch folder ingestion task."""
    task = INGESTION_TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Ingestion task '{task_id}' not found.")
    return task

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Uploads a report (PDF, TXT, CSV, XLSX) and processes it into the vector store."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    res = ingestion_service.ingest_single_file(db=db, file_path=file_path)
    
    return {
        "message": f"File '{file.filename}' processed with PyMuPDF semantic chunking.",
        "document_id": res["document_id"],
        "chunks_indexed": res["chunks_count"],
        "well_name": res["well_name"],
        "field_name": res["field_name"],
        "status": "INDEXED"
    }

@router.get("/status")
def get_all_ingested_documents(db: Session = Depends(get_db)):
    """Returns list of all ingested technical reports with chunk counts and indexing status."""
    docs = db.query(IngestedDocument).order_by(IngestedDocument.created_at.desc()).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "file_type": d.file_type,
            "file_size_bytes": d.file_size_bytes,
            "well_name": d.well_name,
            "chunk_count": d.chunk_count,
            "status": d.status,
            "created_at": d.created_at
        }
        for d in docs
    ]

@router.delete("/purge/all")
def purge_all_documents(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Purges all documents from the ingested documents database and vector store.
    """
    docs = db.query(IngestedDocument).all()
    count = len(docs)
    for doc in docs:
        vector_store_service.delete_document(doc.filename)
        upload_file_path = os.path.join(settings.UPLOAD_DIR, doc.filename)
        if os.path.exists(upload_file_path):
            try:
                os.remove(upload_file_path)
            except Exception as e:
                logger.warning(f"Could not remove {upload_file_path}: {e}")
        db.delete(doc)
    db.commit()
    return {
        "success": True,
        "message": f"Successfully deleted {count} documents from database and vector index.",
        "purged_count": count
    }

@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Deletes an ingested document by ID or filename, purges its vector embeddings from ChromaDB,
    removes any physical file on disk, and deletes all matching records from the database.
    """
    doc = db.query(IngestedDocument).filter(
        (IngestedDocument.id == document_id) | (IngestedDocument.filename == document_id)
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")

    filename = doc.filename
    # 1. Purge from vector store
    deleted_chunks = vector_store_service.delete_document(filename)

    # 2. Delete physical file from disk locations if present
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    possible_paths = [
        os.path.join(settings.UPLOAD_DIR, filename),
        os.path.join(base_dir, "uploads", filename),
        os.path.join(base_dir, "backend", "uploads", filename),
        os.path.join(base_dir, "sample_data", "reports", filename),
    ]
    for p in possible_paths:
        if os.path.exists(p):
            try:
                os.remove(p)
                logger.info(f"Removed physical file: {p}")
            except Exception as e:
                logger.warning(f"Could not remove physical file {p}: {e}")

    # 3. Delete ALL records matching this filename (or ID) from SQL DB
    deleted_db_rows = db.query(IngestedDocument).filter(
        (IngestedDocument.filename == filename) | (IngestedDocument.id == document_id)
    ).delete(synchronize_session=False)
    db.commit()

    return {
        "success": True,
        "message": f"Successfully deleted '{filename}' and purged its vector chunks.",
        "deleted_id": document_id,
        "filename": filename,
        "deleted_records": deleted_db_rows
    }

