from typing import Literal, Optional
from pydantic import BaseModel
import re

IncidentType = Literal[
    "FIRE", "FLOOD", "STORM_CYCLONE", "EARTHQUAKE_COLLAPSE",
    "TRANSPORT_ACCIDENT", "MEDICAL", "VIOLENCE_CRIME", "NON_EMERGENCY"
]

class ClassifyResult(BaseModel):
    incident_type: IncidentType
    probs: dict[str, float]
    severity: float
    attention: list[tuple[str, float]]

class ExtractResult(BaseModel):
    location: Optional[str] = None
    people_affected: Optional[int] = None
    injuries: list[str] = []
    hazards: list[str] = []
    summary: str = ""
    extractor: Literal["flan_t5", "fallback_rules"] = "flan_t5"

class TranscribeResult(BaseModel):
    transcript: str
    confidence: float
    low_confidence: bool
    duration_s: float

def classify(text: str) -> ClassifyResult:
    text_lower = text.lower()
    
    # Simple rule-based mock for testing pipelines
    if any(k in text_lower for k in ["fire", "cylinder", "smoke", "blaze"]):
        itype = "FIRE"
        sev = 4.2
    elif any(k in text_lower for k in ["flood", "waterlogging", "submerged"]):
        itype = "FLOOD"
        sev = 3.5
    elif any(k in text_lower for k in ["accident", "crash", "truck", "car"]):
        itype = "TRANSPORT_ACCIDENT"
        sev = 4.4
    elif any(k in text_lower for k in ["heart attack", "unconscious", "stroke", "bleeding"]):
        itype = "MEDICAL"
        sev = 4.0
    elif any(k in text_lower for k in ["knife", "gun", "robbery", "stabbing", "assault"]):
        itype = "VIOLENCE_CRIME"
        sev = 3.8
    elif any(k in text_lower for k in ["cyclone", "hurricane", "fallen trees"]):
        itype = "STORM_CYCLONE"
        sev = 3.7
    elif any(k in text_lower for k in ["collapse", "earthquake", "trapped"]):
        itype = "EARTHQUAKE_COLLAPSE"
        sev = 4.8
    elif any(k in text_lower for k in ["exam", "weather", "mall open", "test", "hello"]):
        itype = "NON_EMERGENCY"
        sev = 1.0
    else:
        itype = "TRANSPORT_ACCIDENT"
        sev = 3.0

    all_types = [
        "FIRE", "FLOOD", "STORM_CYCLONE", "EARTHQUAKE_COLLAPSE",
        "TRANSPORT_ACCIDENT", "MEDICAL", "VIOLENCE_CRIME", "NON_EMERGENCY"
    ]
    probs = {t: 0.05 for t in all_types}
    probs[itype] = 0.65

    words = re.findall(r"\w+", text)
    attention = [(w, round(0.3 if len(w) % 2 == 0 else 0.8, 2)) for w in words[:15]]

    return ClassifyResult(
        incident_type=itype,
        probs=probs,
        severity=sev,
        attention=attention
    )

def extract(text: str) -> ExtractResult:
    text_lower = text.lower()
    
    # Extraction mock following word-for-word guidelines
    location = None
    if "fc road" in text_lower:
        location = "FC road"
    elif "lonavala" in text_lower:
        location = "Mumbai-Pune expressway near Lonavala exit"
    elif "delhi" in text_lower:
        location = "Connaught Place, Delhi"

    people = 3 if "trapped" in text_lower or "people" in text_lower else 1
    injuries = [w for w in ["bleeding", "unconscious", "not moving", "broken leg"] if w in text_lower]
    hazards = [w for w in ["smoke", "petrol pump", "gas cylinder", "traffic blocked"] if w in text_lower]

    return ExtractResult(
        location=location,
        people_affected=people,
        injuries=injuries,
        hazards=hazards,
        summary=f"Automated incident alert extracted from incoming report text.",
        extractor="flan_t5"
    )

def transcribe(audio_bytes: bytes) -> TranscribeResult:
    return TranscribeResult(
        transcript="Accident on Mumbai-Pune expressway near Lonavala exit, truck hit two cars, one guy not moving, lot of blood, traffic blocked",
        confidence=0.88,
        low_confidence=False,
        duration_s=8.5
    )