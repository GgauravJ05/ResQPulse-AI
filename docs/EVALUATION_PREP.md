# ResQPulse AI: evaluation study notes

Read top to bottom once, then use the **cheat sheet** and **likely questions** right before you go in.
Every number here comes from `reports/results.md`, `reports/metrics.json` or `reports/whisper_wer.json`.

---

## 1. The 30-second pitch (say this first)

> "Emergency reports arrive as messy text and calls, and during disasters they arrive in floods. Someone has to read each one,
> work out what happened, how bad it is and where, then send help. **ResQPulse AI turns a messy report, typed or spoken, into a
> structured, prioritised, explainable alert in about 2 to 4 seconds, on a laptop, offline.** Whisper hears it, DistilBERT
> understands it, Flan-T5 writes it up. On 144 real reports it never saw, it catches **91% of emergencies** and keeps **98% of the
> most severe** ones, against 71% and 75% for a baseline. A human dispatcher confirms every alert."

Problem statement: **PS 15, EmergencyScribe**: convert emergency reports into structured alerts. Required technique: **Transformer + Attention**.

---

## 2. How we score against the rubric (50 marks)

| Criterion (marks) | What we show | Where |
|---|---|---|
| Problem understanding (5) | Dispatcher overload, duplicates, no structured record; we assist, not replace | Deck slide 2, README |
| Innovation (5) | Full alert not a label, continuous severity, attention heatmap, voice, duplicate flagging, offline small models | Deck slide 2 |
| Technical implementation (10) | Two-head DistilBERT, Flan-T5 with retry + fallback, Whisper, FastAPI, honest evaluation pipeline | Deck slide 3, architecture diagram |
| Prototype / functionality (10) | Live dashboard, five screens, real models, voice end to end, queue + map | Live demo |
| SDG (5) | 3.6, 3.d, 11.5, 13.1, 16.1, 16.6, shown **on each alert** | Alert card, README |
| Communication (5) | Clear story, honest limits | Whole talk |
| Metrics: P, R, MSE, RMSE (5) | Precision, recall, F1 vs baseline; severity MSE/RMSE; extraction F1; Whisper WER | Deck slide 5, Model Metrics screen |
| Presentation / demo (5) | Rehearsed 3-minute demo with a fallback | Section 6 below |

---

## 3. The system in one picture

`docs/architecture_diagram.png`:

```
Caller / report ─► Streamlit dashboard ─► FastAPI backend ─┬─► Whisper small.en   (audio → text)
                                                           ├─► DistilBERT         (type + severity + attention)
                                                           ├─► Flan-T5-base       (location, people, injuries, hazards, summary)
                                                           ├─► Geocoder           (offline gazetteer, then OpenStreetMap Nominatim)
                                                           └─► Alert store        (in memory + JSONL logs of alerts and corrections)
```

Everything runs offline on one laptop once the models are downloaded.

**One report, step by step**
1. The dispatcher types a report or records a call. Voice goes to Whisper. The transcript is **editable** before analysis.
2. DistilBERT outputs the **incident type** (8 classes), a **severity score** from 1 to 5, and **attention weights** per word.
3. Flan-T5 writes the fields as one line, `location: … | people: … | injuries: … | hazards: … | summary: …`, which we parse to JSON.
4. Rules add **responders** (fire brigade, ambulance, police, traffic police, NDRF/SDRF) and **SDG tags**. A sentence-embedding model flags **likely duplicates**.
5. The alert goes into a **severity-sorted queue** and onto the **map**. The dispatcher confirms, dispatches or dismisses it, and **every correction is logged**.

---

## 4. The models: what each one is and why we chose it

### DistilBERT (the classifier), `distilbert-base-uncased`, about 66M parameters
- **What it is:** a smaller, faster version of BERT (a Transformer encoder) made by knowledge distillation. It keeps about 97% of BERT's quality at about 60% of the size.
- **What we did:** fine-tuned it with **two heads** on top:
  - **Type head:** 8-way classification, trained with cross-entropy.
  - **Severity head:** one number from 1 to 5 (regression), trained with **masked MSE**. The loss is computed only on rows that have a severity label, because tweets have none.
- **Why:** small enough for a laptop CPU, strong on short noisy text, and it exposes attention for the explanation.

