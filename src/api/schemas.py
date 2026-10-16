from typing import Literal, Optional, List, Dict, Tuple, Any
from pydantic import BaseModel, Field

IncidentType = Literal[
    "FIRE", "FLOOD", "STORM_CYCLONE", "EARTHQUAKE_COLLAPSE",
    "TRANSPORT_ACCIDENT", "MEDICAL", "VIOLENCE_CRIME", "NON_EMERGENCY"
]
AlertStatus = Literal["NEW", "CONFIRMED", "DISPATCHED", "RESOLVED", "DISMISSED"]

# --- API Error Model (SCHEMA §7) ---
class ErrorDetail(BaseModel):
    code: Literal["EMPTY_INPUT", "TEXT_TOO_LONG", "AUDIO_UNREADABLE", "ALERT_NOT_FOUND", "MODEL_NOT_READY"]
    message: str

class ErrorResponse(BaseModel):
    error: ErrorDetail

# --- Request Models ---
class AnalyzeRequest(BaseModel):
    text: str
    source: Literal["text", "voice"] = "text"
    transcript_confidence: Optional[float] = None

class AlertEditPayload(BaseModel):
    incident_type: Optional[IncidentType] = None
    severity: Optional[float] = None
    location: Optional[Dict[str, Any]] = None

class PatchAlertRequest(BaseModel):
    status: Optional[AlertStatus] = None
    edits: Optional[AlertEditPayload] = None

# --- Alert Components (SCHEMA §6) ---
class AlertInput(BaseModel):
    text: str
    source: Literal["text", "voice"]
    transcript_confidence: Optional[float] = None

class AlertLocation(BaseModel):
    text: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    geocoded: bool

class AlertExplanation(BaseModel):
    attention: List[Tuple[str, float]]

# --- Output Models ---
class Alert(BaseModel):
    alert_id: str
    created_at: str
    status: AlertStatus
    is_emergency: bool
    input: AlertInput
    incident_type: IncidentType
    type_confidence: float
    type_probs: Dict[str, float]
    severity: float
    severity_label: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    location: AlertLocation
    people_affected: Optional[int] = None
    injuries: List[str] = []
    hazards: List[str] = []
    summary: str
    responders: List[str] = []
    sdg_targets: List[str] = []
    explanation: AlertExplanation
    duplicate_of: Optional[str] = None
    extractor: Literal["flan_t5", "fallback_rules"] = "flan_t5"
    model_versions: Dict[str, str]
    latency_ms: int

class AlertQueueResponse(BaseModel):
    alerts: List[Alert]

class HealthResponse(BaseModel):
    status: str
    models: Dict[str, bool]

class TranscribeResult(BaseModel):
    transcript: str
    confidence: float
    low_confidence: bool
    duration_s: float
