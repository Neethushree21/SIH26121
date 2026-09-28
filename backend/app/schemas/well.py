from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

class TrajectoryPointSchema(BaseModel):
    id: str
    md: float
    tvd: float
    inclination: float
    azimuth: float
    latitude: float
    longitude: float
    dogleg_severity: Optional[float] = 0.0

    class Config:
        from_attributes = True

class FormationTopSchema(BaseModel):
    id: str
    formation_name: str
    top_md: float
    top_tvd: float
    base_tvd: Optional[float] = None
    lithology_description: Optional[str] = None
    pore_pressure_gradient_ppg: Optional[float] = None

    class Config:
        from_attributes = True

class DrillingHazardSchema(BaseModel):
    id: str
    event_type: str
    severity: str
    depth_md: float
    formation_name: Optional[str] = None
    mud_weight_ppg: Optional[float] = None
    description: str
    remediation_action: Optional[str] = None
    npt_hours: Optional[float] = 0.0
    reported_date: Optional[datetime] = None

    class Config:
        from_attributes = True

class WellSummarySchema(BaseModel):
    id: str
    uwi: str
    name: str
    field_name: str
    operator: str
    status: str
    target_formation: Optional[str] = None
    total_depth_tvd: float
    total_depth_md: float
    latitude: float
    longitude: float
    elevation_kb: float
    hazard_count: Optional[int] = 0

    class Config:
        from_attributes = True

class WellDetailSchema(WellSummarySchema):
    spud_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    trajectories: List[TrajectoryPointSchema] = []
    formations: List[FormationTopSchema] = []
    hazards: List[DrillingHazardSchema] = []

    class Config:
        from_attributes = True

class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: Dict[str, Any]
    properties: Dict[str, Any]

class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]