### Attention and the heatmap (the "Transformer + Attention" requirement)
- **Self-attention:** every word builds a query (Q), key (K) and value (V). It compares its Q with every other word's K, a softmax turns those scores into weights, and it takes a weighted mix of the Vs. So each word "looks at" the words that matter to it.
- **Attention rollout:** we multiply attention across all layers, adding the residual connection, to estimate how much each input word fed the final decision. Those are the heatmap colours.
- **Say this honestly:** "Attention shows what the model focused on. It is an **indicator, not proof** of reasoning, which is why a human confirms every alert." The app prints this sentence under the heatmap.

### Flan-T5-base (the generator), about 250M parameters
- **What it is:** T5 is a Transformer encoder-decoder (text in, text out). Flan-T5 is T5 instruction-tuned on many tasks.
- **What we did:** fine-tuned it in fp32 to write the five fields as a flat `key: value | …` line. T5's vocabulary has no `{ }`, so JSON output was not reliable.
- **Safety net:** retry with a wider beam (4, then 6), then a **rule-based fallback extractor**, then a **people-count rule** that keeps a count only if the text gives evidence for it. The model alone parsed 143 of 144 real reports; the fallback handled the last one.

### Whisper small.en (speech), via faster-whisper, int8
- An encoder-decoder Transformer trained by OpenAI on about 680,000 hours of speech. We **did not train it**. VAD is on, and low-confidence transcripts are flagged for the dispatcher to check.

### Baseline: TF-IDF + logistic regression
- It counts words, weighted by rarity, and draws a linear boundary. It exists to prove the transformer adds value.

### Duplicate detection: `all-MiniLM-L6-v2` (sentence-transformers)
- Turns each report into a vector. Cosine similarity **above 0.75** marks `duplicate_of`. A reworded report of the same fire scored 0.78 to 0.93; unrelated incidents scored under 0.25.

---

## 5. Data

| Kind | What | Why |
|---|---|---|
| Real crisis tweets | **HumAID** (Alam et al., 2021), **CrisisLexT26** (Olteanu et al., 2015), **Kaggle Disaster Tweets** (as non-emergency negatives). About **37,000** after cleaning and de-duplication | Teach the model real disasters |
| Call-style reports | **710** reports written by Claude in 8 styles (panicked, SMS, elderly caller, child, official, vague, …), each with every field labelled. A validator checks that every extracted phrase appears word for word | No public dataset of real emergency calls exists; this is the style the demo uses |
| Gold test set | **144 real reports**, labelled by Claude, re-reviewed in a second pass, then a **human audit of 30 random rows: 30 of 30 agreed** | The honest test; never trained on |

- **Training set:** 9,551 rows: 7,563 real tweets (capped at 1,200 per type), plus 497 unique call-style reports, each repeated 4 times so they are not drowned out.
- **Held out:** 107 call-style reports, 7,755 real tweets (including **6 whole crises the model never saw**), and the gold set.
- **Schema:** 8 types: FIRE, FLOOD, STORM_CYCLONE, EARTHQUAKE_COLLAPSE, TRANSPORT_ACCIDENT, MEDICAL, VIOLENCE_CRIME, NON_EMERGENCY. Severity 1 to 5, bucketed as LOW < 2 ≤ MEDIUM < 3 ≤ HIGH < 4 ≤ CRITICAL.
- **A finding worth saying:** labelling a tweet by its disaster's name was wrong for about **16%** of tweets. Donation appeals, jokes and commentary mention a disaster but report nothing. That is why we built a checked gold set.
- **30 of 30, explained:** with no disagreements in 30 random checks, agreement is at least about 90% at 95% confidence. Do not claim it is perfect.

---

## 6. The live demo (about 3 minutes)

The app is running at **http://localhost:8501**. The sidebar should show the **LIVE · REAL MODELS** pill at the top right.

