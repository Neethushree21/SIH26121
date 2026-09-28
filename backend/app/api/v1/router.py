from fastapi import APIRouter
from app.api.v1.wells import router as wells_router
from app.api.v1.search import router as search_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.ingest import router as ingest_router
from app.api.v1.rtmac import router as rtmac_router

api_router = APIRouter()

api_router.include_router(wells_router, prefix="/wells", tags=["Wells & Geospatial"])
api_router.include_router(search_router, prefix="/search", tags=["Vector RAG Search"])
api_router.include_router(alerts_router, prefix="/alerts", tags=["Drilling Hazards & Alerts"])
api_router.include_router(ingest_router, prefix="/ingest", tags=["Folder Ingestion & Reports"])
api_router.include_router(rtmac_router, prefix="/rtmac", tags=["eRTMAC Telemetry & Real-Time ML"])
