from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.well import Well
from app.models.drilling_event import DrillingHazard
from app.services.geospatial import haversine_distance
from app.schemas.alert import RiskAssessmentResponse, RiskCategorySummary, HazardAlert

class RiskEngine:
    @staticmethod
    def assess_risks(
        db: Session,
        target_lat: float,
        target_lon: float,
        planned_tvd: float,
        radius_km: float = 5.0,
        target_formation: Optional[str] = None
    ) -> RiskAssessmentResponse:
        """Evaluates historical hazards within radius of target location and outputs operational recommendations."""
        wells = db.query(Well).all()
        nearby_well_map = {}
        for w in wells:
            dist = haversine_distance(target_lat, target_lon, w.latitude, w.longitude)
            if dist <= radius_km:
                nearby_well_map[w.id] = (w, dist)

        hazards = []
        if nearby_well_map:
            well_ids = list(nearby_well_map.keys())
            hazard_records = db.query(DrillingHazard).filter(DrillingHazard.well_id.in_(well_ids)).all()
            for h in hazard_records:
                well_obj, dist = nearby_well_map[h.well_id]
                hazards.append({
                    "id": h.id,
                    "well_name": well_obj.name,
                    "uwi": well_obj.uwi,
                    "event_type": h.event_type,
                    "severity": h.severity,
                    "depth_md": h.depth_md,
                    "formation_name": h.formation_name or "N/A",
                    "mud_weight_ppg": h.mud_weight_ppg,
                    "description": h.description,
                    "remediation_action": h.remediation_action,
                    "distance_km": round(dist, 2),
                    "reported_date": h.reported_date
                })

        # Categorize
        categories = {
            "Loss of Circulation": {"count": 0, "highest": "LOW", "warning": "No offset losses recorded."},
            "Gas Kick": {"count": 0, "highest": "LOW", "warning": "No kick incidents recorded within radius."},
            "Stuck Pipe": {"count": 0, "highest": "LOW", "warning": "No mechanical or differential sticking recorded."},
            "Overpressure": {"count": 0, "highest": "LOW", "warning": "Normal hydrostatic pore pressure profile observed."}
        }

        severity_rank = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}

        critical_count = 0
        high_count = 0

        for h in hazards:
            sev = h["severity"]
            if sev == "CRITICAL":
                critical_count += 1
            elif sev == "HIGH":
                high_count += 1

            etype = h["event_type"]
            matched_cat = None
            for cat_key in categories:
                if cat_key.lower() in etype.lower():
                    matched_cat = cat_key
                    break
            if not matched_cat:
                matched_cat = "Loss of Circulation" if "loss" in etype.lower() else "Gas Kick"

            c = categories[matched_cat]
            c["count"] += 1
            if severity_rank.get(sev, 1) > severity_rank.get(c["highest"], 1):
                c["highest"] = sev
            c["warning"] = f"Offset well {h['well_name']} reported {h['event_type']} ({sev}) at {h['depth_md']}m."

        # Overall risk calculation
        if critical_count > 0:
            overall_risk = "CRITICAL"
        elif high_count >= 2:
            overall_risk = "ELEVATED"
        elif high_count == 1 or len(hazards) >= 3:
            overall_risk = "MODERATE"
        else:
            overall_risk = "LOW"

        category_summaries = [
            RiskCategorySummary(
                category=cat,
                count=data["count"],
                highest_severity=data["highest"],
                key_warning=data["warning"]
            )
            for cat, data in categories.items()
        ]

        # Recommended Mud Weight Window (Assam Shelf typical values adjusted for offset events)
        base_min_ppg = 9.8
        base_max_ppg = 12.4
        if any(h["event_type"] == "Gas Kick" for h in hazards):
            base_min_ppg = max(base_min_ppg, 10.4)
        if any("Loss" in h["event_type"] for h in hazards):
            base_max_ppg = min(base_max_ppg, 11.8)

        mud_weight_recommended = {
            "min_ppg": round(base_min_ppg, 2),
            "max_ppg": round(base_max_ppg, 2),
            "surge_margin_ppg": 0.4
        }

        # Recommendations
        recs = [
            f"Set 9-5/8' casing shoe before entering the Barail Sandstone pore pressure transition zone.",
            f"Pre-treat active drilling fluid with fine-to-medium cellulosic LCM prior to drilling through depleted Tipam intervals.",
            f"Conduct flow checks at 15-minute intervals when penetration rate exceeds 18 m/hr.",
            f"Keep choke manifold lined up with trip tank volume monitoring enabled 24/7."
        ]

        hazard_alerts = [HazardAlert(**h) for h in hazards]
        hazard_alerts.sort(key=lambda x: (severity_rank.get(x.severity, 0), -(x.distance_km or 0)), reverse=True)

        return RiskAssessmentResponse(
            target_location={"latitude": target_lat, "longitude": target_lon, "planned_tvd": planned_tvd},
            radius_km=radius_km,
            overall_risk_score=overall_risk,
            mud_weight_recommended_ppg=mud_weight_recommended,
            category_summaries=category_summaries,
            nearby_hazards=hazard_alerts,
            drilling_recommendations=recs
        )

risk_engine = RiskEngine()
