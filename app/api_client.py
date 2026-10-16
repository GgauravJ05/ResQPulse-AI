"""
ResQPulse AI — API Client Module
Centralizes all HTTP requests to the ResQPulse FastAPI backend.
Supports both Mock Mode (offline demo) and Live Mode (HTTP calls).
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DEFAULT_API_URL = "http://localhost:8000"
API_URL = os.getenv("API_URL", DEFAULT_API_URL).rstrip("/")

# Paths to local mock data
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
MOCK_ALERT_PATH = BASE_DIR / "mock_alert.json"
DEMO_SAMPLES_PATH = BASE_DIR / "demo_samples.json"
METRICS_PATH = PROJECT_ROOT / "reports" / "metrics.json"

# In-memory mock alert repository for realistic mock session updates
_MOCK_ALERTS_STORE: List[Dict[str, Any]] = []


class ResQPulseAPIError(Exception):
    """Base exception for ResQPulse API interactions."""
    pass


class BackendNotReachableError(ResQPulseAPIError):
    """Raised when backend connection fails or times out."""
    pass


class APIResponseError(ResQPulseAPIError):
    """Raised when the API returns an HTTP 4xx/5xx or invalid structure."""
    def __init__(self, status_code: int, code: str, message: str):
        super().__init__(f"[{status_code}] {code}: {message}")
        self.status_code = status_code
        self.code = code
        self.message = message


def get_base_url() -> str:
    """Return configured API URL."""
    return os.getenv("API_URL", DEFAULT_API_URL).rstrip("/")


def _load_json_file(file_path: Path) -> Optional[Any]:
    """Safely load JSON from a local path."""
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def _init_mock_alerts() -> List[Dict[str, Any]]:
    """Initialize mock queue of diverse alerts for the dispatcher dashboard."""
    global _MOCK_ALERTS_STORE
    if _MOCK_ALERTS_STORE and len(_MOCK_ALERTS_STORE) >= 5:
        return _MOCK_ALERTS_STORE

    mock_base = _load_json_file(MOCK_ALERT_PATH)
    if not mock_base:
        mock_base = {
            "alert_id": "RQP-000123",
            "created_at": "2026-10-20T14:32:05+05:30",
            "status": "NEW",
            "is_emergency": True,
            "incident_type": "TRANSPORT_ACCIDENT",
            "type_confidence": 0.91,
            "type_probs": {"TRANSPORT_ACCIDENT": 0.91, "MEDICAL": 0.05, "FIRE": 0.01},
            "severity": 4.4,
            "severity_label": "CRITICAL",
            "location": {
                "text": "Mumbai-Pune expressway near Lonavala exit",
                "lat": 18.7546,
                "lon": 73.4062,
                "geocoded": True,
            },
            "people_affected": 1,
            "injuries": ["not moving", "lot of blood"],
            "hazards": ["traffic blocked"],
            "summary": "Truck hit two cars near Lonavala exit; one person unresponsive and bleeding heavily; road blocked.",
            "responders": ["AMBULANCE", "TRAFFIC_POLICE"],
            "sdg_targets": ["3.6"],
            "explanation": {
                "attention": [["accident", 0.71], ["not", 0.64], ["moving", 1.0], ["blood", 0.88]]
            },
            "extractor": "flan_t5",
            "latency_ms": 840,
        }

    # Create a realistic queue sorted by severity descending
    _MOCK_ALERTS_STORE = [
        # 1. Critical Disaster (geocoded)
        {
            "alert_id": "RQP-000101",
            "created_at": "2026-10-20T14:40:10+05:30",
            "status": "NEW",
            "is_emergency": True,
            "incident_type": "EARTHQUAKE_COLLAPSE",
            "type_confidence": 0.97,
            "type_probs": {"EARTHQUAKE_COLLAPSE": 0.97, "FIRE": 0.02},
            "severity": 5.0,
            "severity_label": "CRITICAL",
            "location": {
                "text": "Sector 62 Noida construction site",
                "lat": 28.6279,
                "lon": 77.3732,
                "geocoded": True,
            },
            "people_affected": 8,
            "injuries": ["8 workers trapped", "voice heard under slab"],
            "hazards": ["collapsed concrete slab", "heavy dust"],
            "summary": "Building collapse at Sector 62 Noida; 8 workers trapped under slab; rescue cranes required urgently.",
            "responders": ["DISASTER_RESPONSE", "FIRE_BRIGADE", "AMBULANCE"],
            "sdg_targets": ["11.5"],
            "explanation": {
                "attention": [["collapse", 1.0], ["trapped", 0.95], ["workers", 0.78], ["cranes", 0.65]]
            },
            "extractor": "flan_t5",
            "latency_ms": 780,
        },
        # 2. Critical Fire (geocoded)
        {
            "alert_id": "RQP-000102",
            "created_at": "2026-10-20T14:38:22+05:30",
            "status": "NEW",
            "is_emergency": True,
            "incident_type": "FIRE",
            "type_confidence": 0.94,
            "type_probs": {"FIRE": 0.94, "EARTHQUAKE_COLLAPSE": 0.03},
            "severity": 4.5,
            "severity_label": "CRITICAL",
            "location": {
                "text": "Mira Road Mumbai flat",
                "lat": 19.2812,
                "lon": 72.8561,
                "geocoded": True,
            },
            "people_affected": 2,
            "injuries": ["holding baby", "door full of smoke"],
            "hazards": ["burning sofa and curtains", "heavy smoke"],
            "summary": "Apartment fire in Mira Road flat; mother with infant trapped by smoke; fire brigade dispatched.",
            "responders": ["FIRE_BRIGADE", "AMBULANCE"],
            "sdg_targets": ["11.5"],
            "explanation": {
                "attention": [["fire", 0.92], ["burning", 0.88], ["smoke", 0.96], ["trapped", 0.91]]
            },
            "extractor": "flan_t5",
            "latency_ms": 810,
        },
        # 3. Critical Transport Accident (Section 6 mock)
        mock_base,
        # 4. High Flood (geocoded)
        {
            "alert_id": "RQP-000104",
            "created_at": "2026-10-20T14:30:15+05:30",
            "status": "CONFIRMED",
            "is_emergency": True,
            "incident_type": "FLOOD",
            "type_confidence": 0.92,
            "type_probs": {"FLOOD": 0.92, "STORM_CYCLONE": 0.05},
            "severity": 3.8,
            "severity_label": "HIGH",
            "location": {
                "text": "Mulshi road near Paud",
                "lat": 18.5204,
                "lon": 73.6189,
                "geocoded": True,
            },
            "people_affected": 40,
            "injuries": [],
            "hazards": ["water reached windows", "bus leaning in flood water"],
            "summary": "Student bus stranded in rising flood water on Mulshi Road; bus leaning; evacuation boats required.",
            "responders": ["DISASTER_RESPONSE", "AMBULANCE"],
            "sdg_targets": ["11.5", "13.1"],
            "explanation": {
                "attention": [["flood", 0.95], ["stuck", 0.85], ["water", 0.72], ["students", 0.60]]
            },
            "extractor": "flan_t5",
            "latency_ms": 760,
        },
        # 5. Medium Medical (Missing location coords - test geocoded: false filtering)
        {
            "alert_id": "RQP-000105",
            "created_at": "2026-10-20T14:25:00+05:30",
            "status": "DISPATCHED",
            "is_emergency": True,
            "incident_type": "MEDICAL",
            "type_confidence": 0.89,
            "type_probs": {"MEDICAL": 0.89, "NON_EMERGENCY": 0.08},
            "severity": 2.8,
            "severity_label": "MEDIUM",
            "location": {
                "text": "Near central market",
                "lat": None,
                "lon": None,
                "geocoded": False,
            },
            "people_affected": 1,
            "injuries": ["dizziness and chest tightness"],
            "hazards": [],
            "summary": "Elderly citizen experiencing chest tightness and dizziness near central market.",
            "responders": ["AMBULANCE"],
            "sdg_targets": ["3.d"],
            "explanation": {
                "attention": [["chest", 0.82], ["dizziness", 0.78], ["tightness", 0.75]]
            },
            "extractor": "fallback_rules",
            "latency_ms": 690,
        },
        # 6. Low Violence Crime (Vague)
        {
            "alert_id": "RQP-000106",
            "created_at": "2026-10-20T14:20:00+05:30",
            "status": "NEW",
            "is_emergency": True,
            "incident_type": "VIOLENCE_CRIME",
            "type_confidence": 0.74,
            "type_probs": {"VIOLENCE_CRIME": 0.74, "NON_EMERGENCY": 0.22},
            "severity": 1.8,
            "severity_label": "LOW",
            "location": {
                "text": "house next door",
                "lat": None,
                "lon": None,
                "geocoded": False,
            },
            "people_affected": None,
            "injuries": [],
            "hazards": ["throwing objects"],
            "summary": "Shouting and disturbance reported in neighboring residence.",
            "responders": ["POLICE"],
            "sdg_targets": ["16.1"],
            "explanation": {
                "attention": [["shouting", 0.65], ["throwing", 0.60], ["worried", 0.50]]
            },
            "extractor": "fallback_rules",
            "latency_ms": 610,
        },
    ]
    return _MOCK_ALERTS_STORE


def _generate_mock_alert_for_text(text: str, source: str = "text", transcript_confidence: Optional[float] = None) -> Dict[str, Any]:
    """Generate a high-fidelity mock alert dynamically matching the text topic."""
    samples = _load_json_file(DEMO_SAMPLES_PATH) or []
    cleaned_lower = text.lower()

    # Look for exact sample match or keyword match
    matched_sample = None
    for sample in samples:
        if sample.get("text", "").strip().lower() == cleaned_lower.strip():
            matched_sample = sample
            break

    # Determine incident type and severity
    if matched_sample:
        incident_type = matched_sample.get("expected_type", "TRANSPORT_ACCIDENT")
        severity = float(matched_sample.get("expected_severity", 3.0))
    else:
        # Check non-emergency keywords first
        if any(w in cleaned_lower for w in ["ac is not", " ac ", "air condition", "exam", "service centre", "weather", "is the mall", "joke", "prank", "complaint", "not an emergency", "query"]):
            incident_type = "NON_EMERGENCY"
            severity = 1.0
        elif any(w in cleaned_lower for w in ["fire", "aag", "smoke", "cylinder", "burn"]):
            incident_type = "FIRE"
            severity = 4.2
        elif any(w in cleaned_lower for w in ["flood", "pani", "drowning", "river", "submerged", "dam"]):
            incident_type = "FLOOD"
            severity = 4.5
        elif any(w in cleaned_lower for w in ["storm", "cyclone", "tree fell", "wind", "roof"]):
            incident_type = "STORM_CYCLONE"
            severity = 4.0
        elif any(w in cleaned_lower for w in ["collapse", "building", "slab", "debris", "trapped"]):
            incident_type = "EARTHQUAKE_COLLAPSE"
            severity = 5.0
        elif any(w in cleaned_lower for w in ["accident", "truck", "crash", "collision", "overturned", "highway", "expressway", "flipped", "skid"]):
            incident_type = "TRANSPORT_ACCIDENT"
            severity = 4.4
        elif any(w in cleaned_lower for w in ["pregnant", "bleeding", "heart attack", "unconscious", "breathing"]):
            incident_type = "MEDICAL"
            severity = 4.5
        elif any(w in cleaned_lower for w in ["gang", "gun", "knife", "swords", "police", "attack", "fight"]):
            incident_type = "VIOLENCE_CRIME"
            severity = 4.8
        elif "car" in cleaned_lower:
            incident_type = "TRANSPORT_ACCIDENT"
            severity = 3.5
        else:
            incident_type = "TRANSPORT_ACCIDENT"
            severity = 3.5

    is_emergency = incident_type != "NON_EMERGENCY"
    if not is_emergency:
        severity = 1.0

    # Severity label mapping per SCHEMA §1.2
    if severity < 2.0:
        severity_label = "LOW"
    elif severity < 3.0:
        severity_label = "MEDIUM"
    elif severity < 4.0:
        severity_label = "HIGH"
    else:
        severity_label = "CRITICAL"

    # Location heuristic
    loc_text = None
    lat, lon, geocoded = None, None, False
    if "lonavala" in cleaned_lower or "expressway" in cleaned_lower:
        loc_text = "Mumbai-Pune expressway near Lonavala exit"
        lat, lon, geocoded = 18.7546, 73.4062, True
    elif "mira road" in cleaned_lower:
        loc_text = "Mira Road, Mumbai"
        lat, lon, geocoded = 19.2812, 72.8561, True
    elif "mulshi" in cleaned_lower or "paud" in cleaned_lower:
        loc_text = "Mulshi Road near Paud"
        lat, lon, geocoded = 18.5204, 73.6189, True
    elif "noida" in cleaned_lower or "sector 62" in cleaned_lower:
        loc_text = "Sector 62, Noida"
        lat, lon, geocoded = 28.6279, 77.3732, True
    elif "park street" in cleaned_lower:
        loc_text = "Park Street, Kolkata"
        lat, lon, geocoded = 22.5516, 88.3524, True
    elif "saheed nagar" in cleaned_lower:
        loc_text = "Saheed Nagar, Bhubaneswar"
        lat, lon, geocoded = 20.2885, 85.8456, True
    elif "kolhapur" in cleaned_lower:
        loc_text = "km 112, Kolhapur-Pune highway"
        lat, lon, geocoded = 16.7050, 74.2433, True

    # Responders mapping per SCHEMA §1.1 & §1.3
    responders_map = {
        "FIRE": ["FIRE_BRIGADE", "AMBULANCE"],
        "FLOOD": ["DISASTER_RESPONSE", "AMBULANCE"],
        "STORM_CYCLONE": ["DISASTER_RESPONSE", "AMBULANCE"],
        "EARTHQUAKE_COLLAPSE": ["DISASTER_RESPONSE", "FIRE_BRIGADE", "AMBULANCE"],
        "TRANSPORT_ACCIDENT": ["AMBULANCE", "TRAFFIC_POLICE"],
        "MEDICAL": ["AMBULANCE"],
        "VIOLENCE_CRIME": ["POLICE", "AMBULANCE"],
        "NON_EMERGENCY": [],
    }
    responders = responders_map.get(incident_type, [])

    # SDG Targets per SCHEMA §1.1
    sdg_map = {
        "FIRE": ["11.5"],
        "FLOOD": ["11.5", "13.1"],
        "STORM_CYCLONE": ["11.5", "13.1"],
        "EARTHQUAKE_COLLAPSE": ["11.5"],
        "TRANSPORT_ACCIDENT": ["3.6"],
        "MEDICAL": ["3.d"],
        "VIOLENCE_CRIME": ["16.1"],
        "NON_EMERGENCY": [],
    }
    sdg_targets = sdg_map.get(incident_type, [])

    # Attention scores extraction from text words
    words = [w.strip(".,!?:;\"'()[]") for w in text.split() if w.strip()]
    attention = []
    high_impact_words = {
        "fire", "burning", "smoke", "baby", "trapped", "blood", "accident", "bleeding",
        "collapse", "slab", "workers", "gang", "swords", "flood", "bus", "storm", "roof",
        "pregnant", "unresponsive", "police", "help", "hurry", "urgent", "not", "moving"
    }
    for word in words:
        w_lower = word.lower()
        if w_lower in high_impact_words:
            attention.append([word, 0.85 + (hash(word) % 15) / 100.0])
        elif len(word) > 4:
            attention.append([word, 0.40 + (hash(word) % 35) / 100.0])
        else:
            attention.append([word, 0.15 + (hash(word) % 25) / 100.0])

    alert_id = f"RQP-{hash(text) % 900000 + 100000:06d}"

    alert = {
        "alert_id": alert_id,
        "created_at": "2026-10-20T14:35:00+05:30",
        "status": "DISMISSED" if not is_emergency else "NEW",
        "is_emergency": is_emergency,
        "input": {
            "text": text,
            "source": source,
            "transcript_confidence": transcript_confidence if source == "voice" else None,
        },
        "incident_type": incident_type,
        "type_confidence": 0.94 if is_emergency else 0.88,
        "type_probs": {
            incident_type: 0.94 if is_emergency else 0.88,
            "NON_EMERGENCY": 0.02 if is_emergency else 0.88,
        },
        "severity": severity,
        "severity_label": severity_label,
        "location": {
            "text": loc_text,
            "lat": lat,
            "lon": lon,
            "geocoded": geocoded,
        },
        "people_affected": 2 if is_emergency else None,
        "injuries": ["reported distress", "injuries present"] if is_emergency and severity >= 3.0 else [],
        "hazards": ["ongoing situation"] if is_emergency else [],
        "summary": (
            f"Emergency alert: {incident_type.replace('_', ' ').title()} reported at {loc_text or 'unspecified location'}."
            if is_emergency
            else "Report analyzed as non-emergency inquiry or complaint. No emergency response required."
        ),
        "responders": responders,
        "sdg_targets": sdg_targets,
        "explanation": {
            "attention": attention,
        },
        "duplicate_of": None,
        "extractor": "flan_t5",
        "model_versions": {
            "classifier": "distilbert-v1",
            "generator": "flan-t5-v1",
            "asr": "small.en",
        },
        "latency_ms": 780,
    }

    # Add to mock queue if emergency
    if is_emergency:
        global _MOCK_ALERTS_STORE
        _init_mock_alerts()
        _MOCK_ALERTS_STORE.insert(0, alert)

    return alert


# ==============================================================================
# Public API Functions
# ==============================================================================

def check_health(base_url: Optional[str] = None, timeout: int = 4) -> Dict[str, Any]:
    """
    Check backend health endpoint: GET /health.
    Raises BackendNotReachableError if connection fails.
    """
    url = f"{base_url or get_base_url()}/health"
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
        raise APIResponseError(resp.status_code, "HEALTH_CHECK_FAILED", resp.text)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise BackendNotReachableError(f"backend not reachable at {url}: {e}")
    except Exception as e:
        raise BackendNotReachableError(f"backend not reachable: {e}")


def get_alert(
    text: str,
    source: str = "text",
    transcript_confidence: Optional[float] = None,
    mock_mode: bool = True,
    base_url: Optional[str] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Submit report text for AI classification and extraction.
    Calls POST /analyze in live mode; generates structured alert in mock mode.
    """
    clean_text = text.strip() if text else ""
    if not clean_text:
        raise ResQPulseAPIError("Report text cannot be empty.")

    if len(clean_text) > 2000:
        raise ResQPulseAPIError("Report text exceeds maximum limit of 2,000 characters.")

    if mock_mode:
        return _generate_mock_alert_for_text(clean_text, source=source, transcript_confidence=transcript_confidence)

    # Live Mode
    url = f"{base_url or get_base_url()}/analyze"
    payload = {
        "text": clean_text,
        "source": source,
        "transcript_confidence": transcript_confidence,
    }

    try:
        resp = requests.post(url, json=payload, timeout=timeout)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise BackendNotReachableError(f"backend not reachable at {url}: {e}")
    except Exception as e:
        raise BackendNotReachableError(f"backend not reachable: {e}")

    if resp.status_code == 200:
        try:
            return resp.json()
        except ValueError:
            raise APIResponseError(resp.status_code, "INVALID_JSON", "Backend returned malformed JSON response.")

    # Handle error responses according to SCHEMA §7
    try:
        err_data = resp.json().get("error", {})
        code = err_data.get("code", "ERROR")
        msg = err_data.get("message", resp.text)
    except Exception:
        code = "HTTP_ERROR"
        msg = resp.text
    raise APIResponseError(resp.status_code, code, msg)


