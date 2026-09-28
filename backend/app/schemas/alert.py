from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class HazardAlert(BaseModel):
    id: str
    well_name: str
    uwi: str
    event_type: str
    severity: str
    depth_md: float
    formation_name: Optional[str] = None
    mud_weight_ppg: Optional[float] = None
    description: str
    remediation_action: Optional[str] = None
    distance_km: Optional[float] = None
    reported_date: Optional[datetime] = None

class RiskAssessmentRequest(BaseModel):
    latitude: float
    longitude: float
    planned_tvd: float
    target_formation: Optional[str] = None
    radius_km: float = 5.0

class RiskCategorySummary(BaseModel):
    category: str # Losses, Gas Kicks, Stuck Pipe, Overpressure
    count: int
    highest_severity: str
    key_warning: str

class RiskAssessmentResponse(BaseModel):
    target_location: dict
    radius_km: float
    overall_risk_score: str # LOW, MODERATE, ELEVATED, CRITICAL
    mud_weight_recommended_ppg: dict # min, max, surge_margin
    category_summaries: List[RiskCategorySummary]
    nearby_hazards: List[HazardAlert]
    drilling_recommendations: List[str]

# Phase 3: Explainable Evidence-Chain Schemas
class DocumentCitation(BaseModel):
    document_name: str
    page_number: int = 1
    well_name: str
    depth_interval: str
    snippet: str
    score: float

class EvidenceChainItem(BaseModel):
    offset_well_id: str
    offset_well_name: str
    offset_well_uwi: str
    distance_km: float
    depth_md: float
    formation_name: str
    historical_event: str
    incident_description: str
    npt_hours: float

class OffsetRiskAlert(BaseModel):
    id: str
    risk_type: str # Gas Kick, Loss of Circulation, Differential Stuck Pipe
    severity: str # LOW, MEDIUM, HIGH, CRITICAL
    probability_pct: float # e.g. 88.5%
    confidence_score: float # 0.0 to 1.0
    why_evidence_chain: List[EvidenceChainItem]
    recommended_mitigations: List[str]
    document_citations: List[DocumentCitation]
    timestamp: str

class OffsetRisksAuditResponse(BaseModel):
    target_spud: Dict[str, float]
    radius_km: float
    planned_depth_md: float
    target_formation: str
    overall_risk_tier: str
    total_risks_identified: int
    alerts: List[OffsetRiskAlert]

# Telemetry streaming schemas
class TelemetryTick(BaseModel):
    tick_index: int
    timestamp: str
    depth_md: float
    depth_tvd: float
    rop_m_hr: float
    wob_klbs: float
    torque_kft_lbs: float
    standpipe_pressure_psi: float
    mud_weight_in_ppg: float
    flow_out_pct: float
    active_formation: str

class TelemetryEvaluationResponse(BaseModel):
    telemetry: TelemetryTick
    ml_hazard_probabilities: Dict[str, float]
    hybrid_risk_tier: str # LOW, MEDIUM, HIGH, CRITICAL
    active_warning: Optional[str] = None
    offset_risk_factors: List[str] = []
