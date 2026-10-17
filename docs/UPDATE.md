# Project Update Log

Every change to the project gets an entry here, newest first. **Add your entry in the same PR as the
change**, then update the status table in [RESEARCH_BRIEF.md §16](RESEARCH_BRIEF.md#16-project-status-kept-current)
(and §17 if it changes what we say in the presentation).

**Entry format:**

```
## YYYY-MM-DD · <short title> (PR #n)
**Who:** <role/name> · **Area:** Data | Classifier | Generator | API | ASR | UI | Docs | Repo
- What changed
- Why (especially if it changes the plan)
- Results / numbers, if any
- Follow-ups, if any
```

---

## 2026-10-17 · "Open alert" crashed the dashboard (PR #34)
**Who:** Data lead · **Area:** UI
- Clicking "Open alert" in the queue raised `StreamlitWidgetAlreadyInstantiatedError`: it changed the sidebar page after the sidebar was drawn. It now uses an `on_click` callback, which runs before the page is drawn. Added a test; checked in the browser against the live backend (opens the Alert Card, no error).

## 2026-10-17 · Sidebar could not be reopened (PR #33)
**Who:** Data lead · **Area:** UI
- The redesign hid Streamlit's toolbar, which also holds the button that reopens a collapsed sidebar, so a collapsed sidebar was gone for good. Now only the main menu and Deploy button are hidden; the reopen button shows as a small outlined square at the top left. The sidebar starts open at every width. Checked at 1440 and 900 px: collapse, reopen, both work.

## 2026-10-17 · Evaluation study notes (PR #32)
**Who:** Data lead · **Area:** Docs
- Added `docs/EVALUATION_PREP.md`: the 30-second pitch, rubric mapping, architecture, each model and why, data, the demo run order, a numbers cheat sheet with metric definitions, likely judge questions with answers, limitations, SDGs and restart commands.

## 2026-10-17 · Dashboard works fully offline (PR #31)
**Who:** Data lead · **Area:** UI
- Figtree and JetBrains Mono are now served from `app/static/fonts/` (Streamlit static serving, `enableStaticServing = true`) instead of Google Fonts, with their OFL licences beside them. The browser-tab icon is a local PNG of the brand mark instead of a Google-hosted icon. Checked with Google blocked: both fonts load.
- Removed two unused style tokens left from the redesign. Deleted the merged `fix/audio-upload-formats` branch.

## 2026-10-17 · Dashboard redesign: Kaggle / Motion / Impeccable references, no emoji (PR #29)
**Who:** Data lead (with the Impeccable design skill) · **Area:** UI
- New light console look taken from kaggle.com, motion.dev and impeccable.style: grey ground, white panels with hairlines, black pill buttons, one signal yellow (live dot, active nav, attention heatmap), Figtree for text, JetBrains Mono only for IDs, coordinates and scores.
- Every emoji removed (nav, headings, chips, buttons, map, favicon). Kaggle-style left rail; slim top bar with a live/mock status pill; alert card with a summary column and an evidence column; a five-cell severity ruler on the alert card and every queue row; yellow attention heatmap with a probability list; grouped queue actions with Dispatch as the primary button; quiet grey map tiles with severity dots.
- Report text and Analyze now sit above the voice section (first viewport); a voice transcript is applied before the text box is drawn.
- Reviewed by a separate finish reviewer (two rounds; the remaining items were fixed and checked). Added PRODUCT.md, DESIGN.md and `.impeccable/` design records. Behaviour unchanged; 51 tests pass (1 skipped while a backend runs).

## 2026-10-17 · Final README (PR #28)
**Who:** Data lead · **Area:** Docs
- Rewrote README.md for the finished project: architecture diagram, what it does, models, data, measured results, a claims-and-evidence table, honest limitations, quick start for other machines, dashboard guide, API, reproduction commands, repo structure, SDG table, team and workflow. Removed the outdated "development not started" status, the 12-hour plan and open decisions.

## 2026-10-17 · System architecture diagram (PR #27)
**Who:** Data lead · **Area:** Docs
- Added `docs/architecture_diagram.png`, made with the Archify skill (checks passed; the HTML version is local in `.archify/`, git-ignored). Shows caller, Streamlit dashboard, FastAPI backend, Whisper, DistilBERT, Flan-T5, geocoder and alert store inside the offline-laptop boundary. Can replace the drawn diagram on deck slide 3.

## 2026-10-17 · GenHack submission deck (PR #26)
**Who:** Data lead · **Area:** Docs
- Filled the official template (`docs/Final minihackathon genhack template.pptx`) into `docs/ResQPulse_AI_GenHack.pptx`: title slide + 6 content slides (the instructions slide is removed). Template header, section titles, logos and footer are unchanged; only the body was rebuilt in the template's fonts and colours.
- `scripts/build_deck.py` regenerates it. All numbers come from `reports/results.md` and `reports/whisper_wer.json`.
- To submit: open in PowerPoint or Google Slides (Inter and Poppins are Google Fonts), check the layout, add the other team members' names on slide 1, export as PDF.

## 2026-10-17 · Whisper word error rate and ensemble test (PR #25)
**Who:** Data lead · **Area:** ASR, Docs
- Added `scripts/eval_whisper.py` and `reports/whisper_wer.json`: 20 held-out reports spoken by 4 TTS voices, clean and phone-noisy. WER 9.9% clean, 15.5% noisy; type matches the typed result 18/20 and 16/20. Synthetic speech, disclosed in the brief.
- Tested averaging DistilBERT with the TF-IDF baseline on all three test sets: no gain (gold macro F1 stays 0.765 or drops), so it was not added.

## 2026-10-17 · Frontend visual redesign (PR #24)
**Who:** Data lead (with the Impeccable design skill) · **Area:** UI
- New look: warm paper background, navy masthead with a drawn pulse mark, Newsreader serif for titles and numbers, Hanken Grotesk for text, red kept for critical only. Added `.streamlit/config.toml` (theme).
- Removed emoji from navigation, headings, labels and buttons; removed "Screen N" prefixes; flat severity colours (no gradients, no coloured side borders); calmer queue and metric labels.
- Behaviour unchanged. Navigation label strings changed, so `tests/test_frontend_app.py` was updated. 51 tests pass.

## 2026-10-17 · Duplicate detection on, demo voice clip, threshold study (PR #23)
**Who:** Data lead · **Area:** API, UI, Docs
- Installed `sentence-transformers` (now in requirements.txt). Duplicate threshold lowered from 0.85 to 0.75 because a reworded report of the same fire scored 0.78 (unrelated incidents score under 0.25). The alert card and queue now show "Possible duplicate of RQP-…".
- Added `demo_assets/noisy_phone_report.wav` (phone-band filter plus noise). Whisper transcribes it correctly except the place name.
- Tried moving the emergency threshold to reduce false alarms on gold: it only trades recall for false alarms, so no change (numbers in the brief, slide 6).

## 2026-10-17 · Alert card showed its own HTML source (PR #22)
**Who:** Data lead · **Area:** UI
- The alert card on screen 2 displayed raw HTML as a code block: blank lines and indentation inside the HTML ended the HTML block in Markdown. Added `_flat()` in `app/components.py` and used it for every multi-line HTML snippet (header, empty state, non-emergency card, alert card, heatmap legend).
- Added a regression test. Checked the page in a real browser; 52 tests pass.

## 2026-10-17 · Frontend reviewed, fixed and merged (Gaurav; code by Agastya Singh)
**Who:** Agastya Singh (frontend), review and fixes by Gaurav · **Area:** UI
- Reviewed `feat/streamlit-app-v2` (5 screens, API client, mock mode, 11 tests) and drove the real app against the real backend
  with Streamlit's test harness: it detected the live backend, produced a real-model alert, and all five screens rendered with no
  exceptions. Edge cases checked: hostile HTML input (no raw HTML on any screen), a non-emergency report (calm card), empty and
  2,500-character input (clear message), the backend dying mid-demo (error banner, no crash), starting with no backend (falls back
  to mock, all screens work), voice through the app's own API client (9 s spoken report to alert).
- Fixes added: (1) the root `app.py` from BE1 shadowed the `app/` folder, so `import app.api_client` failed and their tests could
  not even be collected: removed it, the full dashboard replaces it. (2) The app always started in Mock Mode; it now starts in
  Live mode when `/health` answers and falls back to Mock otherwise. (3) The attention heatmap coloured raw rollout scores
  (about 0.5 to 1.0), so nearly every word was dark; scores are now stretched across the report, and only the key words stay
  dark. 4 new tests cover these (51 tests pass in total).
- Run it: `.venv/bin/python -m streamlit run app/streamlit_app.py` (backend: `uvicorn src.api.main:app --port 8000`).
- Known: the app uses `use_container_width`, which newer Streamlit versions deprecate (a warning, not an error); the voice
  microphone widget itself cannot be driven by the test harness, so it needs a manual try before the demo.

## 2026-10-17 · Complete ResQPulse AI Streamlit Frontend (PR #18)
**Who:** Frontend Lead · **Area:** UI, API, Tests
- Implemented the complete 5-screen ResQPulse AI Streamlit frontend (`app/streamlit_app.py`) matching `docs/SCHEMA.md`:
  1. **Report Input:** Multiline input with validation (2,000 char limit), 9 quick demo sample buttons from `demo_samples.json`, live microphone recording (`st.audio_input`), audio file upload, editable Whisper ASR transcript box, and low-confidence dispatcher verification alert (`Please verify the transcript`).
  2. **Alert Card:** Full structured alert representation with incident-type badge and icon, continuous severity bar (1.0–5.0), location text with coordinates badge, people affected counter, injury and hazard tag chips, responder badges (`AMBULANCE`, `FIRE_BRIGADE`, etc.), SDG target badges (SDG 3.6, 3.d, 11.5, 13.1, 16.1), latency indicator, and JSON download button (`st.download_button`). Calm, neutral card for `NON_EMERGENCY` reports (`No emergency detected`).
  3. **Explain (Attention Heatmap):** Word-level token highlight visualization using attention rollout weights (`alert.explanation.attention`), safe HTML escaping, token-level hover tooltips, and the required mandatory disclaimer note: *"Highlighted words are what the model focused on. This is an indicator, not proof."*
  4. **Dispatcher Dashboard:** Executive KPI status ribbon, live emergency triage queue sorted strictly by severity descending, status filter tabs, interactive Folium incident map skipping ungeocoded/invalid coordinates with severity-colored markers, and status transition action controls (`CONFIRMED`, `DISPATCHED`, `DISMISSED`) calling `PATCH /alerts/{id}`.
  5. **Metrics Page:** Full quantitative benchmark tables comparing TF-IDF + Logistic Regression baseline against fine-tuned DistilBERT (accuracy, macro precision, recall, F1, emergency recall on Gold, Test Synth, and Test Public sets), critical safety metrics, severity continuous regression metrics (RMSE, MSE, MAE), Flan-T5 field extraction evaluation table, and confusion matrix PNG viewer with graceful fallback.
- Centralized all backend communication in `app/api_client.py` covering `POST /analyze`, `POST /transcribe`, `GET /alerts`, `PATCH /alerts/{id}`, `GET /metrics`, and `GET /health` with timeout resilience, error code parsing, and connection failure handling (`backend not reachable`).
- Added `app/mock_alert.json` copied exactly from Section 6 of `docs/SCHEMA.md`, and created shared styling system in `app/styles.py` and reusable UI widgets in `app/components.py`.
- Added automated test suite `tests/test_frontend.py` (11 unit tests covering schema compliance, sample completeness, validation, mock/live error flows, and styling tokens) — all passing.
- How to start: `streamlit run app/streamlit_app.py` or `python -m streamlit run app/streamlit_app.py`. Default operates in Mock Mode offline; can toggle to Live Backend API via sidebar with configurable `API_URL` (default: `http://localhost:8000`).

## 2026-10-17 · ML2's laptop CPU check script (Gaurav, code by ML2)
**Who:** VanshBorkar (ML2), added by Gaurav · **Area:** Classifier
- Added `scripts/check_classifier_cpu.py` from `feat/classifier`: runs `classify()` on a laptop CPU and compares with the
  Kaggle predictions CSV. Run against `main`: 12 of 12 rows match, probabilities within 0.0003, 9 to 14 ms per call.
- Only this file was taken from `feat/classifier`. That branch still carries an older `src/models/classifier.py` without the
  `CLASSIFIER_DIR` fallback, so merging the whole branch would undo a fix already in `main`. ML2: rebase on `main` before any new PR.

## 2026-10-17 · Real models wired into the API, BE2 services integrated (Gaurav, with ML2, ML3, BE2)
**Who:** Gaurav (integration and fixes); code by ML2 (classifier), ML3 (model), BE2 (Whisper, geocoding, dedupe) · **Area:** API, ML
- **Real models in the backend.** ML2's `classify()` (merged from `feat/classifier`; attention rollout) and a new
  `src/models/generator.py` (`extract()`: Flan-T5 loaded once, retry with a wider beam, rule-based fallback that works offline,
  ML3's people-count rule). `USE_FAKE_MODELS=false` runs them; `/health` now reports a model as loaded only if its weights
  loaded. Weights live in `models/classifier/` and `models/generator/` (git-ignored). Verified: the classifier reproduces ML2's
  CSV on 50 of 50 sampled rows (CPU 10 to 25 ms); the generator reproduces ML3's CSV exactly and takes 1 to 2.5 s per report.
  The 9 demo reports are classified correctly end to end (first request after startup takes about 6 s, warm it up before the demo).
- **BE2's `BE2_Tasks` branch was not mergeable as submitted**: `main.py` imported `geocode_location` but the module defined
  `get_coordinates` (ImportError on startup), `whisper.py` imported a `TranscribeResult` that did not exist and exposed no
  `transcribe()`, and the dedupe module loaded a model at import and needed an uninstalled package. Fixed while integrating:
  name alias, `TranscribeResult` added to `schemas.py`, `transcribe` alias, dedupe made lazy and optional (the API degrades to
  `duplicate_of: null` if `sentence-transformers` is missing), the extension/empty-speech checks BE2 removed from `/transcribe`
  restored, `rapidfuzz` added.
- **Two bugs found only by running it.** (1) `pydub` fails on Python 3.13 and newer (`audioop` was removed from the standard
  library): `audioop-lts` added to requirements. (2) The geocoder's fuzzy match put "Barrackpore Kalyani expressway" (West Bengal)
  at Lonavala; it now matches only whole known place names (longest wins) and uses fuzzy matching only for typos. Offline city
  table grown to about 55 names; 7 of 9 demo alerts now get a correct pin.
- **Whisper verified**: a spoken demo report (9 s) transcribed in about 4 s on CPU, 79% confidence, one misheard word
  ("Lenavala"), which shows why the transcript box is editable. Whisper accuracy was not evaluated on a test set.
- **Evaluation now uses the real pipeline.** `scripts/predict_generator.py` regenerates the ML3 prediction files through
  `extract()`. Gold people-count exact match 0.285 to 0.500; 143 of 144 gold outputs come from the model and 1 from the fallback
  (replacing ML3's hand repair); synthetic scores unchanged. ML3's original CSVs were kept as a backup. Slide 6 updated.
- 34 tests pass (`pytest tests`).

## 2026-10-16 · Incident classifier: baseline, DistilBERT two-head, classify() (PR #7)
**Who:** Vansh · **Area:** Classifier
- `scripts/baseline_tfidf_lr.py`: TF-IDF (word 1–2-grams + char 2–5-grams) + Logistic Regression. C picked on
  `val.csv` macro-F1 only (C = 8). `--predict_only` writes predictions for unlabelled files
  (`gold_inputs.csv` → `baseline_gold.csv`).
- `src/models/two_head.py` + `scripts/train_classifier.py`: `distilbert-base-uncased` with a type head
  (8-way, cross-entropy) and a severity head (sigmoid, MSE on severity scaled to 0–1, back to 1–5 for output).
  Severity loss is masked for rows without severity and divided by max(count, 1), so real tweets only train
  the type head. Settings as agreed: lr 2e-5, batch 32, max_len 128, 3 epochs, fp16, seed 42, Kaggle T4.
  The **last** epoch is kept (not chosen on val, because val shares events with train).
  `NON_EMERGENCY` severity is forced to 1.0 (SCHEMA §1.2). Model folder = HF encoder + tokenizer + `heads.pt`
  + `label_map.json` (SCHEMA §9 order), saved as Kaggle notebook output (`classifier_run/model/`), not in git.
- `src/models/classifier.py`: `classify(text) -> ClassifyResult` (SCHEMA §5). Model loaded once at import from
  `models/classifier/` (override with env `RESQPULSE_CLASSIFIER_DIR`). `is_ready()` for `/health`;
  `classify()` raises `ModelNotReady` if loading failed (→ `MODEL_NOT_READY`, 503) and `ValueError("EMPTY_INPUT")`
  for blank text. Attention heatmap = attention rollout over all 6 layers (heads averaged, residual added),
  [CLS]/[SEP] dropped, word pieces merged into words (max), punctuation-only tokens skipped, max score = 1.
- Trained on data v2 (Kaggle dataset version 4): `train.csv` 9,551 rows, 1,988 with severity.
- **Results (own sanity check; official numbers come from ML1's scoring of the prediction CSVs).**
  Macro-F1 over the classes present in each set:

  | Set | TF-IDF + LR | DistilBERT |
  |---|---|---|
  | `val.csv` | 0.921 | 0.910 |
  | `test_public.csv` (7 classes, held-out events) | 0.625 | **0.746** |
  | `test_synth.csv` (8 classes) | 0.869 | **0.957** |

  Severity MAE on `test_synth`: 0.51. On `test_public`, VIOLENCE_CRIME F1 rose from 0.29 to 0.79 and
  NON_EMERGENCY precision from 0.44 to 0.61. Both models score about the same on `val`, which shares events
  with train, so the gain shows up on unseen events.
- **Known weaknesses:** TRANSPORT_ACCIDENT recall on `test_public` is about 0.45 for both models. A few real
  tweets are predicted MEDICAL (a class with no real rows), so a macro over all 8 classes on `test_public`
  shows 0.653. Severity is learned only from synthetic text, so severity on real tweets is a rough estimate.
- **Nothing was tuned on test or gold.** Prediction CSVs sent to ML1 for `val`, `test_public`, `test_synth`
  and `gold_inputs` (DistilBERT), plus the baseline for the same sets and `baseline_gold.csv`.
- Follow-ups: BE1 copies the model folder to `models/classifier/` (or sets `RESQPULSE_CLASSIFIER_DIR`).
  `ClassifyResult` is defined in `classifier.py`; move it to a shared schemas module if the API has one.

## 2026-10-16 · ML3 Flan-T5 training notebook added (ML3, reviewed by Gaurav)
**Who:** rugvedas (ML3), committed and reviewed by Gaurav · **Area:** Generator
- `notebooks/flan-t5-train.ipynb`: Kaggle notebook that fine-tunes `google/flan-t5-base` and produces `ml3_test_flan.csv` and
  `ml3_gold.csv`. Scanned for secrets (none) before committing.
- Review: trains only on `train_flan.csv`, validates on `val_flan.csv` (best checkpoint by validation loss), uses `test_flan.csv`
  and `gold_inputs.csv` only for predictions; fp32, seed 42, lr 1e-4, 5 epochs, batch 4 x accumulation 4, beam search 4. The model
  is saved (`model.safetensors` 944 MB; `generator_model.zip` 877 MB on the notebook's Output tab).
- To state honestly: (1) one gold prediction (`kaggle_disaster-996`) had a truncated output and was repaired by hand with a
  hard-coded id (the tweet text copied into the summary), so the raw model parsed 143 of 144 gold rows (99.3%), not 100%;
  `extract()` should use the fallback extractor for this case instead. (2) The people-count rule was written and checked on
  `val_flan.csv` (no change there) but not applied to the CSVs. On gold it would raise people exact match from 0.285 to 0.500
  and lower the synthetic test from 0.607 to 0.598; it needs a resend of both CSVs if adopted.
- Still missing: `src/models/generator.py` (`extract()` plus the fallback extractor) in the repo.

## 2026-10-16 · Backend API with fake models (BE1, reviewed and merged by Gaurav)
**Who:** Aaryan0802 (BE1), review and fixes by Gaurav · **Area:** API
- BE1's FastAPI app (`src/api/main.py`, `schemas.py`), fake models (`src/models/fake.py`), geocoding with a Nominatim lookup and a
  small demo fallback table (`src/services/geocoding.py`), a minimal Streamlit voice page (`app.py`) and API tests.
- Review: ran the real server and exercised every endpoint and error case (health, analyze, empty/too-long/invalid input,
  queue ordering, 404, patch, transcribe checks, metrics, CORS); all behave as in SCHEMA §6 and §7.
- Fixes added on top of BE1's commit: API tests now run the startup hook (4 of 6 failed with 503 because models never loaded);
  `.env.example` restored (the branch deleted it) with `USE_FAKE_MODELS` documented; a model exception now returns the
  `MODEL_NOT_READY` error instead of a raw 500; the alert-id counter is behind a lock; runtime logs (`reports/alerts.jsonl`,
  `reports/corrections.jsonl`, `output/`) are git-ignored. Result: 10 of 10 tests pass.
- Known gaps for BE1/BE2: `USE_FAKE_MODELS=false` needs `src/models/classifier.py`, `src/models/generator.py` and
  `src/asr/whisper.py`, none of which exist yet; geocoding has no city-centre fallback or rate limit; malformed request bodies
  return FastAPI's default 422 `detail`, not the SCHEMA error envelope; the root `app.py` is a minimal voice-only page, the
  full dashboard belongs in `app/`.

## 2026-10-16 · ML3 gold file resent, predictions folder cleaned (PR #15)
**Who:** Gaurav (ML1) · **Area:** Evaluation
- ML3 resent `ml3_gold.csv`: one previously truncated output is now complete (gold parse rate 99.3% to 100%, ROUGE-L 0.428 to
  0.429, all other extraction scores unchanged). `ml3_test_flan.csv` was resent byte-identical. The people-count rule was
  not applied (the model still predicts a people number for 119 of 144 real tweets), so people exact match on gold stays 0.285.
- `predictions/` now holds exactly the 8 required files (`ml2_*`, `baseline_*` for test_synth, test_public and gold, plus
  `ml3_test_flan.csv` and `ml3_gold.csv`); the validation-set predictions and duplicate copies were moved out, not deleted.
- `reports/` regenerated.

## 2026-10-16 · Baseline on gold and the results slide (PR #14)
**Who:** Gaurav (ML1) · **Area:** Evaluation, Docs
- ML2's `baseline_gold.csv` arrived; `reports/` regenerated with the full baseline vs DistilBERT comparison on all three test sets.
- Gold set (144 real reports), macro F1: baseline 0.560, DistilBERT 0.765; emergency recall 0.707 vs 0.909; critical recall
  (severity >= 4) 0.750 vs 0.982. Largest per-class gains: VIOLENCE_CRIME F1 0.19 to 0.91, FIRE 0.36 to 0.80.
- False alarm on gold is similar for both (0.356 baseline, 0.378 DistilBERT), so it is reported as a weakness, not a win.
- Slide 6 (Results) of the presentation guide filled in with real numbers, one failure case with the reason, the
  generalisation result (64% vs 48% on unseen crises) and an explicit note that voice was not evaluated.

## 2026-10-16 · Interim evaluation on real predictions (PR #13)
**Who:** Gaurav (ML1) · **Area:** Evaluation
- First real scores from ML2 (DistilBERT + TF-IDF baseline) and ML3 (Flan-T5), committed as `reports/metrics.json`,
  `results.md`, `error_analysis.md` and confusion matrices so the Streamlit metrics page can be built on real output.
  **Interim**: the baseline has no gold-set predictions yet and ML3 may resend after a post-processing change.
- Incident type, macro F1: synthetic test 0.957 (baseline 0.869); real test tweets 0.746 (baseline 0.625); gold 0.765.
  On the 6 held-out CrisisLex crises (events never seen) DistilBERT scores 0.640 accuracy vs 0.483 for the baseline.
- Weak spots, to state openly: on the gold set 17 of 45 NON_EMERGENCY tweets (mostly commentary that mentions a disaster) are
  flagged as emergencies (false alarm 0.378), and severity generalises poorly from call-style training data to news tweets
  (gold RMSE 1.33 vs 0.75 on synthetic; predictions shrink toward the middle, true 5.0 averages 3.66).
  Emergency recall on gold is 0.909 and critical recall (severity >= 4) is 0.982.
- ML2 delivered files with different names in `predictions/ml2/`; copied to the expected names. Still missing:
  `baseline_gold.csv`.

## 2026-10-16 · Demo samples for the Streamlit app (PR #12)
**Who:** Gaurav (ML1) · **Area:** Data, UI support
- `app/demo_samples.json`: 9 ready-made reports for the app's sample buttons (one per incident type, a non-emergency and a
  vague report), each with the expected type and severity. They come from the held-out `test_synth` set, so the demo does not
  show the models text they were trained on.

## 2026-10-16 · Gold set audit result (PR #11)
**Who:** Gaurav (ML1) · **Area:** Data, Docs
- Gaurav audited a random 30-row sample of the gold set (`data/gold/gold_audit.csv`): all 30 rows agreed on type and
  severity. `build_gold.py audit-score` reports 30/30.
- With 30 samples, 30/30 supports "agreement of at least about 90% with 95% confidence"; it does not prove the set is
  error-free. The brief's slide 5 and the Q&A answer now say "all 30 rows agreed" and warn against overclaiming.

## 2026-10-16 · Data slide with real numbers (PR #10)
**Who:** Gaurav (ML1) · **Area:** Docs
- Presentation guide, slide 5 (Data), rewritten with the real figures: about 37,000 real tweets (13 HumAID disasters,
  26 CrisisLex crises, Kaggle negatives), 710 synthetic reports, 9,551 training rows (7,563 real + 497 unique synthetic x4),
  107 / 7,755 / 144 held-out rows, the 16% event-label error finding, and a per-type table of real, synthetic and gold counts.
- The human-audit agreement is filled in once `data/gold/gold_audit.csv` is scored (result: PR #11).
- Created the `predictions/` folder (git-ignored) where teammates' prediction CSVs go.

## 2026-10-16 · Evaluation script (PR #9)
**Who:** Gaurav (ML1) · **Area:** Data, Evaluation
- `src/eval/metrics.py` (pure metric functions) and `scripts/evaluate.py` score the teammates' prediction CSVs and write
  `reports/metrics.json` (SCHEMA §8), `results.md` (slide tables), `error_analysis.md` (most confident mistakes, worst severity
  and extraction errors) and one confusion-matrix PNG per model and test set.
- Metrics: type precision/recall/F1 (macro over the classes present, weighted F1, per class), emergency recall, false alarm
  rate, critical recall (severity >= 4), severity MSE/RMSE/MAE/bucket accuracy, extraction parse rate, location token F1,
  people exact match, injuries/hazards P/R/F1 (strict and lenient), ROUGE-L, and test_public accuracy per data source.
- Why a central script: one definition of every metric, the gold labels never reach the model builders, and the evaluation
  sheet's Precision/Recall/MSE/RMSE come out in one table with baseline vs model side by side.
- Tested: 10 unit tests against hand-computed values; an end-to-end run on fake predictions (the fake numbers track the noise
  injected, confirming the code measures what it should); and failure cases (empty folder, missing ids, invalid type names,
  duplicate ids, blank severity, missing column) which warn and keep scoring the usable rows.
- `scripts/make_fake_predictions.py` writes fake files for testing only. `data/gold/gold_inputs.csv` (id, text) is the
  label-free input for gold predictions. Prediction formats are in SCHEMA §8.1.

## 2026-10-16 · Gold set second pass and audit sample (PR #8)
**Who:** Gaurav (ML1) · **Area:** Data
- Instead of a full human review, Claude re-reviewed all 146 pre-labelled rows against the written rules. It found
  10 problems in its own first pass: 5 rows changed to NON_EMERGENCY (commentary, relief aircraft, a relief appeal,
  a wind caution the original annotators marked unrelated, thanks to volunteers), 3 severities lowered for follow-up
  news, and 2 near-duplicate retweets dropped. Result: `data/gold/gold.csv`, 144 rows (NON_EMERGENCY 45,
  EARTHQUAKE_COLLAPSE 22, FLOOD 18, VIOLENCE_CRIME 17, STORM_CYCLONE 16, FIRE 15, TRANSPORT_ACCIDENT 11).
- **Honest labelling:** the same model labelled and reviewed, so the gold set is called "Claude-labelled, second-pass
  reviewed", not human-verified. `build_gold.py audit-sample` draws 30 random rows for a person to check and
  `audit-score` reports the agreement rate to quote on the slide. README, brief and review guide were reworded.

## 2026-10-16 · Gold set pre-labels and review pipeline (PR #7)
**Who:** Gaurav (ML1) · **Area:** Data
- `scripts/sample_gold.py` samples 154 real tweets (22 per mapped type) from `test_public.csv`, the data the models never
  train on. `data/gold/gold_prelabels.jsonl` holds Claude's pre-labels (type, severity, location, people, injuries,
  hazards, summary); `scripts/build_gold.py prelabel` merges them into `data/gold/gold_review.csv` for human review
  (146 rows; 8 Spanish-language tweets dropped). All pre-labelled fields pass the word-for-word check.
- `docs/GOLD_REVIEW.md` is the reviewer guide; `scripts/build_gold.py finalize` turns the reviewed sheet into
  `data/gold/gold.csv` in the SCHEMA §2 format.
- **Finding:** 24 of 146 real tweets (16%) have a different type than the event-based mapping gave them, mostly
  donations, jokes, commentary and follow-up news (which are `NON_EMERGENCY`), plus a few wind or river posts filed
  under the wrong disaster. So `test_public` scores are measured against noisy labels; the gold set is the clean benchmark.
- **Limits to state honestly:** the gold set comes from a handful of events (LAX shooting, West Texas explosion, Spain
  train crash, typhoon Pablo and others), and there are no real MEDICAL tweets at all.

## 2026-10-16 · Synthetic round 2, data v2 (PR #6)
**Who:** Gaurav (ML1) · **Area:** Data
- **710 validated synthetic reports** (up from 485): MEDICAL 134, VIOLENCE_CRIME 103, TRANSPORT_ACCIDENT 91,
  FIRE 88, NON_EMERGENCY 87, FLOOD 73, STORM_CYCLONE 67, EARTHQUAKE_COLLAPSE 67. Round 2 targeted the gaps:
  MEDICAL (+60), the three disaster types (+30 each) and VIOLENCE/TRANSPORT/FIRE/NON_EMERGENCY (+16 to +25),
  written longer (mean 26.9 words, up from 21) with more detail, plus more hard negatives (mock drills,
  film shoots with toy guns, lonely callers, lost phones).
- Validator minimum length lowered from 8 to 5 words so short vague reports are kept. 711 in, 710 kept, 2 hazard
  items auto-removed.
- v2 splits: `train.csv` 9,551 rows, `val.csv` 3,576, `test_synth.csv` 107 (8 to 20 per class, up from 73),
  `test_public.csv` 7,755, `train_flan.csv` 497, `val_flan.csv` 106, `test_flan.csv` 107.
- Still small: per-class counts in `test_synth` are 10 to 20, so per-class synthetic scores stay rough;
  the real-text test (`test_public`) and the gold set carry the credible numbers.

## 2026-10-16 · Synthetic reports and final splits, v1 (PR #5)
**Who:** Gaurav (ML1) · **Area:** Data
- **485 synthetic call-style reports** written directly by Claude in a Claude Code session (no API key), covering
  all 8 types: FIRE 76, TRANSPORT_ACCIDENT 75, MEDICAL 74, VIOLENCE_CRIME 74, NON_EMERGENCY 69, FLOOD 43,
  STORM_CYCLONE 37, EARTHQUAKE_COLLAPSE 37. Mixed severities (1–5), 8 writing styles, 100+ Indian cities,
  about 20 words on average, plus hard negatives (figurative speech, pranks, mock drills, film shoots).
- `scripts/validate_synthetic.py` checks enums, ranges and the word-for-word rule and removes near-duplicates:
  of 486 reports, 1 dropped (too short) and 1 hazard item removed; everything else passed.
- `scripts/make_splits.py` builds `train.csv`, `val.csv`, `test_synth.csv`, `test_public.csv` and the Flan-T5 files
  `train_flan.csv`, `val_flan.csv`, `test_flan.csv`, plus `reports/data_card.md`. `src/data/flan.py` is the shared
  serializer/parser for the Flan-T5 line format (round-trip tested).
- **Decisions:** public training rows capped at 1,200 per type and synthetic train rows repeated 4x, so the
  call-style reports are not drowned out by 7,500 real tweets; the real test set (`test_public.csv`) and the
  synthetic test set (`test_synth.csv`) are reported separately.
- **Known gaps:** `test_synth` and `val` synthetic parts are only 73 rows each, too small for per-class metrics;
  MEDICAL has no real rows. A second generation round (about 700 more reports) will fix both. A first bug was
  caught while building the splits: pandas 3 drops the grouping column inside `groupby.apply`, which had removed
  `incident_type` from the public rows; fixed with an explicit loop and a null check.

## 2026-10-16 · Public-data pipeline, v0 splits (PR #4)
**Who:** Gaurav (ML1) · **Area:** Data
- Added `src/data/labels.py` (types, label map, event → type maps, HumAID keep list, CrisisLex held-out crises),
  `src/data/clean.py` (`clean_text`) and `scripts/build_public.py`.
- Output: `data/processed/public_{train,val,test}.csv` in the SCHEMA §2 format. 37,086 rows after removing
  2,086 duplicates and too-short texts: train 16,850 / val 3,470 / test 7,755.
- Choices: HumAID's own splits kept; **CrisisLexT26 split by crisis** (West Texas, Queensland, Pablo, Bohol, Spain
  train crash and LA airport are never trained on); Kaggle `target == 0` rows are `NON_EMERGENCY`; training rows
  capped at 3,000 per type so `STORM_CYCLONE` doesn't dominate.
- **Known gaps:** no `MEDICAL` rows (synthetic only); `VIOLENCE_CRIME` has only 363 real training rows; real text is
  news-style rather than call-style, and CrisisLex contains some non-English tweets. Synthetic data covers these.
- Follow-ups: upload to Kaggle for ML2; Claude synthetic generation next.

## 2026-10-16 · Update log and presentation guide (PR #3)
**Who:** Gaurav · **Area:** Docs
- Added this `UPDATE.md` log; every future change is recorded here.
- RESEARCH_BRIEF is now a living document: added §16 *Project status* (status table + changes from the
  original plan) and §17 *Presentation reading guide* (slide-by-slide script with speakers, rubric
  mapping, result placeholders and a pre-presentation checklist).
- README links the update log.

## 2026-10-16 · Schema v1 and verified dataset links (PR #2)
**Who:** Gaurav · **Area:** Docs, Data
- Added `docs/SCHEMA.md`: shared enums, severity rubric, training CSV format, Claude generation
  (grid, output JSON schema, prompt, API sketch), Flan-T5 text format, model interfaces, alert object,
  API contract, metrics report format.
- Added `docs/DATASETS.md`: verified links for HumAID, CrisisLexT26, Kaggle Disaster Tweets, ESC-50,
  MUSAN, edge-tts and the Hugging Face models, with column formats and label mappings.
- **Plan changes:** added `STORM_CYCLONE` (largest HumAID class); `ROAD_ACCIDENT` → `TRANSPORT_ACCIDENT`
  (CrisisLexT26 includes rail/air crashes); Claude chosen for synthetic data.
- `.env.example` now uses `ANTHROPIC_API_KEY` and `CLAUDE_MODEL`; `anthropic` and `edge-tts` added to requirements.
- Follow-ups: choose the Claude model (budget); confirm whether preparation before the event is allowed.

## 2026-10-16 · Repository setup (PR #1)
**Who:** Gaurav · **Area:** Repo, Docs
- Project folder structure, `.gitignore` (keeps data, audio, weights and secrets out of git),
  `requirements.txt`, `.env.example`, PR template.
- Added `docs/RESEARCH_BRIEF.md` (problem, solution, data, models, voice plan, scoring, roles, timeline).
- Full README with architecture, setup, roles, 12-hour plan and git workflow.