def transcribe_audio(
    file_bytes: bytes,
    filename: str = "audio.wav",
    mock_mode: bool = True,
    base_url: Optional[str] = None,
    timeout: int = 35,
) -> Dict[str, Any]:
    """
    Submit audio file for speech-to-text transcription.
    Calls POST /transcribe in live mode; returns realistic speech result in mock mode.
    """
    if not file_bytes:
        raise ResQPulseAPIError("Audio input is empty or invalid.")

    if mock_mode:
        # High quality mock speech transcription
        return {
            "transcript": "Accident on Mumbai-Pune expressway near Lonavala exit, truck hit two cars, one guy not moving, lot of blood, traffic blocked",
            "confidence": 0.88,
            "low_confidence": False,
            "duration_s": 8.4,
        }

    # Live Mode
    url = f"{base_url or get_base_url()}/transcribe"
    files = {"file": (filename, file_bytes, "audio/wav")}

    try:
        resp = requests.post(url, files=files, timeout=timeout)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise BackendNotReachableError(f"backend not reachable at {url}: {e}")
    except Exception as e:
        raise BackendNotReachableError(f"backend not reachable: {e}")

    if resp.status_code == 200:
        try:
            return resp.json()
        except ValueError:
            raise APIResponseError(resp.status_code, "INVALID_JSON", "Backend returned malformed JSON transcript.")

    try:
        err_data = resp.json().get("error", {})
        code = err_data.get("code", "AUDIO_ERROR")
        msg = err_data.get("message", resp.text)
    except Exception:
        code = "HTTP_ERROR"
        msg = resp.text
    raise APIResponseError(resp.status_code, code, msg)


