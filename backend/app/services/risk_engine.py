import numpy as np
import os
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.well import Well
from app.models.drilling_event import DrillingHazard
from app.services.geospatial import haversine_distance
from app.services.vector_store import vector_store_service
from app.schemas.alert import (
    RiskAssessmentResponse,
    RiskCategorySummary,
    HazardAlert,
    OffsetRiskAlert,
    EvidenceChainItem,
    DocumentCitation,
    OffsetRisksAuditResponse,
    TelemetryTick,
    TelemetryEvaluationResponse
)
import logging

logger = logging.getLogger(__name__)

FORMATION_MAP = {
    "alluvium": 0,
    "dihing": 0,
    "girujan": 1,
    "girujan clay": 1,
    "tipam": 2,
    "tipam sandstone": 2,
    "barail": 3,
    "barail coal": 3,
    "barail coal-shale": 3,
    "barail main": 4,
    "barail main sand": 4,
    "kopili": 5,
    "kopili shale": 5
}

class TelemetryMLRiskModel:
    """
    Lightweight Scikit-learn Random Forest model trained on synthetic
    historical Assam Basin telemetry patterns to predict hazard probabilities.
    """
    def __init__(self):
        self.model = None
        self.is_trained = False
        self._train_synthetic_model()

    def _train_synthetic_model(self):
        try:
            from sklearn.ensemble import RandomForestClassifier
            
            # Generate 1,200 synthetic telemetry samples
            np.random.seed(42)
            n_samples = 1200
            
            # Features: [depth_md, formation_code, mud_weight, rop, wob, torque, pressure]
            X = []
            y = []

            # 0: Normal, 1: Gas Kick, 2: Lost Circulation, 3: Stuck Pipe
            for _ in range(n_samples):
                hazard_type = np.random.choice([0, 1, 2, 3], p=[0.60, 0.15, 0.15, 0.10])
                
                if hazard_type == 0:
                    # Normal drilling
                    depth = np.random.uniform(500, 3800)
                    f_code = 1 if depth < 1800 else (2 if depth < 2800 else 3)
                    mw = np.random.uniform(9.6, 10.8)
                    rop = np.random.uniform(8.0, 16.0)
                    wob = np.random.uniform(18.0, 24.0)
                    torque = np.random.uniform(8.0, 14.0)
                    press = np.random.uniform(2200, 2800)
                    
                elif hazard_type == 1:
                    # Gas Kick (typically Barail Coal-Shale >2800m, rapid ROP drill break, fluctuating pressure)
                    depth = np.random.uniform(2800, 3900)
                    f_code = 3 # Barail
                    mw = np.random.uniform(9.8, 10.5) # slightly underbalanced
                    rop = np.random.uniform(24.0, 45.0) # sudden drilling break!
                    wob = np.random.uniform(14.0, 20.0)
                    torque = np.random.uniform(10.0, 16.0)
                    press = np.random.uniform(1800, 2400) # pressure reduction or gas expansion
                    
                elif hazard_type == 2:
                    # Lost Circulation (Tipam Sandstone, highly porous, sudden pressure loss)
                    depth = np.random.uniform(1800, 2800)
                    f_code = 2 # Tipam
                    mw = np.random.uniform(10.4, 11.5) # heavy mud initiating losses
                    rop = np.random.uniform(15.0, 28.0)
                    wob = np.random.uniform(18.0, 25.0)
                    torque = np.random.uniform(7.0, 12.0)
                    press = np.random.uniform(1400, 2000) # drop in standpipe pressure
                    
                else:
                    # Stuck Pipe (Tipam depleted sand or Girujan swelling clay, high torque spike, zero ROP)
                    depth = np.random.uniform(1200, 3500)
                    f_code = np.random.choice([1, 2])
                    mw = np.random.uniform(10.2, 11.2)
                    rop = np.random.uniform(0.0, 2.5) # stalling out
                    wob = np.random.uniform(26.0, 38.0) # excessive overpull/WOB
                    torque = np.random.uniform(25.0, 42.0) # severe torque spike!
                    press = np.random.uniform(2900, 3800) # pack-off pump pressure spike

                X.append([depth, f_code, mw, rop, wob, torque, press])
                y.append(hazard_type)

            X = np.array(X)
            y = np.array(y)

            clf = RandomForestClassifier(n_estimators=35, max_depth=6, random_state=42)
            clf.fit(X, y)
            self.model = clf
            self.is_trained = True
            logger.info("Hybrid ML Telemetry Risk Model trained successfully.")
        except Exception as e:
            logger.error(f"Failed to train ML telemetry model: {e}")
            self.is_trained = False

    def predict_hazard_probabilities(
        self,
        depth_md: float,
        formation_name: str,
        mud_weight: float,
        rop: float,
        wob: float,
        torque: float,
        pressure: float
    ) -> Dict[str, float]:
        """Returns hazard probabilities: gas_kick, loss_circulation, stuck_pipe, normal."""
        f_norm = formation_name.lower()
        f_code = 3 # default Barail
        for k, code in FORMATION_MAP.items():
            if k in f_norm:
                f_code = code
                break

        features = np.array([[depth_md, f_code, mud_weight, rop, wob, torque, pressure]])

        if self.is_trained and self.model is not None:
            try:
                probs = self.model.predict_proba(features)[0]
                # Classes correspond to [0: Normal, 1: Gas Kick, 2: Loss, 3: Stuck Pipe]
                classes = list(self.model.classes_)
                prob_dict = {
                    "normal": float(probs[classes.index(0)]) if 0 in classes else 0.5,
                    "gas_kick": float(probs[classes.index(1)]) if 1 in classes else 0.1,
                    "loss_circulation": float(probs[classes.index(2)]) if 2 in classes else 0.1,
                    "stuck_pipe": float(probs[classes.index(3)]) if 3 in classes else 0.1,
                }
                return {k: round(v, 4) for k, v in prob_dict.items()}
            except Exception as e:
                logger.error(f"Prediction error: {e}")

        # Rule-based fallback if ML fails
        p_kick = 0.75 if ("barail" in f_norm and rop > 22.0) else 0.15
        p_loss = 0.70 if ("tipam" in f_norm and pressure < 1900) else 0.15
        p_stuck = 0.80 if (torque > 25.0 or wob > 28.0) else 0.10
        return {
            "normal": 0.30,
            "gas_kick": p_kick,
            "loss_circulation": p_loss,
            "stuck_pipe": p_stuck
        }


