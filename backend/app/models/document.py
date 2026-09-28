from sqlalchemy import Column, String, Integer, DateTime, Text
from datetime import datetime
import uuid
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class IngestedDocument(Base):
    __tablename__ = "ingested_documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), default="PDF") # PDF, TXT, CSV, DDR, WCR
    file_size_bytes = Column(Integer, default=0)
    well_name = Column(String(100), nullable=True)
    chunk_count = Column(Integer, default=0)
    status = Column(String(50), default="INDEXED") # PROCESSING, INDEXED, FAILED
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
