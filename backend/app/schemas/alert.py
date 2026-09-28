from pydantic import BaseModel, Field
from typing import List, Optional
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
