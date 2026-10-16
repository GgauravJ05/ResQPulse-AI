# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary: a 112 emergency dispatcher triaging incoming reports during normal operations and disaster surges. For the hackathon, the audience is also the judging panel watching a live demo on a projector or laptop in a lit hall, and teammates running it locally.

## Product Purpose

ResQPulse AI turns a messy emergency report, typed or spoken, into a structured, prioritised, explainable alert: incident type, continuous severity 1 to 5, location, people affected, injuries, hazards, summary, responders and SDG tags. Success is a dispatcher seeing the most severe incidents first, with the evidence for each decision, and confirming every alert themselves.

## Positioning

A full alert, not just a label, from small models that run offline on a laptop, with an attention heatmap showing which words drove each decision and a severity score measured on a continuous scale. Scored honestly against a baseline on 144 real held-out reports.

## Operating Context

Streamlit dashboard (five screens: Report Input, Alert Card, Attention Heatmap, Dispatcher Dashboard, Model Metrics) over a FastAPI backend with DistilBERT, Flan-T5-base and Whisper. Runs in live mode against the backend or in offline mock mode. Demoed live at GenHack v1.0 (Gen AI course, problem statement 15, EmergencyScribe).

## Capabilities and Constraints

- Real data and real model outputs only; every number shown comes from `reports/` or the live backend.
- Behaviour, labels used by tests and the API contract stay fixed; the UI is restyled, not re-scoped.
- English only. The human dispatcher is the safeguard against false alarms (37.8% on the gold set).

## Brand Commitments

- Visual references the team chose: kaggle.com, motion.dev and impeccable.style (light ground, black pill buttons, one signal-yellow accent, small mono metadata labels, Kaggle-style left rail).
- No emoji anywhere in the interface.
- Light theme (projector in a lit hall).

## Evidence on Hand

- `reports/results.md`, `reports/metrics.json`, confusion matrices, `reports/whisper_wer.json`.
- `app/demo_samples.json` (9 demo reports), `app/mock_alert.json`, `demo_assets/noisy_phone_report.wav`.
- `docs/architecture_diagram.png`.

## Product Principles

1. The most severe incident is the first thing the dispatcher reads.
2. Show the evidence beside every decision: confidence, attention, coordinates.
3. Honest numbers over impressive ones.
4. A human confirms every alert.