ml_model = TelemetryMLRiskModel()


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

    @staticmethod
    def evaluate_live_telemetry(
        tick: TelemetryTick,
        offset_hazards: List[DrillingHazard]
    ) -> TelemetryEvaluationResponse:
        """
        Combines Scikit-learn ML probabilities with offset hazard rules
        to establish a reliable risk tier (LOW, MEDIUM, HIGH, CRITICAL)
        and filter false positives.
        """
        ml_probs = ml_model.predict_hazard_probabilities(
            depth_md=tick.depth_md,
            formation_name=tick.active_formation,
            mud_weight=tick.mud_weight_in_ppg,
            rop=tick.rop_m_hr,
            wob=tick.wob_klbs,
            torque=tick.torque_kft_lbs,
            pressure=tick.standpipe_pressure_psi
        )

        p_kick = ml_probs.get("gas_kick", 0.0)
        p_loss = ml_probs.get("loss_circulation", 0.0)
        p_stuck = ml_probs.get("stuck_pipe", 0.0)

        # Cross-reference offset hazards in same formation/depth
        offset_factors = []
        matching_kicks = [h for h in offset_hazards if "kick" in h.event_type.lower() and abs(h.depth_md - tick.depth_md) < 300]
        matching_losses = [h for h in offset_hazards if "loss" in h.event_type.lower() and abs(h.depth_md - tick.depth_md) < 300]
        matching_stuck = [h for h in offset_hazards if "stuck" in h.event_type.lower() and abs(h.depth_md - tick.depth_md) < 300]

        tier = "LOW"
        warning = None

        if p_kick > 0.65 or matching_kicks:
            if matching_kicks and p_kick > 0.40:
                tier = "CRITICAL"
                warning = f"CRITICAL: Gas kick influx detected ({round(p_kick*100)}% ML prob). Offset well {matching_kicks[0].well.name if hasattr(matching_kicks[0], 'well') else 'offset'} took kick at {matching_kicks[0].depth_md}m."
            elif p_kick > 0.70:
                tier = "HIGH"
                warning = f"HIGH: Rapid drilling break (ROP {tick.rop_m_hr} m/hr) indicates potential influx."
            offset_factors.append(f"Historical gas kicks logged in {tick.active_formation}")

        elif p_stuck > 0.60 or matching_stuck:
            if tick.torque_kft_lbs > 26.0:
                tier = "HIGH"
                warning = f"ELEVATED: Torque spike ({tick.torque_kft_lbs} kft-lbs) with low ROP ({tick.rop_m_hr} m/hr). High differential sticking risk."
            else:
                tier = "MEDIUM"
                warning = "ADVISORY: Depleted sand formation requires rotation and mud lubricity monitoring."
            offset_factors.append(f"Historical stuck pipe events in {tick.active_formation}")

        elif p_loss > 0.60 or matching_losses:
            tier = "MEDIUM" if p_loss < 0.75 else "HIGH"
            warning = f"LOSS WARNING: Potential mud loss in fractured {tick.active_formation} (Standpipe {tick.standpipe_pressure_psi} psi)."
            offset_factors.append(f"Porous loss zone documented in {tick.active_formation}")

        return TelemetryEvaluationResponse(
            telemetry=tick,
            ml_hazard_probabilities={
                "gas_kick_prob": round(p_kick, 3),
                "loss_circulation_prob": round(p_loss, 3),
                "stuck_pipe_prob": round(p_stuck, 3),
                "normal_prob": round(ml_probs.get("normal", 0.0), 3)
            },
            hybrid_risk_tier=tier,
            active_warning=warning,
            offset_risk_factors=offset_factors
        )

    @staticmethod
    def generate_evidence_chain_alerts(
        db: Session,
        target_lat: float,
        target_lon: float,
        planned_depth_md: float,
        radius_km: float = 10.0,
        formation: Optional[str] = None
    ) -> OffsetRisksAuditResponse:
        """
        Builds explainable evidence-chain alerts pairing:
          1. Risk Type & Severity Score
          2. The 'Why?' Evidence Chain (matched wells, exact distance, depth, formation)
          3. Recommended Mitigation Actions
          4. Exact Document Citations from ChromaDB
        """
        wells = db.query(Well).all()
        target_fm = formation or "Barail Sandstone"

        # Find nearby offset wells
        nearby_wells_data = []
        for w in wells:
            dist = haversine_distance(target_lat, target_lon, w.latitude, w.longitude)
            if dist <= radius_km:
                nearby_wells_data.append((w, dist))

        nearby_wells_data.sort(key=lambda x: x[1])

        alerts: List[OffsetRiskAlert] = []

        # Risk Category 1: Gas Kick & Overpressure
        kick_evidence: List[EvidenceChainItem] = []
        for w, dist in nearby_wells_data:
            hazards = db.query(DrillingHazard).filter(
                DrillingHazard.well_id == w.id,
                DrillingHazard.event_type.ilike("%kick%")
            ).all()
            for h in hazards:
                kick_evidence.append(EvidenceChainItem(
                    offset_well_id=w.id,
                    offset_well_name=w.name,
                    offset_well_uwi=w.uwi,
                    distance_km=round(dist, 2),
                    depth_md=h.depth_md,
                    formation_name=h.formation_name or "Barail Coal-Shale",
                    historical_event=h.event_type,
                    incident_description=h.description,
                    npt_hours=h.npt_hours
                ))

        if kick_evidence or "barail" in target_fm.lower():
            # Query ChromaDB for exact citations
            citations_raw = vector_store_service.search(
                query="Gas kick influx shut-in SIDPP Wait and Weight Barail",
                top_k=2,
                formation_filter="Barail"
            )
            citations = [
                DocumentCitation(
                    document_name=c.get("document_name", "DDR_BGH_03_Day28.pdf"),
                    page_number=1,
                    well_name=c.get("well_name", "Baghjan-03"),
                    depth_interval=c.get("depth_interval", "3420m"),
                    snippet=c.get("snippet", ""),
                    score=c.get("score", 0.92)
                )
                for c in citations_raw
            ]

            prob = 0.88 if kick_evidence else 0.65
            alerts.append(OffsetRiskAlert(
                id=str(uuid.uuid4()),
                risk_type="High-Pressure Gas Influx / Kick",
                severity="CRITICAL" if any(k.distance_km < 8.0 for k in kick_evidence) else "HIGH",
                probability_pct=round(prob * 100, 1),
                confidence_score=0.94,
                why_evidence_chain=kick_evidence[:3],
                recommended_mitigations=[
                    "Pre-calculate Wait & Weight kill mud density prior to entering Barail Coal stringers.",
                    "Ensure Annular BOP and hydraulic choke lines are tested to 5,000 psi.",
                    "Limit tripping speed and set trip tank volume alarms to +/- 2 bbl."
                ],
                document_citations=citations,
                timestamp=datetime.utcnow().isoformat()
            ))

        # Risk Category 2: Lost Circulation
        loss_evidence: List[EvidenceChainItem] = []
        for w, dist in nearby_wells_data:
            hazards = db.query(DrillingHazard).filter(
                DrillingHazard.well_id == w.id,
                DrillingHazard.event_type.ilike("%loss%")
            ).all()
            for h in hazards:
                loss_evidence.append(EvidenceChainItem(
                    offset_well_id=w.id,
                    offset_well_name=w.name,
                    offset_well_uwi=w.uwi,
                    distance_km=round(dist, 2),
                    depth_md=h.depth_md,
                    formation_name=h.formation_name or "Tipam Sandstone",
                    historical_event=h.event_type,
                    incident_description=h.description,
                    npt_hours=h.npt_hours
                ))

        if loss_evidence or "tipam" in target_fm.lower():
            citations_raw = vector_store_service.search(
                query="Lost circulation fractured Tipam Sandstone LCM pill squeeze",
                top_k=2,
                formation_filter="Tipam"
            )
            citations = [
                DocumentCitation(
                    document_name=c.get("document_name", "DDR_NHK_412_Day14.pdf"),
                    page_number=1,
                    well_name=c.get("well_name", "Nahorkatiya-412"),
                    depth_interval=c.get("depth_interval", "2340m"),
                    snippet=c.get("snippet", ""),
                    score=c.get("score", 0.90)
                )
                for c in citations_raw
            ]

            prob = 0.82 if loss_evidence else 0.58
            alerts.append(OffsetRiskAlert(
                id=str(uuid.uuid4()),
                risk_type="Severe Lost Circulation Zone",
                severity="HIGH" if loss_evidence else "MEDIUM",
                probability_pct=round(prob * 100, 1),
                confidence_score=0.91,
                why_evidence_chain=loss_evidence[:3],
                recommended_mitigations=[
                    "Pre-mix 40-50 bbl cellulosic nut-plug and mica LCM pill in active reserve pit.",
                    "Strictly maintain Equivalent Circulating Density (ECD) below 10.8 ppg.",
                    "Reduce pump circulation rate to 520 GPM when crossing fractured Tipam sands."
                ],
                document_citations=citations,
                timestamp=datetime.utcnow().isoformat()
            ))

        # Risk Category 3: Differential Sticking & Tight Hole
        stuck_evidence: List[EvidenceChainItem] = []
        for w, dist in nearby_wells_data:
            hazards = db.query(DrillingHazard).filter(
                DrillingHazard.well_id == w.id,
                DrillingHazard.event_type.ilike("%stuck%")
            ).all()
            for h in hazards:
                stuck_evidence.append(EvidenceChainItem(
                    offset_well_id=w.id,
                    offset_well_name=w.name,
                    offset_well_uwi=w.uwi,
                    distance_km=round(dist, 2),
                    depth_md=h.depth_md,
                    formation_name=h.formation_name or "Tipam / Barail",
                    historical_event=h.event_type,
                    incident_description=h.description,
                    npt_hours=h.npt_hours
                ))

        if stuck_evidence:
            citations_raw = vector_store_service.search(
                query="Differential sticking pipe-freeing soak pill jar overpull",
                top_k=1
            )
            citations = [
                DocumentCitation(
                    document_name=c.get("document_name", "WCR_MOR_88.txt"),
                    page_number=1,
                    well_name=c.get("well_name", "Moran-88"),
                    depth_interval=c.get("depth_interval", "2890m"),
                    snippet=c.get("snippet", ""),
                    score=c.get("score", 0.88)
                )
                for c in citations_raw
            ]

            alerts.append(OffsetRiskAlert(
                id=str(uuid.uuid4()),
                risk_type="Differential Sticking / Pack-off",
                severity="HIGH",
                probability_pct=76.4,
                confidence_score=0.88,
                why_evidence_chain=stuck_evidence[:3],
                recommended_mitigations=[
                    "Maintain continuous drillstring rotation during directional MWD surveys.",
                    "Treat drilling fluid with ester-based lubricant to minimize wall cake friction.",
                    "Have 45 bbl pipe-freeing soak pill staged on rig floor."
                ],
                document_citations=citations,
                timestamp=datetime.utcnow().isoformat()
            ))

        tier = "CRITICAL" if any(a.severity == "CRITICAL" for a in alerts) else ("HIGH" if alerts else "LOW")

        return OffsetRisksAuditResponse(
            target_spud={"latitude": target_lat, "longitude": target_lon},
            radius_km=radius_km,
            planned_depth_md=planned_depth_md,
            target_formation=target_fm,
            overall_risk_tier=tier,
            total_risks_identified=len(alerts),
            alerts=alerts
        )

risk_engine = RiskEngine()
