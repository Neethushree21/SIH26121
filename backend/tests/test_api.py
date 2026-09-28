import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("[PASS] Health check passed")

def test_list_wells():
    response = client.get("/api/v1/wells")
    assert response.status_code == 200
    wells = response.json()
    assert len(wells) > 0
    print(f"[PASS] List wells passed (Found {len(wells)} wells)")

def test_nearby_wells():
    # Spud location near Nahorkatiya
    payload = {
        "latitude": 27.2891,
        "longitude": 95.3524,
        "radius_km": 10.0
    }
    response = client.post("/api/v1/wells/nearby", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_found"] > 0
    print(f"[PASS] Nearby wells query passed ({data['total_found']} offset wells within {data['radius_km']}km)")

def test_hazard_feed():
    response = client.get("/api/v1/alerts/feed")
    assert response.status_code == 200
    hazards = response.json()
    assert len(hazards) > 0
    print(f"[PASS] Drilling hazard feed passed ({len(hazards)} alerts active)")

def test_rag_search():
    payload = {
        "question": "What caused the mud loss in Nahorkatiya Tipam Sandstone?",
        "top_k": 3
    }
    response = client.post("/api/v1/search/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["citations"]) > 0
    assert "Tipam" in data["answer"] or "Nahorkatiya" in data["answer"] or "LCM" in data["answer"]
    print(f"[PASS] RAG vector search passed ({len(data['citations'])} citations retrieved)")

def test_nearby_get_with_similarity():
    # Test GET /api/v1/wells/nearby with multi-factor similarity scoring
    params = {
        "latitude": 27.2891,
        "longitude": 95.3524,
        "radius_km": 15.0,
        "target_depth_md": 3700.0,
        "formation": "Barail Sandstone",
        "planned_mud_weight": 10.5
    }
    response = client.get("/api/v1/wells/nearby", params=params)
    assert response.status_code == 200
    data = response.json()
    assert data["total_found"] > 0
    top_offset = data["offset_wells"][0]
    assert "composite_similarity_score" in top_offset
    assert top_offset["composite_similarity_score"] > 0.0
    assert "similarity_breakdown" in top_offset
    breakdown = top_offset["similarity_breakdown"]
    assert "formation_match" in breakdown
    assert "depth_proximity" in breakdown
    assert "spatial_proximity" in breakdown
    assert "parameter_similarity" in breakdown
    assert "event_overlap" in breakdown
    print(f"[PASS] GET /nearby Multi-Factor Similarity passed (Top: {top_offset['name']}, Score: {top_offset['composite_similarity_score']} / {breakdown['composite_pct']}%)")

def test_folder_ingestion():
    # Test POST /api/v1/ingest/folder
    sample_dir = os.path.join(os.path.dirname(__file__), "..", "..", "sample_data", "reports")
    payload = {"folder_path": os.path.abspath(sample_dir)}
    response = client.post("/api/v1/ingest/folder", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert "task_id" in res_data
    task_id = res_data["task_id"]
    print(f"[PASS] POST /ingest/folder initiated (Task ID: {task_id[:8]}...)")

    # Test GET /api/v1/ingest/status/{task_id}
    status_resp = client.get(f"/api/v1/ingest/status/{task_id}")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["task_id"] == task_id
    assert status_data["status"] in ["QUEUED", "SCANNING", "PROCESSING", "COMPLETED"]
    print(f"[PASS] GET /ingest/status/{{task_id}} passed (Status: {status_data['status']})")

def test_rtmac_telemetry():
    # Test GET /api/v1/rtmac/tick
    response = client.get("/api/v1/rtmac/tick")
    assert response.status_code == 200
    data = response.json()
    assert "telemetry" in data
    assert "ml_hazard_probabilities" in data
    assert "hybrid_risk_tier" in data
    telem = data["telemetry"]
    probs = data["ml_hazard_probabilities"]
    assert telem["depth_md"] > 0
    assert "gas_kick_prob" in probs
    assert "loss_circulation_prob" in probs
    assert "stuck_pipe_prob" in probs
    print(f"[PASS] eRTMAC Telemetry Tick passed (Depth: {telem['depth_md']}m, ROP: {telem['rop_m_hr']}m/hr, Risk Tier: {data['hybrid_risk_tier']})")

def test_explainable_evidence_chain():
    # Test GET /api/v1/alerts/offset-risks
    params = {
        "latitude": 27.2891,
        "longitude": 95.3524,
        "planned_depth_md": 3700.0,
        "radius_km": 15.0,
        "formation": "Barail Sandstone"
    }
    response = client.get("/api/v1/alerts/offset-risks", params=params)
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert len(data["alerts"]) > 0
    first_alert = data["alerts"][0]
    assert "risk_type" in first_alert
    assert "probability_pct" in first_alert
    assert "why_evidence_chain" in first_alert
    assert "recommended_mitigations" in first_alert
    assert "document_citations" in first_alert
    print(f"[PASS] Explainable Evidence-Chain Alerts passed ({len(data['alerts'])} hazard risks audit-ready; Top: {first_alert['risk_type']} [{first_alert['probability_pct']}%])")

if __name__ == "__main__":
    test_health()
    test_list_wells()
    test_nearby_wells()
    test_nearby_get_with_similarity()
    test_hazard_feed()
    test_rag_search()
    test_folder_ingestion()
    test_rtmac_telemetry()
    test_explainable_evidence_chain()
    print("\nALL PHASE 1, 2 & 3 BACKEND API TESTS PASSED SUCCESSFULLY!")