1. **Report Input** → click **Transport Accident** (or type a report) → **Analyze Report**. Say: "type, severity, location, people, all in a few seconds."
2. **Alert Card** → point at the **severity ruler** (5 cells, 4.x of 5), the **evidence column** (coordinates, confidence, response time) and the **SDG tag**.
3. **Attention Heatmap** → point at the darkest yellow words: "these drove the decision. It's an indicator, not proof." The class probabilities sit underneath.
4. **Voice**: on Report Input, upload `demo_assets/noisy_phone_report.wav` → **Transcribe Audio Now**. Whisper hears "Lonavala" as "La Navalan"; **fix the word in the box**, then Analyze. "The dispatcher can always correct the transcript."
5. **Duplicates**: analyse the same incident reworded. The alert shows **Possible duplicate of RQP-…**.
6. **Dispatcher Dashboard** → the most severe alert is at the top, with dots on the map. Click **Dispatch**.
7. **Non-emergency**: type "is the mall open today?" → calm **No emergency detected** card.
8. **Model Metrics** → the baseline vs DistilBERT tables and the confusion matrix.

**If something breaks:** say "let me show the recorded run" and switch to the backup. The first request after a restart takes about 6 seconds while the models warm up.

---

## 7. Numbers cheat sheet (memorise the bold ones)

**Incident type, baseline → ours**

| Test set | Macro precision | Macro recall | Macro F1 |
|---|---|---|---|
| **Gold, 144 real** | 0.61 → **0.76** | 0.59 → **0.79** | 0.56 → **0.77** |
| Call-style, 107 | 0.89 → 0.96 | 0.86 → 0.96 | 0.87 → 0.96 |
| Real tweets, 7,755 | 0.73 → 0.79 | 0.62 → 0.75 | 0.63 → 0.75 |

- **Emergency recall (gold): 0.91** (baseline 0.71). Of the real emergencies, 91% were flagged.
- **Severe reports kept (gold): 0.98** (baseline 0.75). We missed only 1 of 27 reports labelled severity 4 or 5.
- **False alarms (gold): 0.38** (baseline 0.36). This is our weak spot.
- **Unseen crises:** accuracy **64% vs 48%**. This is the strongest argument for the transformer.
- Biggest class gains on gold: **violent crime F1 0.19 → 0.91**, **fire 0.36 → 0.80**.
- **Severity:** **RMSE 0.75, MSE 0.57** on call-style reports (87% within one point). RMSE 1.33, MSE 1.77 on real tweets.
- **Extraction (call-style):** parses **100%**, location F1 **0.78**, people count exact 60%, injuries F1 0.54 (0.64 lenient), hazards F1 0.38 (0.59 lenient), summary ROUGE-L 0.50.
- **Voice:** word error rate **9.9% clean, 15.5% noisy** (20 clips, synthetic voices). Incident type matched the typed result in 18/20 and 16/20.
- **Speed:** about **2 to 4 s** per report on a laptop CPU once warm.
- **Tests:** 52 automated tests.

### What the metrics mean (be ready to define them)
- **Precision:** of the reports we labelled FIRE, how many really were fire. Low precision means false alarms.
- **Recall:** of the real fires, how many we caught. Low recall means misses.
- **F1:** the harmonic mean of precision and recall, so it is high only when both are.
- **Macro average:** compute the score per class, then average, so small classes count as much as big ones. We average only over classes present in the test set; the gold set has no MEDICAL.
- **MSE:** the mean of squared errors. It punishes big mistakes heavily; the units are severity points squared.
- **RMSE:** the square root of MSE, back in severity points. "On average our severity is about 0.75 points off on a 1-to-5 scale."
- **Word error rate:** (substitutions + deletions + insertions) ÷ number of reference words.
- **ROUGE-L:** overlap of the longest common word sequence between our summary and the reference.
- **Why recall first:** a missed emergency costs a life; a false alarm costs a minute of a dispatcher's time.

---

## 8. Likely judge questions, with answers

**"Isn't this just a classifier?"**
No. It produces a full alert: type, a continuous severity, five extracted fields, responders, SDG tags, map position and duplicate flags. It also explains itself with the heatmap.

**"Why not just use GPT or Claude?"**
Cost, latency, privacy and offline operation. Emergency data shouldn't leave the control room, and a control room can lose internet in a disaster. Our models are small enough for a laptop CPU. We did use Claude **offline** to write training reports and pre-label the gold set, never at run time.

