from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.drilling_event import DrillingHazard
from app.models.well import Well
from app.schemas.alert import HazardAlert, RiskAssessmentRequest, RiskAssessmentResponse, OffsetRisksAuditResponse
from app.services.risk_engine import risk_engine

router = APIRouter()

@router.get("/feed", response_model=List[HazardAlert])
def get_hazard_feed(
    severity: Optional[str] = None,
    limit: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Returns active and historical drilling hazard alerts across all Oil India fields."""
    query = db.query(DrillingHazard, Well).join(Well, DrillingHazard.well_id == Well.id)
    if severity:
        query = query.filter(DrillingHazard.severity == severity.upper())
    
    query = query.order_by(DrillingHazard.reported_date.desc())
    records = query.limit(limit).all()
    
    alerts = []
    for hazard, well in records:
        alerts.append(HazardAlert(
            id=hazard.id,
            well_name=well.name,
            uwi=well.uwi,
            event_type=hazard.event_type,
            severity=hazard.severity,
            depth_md=hazard.depth_md,
            formation_name=hazard.formation_name,
            mud_weight_ppg=hazard.mud_weight_ppg,
            description=hazard.description,
            remediation_action=hazard.remediation_action,
            distance_km=None,
            reported_date=hazard.reported_date
        ))
    return alerts

@router.post("/assess", response_model=RiskAssessmentResponse)
def assess_spud_location_risks(payload: RiskAssessmentRequest, db: Session = Depends(get_db)):
    """Computes comprehensive hazard matrix, safe mud weight window, and precautions for a new well spud."""
    return risk_engine.assess_risks(
        db=db,
        target_lat=payload.latitude,
        target_lon=payload.longitude,
        planned_tvd=payload.planned_tvd,
        radius_km=payload.radius_km,
        target_formation=payload.target_formation
    )

@router.get("/offset-risks", response_model=OffsetRisksAuditResponse)
def get_explainable_offset_risks(
    latitude: float = Query(..., description="Target spud latitude in decimal degrees"),
    longitude: float = Query(..., description="Target spud longitude in decimal degrees"),
    planned_depth_md: float = Query(default=3700.0, description="Planned total depth MD (m)"),
    radius_km: float = Query(default=10.0, ge=0.1, le=100.0, description="Corridor radius in km"),
    formation: Optional[str] = Query(default=None, description="Planned target formation (e.g. Barail, Tipam)"),
    db: Session = Depends(get_db)
):
    """
    Returns an explainable, audit-ready drilling hazard report with:
      1. Risk Type & Severity Score (Hybrid ML probability)
      2. The 'Why?' Evidence Chain (matched offset wells, distance, depth, formation)
      3. Recommended Mitigation Actions
      4. Exact Document Citations from ChromaDB (file, page, snippet)
    """
    return risk_engine.generate_evidence_chain_alerts(
        db=db,
        target_lat=latitude,
        target_lon=longitude,
        planned_depth_md=planned_depth_md,
        radius_km=radius_km,
        formation=formation
    )