def get_alerts(
    status: Optional[str] = None,
    limit: int = 50,
    mock_mode: bool = True,
    base_url: Optional[str] = None,
    timeout: int = 10,
) -> Dict[str, Any]:
    """
    Retrieve priority queue of alerts.
    Calls GET /alerts in live mode.
    """
    if mock_mode:
        alerts = _init_mock_alerts()
        filtered = alerts
        if status:
            filtered = [a for a in alerts if a.get("status") == status]
        sorted_alerts = sorted(
            filtered,
            key=lambda x: (-float(x.get("severity", 0.0)), str(x.get("created_at", "")))
        )
        return {"alerts": sorted_alerts[:limit]}

    # Live Mode
    url = f"{base_url or get_base_url()}/alerts"
    params: Dict[str, Any] = {"limit": limit}
    if status:
        params["status"] = status

    try:
        resp = requests.get(url, params=params, timeout=timeout)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise BackendNotReachableError(f"backend not reachable at {url}: {e}")
    except Exception as e:
        raise BackendNotReachableError(f"backend not reachable: {e}")

    if resp.status_code == 200:
        try:
            return resp.json()
        except ValueError:
            raise APIResponseError(resp.status_code, "INVALID_JSON", "Backend returned invalid alert list JSON.")

    raise APIResponseError(resp.status_code, "GET_ALERTS_FAILED", resp.text)


