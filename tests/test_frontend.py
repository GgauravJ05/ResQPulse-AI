"""
Tests for ResQPulse AI Frontend and API Client
Validates schema compliance, API client behavior, mock/live modes,
error-handling paths, and component rendering logic.
"""

import json
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock
import requests

from app.api_client import (
    get_alert,
    transcribe_audio,
    get_alerts,
    update_alert,
    get_metrics,
    check_health,
    ResQPulseAPIError,
    BackendNotReachableError,
    APIResponseError,
    MOCK_ALERT_PATH,
    DEMO_SAMPLES_PATH,
)
from app.styles import (
    get_severity_style,
    get_incident_type_meta,
    SEVERITY_COLORS,
    INCIDENT_TYPE_META,
    SDG_META,
)


def test_mock_alert_schema():
    """Verify mock_alert.json matches Section 6 of SCHEMA.md."""
    assert MOCK_ALERT_PATH.exists(), "app/mock_alert.json does not exist"
    with open(MOCK_ALERT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    required_keys = [
        "alert_id", "created_at", "status", "is_emergency", "input",
        "incident_type", "type_confidence", "type_probs", "severity",
        "severity_label", "location", "people_affected", "injuries",
        "hazards", "summary", "responders", "sdg_targets", "explanation",
        "extractor", "latency_ms"
    ]
    for key in required_keys:
        assert key in data, f"Missing key in mock_alert.json: {key}"

    assert data["incident_type"] == "TRANSPORT_ACCIDENT"
    assert data["severity_label"] == "CRITICAL"
    assert data["severity"] == 4.4
    assert isinstance(data["explanation"]["attention"], list)
    assert len(data["explanation"]["attention"]) > 0


def test_demo_samples_count_and_types():
    """Verify demo_samples.json contains 9 samples covering all types."""
    assert DEMO_SAMPLES_PATH.exists(), "app/demo_samples.json does not exist"
    with open(DEMO_SAMPLES_PATH, "r", encoding="utf-8") as f:
        samples = json.load(f)

    assert len(samples) == 9, f"Expected 9 demo samples, found {len(samples)}"

    types_found = {s["expected_type"] for s in samples}
    expected_types = {
        "FIRE", "FLOOD", "STORM_CYCLONE", "EARTHQUAKE_COLLAPSE",
        "TRANSPORT_ACCIDENT", "MEDICAL", "VIOLENCE_CRIME", "NON_EMERGENCY"
    }
    for et in expected_types:
        assert et in types_found, f"Missing expected incident type in samples: {et}"

    # Verify at least one non-emergency and one vague report
    has_non_emergency = any(s["expected_type"] == "NON_EMERGENCY" for s in samples)
    has_vague = any("vague" in s.get("label", "").lower() for s in samples)
    assert has_non_emergency, "Must include at least one NON_EMERGENCY sample"
    assert has_vague, "Must include at least one vague sample"


def test_get_alert_input_validation():
    """Test validation of empty and overlong inputs."""
    with pytest.raises(ResQPulseAPIError, match="Report text cannot be empty"):
        get_alert("")

    with pytest.raises(ResQPulseAPIError, match="Report text cannot be empty"):
        get_alert("   \n\t  ")

    long_text = "Emergency! " * 250  # > 2,500 characters
    with pytest.raises(ResQPulseAPIError, match="exceeds maximum limit of 2,000 characters"):
        get_alert(long_text)


def test_get_alert_mock_mode():
    """Test mock alert generation for standard and non-emergency inputs."""
    alert = get_alert("Accident on highway, car flipped and passenger bleeding", mock_mode=True)
    assert alert["incident_type"] == "TRANSPORT_ACCIDENT"
    assert alert["is_emergency"] is True
    assert alert["severity"] >= 3.0
    assert "AMBULANCE" in alert["responders"]
    assert "3.6" in alert["sdg_targets"]
    assert len(alert["explanation"]["attention"]) > 0

    # Test Non-emergency
    non_emerg = get_alert("My car AC is not working and it is hot today", mock_mode=True)
    assert non_emerg["incident_type"] == "NON_EMERGENCY"
    assert non_emerg["is_emergency"] is False
    assert non_emerg["severity"] == 1.0
    assert non_emerg["status"] == "DISMISSED"
    assert non_emerg["responders"] == []


def test_get_alert_backend_unreachable():
    """Test that live mode raises BackendNotReachableError when connection fails."""
    with patch("requests.post", side_effect=requests.exceptions.ConnectionError("Connection refused")):
        with pytest.raises(BackendNotReachableError, match="backend not reachable"):
            get_alert("Fire in shop", mock_mode=False, base_url="http://invalid-host:9999")


def test_transcribe_audio_mock_and_errors():
    """Test audio transcription mock and error flows."""
    with pytest.raises(ResQPulseAPIError, match="Audio input is empty or invalid"):
        transcribe_audio(b"")

    res = transcribe_audio(b"FAKE_AUDIO_BYTES", mock_mode=True)
    assert "transcript" in res
    assert "confidence" in res
    assert "low_confidence" in res
    assert "duration_s" in res

    with patch("requests.post", side_effect=requests.exceptions.Timeout("Read timeout")):
        with pytest.raises(BackendNotReachableError, match="backend not reachable"):
            transcribe_audio(b"DATA", mock_mode=False, base_url="http://invalid-host:9999")


def test_get_alerts_mock_and_filtering():
    """Test alert queue retrieval and status filtering in mock mode."""
    res = get_alerts(mock_mode=True)
    assert "alerts" in res
    alerts = res["alerts"]
    assert len(alerts) >= 5

    # Check ordering: severity descending
    severities = [a["severity"] for a in alerts]
    assert severities == sorted(severities, reverse=True), "Queue must be sorted by severity descending"

    # Status filter
    res_new = get_alerts(status="NEW", mock_mode=True)
    for a in res_new["alerts"]:
        assert a["status"] == "NEW"


def test_update_alert_mock():
    """Test updating alert status in mock mode."""
    updated = update_alert("RQP-000101", status="CONFIRMED", mock_mode=True)
    assert updated["status"] == "CONFIRMED"

    dispatched = update_alert("RQP-000101", status="DISPATCHED", mock_mode=True)
    assert dispatched["status"] == "DISPATCHED"


def test_styles_severity_tokens():
    """Test severity color token mapping and fallback."""
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "NON_EMERGENCY"]:
        style = get_severity_style(sev)
        assert "badge_bg" in style
        assert "border" in style
        assert "map_color" in style

    fallback = get_severity_style("UNKNOWN_LABEL")
    assert fallback == SEVERITY_COLORS["LOW"]


def test_styles_incident_type_meta():
    """Test incident type metadata and fallback."""
    for itype in ["FIRE", "FLOOD", "STORM_CYCLONE", "EARTHQUAKE_COLLAPSE",
                  "TRANSPORT_ACCIDENT", "MEDICAL", "VIOLENCE_CRIME", "NON_EMERGENCY"]:
        meta = get_incident_type_meta(itype)
        assert "icon" in meta
        assert "name" in meta

    fallback = get_incident_type_meta("ALIEN_INVASION")
    assert fallback["icon"] == ""                    # the interface uses words, not pictograms


def test_get_metrics_mock():
    """Test metrics retrieval in mock mode."""
    metrics = get_metrics(mock_mode=True)
    assert metrics is not None
    assert "classification" in metrics
    assert "severity" in metrics
    assert "extraction" in metrics
