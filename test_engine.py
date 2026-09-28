import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from app.core.database import SessionLocal
from app.services.risk_engine import risk_engine

db = SessionLocal()
report = risk_engine.generate_evidence_chain_alerts(
    db=db,
    target_lat=27.2891,
    target_lon=95.3524,
    planned_depth_md=3700.0,
    radius_km=10.0,
    formation="Barail"
)
db.close()

print(f"Total risks identified: {report.total_risks_identified}")
print(f"Primary risk tier: {report.overall_risk_tier}")
for alert in report.alerts:
    print(f"\n[RISK] {alert.risk_type} [{alert.severity}] - {alert.probability_pct}% ML Prob (Confidence: {alert.confidence_score*100:.0f}%)")
    print(f"  Evidence items: {len(alert.why_evidence_chain)}")
    for ev in alert.why_evidence_chain[:2]:
        print(f"    * Well: {ev.offset_well_name} ({ev.offset_well_uwi}) | Dist: {ev.distance_km}km | Depth: {ev.depth_md}m | Event: {ev.historical_event}")
    print(f"  Mitigations: {len(alert.recommended_mitigations)}")
    for m in alert.recommended_mitigations[:2]:
        print(f"    - {m}")
    print(f"  Citations: {len(alert.document_citations)}")
    for cit in alert.document_citations[:2]:
        print(f"    [Citation] {cit.document_name} (p.{cit.page_number}) -> \"{cit.snippet[:80]}...\"")
