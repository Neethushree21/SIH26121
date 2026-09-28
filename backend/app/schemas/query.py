from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.schemas.well import WellSummarySchema

class SimilarityBreakdown(BaseModel):
    formation_match: float = Field(..., description="30% Formation stratigraphic top match score (0-1)")
    depth_proximity: float = Field(..., description="25% TVD/MD depth alignment score (0-1)")
    spatial_proximity: float = Field(..., description="20% PostGIS distance score (0-1)")
    parameter_similarity: float = Field(..., description="15% Mud weight & drilling parameter score (0-1)")
    event_overlap: float = Field(..., description="10% Historical hazard & NPT value score (0-1)")
    composite_pct: float = Field(..., description="Overall weighted composite similarity percentage (0-100%)")

class NearbyWellsQuery(BaseModel):
    latitude: float = Field(..., description="Target spud latitude in decimal degrees")
    longitude: float = Field(..., description="Target spud longitude in decimal degrees")
    radius_km: float = Field(default=10.0, ge=0.1, le=100.0, description="Search radius in kilometers")
    target_depth_md: Optional[float] = Field(default=None, description="Planned total depth MD/TVD (m)")
    formation: Optional[str] = Field(default=None, description="Optional target formation filter (e.g. Barail, Tipam)")
    planned_mud_weight: Optional[float] = Field(default=None, description="Planned drilling fluid weight (ppg)")
    max_results: Optional[int] = Field(default=20, ge=1, le=100)

class OffsetWellResult(WellSummarySchema):
    distance_km: float
    bearing_degrees: float
    critical_hazards_count: int = 0
    nearest_formation: Optional[str] = None
    composite_similarity_score: float = 0.0
    similarity_breakdown: Optional[SimilarityBreakdown] = None

class NearbyWellsResponse(BaseModel):
    target_latitude: float
    target_longitude: float
    radius_km: float
    total_found: int
    offset_wells: List[OffsetWellResult]