def update_alert(
    alert_id: str,
    status: Optional[str] = None,
    edits: Optional[Dict[str, Any]] = None,
    mock_mode: bool = True,
    base_url: Optional[str] = None,
    timeout: int = 10,
) -> Dict[str, Any]:
    """
    Update alert status and/or edits via PATCH /alerts/{alert_id}.
    """
    if mock_mode:
        alerts = _init_mock_alerts()
        for a in alerts:
            if a.get("alert_id") == alert_id:
                if status:
                    a["status"] = status
                if edits:
                    for k, v in edits.items():
                        a[k] = v
                return a
        # If not found in mock queue, create a synthetic updated stub
        return {"alert_id": alert_id, "status": status or "CONFIRMED"}

    # Live Mode
    url = f"{base_url or get_base_url()}/alerts/{alert_id}"
    payload: Dict[str, Any] = {}
    if status:
        payload["status"] = status
    if edits:
        payload["edits"] = edits

    try:
        resp = requests.patch(url, json=payload, timeout=timeout)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise BackendNotReachableError(f"backend not reachable at {url}: {e}")
    except Exception as e:
        raise BackendNotReachableError(f"backend not reachable: {e}")

    if resp.status_code == 200:
        try:
            return resp.json()
        except ValueError:
            raise APIResponseError(resp.status_code, "INVALID_JSON", "Backend returned invalid updated alert JSON.")

    raise APIResponseError(resp.status_code, "UPDATE_ALERT_FAILED", resp.text)


def get_metrics(
    mock_mode: bool = True,
    base_url: Optional[str] = None,
    timeout: int = 10,
) -> Optional[Dict[str, Any]]:
    """
    Fetch evaluation metrics.
    Calls GET /metrics in live mode or reads reports/metrics.json locally.
    """
    if mock_mode:
        metrics_data = _load_json_file(METRICS_PATH)
        return metrics_data

    # Live Mode
    url = f"{base_url or get_base_url()}/metrics"
    try:
        resp = requests.get(url, timeout=timeout)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise BackendNotReachableError(f"backend not reachable at {url}: {e}")
    except Exception as e:
        raise BackendNotReachableError(f"backend not reachable: {e}")

    if resp.status_code == 200:
        try:
            return resp.json()
        except ValueError:
            raise APIResponseError(resp.status_code, "INVALID_JSON", "Backend returned invalid metrics JSON.")

    raise APIResponseError(resp.status_code, "GET_METRICS_FAILED", resp.text)
