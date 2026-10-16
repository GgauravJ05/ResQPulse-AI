"""ML3: field extraction interface (docs/SCHEMA.md §5).

    from src.models.generator import extract
    r = extract("Fire near FC road petrol pump, 3 people stuck inside")
    r.location, r.people_affected, r.injuries, r.hazards, r.summary, r.extractor

The fine-tuned Flan-T5 model is loaded ONCE, when the module is imported, from
    models/generator/   (override with env var RESQPULSE_GENERATOR_DIR or GENERATOR_DIR)
If it cannot load, the module still imports: is_ready() is False and extract() uses the rule-based fallback
(extractor = "fallback_rules"), so the demo keeps working. The fallback is pure Python and needs no network.

Pipeline: generate (4 beams) -> parse -> if the line is incomplete or the summary is empty, retry once with 6 beams
-> if still bad, fallback. The people-count rule is ML3's, from notebooks/flan-t5-train.ipynb cell 35: the model writes
"people: 1" by default, so the number is kept only if the text gives some evidence for a count.
"""
import os
import re
import threading
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel

from src.data.flan import format_input, parse_target

try:  # pick up GENERATOR_DIR from .env when this module is used on its own
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parents[2]
MAX_INPUT_TOKENS, MAX_OUTPUT_TOKENS = 256, 160
MODEL_VERSION = "flan-t5-v1"
_FIELD_KEYS = ["location:", "people:", "injuries:", "hazards:", "summary:"]


def _model_dir() -> Path:
    raw = os.environ.get("RESQPULSE_GENERATOR_DIR") or os.environ.get("GENERATOR_DIR") or "models/generator"
    path = Path(raw)
    return path if path.is_absolute() else REPO_ROOT / path


MODEL_DIR = _model_dir()


class ExtractResult(BaseModel):
    location: Optional[str] = None
    people_affected: Optional[int] = None
    injuries: list[str] = []
    hazards: list[str] = []
    summary: str = ""
    extractor: Literal["flan_t5", "fallback_rules"] = "flan_t5"


# ---------------------------------------------------------------- load once at import
_model = _tokenizer = None
_load_error: Optional[str] = None
_lock = threading.Lock()
try:
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    _tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
    _model = AutoModelForSeq2SeqLM.from_pretrained(str(MODEL_DIR)).eval()
except Exception as e:  # keep the API importable; the fallback still works
    _load_error = f"{type(e).__name__}: {e}"


def is_ready() -> bool:
    """True when the Flan-T5 model is loaded (the fallback works either way)."""
    return _model is not None


# ---------------------------------------------------------------- people-count rule (ML3, notebook cell 35)
PEOPLE_EVIDENCE = re.compile(
    r"\d+|"
    r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|dozen|hundreds|hundred|family|"
    r"mother|father|wife|husband|child|children|baby|babies|"
    r"kid|kids|man|woman|men|women|driver|farmer|biker|"
    r"cyclist|passenger|passengers|victim|victims|person|people|"
    r"worker|workers|resident|residents|patient|patients|"
    r"I|my|we|our|me|injured|injury|injuries|bleeding|"
    r"wounded|cut|fracture|unconscious|responding)\b",
    re.IGNORECASE,
)


def apply_people_rule(text: str, people: Optional[int]) -> Optional[int]:
    """Keep the model's people count only if the text contains evidence for a count."""
    return people if people is not None and PEOPLE_EVIDENCE.search(text) else None


# ---------------------------------------------------------------- model path
def _generate(text: str, beams: int) -> str:
    enc = _tokenizer(format_input(text), return_tensors="pt", truncation=True, max_length=MAX_INPUT_TOKENS)
    with _lock, torch.no_grad():
        out = _model.generate(**enc, max_length=MAX_OUTPUT_TOKENS, num_beams=beams)
    return _tokenizer.decode(out[0], skip_special_tokens=True)


def _clean(raw: str) -> str:
    """A summary that starts with 'none ' keeps the text after it (ML3 notebook cell 28)."""
    m = re.search(r"(?:^|\s*\|\s*)summary:\s*", raw)
    if m and raw[m.end():].lower().startswith("none "):
        raw = raw[:m.end()] + raw[m.end() + 5:].strip()
    return raw


def _complete(raw: str) -> bool:
    """All five fields present and a non-empty summary."""
    return all(k in raw for k in _FIELD_KEYS) and bool(parse_target(raw)["summary"].strip())


