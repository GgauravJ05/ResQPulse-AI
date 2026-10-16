import os
import time
import json
import uuid
import tempfile
import threading
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Tuple
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, Query, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.api.schemas import (
    AnalyzeRequest, PatchAlertRequest, Alert, AlertInput, AlertLocation,
    AlertExplanation, AlertQueueResponse, HealthResponse, ErrorResponse, ErrorDetail
)
from src.services.geocoding import geocode_location

load_dotenv()

USE_FAKE_MODELS = os.getenv("USE_FAKE_MODELS", "true").lower() == "true"

# Base directories
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = ROOT_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

ALERTS_LOG = REPORTS_DIR / "alerts.jsonl"
CORRECTIONS_LOG = REPORTS_DIR / "corrections.jsonl"
METRICS_FILE = REPORTS_DIR / "metrics.json"

app = FastAPI(title="ResQPulse AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global store & model holders
alert_store: Dict[str, Alert] = {}
alert_counter = 1
counter_lock = threading.Lock()
models_loaded = {"classifier": False, "generator": False, "asr": False}

# Model references
classify_fn = None
extract_fn = None
transcribe_fn = None

# --- Startup Lifespan ---
@app.on_event("startup")
def load_models_once():
    global classify_fn, extract_fn, transcribe_fn, models_loaded
    if USE_FAKE_MODELS:
        from src.models.fake import classify, extract, transcribe
        classify_fn = classify
        extract_fn = extract
        transcribe_fn = transcribe
        models_loaded = {"classifier": True, "generator": True, "asr": True}
    else:
        # Load real models when ML2/ML3 deliver them
        try:
            from src.models.classifier import classify as real_classify
            classify_fn = real_classify
            models_loaded["classifier"] = True
        except Exception:
            models_loaded["classifier"] = False

        try:
            from src.models.generator import extract as real_extract
            extract_fn = real_extract
            models_loaded["generator"] = True
        except Exception:
            models_loaded["generator"] = False

        try:
            from src.asr.whisper import transcribe as real_transcribe
            transcribe_fn = real_transcribe
            models_loaded["asr"] = True
        except Exception:
            models_loaded["asr"] = False

# --- Helper Functions ---
def format_error(code: str, message: str, status_code: int):
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}}
    )

def get_ist_timestamp() -> str:
    ist = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist).isoformat(timespec="seconds")

def compute_severity_label(severity: float) -> str:
    if severity < 2.0:
        return "LOW"
    elif severity < 3.0:
        return "MEDIUM"
    elif severity < 4.0:
        return "HIGH"
    return "CRITICAL"

def resolve_responders_and_sdgs(
    incident_type: str,
    injuries: List[str],
    severity: float,
    people_affected: Optional[int],
    text: str
) -> Tuple[List[str], List[str]]:
    if incident_type == "NON_EMERGENCY":
        return [], []

    defaults = {
        "FIRE": (["FIRE_BRIGADE", "AMBULANCE"], ["11.5"]),
        "FLOOD": (["DISASTER_RESPONSE", "AMBULANCE"], ["11.5", "13.1"]),
        "STORM_CYCLONE": (["DISASTER_RESPONSE", "AMBULANCE"], ["11.5", "13.1"]),
        "EARTHQUAKE_COLLAPSE": (["DISASTER_RESPONSE", "FIRE_BRIGADE", "AMBULANCE"], ["11.5"]),
        "TRANSPORT_ACCIDENT": (["AMBULANCE", "TRAFFIC_POLICE"], ["3.6"]),
        "MEDICAL": (["AMBULANCE"], ["3.d"]),
        "VIOLENCE_CRIME": (["POLICE", "AMBULANCE"], ["16.1"]),
    }
    
    responders, sdgs = defaults.get(incident_type, (["AMBULANCE"], []))
    responders = list(responders)

    if injuries and "AMBULANCE" not in responders:
        responders.append("AMBULANCE")

    is_trapped = "trapped" in text.lower() or "stuck" in text.lower()
    affected_count = people_affected or 0
    if severity >= 4.5 and (is_trapped or affected_count > 10):
        if "DISASTER_RESPONSE" not in responders:
            responders.append("DISASTER_RESPONSE")

    return responders, sdgs

# --- Endpoints ---

@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok", models=models_loaded)

@app.post("/transcribe")
async def transcribe_endpoint(file: UploadFile = File(...)):
    if not models_loaded["asr"] or transcribe_fn is None:
        return format_error("MODEL_NOT_READY", "ASR model is not ready.", status.HTTP_503_SERVICE_UNAVAILABLE)

    filename = file.filename or ""
    allowed_exts = (".wav", ".mp3", ".m4a", ".webm")
    if not filename.lower().endswith(allowed_exts):
        return format_error("AUDIO_UNREADABLE", "Unsupported file extension.", status.HTTP_400_BAD_REQUEST)

    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp:
        content = await file.read()
        if len(content) == 0:
            return format_error("AUDIO_UNREADABLE", "Empty audio file.", status.HTTP_400_BAD_REQUEST)
        tmp.write(content)
        tmp_path = tmp.name

    try:
        res = transcribe_fn(tmp_path)
        if res.duration_s > 60.0:
            return format_error("AUDIO_UNREADABLE", "Audio exceeds 60 seconds limit.", status.HTTP_400_BAD_REQUEST)
        if not res.transcript.strip():
            return format_error("AUDIO_UNREADABLE", "Audio contains no recognizable speech.", status.HTTP_400_BAD_REQUEST)
        return res
    except Exception as e:
        return format_error("AUDIO_UNREADABLE", f"Could not decode audio: {str(e)}", status.HTTP_400_BAD_REQUEST)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/analyze", response_model=Alert)
