from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class CitationSource(BaseModel):
    document_name: str
    well_name: Optional[str] = "General OIL Field"
    formation: Optional[str] = None
    depth_interval: Optional[str] = None
    snippet: str
    score: float

class ChatQueryRequest(BaseModel):
    question: str = Field(..., description="Drilling engineering or offset well question")
    well_filter: Optional[str] = Field(default=None, description="Filter citations by well name")
    formation_filter: Optional[str] = Field(default=None, description="Filter citations by formation")
    top_k: int = Field(default=4, ge=1, le=10)

class ChatQueryResponse(BaseModel):
    question: str
    answer: str
    citations: List[CitationSource]
    suggested_followups: List[str] = []
