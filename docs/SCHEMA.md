# ResQPulse AI — Project Schema (v1)

**The single source of truth for every data format in the project.** Data files, Claude generation output,
model inputs/outputs, the API and the UI all follow this document. If you need to change something here,
change it in a PR and tell the whole team, since every part depends on it.

| Section | Who uses it |
|---|---|
| [1. Shared enums](#1-shared-enums) | Everyone |
| [2. Training data row](#2-training-data-row-unified-csv) | ML1 writes, ML2/ML3 read |
| [3. Synthetic generation with Claude](#3-synthetic-generation-with-claude) | ML1 |
| [4. Generator (Flan-T5) text format](#4-generator-flan-t5-text-format) | ML1 writes, ML3 trains |
| [5. Model interfaces](#5-model-interfaces-python) | ML2, ML3, BE2 implement; BE1 calls |
| [6. Alert object](#6-alert-object) | BE1 builds, FE displays |
| [7. API contract](#7-api-contract) | BE1 implements, FE calls |
| [8. Metrics report](#8-metrics-report) | ML1/ML2/ML3 write, FE displays |
| [9. Conventions](#9-conventions) | Everyone |

---

## 1. Shared enums

### 1.1 `incident_type` (8 classes)

| Value | Covers | Default responders | SDG |
|---|---|---|---|
| `FIRE` | Building/vehicle/forest fire, explosion, gas leak | `FIRE_BRIGADE`, `AMBULANCE` | 11.5 |
| `FLOOD` | Flooding, waterlogging, dam/embankment breach, landslide from rain | `DISASTER_RESPONSE`, `AMBULANCE` | 11.5, 13.1 |
| `STORM_CYCLONE` | Cyclone, hurricane, storm, strong winds, fallen trees/poles | `DISASTER_RESPONSE`, `AMBULANCE` | 11.5, 13.1 |
| `EARTHQUAKE_COLLAPSE` | Earthquake, building/wall/bridge collapse, people trapped under debris | `DISASTER_RESPONSE`, `FIRE_BRIGADE`, `AMBULANCE` | 11.5 |
| `TRANSPORT_ACCIDENT` | Road, rail or air accident | `AMBULANCE`, `TRAFFIC_POLICE` | 3.6 |
| `MEDICAL` | Collapse, heart attack, stroke, breathing trouble, labour, poisoning, severe injury without another cause | `AMBULANCE` | 3.d |
| `VIOLENCE_CRIME` | Assault, shooting, stabbing, bombing, robbery in progress, riot | `POLICE`, `AMBULANCE` | 16.1 |
| `NON_EMERGENCY` | Questions, complaints, jokes, figurative use ("my phone is on fire"), test/prank calls | none | – |

> `STORM_CYCLONE` was added because hurricanes/cyclones are the largest part of HumAID. `TRANSPORT_ACCIDENT`
> replaces `ROAD_ACCIDENT` so CrisisLexT26's train and helicopter crashes fit. See DATASETS.md.

### 1.2 `severity` (float 1.0–5.0) and `severity_label`

Use this rubric **everywhere**: in the Claude prompt, when verifying the gold set, and in the pitch.

| Score | Meaning | Examples |
|---|---|---|
| **1** | Minor, nobody hurt, no spreading risk | Small dustbin fire put out; minor fender-bender |
| **2** | Minor injuries, or property damage that's contained | Bike skid, scraped knee; waterlogged street |
| **3** | One serious injury, or property/lives at real risk | Person with a fracture; kitchen fire spreading |
| **4** | Life-threatening, or several people hurt | Unconscious person; multi-car crash with bleeding |
| **5** | Deaths, mass casualties, people trapped, hazard spreading fast | Building collapse with people trapped; fire near a gas cylinder with people inside |

Half-points (e.g. 3.5) are allowed. `NON_EMERGENCY` is always **1.0**.

| `severity_label` | Range |
|---|---|
| `LOW` | severity < 2.0 |
| `MEDIUM` | 2.0 ≤ severity < 3.0 |
| `HIGH` | 3.0 ≤ severity < 4.0 |
| `CRITICAL` | severity ≥ 4.0 |

### 1.3 Other enums

| Enum | Values |
|---|---|
| `responder` | `FIRE_BRIGADE`, `AMBULANCE`, `POLICE`, `TRAFFIC_POLICE`, `DISASTER_RESPONSE` (NDRF/SDRF) |
| `input_source` | `text`, `voice` |
| `data_source` | `humaid`, `crisislex`, `kaggle_disaster`, `synthetic`, `synthetic_asr`, `gold_manual` |
| `split` | `train`, `val`, `test`, `gold` |
| `style` (synthetic only) | `panicked_caller`, `calm_bystander`, `sms_shorthand`, `whatsapp_message`, `elderly_caller`, `child_caller`, `official_report`, `vague_report` |
| `alert_status` | `NEW`, `CONFIRMED`, `DISPATCHED`, `RESOLVED`, `DISMISSED` |
| `extractor` | `flan_t5`, `fallback_rules` |

**Responder rules** (applied by BE1 after the models run): start with the type's default responders; add
`AMBULANCE` if `injuries` is non-empty; add `DISASTER_RESPONSE` if severity ≥ 4.5 and people are trapped or
more than 10 are affected. `NON_EMERGENCY` → empty list.

---

## 2. Training data row (unified CSV)

ML1 converts **every** source into this one format. Files: `data/processed/{train,val,test_synth}.csv`
and `data/gold/gold.csv`. UTF-8, comma-separated, header row, quoted text.

| Column | Type | Required | Notes |
|---|---|---|---|
| `id` | string | ✅ | `<data_source>-<original id or running number>`, e.g. `humaid-798064896545996801`, `synthetic-000412` |
| `text` | string | ✅ | Cleaned report text (URLs → removed, `@user` → removed, `RT` removed, `#word` → `word`) |
| `incident_type` | enum §1.1 | ✅ | |
| `severity` | float or empty | – | Empty for real tweets (the severity loss is masked for them) |
| `fields_json` | JSON string or empty | – | §2.1. Empty for real tweets, except in the gold set |
| `data_source` | enum §1.3 | ✅ | Needed to report scores per source |
| `split` | enum §1.3 | ✅ | |
| `style` | enum §1.3 or empty | – | Synthetic only |
| `event` | string or empty | – | Original event/crisis name, e.g. `kerala_floods_2018`. Used for crisis-level splits |
| `humanitarian_label` | string or empty | – | Original HumAID/CrisisLex label, kept for analysis |

### 2.1 `fields_json`

```json
{
  "location": "petrol pump on FC road",
  "people_affected": 3,
  "injuries": ["stuck inside the shop"],
  "hazards": ["smoke", "petrol pump"],
  "summary": "Fire near FC Road petrol pump; 2-3 people trapped inside a shop; heavy smoke."
}
```

| Field | Type | Rule |
|---|---|---|
| `location` | string or `null` | **Copied word for word** from `text`. `null` if no place is mentioned |
| `people_affected` | int or `null` | Number of people hurt, trapped or at direct risk. For a range ("2-3") take the **upper** bound. `null` if unknown |
| `injuries` | list of strings | Each item **word for word** from `text` ("not moving", "bleeding"). `[]` if none |
| `hazards` | list of strings | Each item **word for word** from `text` ("gas cylinder", "smoke"). `[]` if none |
| `summary` | string | One sentence, ≤ 30 words, neutral dispatcher style. **Not** word for word |

The word-for-word rule is what makes extraction measurable. ML1 **validates** it: any `location`, `injuries` or
`hazards` item that doesn't appear in `text` (case-insensitive) is removed. If the location fails the check,
it is set to `null`.

---

## 3. Synthetic generation with Claude

> **How it was actually done:** with no API key available, the reports were written directly by Claude in a Claude Code session, following this schema and the rubric in §1.2, one batch per incident type, and checked by `scripts/validate_synthetic.py`. The API sketch in §3.4 remains valid for reproducing or extending the data.

### 3.1 Generation grid

Don't ask for "3,000 reports". Loop over a grid and fill these values into each request:

| Dimension | Values |
|---|---|
| `incident_type` | the 8 types (§1.1). About 10% `NON_EMERGENCY`, the rest split evenly |
| `target_severity` | 1–5, spread evenly within each type (`NON_EMERGENCY` → 1) |
| `style` | the 8 styles (§1.3) |
| `city` | Pune, Mumbai, Delhi, Bengaluru, Chennai, Kolkata, Hyderabad, Ahmedabad, Jaipur, Lucknow, Nagpur, Guwahati, Kochi, Bhubaneswar, Indore, a rural village/highway |
| `detail_level` | `full` (location + numbers), `partial` (one of them missing), `vague` (neither) |

**Per request:** one `incident_type` + one `city`, and a list of 15 (severity, style, detail_level) combinations.
200 requests give 3,000 reports.

### 3.2 Output schema (what Claude returns)

Use **structured outputs** (`output_config.format`) so every response is valid JSON matching this schema:

```json
{
  "type": "object",
  "properties": {
    "reports": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "text":            { "type": "string" },
          "incident_type":   { "type": "string", "enum": ["FIRE","FLOOD","STORM_CYCLONE","EARTHQUAKE_COLLAPSE","TRANSPORT_ACCIDENT","MEDICAL","VIOLENCE_CRIME","NON_EMERGENCY"] },
          "severity":        { "type": "number" },
          "style":           { "type": "string", "enum": ["panicked_caller","calm_bystander","sms_shorthand","whatsapp_message","elderly_caller","child_caller","official_report","vague_report"] },
          "location":        { "anyOf": [{ "type": "string" }, { "type": "null" }] },
          "people_affected": { "anyOf": [{ "type": "integer" }, { "type": "null" }] },
          "injuries":        { "type": "array", "items": { "type": "string" } },
          "hazards":         { "type": "array", "items": { "type": "string" } },
          "summary":         { "type": "string" }
        },
        "required": ["text","incident_type","severity","style","location","people_affected","injuries","hazards","summary"],
        "additionalProperties": false
      }
    }
  },
  "required": ["reports"],
  "additionalProperties": false
}
```

Range checks (severity 1–5, report length) are done **in Python after generation**, not in the schema.

### 3.3 Prompt template

**System:**
```
You generate realistic emergency reports for training an emergency-dispatch AI in India.
Reports must read like real people calling or messaging the 112 emergency line: informal,
sometimes panicked, sometimes with typos or Indian English phrasing, 1-4 sentences, 15-80 words.
Do not use real people's names. Use realistic Indian place names (roads, landmarks, areas).

Severity rubric (1.0-5.0, half points allowed):
1 = minor, nobody hurt; 2 = minor injuries or contained damage; 3 = one serious injury or lives at
real risk; 4 = life-threatening or several people hurt; 5 = deaths, mass casualties, people
trapped, or a hazard spreading fast. NON_EMERGENCY is always 1.0.

Label rules:
- location, every injuries item and every hazards item must be copied EXACTLY, word for word, from
  the report text. Use null / [] when the report doesn't mention them.
- people_affected: people hurt, trapped or at direct risk; for a range take the upper bound; null if unknown.
- summary: one neutral sentence, at most 30 words, written like a dispatcher's note.
- Every report must be different in wording, situation and details.
```

**User (one per request):**
```
Generate 15 reports.
incident_type: {incident_type}
city: {city}
For each report use this combination, in order:
1. severity {s1}, style {style1}, detail_level {d1}
2. ...
15. severity {s15}, style {style15}, detail_level {d15}
detail_level: full = location and numbers given; partial = one of them missing; vague = neither.
```

For `NON_EMERGENCY`, add: *"Mix questions to the helpline, complaints, figurative language that sounds like an
emergency ('this exam is a disaster'), and test or prank calls."*

### 3.4 API call (sketch for `scripts/generate_reports.py`)

```python
import json
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment / .env

response = client.beta.messages.create(
    model="claude-opus-5-5",
    max_tokens=16000,
    betas=["server-side-fallback-2026-07-01"],
    fallbacks="default",              # if a report trips a safety filter, the API retries on a fallback model
    system=SYSTEM_PROMPT,
    messages=[{"role": "user", "content": user_prompt}],
    output_config={
        "effort": "medium",
        "format": {"type": "json_schema", "schema": REPORTS_SCHEMA},
    },
)

if response.stop_reason == "refusal":
    log_and_skip(user_prompt)          # rare: violence prompts may be declined
elif response.stop_reason == "max_tokens":
    retry_with_fewer_reports(user_prompt)
else:
    text = next(b.text for b in response.content if b.type == "text")
    reports = json.loads(text)["reports"]
```

**Notes for ML1:**
- **Model:** `claude-opus-5-5` gives the most varied, realistic reports. `claude-sonnet-5-5` ($2/$10 per million
  tokens) or `claude-haiku-5-5` ($0.10/$0.50) are much cheaper if budget matters. Opus 5.5 is $4/$20.
  3,000 reports is roughly 1M output tokens, so this is a team budget decision.
- **Run requests in parallel** (e.g. 5–8 threads). 200 sequential requests would take too long.
- **Batches API** (`client.messages.batches`) is 50% cheaper but can take hours to finish. Use it only if
  you generate the data **before** the event. `fallbacks` isn't supported on batches.
- **Save each raw response** to `data/raw/synthetic/<request_id>.json` before parsing, so a crash never loses
  paid output.
- **After generating:** validate the word-for-word rule (§2.1), drop reports outside 1–5 severity or 15–80 words,
  remove near-duplicates (TF-IDF cosine > 0.9), then convert to the §2 CSV format with `data_source = synthetic`.

---

## 4. Generator (Flan-T5) text format

T5's vocabulary has **no `{` or `}`**, so Flan-T5 is trained on a flat text format instead of JSON.

**Input:**
```
extract alert: <report text>
```

**Target (one line, fixed field order, ` | ` between fields, `; ` between list items, `none` for null/empty):**
```
location: petrol pump on FC road | people: 3 | injuries: stuck inside the shop | hazards: smoke; petrol pump | summary: Fire near FC Road petrol pump; 2-3 people trapped inside a shop; heavy smoke.
```

| Field | Encoding |
|---|---|
| `location` | text or `none` |
| `people` | integer or `none` |
| `injuries`, `hazards` | items joined with `; `, or `none` |
| `summary` | text (strip any `|` characters from it before training) |

**Parser rules** (`src/models/generator.py`): split on ` | `, then split each part on the first `: `. Unknown or
missing keys → default value. `people` that doesn't parse as an integer → `null`. The result must validate against
`ExtractResult` (§5), otherwise fall back to the rule-based extractor and set `extractor = fallback_rules`.

---

## 5. Model interfaces (Python)

These are the only functions BE1 calls. Until the real models are ready, BE1 uses **fake versions with the same
signatures**.

```python
from typing import Literal, Optional
from pydantic import BaseModel

IncidentType = Literal["FIRE", "FLOOD", "STORM_CYCLONE", "EARTHQUAKE_COLLAPSE",
                       "TRANSPORT_ACCIDENT", "MEDICAL", "VIOLENCE_CRIME", "NON_EMERGENCY"]

class ClassifyResult(BaseModel):                    # ML2: src/models/classifier.py
    incident_type: IncidentType
    probs: dict[str, float]                         # all 8 types, sums to 1
    severity: float                                 # 1.0–5.0, clipped
    attention: list[tuple[str, float]]              # (word, score), in text order, scores 0–1 (max = 1)

class ExtractResult(BaseModel):                     # ML3: src/models/generator.py
    location: Optional[str] = None
    people_affected: Optional[int] = None
    injuries: list[str] = []
    hazards: list[str] = []
    summary: str = ""
    extractor: Literal["flan_t5", "fallback_rules"] = "flan_t5"

class TranscribeResult(BaseModel):                  # BE2: src/asr/whisper.py
    transcript: str
    confidence: float                               # 0–1, mean of exp(avg_logprob) over segments
    low_confidence: bool                            # confidence < 0.5 or no_speech_prob > 0.6
    duration_s: float

def classify(text: str) -> ClassifyResult: ...
def extract(text: str) -> ExtractResult: ...
def transcribe(audio_path: str) -> TranscribeResult: ...
```

Models are loaded **once** when the module is imported (or in a FastAPI startup hook), never per call.

---

## 6. Alert object

What `/analyze` returns and what the dashboard shows. Built by BE1 from `ClassifyResult` + `ExtractResult` +
geocoding + responder rules.

```json
{
  "alert_id": "RQP-000123",
  "created_at": "2026-10-20T14:32:05+05:30",
  "status": "NEW",
  "is_emergency": true,

  "input": {
    "text": "Accident on Mumbai-Pune expressway near Lonavala exit, truck hit two cars, one guy not moving, lot of blood, traffic blocked",
    "source": "voice",
    "transcript_confidence": 0.82
  },

  "incident_type": "TRANSPORT_ACCIDENT",
  "type_confidence": 0.91,
  "type_probs": { "TRANSPORT_ACCIDENT": 0.91, "MEDICAL": 0.05, "FIRE": 0.01 },

  "severity": 4.4,
  "severity_label": "CRITICAL",

  "location": {
    "text": "Mumbai-Pune expressway near Lonavala exit",
    "lat": 18.7546,
    "lon": 73.4062,
    "geocoded": true
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

  "duplicate_of": null,
  "extractor": "flan_t5",
  "model_versions": { "classifier": "distilbert-v1", "generator": "flan-t5-v1", "asr": "small.en" },
  "latency_ms": 840
}
```

| Field | Rule |
|---|---|
| `alert_id` | `RQP-` + 6-digit running number |
| `created_at` | ISO 8601 with offset (IST `+05:30`) |
| `is_emergency` | `false` when `incident_type == NON_EMERGENCY`. Such alerts get `status = DISMISSED` and stay out of the queue |
| `location.lat/lon` | `null` with `geocoded: false` when geocoding fails or there is no location. The map skips these |
| `sdg_targets` | From the type's SDG column (§1.1) |
| `duplicate_of` | `alert_id` of an earlier alert this one duplicates (stretch feature), otherwise `null` |
| `input.transcript_confidence` | `null` for typed input |

**Queue order:** `severity` descending, then `created_at` ascending.

---

## 7. API contract

Base URL from `API_URL` in `.env` (default `http://localhost:8000`). JSON everywhere except the audio upload.

| Method | Path | Request | Response |
|---|---|---|---|
| `GET` | `/health` | – | `{"status": "ok", "models": {"classifier": true, "generator": true, "asr": true}}` |
| `POST` | `/transcribe` | `multipart/form-data`, field `file` (wav/mp3/m4a/webm, ≤ 60 s) | `TranscribeResult` (§5) |
| `POST` | `/analyze` | `{"text": "...", "source": "text" \| "voice", "transcript_confidence": 0.82 \| null}` | Alert (§6) |
| `GET` | `/alerts` | query: `status` (optional), `limit` (default 50) | `{"alerts": [Alert, ...]}` in queue order |
| `GET` | `/alerts/{alert_id}` | – | Alert |
| `PATCH` | `/alerts/{alert_id}` | `{"status": "CONFIRMED", "edits": {"incident_type": "FIRE", "severity": 4.0, "location": {"text": "..."}}}` (all optional) | Updated Alert. Edits are also logged to `reports/corrections.jsonl` for future retraining |
| `GET` | `/metrics` | – | Contents of `reports/metrics.json` (§8) |

**Voice flow:** FE calls `/transcribe` → shows the transcript in an editable box (with a warning if
`low_confidence`) → the dispatcher presses Analyze → FE calls `/analyze` with `source: "voice"`.

**Errors:** HTTP 4xx/5xx with

```json
{ "error": { "code": "EMPTY_INPUT", "message": "Report text is empty." } }
```

| Code | HTTP | When |
|---|---|---|
| `EMPTY_INPUT` | 400 | Text is empty or whitespace |
| `TEXT_TOO_LONG` | 400 | More than 2,000 characters |
| `AUDIO_UNREADABLE` | 400 | Audio can't be decoded, is longer than 60 s, or contains no speech |
| `ALERT_NOT_FOUND` | 404 | Unknown `alert_id` |
| `MODEL_NOT_READY` | 503 | A model failed to load |

Alerts are stored in memory plus a `reports/alerts.jsonl` append log (no database needed for the demo).

---

## 8. Metrics report

All evaluation notebooks write `reports/metrics.json`. The Streamlit metrics page and the README results table
read from it.

```json
{
  "generated_at": "2026-10-20T18:00:00+05:30",
  "eval_sets": {
    "gold":       { "n": 420 },
    "test_synth": { "n": 450 },
    "crisislex":  { "n": 1200 },
    "voice":      { "n": 50 }
  },
  "classification": {
    "baseline_tfidf_lr": { "gold": { "macro_precision": 0.0, "macro_recall": 0.0, "macro_f1": 0.0, "accuracy": 0.0 } },
    "distilbert":        { "gold": { "macro_precision": 0.0, "macro_recall": 0.0, "macro_f1": 0.0, "accuracy": 0.0,
                                     "per_class": { "FIRE": { "precision": 0.0, "recall": 0.0, "f1": 0.0, "support": 0 } } } }
  },
  "severity": {
    "distilbert": { "test_synth": { "mse": 0.0, "rmse": 0.0, "mae": 0.0, "bucket_accuracy": 0.0 } }
  },
  "extraction": {
    "flan_t5": { "test_synth": { "parse_rate": 0.0,
                                 "location_token_f1": 0.0,
                                 "people_exact_match": 0.0,
                                 "injuries": { "precision": 0.0, "recall": 0.0, "f1": 0.0 },
                                 "hazards":  { "precision": 0.0, "recall": 0.0, "f1": 0.0 },
                                 "summary_rougeL": 0.0 } }
  },
  "voice": { "wer": 0.0, "type_macro_f1_typed": 0.0, "type_macro_f1_spoken": 0.0 },
  "latency_ms": { "text_p50": 0, "voice_p50": 0 },
  "confusion_matrix_png": "reports/confusion_matrix_gold.png"
}
```

Keys can be added; **existing keys must not be renamed** without updating the app.

---

## 9. Conventions

| Item | Convention |
|---|---|
| Text encoding | UTF-8 everywhere |
| Times | ISO 8601 with offset, IST `+05:30` |
| Enum values | `UPPER_SNAKE_CASE` for types/statuses/responders; `lower_snake_case` for sources/styles/splits |
| JSON keys | `lower_snake_case` |
| Random seed | `42` for splits and training |
| Text cleaning (all sources) | strip URLs, `@mentions`, leading `RT`, the `#` in hashtags, HTML entities (`&amp;` → `&`); collapse whitespace. **Don't** lowercase in the CSV (DistilBERT uncased lowercases on its own; T5 needs the original casing) |
| Max lengths | Classifier 128 tokens; generator input 256 / output 160 tokens; API text 2,000 chars; audio 60 s |
| Model folders | `models/classifier/`, `models/generator/` (Hugging Face `save_pretrained` format) + `label_map.json` |
| `label_map.json` | `{"FIRE": 0, "FLOOD": 1, "STORM_CYCLONE": 2, "EARTHQUAKE_COLLAPSE": 3, "TRANSPORT_ACCIDENT": 4, "MEDICAL": 5, "VIOLENCE_CRIME": 6, "NON_EMERGENCY": 7}` (this order, fixed) |

## Changelog

| Version | Date | Change |
|---|---|---|
| v1 | 2026-10-16 | First version. Adds `STORM_CYCLONE`; `ROAD_ACCIDENT` → `TRANSPORT_ACCIDENT` |
