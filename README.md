# ResQPulse AI

**Turning messy emergency reports, typed or spoken, into structured, prioritised, explainable alerts for a 112 dispatcher.**

GenHack v1.0 (Mini Hackathon) · Gen AI course · **Problem statement 15: EmergencyScribe** · Technique: **Transformer + Attention**
· Team **P 25** · [MIT licence](LICENSE)

<p align="center"><img src="docs/architecture_diagram.png" alt="ResQPulse AI system architecture" width="900" /></p>

A caller says: *"bhai there's a huge fire near the petrol pump on FC road, 2-3 people stuck inside the shop, smoke everywhere."*
ResQPulse returns an alert: **FIRE · severity 4.5 (CRITICAL) · FC road · 3 people · smoke · send the fire brigade**, with the words that drove the
decision highlighted, a pin on the map, and a place in the priority queue. A human dispatcher confirms every alert.

> **Status:** complete and running end to end with the real models. 52 automated tests; the full pipeline was run in a browser with typed
> and voice reports. Measured results and their limits are in [Results](#results) and [Limitations](#limitations).

**Docs:** [Research brief](docs/RESEARCH_BRIEF.md) (the reasoning, and the doc to present from) ·
[Schema](docs/SCHEMA.md) (every data format and the API contract) · [Datasets](docs/DATASETS.md) ·
[Update log](docs/UPDATE.md) · [GenHack deck](docs/ResQPulse_AI_GenHack.pptx)

---

## Contents

1. [The problem](#the-problem)
2. [What it does](#what-it-does)
3. [Architecture](#architecture)
4. [Models](#models)
5. [Data](#data)
6. [Results](#results)
7. [Claims and the evidence behind them](#claims-and-the-evidence-behind-them)
8. [Limitations](#limitations)
9. [Quick start](#quick-start)
10. [Using the dashboard](#using-the-dashboard)
11. [API](#api)
12. [Alert format](#alert-format)
13. [Reproducing the results](#reproducing-the-results)
14. [Repository structure](#repository-structure)
15. [SDG alignment](#sdg-alignment)
16. [Team and workflow](#team-and-workflow)
17. [Future work](#future-work)

---

## The problem

During a disaster, control rooms are flooded with unstructured reports from calls, SMS, WhatsApp and social media. Many are duplicates,
and urgent ones get buried. Triage is done by hand, so it is slow, varies between operators and leaves no machine-readable record.

ResQPulse **assists** the dispatcher; it does not replace them. Every alert is reviewed and confirmed by a person.

## What it does

| | |
|---|---|
| **Input** | A typed report, a microphone recording, or an uploaded audio file |
| **Understands** | Incident type (8 classes) and a continuous severity score from 1 to 5 |
| **Extracts** | Location, people affected, injuries, hazards and a one-line summary |
| **Explains** | An attention heatmap showing which words drove the decision |
| **Acts** | Geocodes the place, suggests responders, tags UN SDG targets, flags likely duplicate reports |
| **Dashboard** | Report input, alert card, heatmap, severity-sorted queue with an incident map, and model metrics |
| **Human in the loop** | The dispatcher confirms, dispatches or dismisses; every correction is logged |

## Architecture

The diagram at the top shows the system. In words:

1. The **Streamlit dashboard** takes a typed or spoken report and calls the **FastAPI backend** (`POST /analyze`, `POST /transcribe`).
2. Voice goes to **Whisper small.en** first; the transcript can be edited before analysis.
3. The backend sends the text to **DistilBERT** (incident type, severity, attention scores) and **Flan-T5-base** (location, people, injuries, hazards, summary).
4. The backend geocodes the place, adds responders and SDG tags by rule, checks for duplicates, and saves the alert (in memory plus JSONL logs).
5. The dashboard shows the alert, the heatmap, the priority queue and the map.

Everything runs offline on one laptop once the models are downloaded. If a model fails, the backend falls back: a rule-based extractor replaces
Flan-T5, and an offline mock mode keeps the dashboard working with no backend at all.

## Models

| Component | Model | Notes |
|---|---|---|
| Baseline | TF-IDF + logistic regression | Exists to show the transformer is better |
| Classifier | `distilbert-base-uncased` with two heads | Type (cross-entropy) and severity (masked MSE); heatmap from attention rollout |
| Generator | `google/flan-t5-base` (fp32) | Writes a flat `key: value \| ...` line (T5 has no `{}` tokens), parsed to JSON; retry with a wider beam, then rule fallback, then a people-count rule |
| Speech | `faster-whisper` `small.en` (int8, VAD on) | Not trained by us; low-confidence transcripts are flagged for review |
| Duplicates | `all-MiniLM-L6-v2` (sentence-transformers) | Cosine similarity above 0.75 marks `duplicate_of` |

Training ran on Kaggle T4 GPUs ([classifier notebook](notebooks/classifier-notebook.ipynb), [generator notebook](notebooks/flan-t5-train.ipynb)).
Inference runs on a laptop CPU.

## Data

| Kind | Source | Used for |
|---|---|---|
| Real crisis tweets | [HumAID](https://crisisnlp.qcri.org/humaid_dataset), [CrisisLexT26](https://crisislex.org/data-collections.html), [Kaggle Disaster Tweets](https://www.kaggle.com/competitions/nlp-getting-started) (negatives) | Teaching the models disasters; about 37,000 tweets after cleaning and de-duplication |
| Call-style reports | 710 reports written by Claude, 8 writing styles, every field labelled and validated | Everyday emergencies and the demo style; each phrase checked to appear word for word in the text |
| Gold test set | 144 real reports labelled by Claude, re-reviewed in a second pass, then audited by a person on 30 random rows (30 of 30 agreed) | Never trained on; the main test of real-world performance |

- Training set: 9,551 rows (7,563 real, plus 497 unique call-style reports each repeated 4 times).
- Held out and never trained on: 107 call-style reports, 7,755 real tweets (including 6 crises the models never saw) and the gold set.
- **A finding:** naming a tweet's label by its disaster was wrong for about 16% of tweets (donation appeals, jokes, commentary mention a disaster but report nothing). That is why we built the gold set.
- Raw data, processed data and model weights are not committed. Links, formats and label mappings: [docs/DATASETS.md](docs/DATASETS.md). Dataset on Kaggle: [ggauravj05/resqpulse-data](https://www.kaggle.com/datasets/ggauravj05/resqpulse-data).

## Results

One script ([scripts/evaluate.py](scripts/evaluate.py)) scores every model from prediction files; the models never see the test labels. Full tables: [reports/results.md](reports/results.md).

**Incident type: baseline (TF-IDF + logistic regression) → our DistilBERT**

| Test set | Macro precision | Macro recall | Macro F1 |
|---|---|---|---|
| **Gold: 144 real reports** | 0.61 → **0.76** | 0.59 → **0.79** | 0.56 → **0.77** |
| Call-style: 107 reports | 0.89 → **0.96** | 0.86 → **0.96** | 0.87 → **0.96** |
| Real tweets: 7,755 | 0.73 → **0.79** | 0.62 → **0.75** | 0.63 → **0.75** |

On the 6 crises the models never saw, accuracy is **64% vs 48%** for the baseline: the strongest evidence for using a transformer.

**Safety numbers (gold set).** A missed emergency costs more than a false alarm.

| | Baseline | Ours |
|---|---|---|
| Real emergencies caught (emergency recall) | 0.71 | **0.91** |
| Severity 4 or 5 reports not dismissed as non-emergency | 0.75 | **0.98** |
| False alarms on non-emergencies | 0.36 | 0.38 |

**Severity (1 to 5):** RMSE **0.75** / MSE 0.57 on call-style reports (87% within one point); RMSE 1.33 / MSE 1.77 on real tweets.

**Field extraction (Flan-T5):** output parses 100% of the time; on call-style reports location F1 0.78, injuries F1 0.54 (0.64 lenient),
hazards F1 0.38 (0.59 lenient), summary ROUGE-L 0.50. Scores come from the real pipeline that runs in the demo (generation, retry, fallback, people-count rule).

**Voice:** word error rate **9.9% clean, 15.5% noisy** on 20 held-out reports spoken by 4 text-to-speech voices ([scripts/eval_whisper.py](scripts/eval_whisper.py)).
The incident type from speech matched the typed-text result in 18 of 20 clips (clean) and 16 of 20 (noisy). Most errors are place names and digits.

<p align="center"><img src="reports/confusion_matrix_gold_ml2.png" alt="Confusion matrix on the gold set" width="520" /></p>

## Claims and the evidence behind them

| Claim | Evidence |
|---|---|
| Beats the baseline on real, checked reports | Gold macro F1 0.77 vs 0.56; [reports/results.md](reports/results.md) |
| Catches 91% of real emergencies and keeps 98% of severe reports | Gold set, `emergency_recall` and `critical_recall` in [reports/metrics.json](reports/metrics.json) |
| Generalises to events it has not seen | 64% vs 48% accuracy on 6 held-out crises |
| Explains its decisions | Attention rollout heatmap on every alert; the dashboard states it is an indicator, not proof |
| Voice works end to end | Tested through the real models; word error rate 9.9% clean, 15.5% noisy ([reports/whisper_wer.json](reports/whisper_wer.json)) |
| Flags duplicate reports | Reworded reports of one fire scored 0.78 to 0.93 similarity, unrelated incidents under 0.25 |
| Runs offline on a laptop | Both models and Whisper run locally; about 2 to 4 s per report once warm |
| Raising the emergency threshold does not fix false alarms | Sweep on all three test sets: false alarms 0.38 to 0.31 costs emergency recall 0.93 to 0.87 and critical recall 0.98 to 0.95, so the default stays |
| Averaging with the baseline does not help | Gold macro F1 stays at 0.765 or drops, so it was not added |
| Works as a system, not only as models | 52 automated tests (metrics, API, generator, services, dashboard) |

## Limitations

Stated plainly, because the scores depend on them:

- **False alarms:** 37.8% of non-emergency tweets on the gold set are flagged (commentary that uses disaster vocabulary). The model reads the topic, not the intent. The human dispatcher is the safeguard.
- **Severity on real tweets is weaker** (RMSE 1.33 vs 0.75). The severity head was trained on call-style reports only, so scores shrink toward the middle on news-style text.
- **No real 112 calls:** everyday emergencies rely on generated data. `MEDICAL` has no real tweets at all.
- **Gold labels are Claude's,** checked by a person on 30 rows (30 of 30 agreed, meaning at least about 90% agreement at 95% confidence), not hand-labelled throughout.
- **Voice was tested on synthetic speech, 20 clips,** not real callers. Place names and numbers are the usual errors, which is why the transcript is editable.
- **English only.** Attention is an indicator of focus, not proof of reasoning.
- The first request after start-up takes about 6 seconds while models warm up.

## Quick start

You need Python 3.10 or newer, and ffmpeg for voice (`brew install ffmpeg`, `winget install ffmpeg` or `sudo apt install ffmpeg`).

```bash
git clone https://github.com/GgauravJ05/ResQPulse_AI.git
cd ResQPulse_AI
python3 -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

**Models.** The trained weights are not in git (about 1.2 GB). Copy them into the repo as `models/classifier/` (6 files) and
`models/generator/` (6 files, including the 944 MB `model.safetensors`). Whisper (about 480 MB) and the duplicate-check model (about 90 MB)
download themselves the first time they are used, so run once with internet.

**Run (two terminals, both in the repo folder with the venv active):**

```bash
# Terminal 1: backend. Wait for "Application startup complete".
USE_FAKE_MODELS=false python -m uvicorn src.api.main:app --port 8000

# Terminal 2: dashboard
python -m streamlit run app/streamlit_app.py       # opens http://localhost:8501
```

On Windows PowerShell set the variable first: `$env:USE_FAKE_MODELS="false"`. To let others on your Wi-Fi open the dashboard,
add `--server.address 0.0.0.0` and share `http://<your-ip>:8501` (the microphone only works on localhost).

**Check it:**

```bash
curl http://localhost:8000/health
# {"status":"ok","models":{"classifier":true,"generator":true,"asr":true}}
```

The sidebar of the dashboard should say **Live mode: real models**. Send one report first to warm the models up.

**No models yet?** Start the backend with `USE_FAKE_MODELS=true` for fake alerts, or start only the dashboard and it falls back to offline
mock mode. Every screen still works, so teammates can develop the UI without any weights.

**Start order matters:** the dashboard picks Live mode only if the backend is already running when it starts.

## Using the dashboard

| Screen | What to do |
|---|---|
| **Report Input** | Click a demo sample, type a report, record with the microphone, or upload audio. For voice, click *Transcribe Audio Now*, fix any misheard word, then *Analyze Report*. |
| **Alert Card** | Type, severity bar, summary, location with coordinates, people affected, confidence, responders, SDG targets, injuries, hazards, JSON download. Possible duplicates are flagged. |
| **Attention Heatmap** | Words coloured by how much the model focused on them, plus the class probabilities. |
| **Dispatcher Dashboard** | Severity-sorted queue, filters, confirm / dispatch / dismiss buttons, and the incident map. |
| **Model Metrics** | Baseline vs DistilBERT tables, severity regression, extraction scores and confusion matrices. |

Suggested live demo: type a report → alert card → heatmap → play `demo_assets/noisy_phone_report.wav` (phone-quality audio; Whisper hears
"Lonavala" as "La Navalan", a good moment to correct the transcript) → queue and map → a non-emergency such as "is the mall open today?" → calm
"No emergency detected" card.

## API

| Endpoint | Purpose |
|---|---|
| `GET /health` | Which models are loaded |
| `POST /transcribe` | Audio file → transcript, confidence, duration |
| `POST /analyze` | Report text → full alert |
| `GET /alerts` | Severity-sorted queue (filter by status) |
| `GET /alerts/{id}`, `PATCH /alerts/{id}` | Read an alert; confirm, dispatch or dismiss it (logged as a correction) |
| `GET /metrics` | Stored evaluation numbers for the dashboard |

Details and error codes: [docs/SCHEMA.md §7](docs/SCHEMA.md).

## Alert format

Full specification in [docs/SCHEMA.md](docs/SCHEMA.md) (schema v1). Incident types: `FIRE`, `FLOOD`, `STORM_CYCLONE`, `EARTHQUAKE_COLLAPSE`,
`TRANSPORT_ACCIDENT`, `MEDICAL`, `VIOLENCE_CRIME`, `NON_EMERGENCY`. Severity 1.0 to 5.0 → `LOW` < 2 ≤ `MEDIUM` < 3 ≤ `HIGH` < 4 ≤ `CRITICAL`.

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
  "duplicate_of": null,
  "explanation": { "attention": [["moving", 1.0], ["blood", 0.88]] }
}
```

## Reproducing the results

```bash
.venv/bin/python -m pytest tests -q                      # 52 tests
.venv/bin/python scripts/evaluate.py                     # scores every prediction file in predictions/ → reports/
.venv/bin/python scripts/eval_whisper.py --n 20          # voice word error rate (backend running, macOS `say` voices)
.venv/bin/python scripts/predict_generator.py --out predictions   # re-run the real extractor over the test inputs
.venv/bin/python scripts/build_deck.py                   # rebuild the GenHack deck from the template
```

The data pipeline scripts are in [scripts/](scripts/) (`build_public.py`, `validate_synthetic.py`, `make_splits.py`, `build_gold.py`).
Prediction CSV formats are in [docs/SCHEMA.md §8.1](docs/SCHEMA.md).

## Repository structure

```
ResQPulse_AI/
├── app/                  Streamlit dashboard (5 screens, mock and live modes)
├── src/
│   ├── api/              FastAPI app and schemas
│   ├── models/           classifier (DistilBERT two-head), generator (Flan-T5), fake models for development
│   ├── services/         geocoding, duplicate detection
│   ├── asr/              Whisper wrapper
│   ├── data/             label mapping, cleaning, Flan input/target format
│   └── eval/             metric functions
├── scripts/              data pipeline, evaluation, voice evaluation, deck builder
├── notebooks/            Kaggle training notebooks (classifier, generator)
├── data/gold/            the 144-report gold set (committed; raw and processed data are git-ignored)
├── reports/              metrics, results tables, confusion matrices, Whisper evaluation
├── tests/                52 automated tests
├── docs/                 research brief, schema, datasets, update log, architecture diagram, GenHack deck
├── demo_assets/          noisy phone-quality voice clip for the demo
├── models/               trained weights (git-ignored, about 1.2 GB)
├── .env.example · requirements.txt
└── README.md
```

## SDG alignment

| SDG target | How ResQPulse supports it |
|---|---|
| **3.6** halve road-traffic deaths and injuries | Faster triage of accident reports leads to faster ambulance dispatch |
| **3.d** early warning and management of health risks | Severity-ranked medical alerts |
| **11.5** reduce deaths and people affected by disasters | Structured, prioritised alerts during surges of disaster reports |
| **13.1** resilience to climate-related hazards | Processes flood and cyclone reports at scale |
| **16.1** reduce all forms of violence | Faster police and ambulance dispatch for violence and crime reports |
| **16.6** effective, accountable, transparent institutions | Explainable decisions and a JSON log of every alert and correction |

Each alert carries its SDG tags in the app, not only in this table.

## Team and workflow

| Role | Owns |
|---|---|
| **ML1: Data** (Gaurav Jadhav) | Synthetic data, public-data mapping, splits, gold set, evaluation, integration |
| **ML2: Classifier** | Baseline, DistilBERT two-head model, attention heatmap |
| **ML3: Generator** | Flan-T5 fine-tuning, parsing, fallback extractor |
| **BE1: API** | FastAPI, model loading, inference pipeline |
| **BE2: Services** | Whisper, geocoding, alert store and queue, duplicate detection |
| **FE: UI** | Streamlit screens, map, heatmap view, metrics page |

Every change goes on a branch and into `main` through a pull request, and is logged in [docs/UPDATE.md](docs/UPDATE.md).
The research brief ([docs/RESEARCH_BRIEF.md](docs/RESEARCH_BRIEF.md)) is kept current as the document to present from.

## Future work

- Train on real anonymised 112 transcripts, which would also fix the missing real `MEDICAL` data.
- Hindi, Marathi and Hinglish (MuRIL or XLM-R, multilingual Whisper).
- Retrain the severity head on news-style text and add more hard negatives to cut false alarms.
- Learn from the dispatcher corrections that are already logged; integrate with 112 ERSS.
- Human-labelled gold labels, a persistent database and authentication.

## License

[MIT](LICENSE) © 2026 Gaurav Jadhav