**"Your training data is synthetic. Isn't that a problem?"**
It's a real limitation, and we said so. That is why we test on **real** held-out reports (the gold set and 7,755 tweets) and report those numbers separately. On real reports we still beat the baseline by 0.21 F1. The fix is real anonymised 112 transcripts.

**"Who labelled the gold set?"**
Claude labelled it, in a second checking pass, and a person audited 30 random rows with 30 of 30 agreement. We don't claim it is hand-labelled throughout.

**"Why is your false alarm rate so high?"**
Commentary that uses disaster words gets flagged, for example "Photo of dummy presented as wounded LAX shooter by media". The model reads topic, not intent. We tested raising the emergency threshold: false alarms fell from 0.38 to 0.31, but emergency recall fell from 0.93 to 0.87 and severe-report recall from 0.98 to 0.95. Missing emergencies is worse, so we kept the default. The dispatcher is the safeguard.

**"Why does severity do worse on tweets?"**
The severity head was trained only on call-style reports, which have severity labels; tweets don't. On news-style text the scores shrink toward the middle: reports we labelled 5.0 average 3.7.

**"How does attention prove anything?"**
It doesn't prove reasoning. It shows where the model looked, and it is a useful check: if "blood" and "not moving" light up for an accident, the decision is plausible. We label it as an indicator.

**"What is attention rollout?"**
Raw attention in one layer only shows one hop. Rollout multiplies the attention matrices across all layers, with the residual connection added, to trace how much each input word reached the final representation.

**"Why DistilBERT and not BERT or RoBERTa?"**
It is 40% smaller and 60% faster with most of the accuracy, and it runs on a laptop CPU. A bigger encoder is our next step.

**"Why Flan-T5 and not regex or NER?"**
Reports are messy ("2-3 people stuck", "my mother"), and locations are free text. A generator handles that and also writes a summary. We still keep a rule fallback for safety.

**"How do you handle voice errors?"**
Whisper flags low confidence, and the transcript is editable before analysis. Measured word error rate is 9.9% clean and 15.5% noisy, mostly place names and digits.

**"How do duplicates work?"**
Each report becomes a sentence embedding. If cosine similarity with an earlier alert is above 0.75, we mark it as a possible duplicate, and the dispatcher merges or dismisses it.

**"How would this be deployed for real?"**
Integrated with 112 ERSS. The dispatcher's confirm, dispatch and dismiss actions are already logged as training data. Next steps: a persistent database, login, Hindi, Marathi and Hinglish (MuRIL, multilingual Whisper), and real call transcripts.

**"What did each team member do?"**
Data and evaluation (ML1), classifier (ML2), generator (ML3), API (BE1), services such as Whisper, geocoding and duplicates (BE2), and dashboard (FE). Each person names their part.

**"What would you do with more time?"**
Real transcripts, retrain the severity head on news-style text, more hard negatives against false alarms, multilingual support, and learning from the logged corrections.

---

## 9. Limitations (say them before they're asked)

- 37.8% false alarms on non-emergency tweets in the gold set.
- Severity is weaker on tweets (RMSE 1.33).
- No real 112 calls; MEDICAL has no real tweets.
- The gold labels are Claude's, with a 30-row human audit.
- Voice was tested on 20 synthetic-voice clips, not real callers.
- English only.
- Attention is an indicator, not proof.

---

## 10. SDG targets (each alert carries its tag)

| Target | Link |
|---|---|
| **3.6** road traffic deaths | Faster triage of accidents, faster ambulances |
| **3.d** health risk early warning | Severity-ranked medical alerts |
| **11.5** disaster deaths and losses | Prioritised alerts during report surges |
| **13.1** climate resilience | Floods and cyclones processed at scale |
| **16.1** reduce violence | Faster police and ambulance dispatch |
| **16.6** accountable institutions | Explainable decisions and a logged audit trail |

---

## 11. If you need to restart the app during evaluation

```bash
# Terminal 1 (backend, real models): wait for "Application startup complete"
USE_FAKE_MODELS=false .venv/bin/python -m uvicorn src.api.main:app --port 8000
# Terminal 2 (dashboard)
.venv/bin/python -m streamlit run app/streamlit_app.py --server.address 0.0.0.0
# Check
curl http://localhost:8000/health      # classifier, generator, asr: true
```

Start the backend **first**. Then send one report to warm up.
