import math
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.well import Well, TrajectoryPoint, FormationTop
from app.models.drilling_event import DrillingHazard
from app.core.database import is_sqlite

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two points in kilometers."""
    R = 6371.0 # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates bearing from point 1 to point 2 in degrees (0-360)."""
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    dlon_r = math.radians(lon2 - lon1)
    y = math.sin(dlon_r) * math.cos(lat2_r)
    x = math.cos(lat1_r) * math.sin(lat2_r) - math.sin(lat1_r) * math.cos(lat2_r) * math.cos(dlon_r)
    initial_bearing = math.degrees(math.atan2(y, x))
    return (initial_bearing + 360) % 360

def compute_similarity_breakdown(
    well: Well,
    distance_km: float,
    radius_km: float,
    target_formation: Optional[str] = None,
    target_depth: Optional[float] = None,
    planned_mud_weight: Optional[float] = None,
    hazards: List[DrillingHazard] = None
) -> Tuple[float, Dict[str, float]]:
    """
    Computes Composite Offset Similarity Scoring:
      - 30% Formation Match (Barail/Tipam/Girujan)
      - 25% Depth Proximity (matching TVD/MD zones)
      - 20% Spatial Proximity (PostGIS distance)
      - 15% Drilling Parameter Similarity (mud weight & pore pressure)
      - 10% Historical Event Overlap (kicks, losses, stuck pipes)
    """
    # 1. Formation Match (30%)
    formation_score = 0.50
    well_target = (well.target_formation or "").lower()
    formation_names = [f.formation_name.lower() for f in (well.formations or [])]
    
    query_form = (target_formation or "Barail").lower()
    if query_form in well_target:
        formation_score = 1.00
    elif any(query_form in fn for fn in formation_names):
        formation_score = 0.88
    elif "barail" in query_form and any("tipam" in fn for fn in formation_names):
        formation_score = 0.65 # Adjacent stratigraphic unit in Assam Basin
    elif "tipam" in query_form and any("barail" in fn for fn in formation_names):
        formation_score = 0.65
    else:
        formation_score = 0.35

    # 2. Depth Proximity (25%)
    depth_score = 0.85
    if target_depth is not None and target_depth > 0:
        depth_diff = abs(well.total_depth_tvd - target_depth)
        # 1500m depth window for normalization
        depth_score = max(0.10, 1.0 - (depth_diff / 1800.0))

    # 3. Spatial Proximity (20%)
    # Normalized over the configured radius
    spatial_score = max(0.05, 1.0 - (distance_km / max(radius_km, 0.1)))

    # 4. Drilling Parameter Similarity (15%)
    param_score = 0.80
    well_mud_weights = [h.mud_weight_ppg for h in (hazards or []) if h.mud_weight_ppg]
    if not well_mud_weights and hasattr(well, "formations") and well.formations:
        well_mud_weights = [f.pore_pressure_gradient_ppg for f in well.formations if f.pore_pressure_gradient_ppg]

    if planned_mud_weight is not None and well_mud_weights:
        avg_offset_mw = sum(well_mud_weights) / len(well_mud_weights)
        mw_diff = abs(avg_offset_mw - planned_mud_weight)
        param_score = max(0.15, 1.0 - (mw_diff / 2.5))

    # 5. Historical Event Overlap (10%)
    event_score = 0.40 # Base score for clean well
    if hazards:
        has_critical = any(h.severity == "CRITICAL" for h in hazards)
        has_high = any(h.severity == "HIGH" for h in hazards)
        has_medium = any(h.severity == "MEDIUM" for h in hazards)
        if has_critical:
            event_score = 1.00 # Critical kick/loss gives vital offset lessons
        elif has_high:
            event_score = 0.85
        elif has_medium:
            event_score = 0.70

    # Composite Weighted Calculation
    composite = (
        0.30 * formation_score +
        0.25 * depth_score +
        0.20 * spatial_score +
        0.15 * param_score +
        0.10 * event_score
    )

    breakdown = {
        "formation_match": round(formation_score, 2),
        "depth_proximity": round(depth_score, 2),
        "spatial_proximity": round(spatial_score, 2),
        "parameter_similarity": round(param_score, 2),
        "event_overlap": round(event_score, 2),
        "composite_pct": round(composite * 100, 1)
    }

    return round(composite, 4), breakdown