# ---------------------------------------------------------------- rule-based fallback (no model, no network)
_NUM_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
              "ten": 10, "eleven": 11, "twelve": 12, "dozen": 12, "couple": 2}
_NOUNS = (r"(?:people|persons?|passengers?|students?|children|kids?|workers?|labourers?|families|men|women|residents|"
          r"patients|victims|villagers|guests|tourists|employees|boys|girls|customers|pilgrims|devotees)")
_PEOPLE_RE = re.compile(rf"\b(\d+|{'|'.join(_NUM_WORDS)})\+?\s+(?:[A-Za-z-]+\s+){{0,2}}?{_NOUNS}\b", re.I)
_SINGLE_RE = re.compile(r"\b(?:a|an|my|one|the)\s+(?:old\s+|elderly\s+|young\s+|small\s+)?"
                        r"(man|woman|child|boy|girl|baby|driver|rider|worker|patient|person|father|mother|wife|husband|"
                        r"brother|sister|grandmother|grandfather|farmer|guard|student|teacher)\b", re.I)
_PLACE_WORDS = ("road|street|marg|nagar|chowk|circle|bridge|station|highway|expressway|market|hospital|school|temple|"
                "colony|junction|flyover|exit|stand|gate|park|lake|pump|bypass|crossing|square|lane|sector|phase|"
                "apartments|office|village|camp|complex")
# a place = a preposition, then capitalised or numeric words, which may continue through common place words
_LOCATION_RE = re.compile(
    r"\b(?:near|at|in|on|outside|behind|opposite|inside|towards|from)\s+"
    rf"((?:the\s+)?[A-Z0-9][\w'.-]*(?:[ ,]+(?:[A-Z0-9][\w'.-]*|(?i:{_PLACE_WORDS})\b)){{0,4}})")
_INJURY_WORDS = ["not breathing", "not moving", "bleeding", "unconscious", "unresponsive", "fainted", "chest pain",
                 "head injury", "fracture", "broken", "burns", "burnt", "injured", "wounded", "trapped", "stuck",
                 "vomiting", "seizure", "dead", "died", "killed", "missing", "cut", "stabbed", "shot"]
_HAZARD_WORDS = ["gas cylinder", "cylinder", "explosion", "blast", "smoke", "fire", "flames", "fuel", "petrol",
                 "diesel", "chemical", "live wire", "sparking", "collapsed", "landslide", "debris", "flood",
                 "water level", "waterlogging", "strong wind", "hailstorm", "traffic blocked", "road blocked",
                 "fog", "knife", "gun", "weapon", "rods"]


def _find_phrases(text: str, words: list, limit: int = 4) -> list:
    found = []
    for w in words:
        m = re.search(rf"\b{re.escape(w)}\b", text, re.I)
        if m and m.group(0) not in found and not any(m.group(0).lower() in f.lower() for f in found):
            found.append(m.group(0))
    return found[:limit]


def _fallback(text: str) -> ExtractResult:
    people = None
    m = _PEOPLE_RE.search(text)
    if m:
        tok = m.group(1).lower()
        people = int(tok) if tok.isdigit() else _NUM_WORDS[tok]
    elif _SINGLE_RE.search(text):
        people = 1
    loc = next((m.group(1).strip(" ,") for m in _LOCATION_RE.finditer(text)
                if not re.match(r"^(?:the\s+)?(?:I|My|We|The|It|He|She|They)\b", m.group(1))), None)
    first = re.split(r"(?<=[.!?])\s+", text.strip())[0]
    summary = " ".join(first.split()[:25]) or "Emergency report received."
    return ExtractResult(location=loc, people_affected=people, injuries=_find_phrases(text, _INJURY_WORDS),
                         hazards=_find_phrases(text, _HAZARD_WORDS), summary=summary, extractor="fallback_rules")


# ---------------------------------------------------------------- public API
def extract(text: str) -> ExtractResult:
    if not text or not text.strip():
        raise ValueError("EMPTY_INPUT")
    text = text.strip()
    if _model is not None:
        for beams in (4, 6):          # second attempt uses a wider beam: same input, different decode
            try:
                raw = _clean(_generate(text, beams))
            except Exception:
                continue
            if _complete(raw):
                d = parse_target(raw)
                return ExtractResult(location=d["location"], people_affected=apply_people_rule(text, d["people_affected"]),
                                     injuries=d["injuries"], hazards=d["hazards"], summary=d["summary"],
                                     extractor="flan_t5")
    return _fallback(text)
