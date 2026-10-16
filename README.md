# ResQPulse AI

**Turning messy emergency reports into structured, prioritised, explainable alerts.**

GenHack v1.0 · Gen AI course · **PS 15: EmergencyScribe — Convert Emergency Reports Into Structured Alerts**
· Technique: **Transformer + Attention**

> **Status:** repository set up, development not started. Results and run commands are filled in as
> each part is built.
>
> **Team docs, read before your first task:**
> - **[docs/RESEARCH_BRIEF.md](docs/RESEARCH_BRIEF.md)**: the problem, our approach and the reasoning behind every decision
> - **[docs/SCHEMA.md](docs/SCHEMA.md)**: every data format: enums, training CSV, Claude generation, model interfaces, API, alert, metrics
> - **[docs/DATASETS.md](docs/DATASETS.md)**: verified download links for all datasets and models, and how each maps to our labels
> - **[docs/UPDATE.md](docs/UPDATE.md)**: log of every change to the project, newest first

---

## Contents

1. [The problem](#1-the-problem)
2. [Our solution](#2-our-solution)
3. [What makes it different](#3-what-makes-it-different)
4. [Architecture](#4-architecture)
5. [Alert schema](#5-alert-schema)
6. [Data](#6-data)
7. [Models](#7-models)
8. [Evaluation](#8-evaluation)
9. [SDG alignment](#9-sdg-alignment)
10. [Repository structure](#10-repository-structure)
11. [Setup](#11-setup)
12. [Team and roles](#12-team-and-roles)
13. [12-hour plan](#13-12-hour-plan)
14. [Git workflow](#14-git-workflow)
15. [Open decisions](#15-open-decisions)
16. [Limitations and future work](#16-limitations-and-future-work)

---

## 1. The problem

People report emergencies in messy, unstructured language, through calls, SMS, WhatsApp and social media:

> "bhai there's a huge fire near the petrol pump on FC road, 2-3 people stuck inside the shop, smoke everywhere, pls send help fast"

A dispatcher has to work out **what** happened, **how bad** it is, **where**, **how many** people are
affected, **what hazards** exist and **whom to send**, quickly and under pressure. During disasters,
report volume spikes, many reports are duplicates, and urgent ones get buried. Manual triage is slow,
inconsistent between operators, and leaves no machine-readable record.

**User:** the emergency dispatcher / control-room operator (e.g. India's 112 ERSS). ResQPulse **assists**
them and does not replace them: every alert is confirmed by a human.

## 2. Our solution

ResQPulse takes a **typed or spoken** report and, in about a second, produces a **structured alert**:
incident type, severity score, location on a map, people affected, injuries, hazards, responders to send,
and a one-line summary. An **attention heatmap** shows which words drove the decision. Alerts appear on a
**live dispatcher dashboard**, sorted by severity.

**Example**

Input:
> "Accident on Mumbai–Pune expressway near Lonavala exit, truck hit two cars, one guy not moving, lot of blood, traffic blocked"

Output: `TRANSPORT_ACCIDENT` · severity **4.4 (CRITICAL)** · Lonavala exit (mapped) · 1 person unresponsive,
heavy bleeding · hazards: traffic blocked, multiple vehicles · send **ambulance + traffic police**.

## 3. What makes it different

| | Feature | Why it matters |
|---|---|---|
| 1 | **Full structured alert, not just a label** | Prior work (CrisisNLP, HumAID) classifies tweets; we produce a dispatch-ready record |
| 2 | **Attention-based explainability** | Dispatchers see *why* an alert is critical |
| 3 | **Continuous severity score (1–5)** | Fine-grained priority ordering |
| 4 | **Voice input (Whisper)** | Real emergencies are mostly calls |
| 5 | **Live priority queue + map** | A dispatch tool, not just a model |
| 6 | **Small, offline, free models** | Emergency data is sensitive; no per-call cost or internet dependency |
| 7 | *(stretch)* **Duplicate-report merging** | 10 reports of one fire become 1 alert |

## 4. Architecture

Three transformers work together: **Whisper hears the report, DistilBERT understands it, Flan-T5 writes the alert.**

```
 Text ─────────────────────────────┐
                                   ▼
 Voice ─► Whisper (speech→text) ─► editable transcript (dispatcher check)
                                   │
                                   ▼
            ┌─────────────────────────────────────┐
            │ DistilBERT, multi-task               │──► incident type   (classification)
            │                                      │──► severity 1–5    (regression)
            │                                      │──► attention heatmap (rollout)
            └─────────────────┬───────────────────┘
                              ▼
            ┌─────────────────────────────────────┐
            │ Flan-T5-base, fine-tuned             │──► location, people, injuries,
            │ report → structured fields          │    hazards, summary
            └─────────────────┬───────────────────┘
                              ▼
            Post-processing: Pydantic validation · geocoding · type→responders · (stretch) dedupe
                              ▼
            FastAPI  (/transcribe · /analyze · /alerts)
                              ▼
            Streamlit dashboard: input · alert card · heatmap · priority queue · map · metrics
```

**Why two models?** Each does what it is best at (understanding vs. generating), two ML members can train
them in parallel, and each has a fallback if the other struggles.

## 5. Alert schema

The full specification is in **[docs/SCHEMA.md](docs/SCHEMA.md)** (schema v1). The essentials:

**Incident types (8):** `FIRE` · `FLOOD` · `STORM_CYCLONE` · `EARTHQUAKE_COLLAPSE` · `TRANSPORT_ACCIDENT` ·
`MEDICAL` · `VIOLENCE_CRIME` · `NON_EMERGENCY`

**Severity:** 1.0–5.0 using a shared rubric → `LOW` < 2 ≤ `MEDIUM` < 3 ≤ `HIGH` < 4 ≤ `CRITICAL`

**Responders:** `FIRE_BRIGADE` · `AMBULANCE` · `POLICE` · `TRAFFIC_POLICE` · `DISASTER_RESPONSE`

**Alert (shortened):**

```json
{
  "alert_id": "RQP-000123",
  "status": "NEW",
  "is_emergency": true,
  "input": { "text": "...", "source": "voice", "transcript_confidence": 0.82 },
  "incident_type": "TRANSPORT_ACCIDENT",
  "type_confidence": 0.91,
  "severity": 4.4,
  "severity_label": "CRITICAL",
  "location": { "text": "Mumbai-Pune expressway near Lonavala exit", "lat": 18.7546, "lon": 73.4062, "geocoded": true },
  "people_affected": 1,
  "injuries": ["not moving", "lot of blood"],
  "hazards": ["traffic blocked"],
  "summary": "Truck hit two cars near Lonavala exit; one person unresponsive and bleeding heavily; road blocked.",
  "responders": ["AMBULANCE", "TRAFFIC_POLICE"],
  "sdg_targets": ["3.6"],
  "explanation": { "attention": [["moving", 1.0], ["blood", 0.88]] }
}
```

**API:** `GET /health` · `POST /transcribe` · `POST /analyze` · `GET /alerts` · `GET|PATCH /alerts/{id}` ·
`GET /metrics` (details and error codes in SCHEMA.md §7).

## 6. Data

| Kind | Source | Labels |
|---|---|---|
| **A: Real crisis posts** | [HumAID](https://crisisnlp.qcri.org/humaid_dataset) set 1 (~43k tweets, 13 disasters), [CrisisLexT26](https://crisislex.org/data-collections.html) (~28k tweets, 26 crises), [Kaggle *NLP with Disaster Tweets*](https://www.kaggle.com/competitions/nlp-getting-started) | Incident type (mapped from event/crisis name), emergency vs. not |
| **B: Generated call-style reports** | ~3,000 reports from **Claude**, using a type × severity × style × city grid | Everything: type, severity, all fields |
| **Gold test set** | 144 real reports labelled by Claude, then re-reviewed in a second pass, with a 30-row human audit to measure agreement | Real text with type, severity and fields; **never trained on** |
| **Voice** | ~50 teammate recordings + ~300 TTS clips with added noise | For demo, voice evaluation, and speech-style training text |

- All links, file formats and label mappings: **[docs/DATASETS.md](docs/DATASETS.md)**.
- Train on A + B, demo on B-style reports. CrisisLexT26 also serves as a **cross-dataset test**. Split 70/15/15, stratified, deduplicated across splits.
- Gold-set and synthetic-set scores are **always reported separately**.
- Raw data, processed data, audio recordings and model weights are **not committed** (see `.gitignore`).
  Data lives on Kaggle; only small gold/sample files go in git.

## 7. Models

| Component | Model | Notes |
|---|---|---|
| Baseline | TF-IDF + Logistic Regression | Exists to show the transformer is better |
| Classifier | `distilbert-base-uncased` + 2 heads | Type (cross-entropy) + severity (masked MSE); heatmap via attention rollout |
| Generator | `google/flan-t5-base` | Outputs a flat `key: value \| …` line (T5 has no `{}` tokens), parsed to JSON; trained in fp32 |
| Fallback extractor | `dslim/bert-base-NER` + rules | Used if Flan-T5 underperforms |
| Speech | `faster-whisper` `small.en` (int8) | Not trained; VAD on; confidence flags |

Training runs on **Kaggle T4 GPUs** (separate accounts, so models train in parallel). Inference runs on a laptop CPU.

## 8. Evaluation

Results are filled in after training.

| Task | Metric | Baseline | Ours (gold) | Ours (synthetic) |
|---|---|---|---|---|
| Incident type | Macro Precision / Recall / F1 | – | – | – |
| Severity | MSE / RMSE / MAE | – | – | – |
| Field extraction | Per-field P / R / F1, JSON validity % | – | – | – |
| Summary | ROUGE-L | – | – | – |
| Voice | WER; type F1 typed vs. spoken | – | – | – |
| System | Latency per report (CPU) | – | – | – |

We emphasise **recall on critical incidents**, because missing a real emergency is worse than a false alarm.
Confusion matrices and error analysis go in `reports/`.

**All numbers come from one script**, so every model is scored the same way and the models never see the test labels:

```bash
# teammates' prediction CSVs go in predictions/ (formats: docs/SCHEMA.md §8.1)
.venv/bin/python scripts/evaluate.py          # writes reports/metrics.json, results.md, error_analysis.md, confusion matrices
.venv/bin/python tests/test_metrics.py        # metric unit tests (hand-computed values)
.venv/bin/python scripts/make_fake_predictions.py --out /tmp/fake   # fake files to try the pipeline; numbers are meaningless
```

## 9. SDG alignment

| SDG target | How ResQPulse supports it |
|---|---|
| **3.6**: halve road-traffic deaths and injuries | Faster triage of accident reports → faster ambulance dispatch |
| **3.d**: early warning and management of health risks | Severity-ranked medical alerts |
| **11.5**: reduce deaths and people affected by disasters | Structured, prioritised alerts during disaster report surges |
| **13.1**: resilience to climate-related hazards | Processes flood and cyclone reports at scale |
| **16.1**: reduce all forms of violence | Faster police + ambulance dispatch for violence/crime reports |
| **16.6**: effective, accountable, transparent institutions | Explainable decisions + JSON audit log of every alert |

## 10. Repository structure

```
ResQPulse_AI/
├── app/                 # Streamlit dashboard (FE)
├── data/
│   ├── raw/             # downloaded datasets          (git-ignored)
│   ├── processed/       # cleaned splits               (git-ignored)
│   ├── gold/            # gold test set (real text, Claude-labelled + audited) (committed, small)
│   └── audio/           # voice recordings             (git-ignored, personal data)
├── docs/
│   ├── RESEARCH_BRIEF.md  # problem, approach, decisions
│   ├── SCHEMA.md          # all data formats and the API contract
│   ├── DATASETS.md        # dataset and model links
│   └── UPDATE.md          # change log, one entry per PR
├── models/              # trained weights from Kaggle  (git-ignored)
├── notebooks/           # Kaggle training / eval notebooks
├── reports/             # metrics JSON, confusion matrices, model cards
├── scripts/             # one-off scripts (data generation, TTS, downloads)
├── src/
│   ├── data/            # loaders, label mapping, synthetic generation (ML1)
│   ├── models/          # classifier + generator inference (ML2, ML3)
│   ├── explain/         # attention rollout, heatmaps (ML2)
│   ├── asr/             # Whisper wrapper (BE2)
│   └── api/             # FastAPI app (BE1)
├── .env.example
├── requirements.txt
└── README.md
```

## 11. Setup

**Requirements:** Python 3.11 recommended (matches Kaggle), `ffmpeg` (for audio).

```bash
git clone https://github.com/GgauravJ05/ResQPulse_AI.git
cd ResQPulse_AI
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then fill in the values
brew install ffmpeg           # macOS; use apt on Linux
```

### Run the backend

```bash
# Fake models (no weights needed, good for developing the app):
USE_FAKE_MODELS=true .venv/bin/python -m uvicorn src.api.main:app --port 8000

# Real models: put the trained folders in models/ (git-ignored, ~1.2 GB in total), set USE_FAKE_MODELS=false in .env
#   models/classifier/   config.json, model.safetensors, heads.pt, label_map.json, tokenizer files   (ML2, DistilBERT)
#   models/generator/    config.json, model.safetensors, tokenizer files                              (ML3, Flan-T5)
.venv/bin/python -m uvicorn src.api.main:app --port 8000
curl localhost:8000/health       # classifier / generator are true only if the weights actually loaded
```

The first request after startup takes a few seconds (warm-up); later ones take about 1 to 2 seconds on a laptop CPU.
If the Flan-T5 model cannot load, extraction falls back to rules (`extractor: "fallback_rules"`) and the API keeps working.
Tests: `.venv/bin/python -m pytest tests -q`.

## 12. Team and roles

| Role | Owns |
|---|---|
| **ML1: Data** | Synthetic generation, public-data mapping, splits, gold set, evaluation report |
| **ML2: Classifier** | Baseline, DistilBERT multi-task, attention rollout heatmap |
| **ML3: Generator** | Flan-T5 fine-tuning, parsing/validation, fallback extractor |
| **BE1: API** | FastAPI, model loading, inference pipeline, error handling |
| **BE2: Services** | Whisper, geocoding, alert store + priority queue, TTS pipeline, gold-set verification |
| **FE: UI** | Streamlit screens, map, heatmap view, metrics page, slide design |

**Interfaces agreed in hour 0**, so the backend can use fake versions until the models are ready:

```python
classify(text: str) -> ClassifyResult          # ML2: incident_type, probs, severity, attention
extract(text: str) -> ExtractResult            # ML3: location, people_affected, injuries, hazards, summary
transcribe(audio_path: str) -> TranscribeResult  # BE2: transcript, confidence, low_confidence, duration_s
```

The Pydantic definitions are in [SCHEMA.md §5](docs/SCHEMA.md#5-model-interfaces-python).

## 13. 12-hour plan

| Hours | Work | Exit criterion |
|---|---|---|
| 0–1 | Lock incident types, schema, API contract; repo + Kaggle setup; generation prompt | Contract committed |
| 1–3 | Data generation · baseline · training code · FastAPI with fake responses · Whisper + geocoding · UI against the fake API | Fake alert shown end to end |
| 3–6 | Real training runs · real models wired in · map + alert card | **Hour 6: full app works with real models** |
| 6–9 | Heatmap · gold-set evaluation · validation/fallback · metrics page | All metrics on the gold set |
| 9–10 | Fixes and polish; stretch features only if everything works | **Code freeze at hour 10** |
| 10–12 | Slides, backup demo video, README results, two timed rehearsals | Ready to present |

**Rule:** a rough working version first, then improve.

## 14. Git workflow

- **`main` is always demo-able.** Nobody pushes directly to it.
- **Every major change goes on a branch and is merged through a Pull Request.** Small fixes can go in the
  same branch as the feature they belong to.
- **Branch names:** `<type>/<short-description>`, e.g. `feat/classifier-training`, `feat/whisper-asr`,
  `fix/geocode-timeout`, `docs/readme-results`, `chore/repo-setup`.
- **Commit messages:** `<type>: <what changed>`, with types `feat`, `fix`, `docs`, `chore`, `refactor`,
  `test`, `data`. Example: `feat: add masked severity loss to classifier`.
- **Commit often**: small commits that each do one thing, so a broken change is easy to revert.
- **Pull requests** use the template in `.github/`: what it does, how it was tested, checklist.
  Another teammate reviews if time allows; during the hackathon, a quick look is enough.
- **Every PR adds an entry to [docs/UPDATE.md](docs/UPDATE.md)** and updates the status table in
  [RESEARCH_BRIEF.md §16](docs/RESEARCH_BRIEF.md#16-project-status-kept-current). If the change affects what we
  say on stage, update the presentation guide in §17 too. By the end, the brief is the doc we present from.
- **Never commit** secrets (`.env`, `kaggle.json`), raw data, audio recordings or model weights.

```bash
git checkout main && git pull
git checkout -b feat/my-feature
# ...work, commit often...
git push -u origin feat/my-feature
gh pr create --fill          # or open the PR on GitHub
```

## 15. Open decisions

To settle in hour 0:

- [x] Incident types: 8 classes, schema v1 ([SCHEMA.md](docs/SCHEMA.md))
- [x] Synthetic data generator: Claude
- [ ] Claude model for generation (`claude-opus-5-5` default; Sonnet/Haiku 5.5 are cheaper), which is a budget call
- [ ] Whether preparation before the event is allowed (dataset downloads, cached models, generated data)
- [ ] Teammates' consent to record voice clips
- [ ] Role assignments and which stretch features to attempt

## 16. Limitations and future work

- Everyday emergencies (accidents, medical, crime) rely on generated data, because no public dataset of
  Indian emergency calls exists. Future work: train on real anonymised 112 transcripts.
- English only for now. Next: Hindi, Marathi and Hinglish (MuRIL / XLM-R, multilingual Whisper).
- Attention shows what the model focused on; it is an indicator, not proof of reasoning.
- Learning from dispatcher corrections (active learning) and integration with 112 ERSS.

## License

[MIT](LICENSE)
