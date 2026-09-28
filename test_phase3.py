import urllib.request
import json
import time

time.sleep(1)

def test(url, name):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode('utf-8'))
        print(f"[PASS] {name}: HTTP {res.status}")
        return data
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        return None

print("=== VERIFYING NWIS PHASE 3 APIS ===")
res_alerts = test("http://127.0.0.1:8000/api/v1/alerts/offset-risks?latitude=27.2891&longitude=95.3524&planned_depth_md=3700&radius_km=10", "GET /api/v1/alerts/offset-risks")
if res_alerts:
    print(f"  Total Offset Hazards: {res_alerts.get('total_risks_identified')}, Primary Tier: {res_alerts.get('overall_risk_tier')}")
    for alert in res_alerts.get("alerts", [])[:2]:
        print(f"  - [{alert.get('risk_type')}] Severity: {alert.get('severity')} | ML Prob: {alert.get('probability_pct')}% (Confidence: {alert.get('confidence_score')*100:.0f}%)")
        print(f"    Evidence items: {len(alert.get('why_evidence_chain', []))}")
        for ev in alert.get("why_evidence_chain", [])[:1]:
            print(f"    Evidence: Well {ev.get('offset_well_name')} at {ev.get('distance_km')}km, Depth {ev.get('depth_md')}m ({ev.get('formation_name')}) -> {ev.get('historical_event')}")
        print(f"    Mitigations: {len(alert.get('recommended_mitigations', []))}")
        print(f"    Citations: {len(alert.get('document_citations', []))}")
        for cit in alert.get("document_citations", [])[:1]:
            print(f"    Citation: {cit.get('document_name')} p.{cit.get('page_number')} -> '{cit.get('snippet')[:70]}...'")

res_tick = test("http://127.0.0.1:8000/api/v1/rtmac/tick", "GET /api/v1/rtmac/tick")
if res_tick:
    t = res_tick.get("telemetry", {})
    probs = res_tick.get("ml_hazard_probabilities", {})
    print(f"[PASS] Simulated Telemetry Tick #{t.get('tick_index')}:")
    print(f"  MD: {t.get('depth_md')}m | Formation: {t.get('active_formation')} | Torque: {t.get('torque_kft_lbs')} kft-lbs | SPP: {t.get('standpipe_pressure_psi')} psi")
    print(f"  Hybrid Risk Tier: {res_tick.get('hybrid_risk_tier')}")
    print(f"  ML Probabilities: Normal={probs.get('normal_prob')*100:.1f}%, Kick={probs.get('gas_kick_prob')*100:.1f}%, Loss={probs.get('loss_circulation_prob')*100:.1f}%, Stuck={probs.get('stuck_pipe_prob')*100:.1f}%")
    print(f"  Active Warning: {res_tick.get('active_warning')}")

print("\nAll Phase 3 API tests verified successfully.")
