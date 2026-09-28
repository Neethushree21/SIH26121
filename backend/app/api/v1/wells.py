from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.well import Well
from app.models.user import User
from app.core.security import get_optional_current_user
from app.schemas.well import WellSummarySchema, WellDetailSchema, GeoJSONFeatureCollection
from app.schemas.query import NearbyWellsQuery, NearbyWellsResponse, OffsetWellResult
from app.services.geospatial import find_nearby_wells, generate_wells_geojson

router = APIRouter()

@router.get("", response_model=List[WellSummarySchema])
def list_wells(
    field_name: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Well)
    if field_name:
        query = query.filter(Well.field_name.ilike(f"%{field_name}%"))
    if status:
        query = query.filter(Well.status == status)
    
    wells = query.all()
    results = []
    for w in wells:
        results.append(WellSummarySchema(
            id=w.id,
            uwi=w.uwi,
            name=w.name,
            field_name=w.field_name,
            operator=w.operator,
            status=w.status,
            target_formation=w.target_formation,
            total_depth_tvd=w.total_depth_tvd,
            total_depth_md=w.total_depth_md,
            latitude=w.latitude,
            longitude=w.longitude,
            elevation_kb=w.elevation_kb,
            hazard_count=len(w.hazards)
        ))
    return results

@router.get("/geojson", response_model=GeoJSONFeatureCollection)
def get_wells_geojson(db: Session = Depends(get_db)):
    wells = db.query(Well).all()
    return generate_wells_geojson(wells)

@router.get("/nearby", response_model=NearbyWellsResponse)
def get_nearby_wells_get(
    latitude: float = Query(..., description="Target spud latitude in decimal degrees"),
    longitude: float = Query(..., description="Target spud longitude in decimal degrees"),
    radius_km: float = Query(default=10.0, ge=0.1, le=100.0, description="Spatial radius in km"),
    target_depth_md: Optional[float] = Query(default=None, description="Planned total depth MD/TVD (m)"),
    formation: Optional[str] = Query(default=None, description="Target formation (e.g. Barail, Tipam)"),
    planned_mud_weight: Optional[float] = Query(default=None, description="Planned mud weight (ppg)"),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Executes PostGIS ST_DWithin spatial query and ranks candidate offset wells
    using the Composite Offset Similarity Scoring algorithm:
      - 30% Formation Match
      - 25% Depth Proximity
      - 20% Spatial Proximity
      - 15% Drilling Parameter Similarity
      - 10% Historical Event Overlap
    """
    offset_wells = find_nearby_wells(
        db=db,
        target_lat=latitude,
        target_lon=longitude,
        radius_km=radius_km,
        target_depth=target_depth_md,
        formation=formation,
        planned_mud_weight=planned_mud_weight,
        limit=limit
    )

    return NearbyWellsResponse(
        target_latitude=latitude,
        target_longitude=longitude,
        radius_km=radius_km,
        total_found=len(offset_wells),
        offset_wells=[OffsetWellResult(**w) for w in offset_wells]
    )

@router.post("/nearby", response_model=NearbyWellsResponse)
def get_nearby_wells(
    payload: NearbyWellsQuery,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    offset_wells = find_nearby_wells(
        db=db,
        target_lat=payload.latitude,
        target_lon=payload.longitude,
        radius_km=payload.radius_km,
        target_depth=payload.target_depth_md,
        formation=payload.formation,
        planned_mud_weight=payload.planned_mud_weight,
        limit=payload.max_results
    )
    
    return NearbyWellsResponse(
        target_latitude=payload.latitude,
        target_longitude=payload.longitude,
        radius_km=payload.radius_km,
        total_found=len(offset_wells),
        offset_wells=[OffsetWellResult(**w) for w in offset_wells]
    )

@router.get("/{well_id}", response_model=WellDetailSchema)
def get_well_detail(well_id: str, db: Session = Depends(get_db)):
    well = db.query(Well).filter(Well.id == well_id).first()
    if not well:
        raise HTTPException(status_code=404, detail=f"Well with ID '{well_id}' not found.")
    
    return WellDetailSchema(
        id=well.id,
        uwi=well.uwi,
        name=well.name,
        field_name=well.field_name,
        operator=well.operator,
        status=well.status,
        target_formation=well.target_formation,
        total_depth_tvd=well.total_depth_tvd,
        total_depth_md=well.total_depth_md,
        latitude=well.latitude,
        longitude=well.longitude,
        elevation_kb=well.elevation_kb,
        hazard_count=len(well.hazards),
        spud_date=well.spud_date,
        completion_date=well.completion_date,
        trajectories=well.trajectories,
        formations=well.formations,
        hazards=well.hazards
    )
