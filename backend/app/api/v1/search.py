from fastapi import APIRouter, Depends
from typing import Optional
from app.schemas.chat import ChatQueryRequest, ChatQueryResponse, CitationSource
from app.services.vector_store import vector_store_service
from app.models.user import User
from app.core.security import get_optional_current_user

router = APIRouter()

@router.post("/query", response_model=ChatQueryResponse)
def query_knowledge_base(
    payload: ChatQueryRequest,
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    RAG endpoint: semantic search over historical Daily Drilling Reports (DDRs)
    and Well Completion Reports (WCRs).
    """
    citations = vector_store_service.search(
        query=payload.question,
        top_k=payload.top_k,
        well_filter=payload.well_filter,
        formation_filter=payload.formation_filter
    )
    
    answer = vector_store_service.synthesize_answer(payload.question, citations)
    
    followups = [
        "What was the mud weight window in Barail Sand for Nahorkatiya wells?",
        "Did Moran-88 experience stuck pipe during 12-1/4 inch section drilling?",
        "What LCM recipe successfully sealed the lost circulation zone in Baghjan-03?"
    ]
    
    return ChatQueryResponse(
        question=payload.question,
        answer=answer,
        citations=[CitationSource(**c) for c in citations],
        suggested_followups=followups
    )