def find_nearby_wells(
    db: Session,
    target_lat: float,
    target_lon: float,
    radius_km: float = 10.0,
    target_depth: Optional[float] = None,
    formation: Optional[str] = None,
    planned_mud_weight: Optional[float] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Executes PostGIS ST_DWithin spatial proximity query and ranks candidates
    by the Composite Offset Similarity Scoring algorithm.
    """
    candidates = []

    if not is_sqlite:
        try:
            # PostGIS ST_DWithin query with geography casting
            query = text("""
                SELECT id, uwi, name, field_name, operator, status, target_formation,
                       total_depth_tvd, total_depth_md, latitude, longitude, elevation_kb,
                       ST_Distance_Sphere(ST_MakePoint(longitude, latitude), ST_MakePoint(:lon, :lat)) / 1000.0 AS distance_km
                FROM wells
                WHERE ST_DWithin(
                    ST_MakePoint(longitude, latitude)::geography,
                    ST_MakePoint(:lon, :lat)::geography,
                    :radius_m
                )
                ORDER BY distance_km ASC;
            """)
            rows = db.execute(query, {
                "lon": target_lon,
                "lat": target_lat,
                "radius_m": radius_km * 1000.0
            }).fetchall()

            for r in rows:
                well_obj = db.query(Well).filter(Well.id == r.id).first()
                if not well_obj:
                    continue
                hazards = db.query(DrillingHazard).filter(DrillingHazard.well_id == r.id).all()
                bearing = calculate_bearing(target_lat, target_lon, r.latitude, r.longitude)
                
                comp_score, breakdown = compute_similarity_breakdown(
                    well=well_obj,
                    distance_km=r.distance_km,
                    radius_km=radius_km,
                    target_formation=formation,
                    target_depth=target_depth,
                    planned_mud_weight=planned_mud_weight,
                    hazards=hazards
                )

                candidates.append({
                    "id": r.id,
                    "uwi": r.uwi,
                    "name": r.name,
                    "field_name": r.field_name,
                    "operator": r.operator,
                    "status": r.status,
                    "target_formation": r.target_formation,
                    "total_depth_tvd": r.total_depth_tvd,
                    "total_depth_md": r.total_depth_md,
                    "latitude": r.latitude,
                    "longitude": r.longitude,
                    "elevation_kb": r.elevation_kb,
                    "distance_km": round(r.distance_km, 2),
                    "bearing_degrees": round(bearing, 1),
                    "hazard_count": len(hazards),
                    "critical_hazards_count": sum(1 for h in hazards if h.severity in ["HIGH", "CRITICAL"]),
                    "composite_similarity_score": comp_score,
                    "similarity_breakdown": breakdown
                })
        except Exception as e:
            candidates = []

    # If PostGIS query returned candidates, rank them. Otherwise run spherical fallback
    if not candidates:
        all_wells = db.query(Well).all()
        for w in all_wells:
            dist = haversine_distance(target_lat, target_lon, w.latitude, w.longitude)
            if dist <= radius_km:
                bearing = calculate_bearing(target_lat, target_lon, w.latitude, w.longitude)
                hazards = db.query(DrillingHazard).filter(DrillingHazard.well_id == w.id).all()

                comp_score, breakdown = compute_similarity_breakdown(
                    well=w,
                    distance_km=dist,
                    radius_km=radius_km,
                    target_formation=formation,
                    target_depth=target_depth,
                    planned_mud_weight=planned_mud_weight,
                    hazards=hazards
                )

                candidates.append({
                    "id": w.id,
                    "uwi": w.uwi,
                    "name": w.name,
                    "field_name": w.field_name,
                    "operator": w.operator,
                    "status": w.status,
                    "target_formation": w.target_formation,
                    "total_depth_tvd": w.total_depth_tvd,
                    "total_depth_md": w.total_depth_md,
                    "latitude": w.latitude,
                    "longitude": w.longitude,
                    "elevation_kb": w.elevation_kb,
                    "distance_km": round(dist, 2),
                    "bearing_degrees": round(bearing, 1),
                    "hazard_count": len(hazards),
                    "critical_hazards_count": sum(1 for h in hazards if h.severity in ["HIGH", "CRITICAL"]),
                    "composite_similarity_score": comp_score,
                    "similarity_breakdown": breakdown
                })

    # Sort primarily by composite similarity score descending, secondarily by distance ascending
    candidates.sort(key=lambda x: (x["composite_similarity_score"], -x["distance_km"]), reverse=True)
    return candidates[:limit]

def generate_wells_geojson(wells: List[Well]) -> Dict[str, Any]:
    """Converts a list of Well ORM objects into a GeoJSON FeatureCollection for frontend maps."""
    features = []
    for w in wells:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [w.longitude, w.latitude]
            },
            "properties": {
                "id": w.id,
                "uwi": w.uwi,
                "name": w.name,
                "field_name": w.field_name,
                "operator": w.operator,
                "status": w.status,
                "target_formation": w.target_formation,
                "total_depth_tvd": w.total_depth_tvd,
                "total_depth_md": w.total_depth_md,
                "elevation_kb": w.elevation_kb,
                "hazard_count": len(w.hazards) if hasattr(w, 'hazards') and w.hazards else 0
            }
        })
    return {
        "type": "FeatureCollection",
        "features": features
    }
