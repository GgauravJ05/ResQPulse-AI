import pytest
from fastapi.testclient import TestClient
from src.api.main import app, alert_store, CORRECTIONS_LOG

client = TestClient(app)

def setup_function():
    alert_store.clear()

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
    assert res.json()["models"]["classifier"] is True

def test_empty_input_error():
    res = client.post("/analyze", json={"text": "   "})
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "EMPTY_INPUT"

def test_text_too_long_error():
    long_text = "fire " * 501  # > 2000 chars
    res = client.post("/analyze", json={"text": long_text})
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "TEXT_TOO_LONG"

def test_non_emergency():
    res = client.post("/analyze", json={"text": "Hello is the mall open today or what?"})
    assert res.status_code == 200
    data = res.json()
    assert data["incident_type"] == "NON_EMERGENCY"
    assert data["is_emergency"] is False
    assert data["status"] == "DISMISSED"
    assert data["responders"] == []

    # Non-emergencies must stay out of the queue
    queue_res = client.get("/alerts")
    assert len(queue_res.json()["alerts"]) == 0

def test_normal_emergency_and_queue_sorting():
    # Submit first alert (severity 4.4)
    r1 = client.post("/analyze", json={"text": "Crash on Mumbai-Pune expressway near Lonavala exit, bleeding"})
    assert r1.status_code == 200
    
    # Submit second alert (severity 4.8)
    r2 = client.post("/analyze", json={"text": "Major earthquake collapse, 12 people trapped inside building"})
    assert r2.status_code == 200

    q_res = client.get("/alerts")
    alerts = q_res.json()["alerts"]
    assert len(alerts) == 2
    # Severity 4.8 should come before 4.4
    assert alerts[0]["severity"] >= alerts[1]["severity"]

def test_patch_and_correction_logging():
    r1 = client.post("/analyze", json={"text": "Small smoke near FC road"})
    alert_id = r1.json()["alert_id"]

    patch_res = client.patch(f"/alerts/{alert_id}", json={
        "status": "CONFIRMED",
        "edits": {
            "severity": 4.9,
            "incident_type": "FIRE"
        }
    })
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["status"] == "CONFIRMED"
    assert updated["severity"] == 4.9
    assert updated["severity_label"] == "CRITICAL"
    assert updated["incident_type"] == "FIRE"

    # Confirm logged to corrections.jsonl
    assert CORRECTIONS_LOG.exists()