def analyze_endpoint(payload: AnalyzeRequest):
    t0 = time.time()
    
    # Validation
    cleaned_text = payload.text.strip()
    if not cleaned_text:
        return format_error("EMPTY_INPUT", "Report text is empty.", status.HTTP_400_BAD_REQUEST)
    if len(payload.text) > 2000:
        return format_error("TEXT_TOO_LONG", "Text exceeds maximum 2000 characters.", status.HTTP_400_BAD_REQUEST)
    if not models_loaded["classifier"] or not models_loaded["generator"]:
        return format_error("MODEL_NOT_READY", "Inference models are not loaded.", status.HTTP_503_SERVICE_UNAVAILABLE)

    # 1. Model inference
    try:
        cls_res = classify_fn(cleaned_text)
        ext_res = extract_fn(cleaned_text)
    except Exception as e:
        return format_error("MODEL_NOT_READY", f"Model inference failed: {e}", status.HTTP_503_SERVICE_UNAVAILABLE)

    # 2. Rule derivations
    is_emergency = cls_res.incident_type != "NON_EMERGENCY"
    severity = 1.0 if not is_emergency else cls_res.severity
    severity_label = compute_severity_label(severity)
    alert_status = "DISMISSED" if not is_emergency else "NEW"

    responders, sdg_targets = resolve_responders_and_sdgs(
        incident_type=cls_res.incident_type,
        injuries=ext_res.injuries,
        severity=severity,
        people_affected=ext_res.people_affected,
        text=cleaned_text
    )

    # 3. Geocode
    lat, lon, geocoded = geocode_location(ext_res.location)

    # 4. Construct Alert
    global alert_counter
    with counter_lock:
        alert_id = f"RQP-{alert_counter:06d}"
        alert_counter += 1

    latency_ms = int((time.time() - t0) * 1000)

    alert = Alert(
        alert_id=alert_id,
        created_at=get_ist_timestamp(),
        status=alert_status,
        is_emergency=is_emergency,
        input=AlertInput(
            text=payload.text,
            source=payload.source,
            transcript_confidence=payload.transcript_confidence
        ),
        incident_type=cls_res.incident_type,
        type_confidence=cls_res.probs.get(cls_res.incident_type, 0.0),
        type_probs=cls_res.probs,
        severity=severity,
        severity_label=severity_label,
        location=AlertLocation(
            text=ext_res.location,
            lat=lat,
            lon=lon,
            geocoded=geocoded
        ),
        people_affected=ext_res.people_affected,
        injuries=ext_res.injuries,
        hazards=ext_res.hazards,
        summary=ext_res.summary,
        responders=responders,
        sdg_targets=sdg_targets,
        explanation=AlertExplanation(attention=cls_res.attention),
        duplicate_of=None,
        extractor=ext_res.extractor,
        model_versions={
            "classifier": "fake-distilbert" if USE_FAKE_MODELS else "distilbert-v1",
            "generator": "fake-flan-t5" if USE_FAKE_MODELS else "flan-t5-v1",
            "asr": "fake-whisper" if USE_FAKE_MODELS else "small.en"
        },
        latency_ms=latency_ms
    )

    # In-memory store
    alert_store[alert_id] = alert

    # Append to reports/alerts.jsonl
    with open(ALERTS_LOG, "a", encoding="utf-8") as f:
        f.write(alert.model_dump_json() + "\n")

    return alert

@app.get("/alerts", response_model=AlertQueueResponse)
def get_alerts_queue(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = 50
):
    # Only emergencies stay in queue
    eligible = [a for a in alert_store.values() if a.is_emergency and a.status != "DISMISSED"]

    if status_filter:
        eligible = [a for a in eligible if a.status == status_filter]

    # Queue order: severity DESC, then created_at ASC
    sorted_alerts = sorted(eligible, key=lambda a: (-a.severity, a.created_at))
    return AlertQueueResponse(alerts=sorted_alerts[:limit])

@app.get("/alerts/{alert_id}", response_model=Alert)
def get_single_alert(alert_id: str):
    if alert_id not in alert_store:
        return format_error("ALERT_NOT_FOUND", f"Alert '{alert_id}' was not found.", status.HTTP_404_NOT_FOUND)
    return alert_store[alert_id]

@app.patch("/alerts/{alert_id}", response_model=Alert)
def patch_alert(alert_id: str, payload: PatchAlertRequest):
    if alert_id not in alert_store:
        return format_error("ALERT_NOT_FOUND", f"Alert '{alert_id}' was not found.", status.HTTP_404_NOT_FOUND)

    alert = alert_store[alert_id]
    corrections_entry = {
        "timestamp": get_ist_timestamp(),
        "alert_id": alert_id,
        "original": {
            "status": alert.status,
            "incident_type": alert.incident_type,
            "severity": alert.severity,
            "location": alert.location.model_dump()
        },
        "edits": payload.model_dump(exclude_unset=True)
    }

    if payload.status:
        alert.status = payload.status

    if payload.edits:
        if payload.edits.incident_type:
            alert.incident_type = payload.edits.incident_type
        if payload.edits.severity is not None:
            alert.severity = payload.edits.severity
            alert.severity_label = compute_severity_label(payload.edits.severity)
        if payload.edits.location:
            loc_text = payload.edits.location.get("text", alert.location.text)
            lat, lon, geocoded = geocode_location(loc_text)
            alert.location = AlertLocation(text=loc_text, lat=lat, lon=lon, geocoded=geocoded)

    alert_store[alert_id] = alert

    # Log every edit to reports/corrections.jsonl
    with open(CORRECTIONS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(corrections_entry) + "\n")

    return alert

@app.get("/metrics")
def get_metrics():
    if not METRICS_FILE.exists():
        return {}
    try:
        with open(METRICS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}