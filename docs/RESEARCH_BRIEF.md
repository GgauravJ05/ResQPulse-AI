# ResQPulse AI — Team Research Brief

> Read this before the hackathon starts. It covers the problem, our solution, what makes it different,
> how it works, how we'll be scored, and what each of us does in the 12 hours.
> Items marked **[DECIDE]** are still open and will be settled in the first hour.
>
> **This is a living document.** It is updated with every change to the project, so by the end it describes
> what we actually built, and **§17 becomes the doc we read from when presenting**. Each change is also logged
> in [UPDATE.md](UPDATE.md).

---

## 1. The problem statement

**PS 15: EmergencyScribe — Convert Emergency Reports Into Structured Alerts**
**Required technique:** Transformer + Attention

### What it means in plain words

When something goes wrong (a fire, a crash, a flood, someone collapsing), people report it in **messy,
unstructured language**:

> "bhai there's a huge fire near the petrol pump on FC road, 2-3 people stuck inside the shop, smoke everywhere, pls send help fast"

A dispatcher has to read or hear this and work out, quickly and correctly:

- **What** happened? (fire)
- **How bad** is it? (high, since people are trapped and fuel is nearby)
- **Where?** (petrol pump, FC Road)
- **Who and how many** are affected? (2–3 people, trapped)
- **What hazards** are there? (fuel, smoke)
- **Whom to send?** (fire brigade + ambulance)

Our job is to **automate that conversion**: free text in, a structured alert out, which a system can
sort, route and map.

### Why it is a real problem

- India's emergency number **112 (ERSS)** brings police, fire and ambulance under one number, so one
  control room receives very mixed reports.
- During **disasters (floods, cyclones, earthquakes)** report volume spikes, and many reports are
  duplicates of the same incident. Humans can't triage them fast enough, and urgent ones get buried.
- Reports arrive through many channels: calls, SMS, WhatsApp and social media. All are unstructured.
- Manual triage is **slow, inconsistent between operators, and leaves no machine-readable record**.

> **Action item for the pitch:** find 2–3 cited statistics (for example, average response times,
> 112 call volumes, disaster-time social media volume). Use only real, cited numbers. Never invent them.

### Who is the user?

The **emergency dispatcher / control-room operator**. Our tool **assists** them. It does not replace
them, because a human still confirms each alert. Say this explicitly: it answers "what if the model
is wrong?"

---

## 2. Background research (what you need to know)

### 2.1 Why a Transformer?

Older NLP models (bag-of-words, RNNs/LSTMs) either ignore word order or struggle to link words that
are far apart in a sentence. A **Transformer** processes all words at once and uses **attention** to
let every word look at every other word.

In "*people stuck inside the shop near the petrol pump*", the model learns that **"stuck"** and
**"petrol"** matter most for severity, wherever they appear in the sentence.

### 2.2 What is Attention?

For each word, attention computes **how much it should focus on each other word**:

```
Attention(Q, K, V) = softmax( Q·Kᵀ / √d ) · V
```

- **Q (query):** what this word is looking for
- **K (key):** what each word offers
- **V (value):** the information that actually gets passed along
- softmax turns the scores into weights that sum to 1

**Multi-head attention** runs this several times in parallel, so different heads learn different
relationships (one tracks locations, another tracks danger words, and so on).

**Why it matters for us:** we can **extract the attention weights and show them as a heatmap**. That
lets the dispatcher see *which words* drove the decision. This is our explainability feature, and it
ties directly to "Transformer + Attention" in the PS title.

> **Honest caveat (judges may ask):** attention weights are a *useful indicator*, not a perfect proof
> of why a model decided something. We present them as "what the model focused on".

### 2.3 Encoder vs. generator (we use both)

| Type | Example | Good at | Our use |
|---|---|---|---|
| **Encoder** (BERT family) | DistilBERT | *Understanding* text: classification, scoring | Incident type + severity |
| **Encoder–decoder** (seq2seq) | Flan-T5 | *Generating* text from text | Report → JSON alert + summary |

**Fine-tuning** means taking a model already pre-trained on huge amounts of text and training it a bit
more on *our* task. It needs far less data and compute than training from scratch, which is why it
fits 12 hours on a Kaggle T4.

### 2.4 Whisper is a transformer too

Whisper (speech → text) is also an encoder–decoder Transformer:

1. Audio is turned into a **log-mel spectrogram** (a picture of which frequencies occur over time) in 30-second windows.
2. The **encoder** reads it with self-attention.
3. The **decoder** writes the text token by token, using **cross-attention** to look back at the relevant part of the audio.
4. It was trained by OpenAI on about 680k hours of speech, so it handles accents and noise without any training from us.

**Pitch line:** *"Three transformers work together: Whisper hears the report, DistilBERT understands it, Flan-T5 writes the alert."*

### 2.5 Related work (mention in the pitch)

- **CrisisNLP / CrisisLex**: research groups that released labelled crisis tweet datasets.
- **HumAID** (Alam et al., 2021): about 77k human-labelled tweets from 19 real disasters, labelled into
  humanitarian categories.
- **CrisisTransformers / crisis-specific BERT models**: prior work shows transformers clearly
  outperform classic ML on crisis text classification.
- **Gap we fill:** most prior work **classifies tweets**. It does not produce a **complete, structured,
  dispatch-ready alert** (type + severity + location + people + hazards + responders) with
  explanations.

---

## 3. Our solution: ResQPulse AI

### One-line pitch

> **ResQPulse turns messy emergency reports (text or voice) into structured, prioritised, explainable
> alerts in about a second, and puts them on a live dispatcher dashboard.**

### Input → output example

**Input:**
> "Accident on Mumbai–Pune expressway near Lonavala exit, truck hit two cars, one guy not moving, lot of blood, traffic blocked"

**Output alert:**
```json
{
  "alert_id": "RQP-000123",
  "incident_type": "TRANSPORT_ACCIDENT",
  "severity": 4.4,
  "severity_label": "CRITICAL",
  "location": { "text": "Mumbai–Pune expressway near Lonavala exit", "lat": 18.75, "lon": 73.40 },
  "people_affected": 1,
  "injuries": ["unconscious", "heavy bleeding"],
  "hazards": ["traffic blocked", "multiple vehicles"],
  "responders": ["AMBULANCE", "TRAFFIC_POLICE"],
  "summary": "Truck–car collision near Lonavala exit; one person unresponsive with heavy bleeding; road blocked.",
  "confidence": 0.89
}
```

---

## 4. What makes us different

| # | Differentiator | Why it matters |
|---|---|---|
| 1 | **Full structured alert, not just a label** | Prior work stops at classifying tweets. We produce a complete, dispatch-ready record. |
| 2 | **Explainable via attention heatmaps** | Dispatchers can see *why* something was marked critical, which builds trust. |
| 3 | **Severity as a continuous score (1–5)** | Allows fine-grained priority ordering, not just high/low. |
| 4 | **Voice input (Whisper)** | Real emergencies are often calls, not typed text. |
| 5 | **Live priority queue + map** | Turns a model into an actual dispatch tool. |
| 6 | **Small, offline, free models** | Emergency data is sensitive. Our models run locally, cost nothing per call, and don't depend on internet or paid APIs. |
| 7 | *(stretch)* **Duplicate-report merging** | During a disaster, 10 reports of the same fire become 1 alert, not 10. |

---

## 5. System architecture

```
          ┌──────────────────────────────┐
 Text ───►│                              │
          │   Input layer                │
 Voice ──►│   (Whisper: speech → text)   │
          └──────────────┬───────────────┘
                         ▼
          ┌──────────────────────────────┐
          │ Model 1: DistilBERT (2 heads)│──► incident_type   (classification)
          │                              │──► severity 1–5    (regression)
          │                              │──► attention map   (explainability)
          └──────────────┬───────────────┘
                         ▼
          ┌──────────────────────────────┐
          │ Model 2: Flan-T5 (fine-tuned)│──► location, people, injuries,
          │ report → JSON                │    hazards, summary
          └──────────────┬───────────────┘
                         ▼
          ┌──────────────────────────────┐
          │ Post-processing              │
          │ • JSON validation (Pydantic) │
          │ • geocoding (location → map) │
          │ • type → responders mapping  │
          │ • (stretch) duplicate merge  │
          └──────────────┬───────────────┘
                         ▼
          ┌──────────────────────────────┐
          │ FastAPI backend              │
          │ /analyze  /transcribe /alerts│
          └──────────────┬───────────────┘
                         ▼
          ┌──────────────────────────────┐
          │ Streamlit dashboard          │
          │ input · alert card · heatmap │
          │ priority queue · map · metrics│
          └──────────────────────────────┘
```

### Why two models instead of one?

- **Model 1 (DistilBERT, 66M params)** is fast, accurate for classification and regression, and lets
  us extract attention for the heatmap.
- **Model 2 (Flan-T5-base, ~250M params)** is the **generative** part, the Gen AI core of the course.
  It reads the report and writes the structured fields and a summary.
- Splitting them lets **two ML people train in parallel** on separate Kaggle accounts, and if one
  struggles the other still works.

### Fallback plan (if Flan-T5 underperforms by hour 7)

Swap Model 2 for an off-the-shelf NER model (`dslim/bert-base-NER`) + rules/templates for the fields.
The demo keeps working. We mention it honestly as a backup.

---

## 6. Data strategy

### 6.1 Two kinds of data

| Type | What | Source | Labels it gives us |
|---|---|---|---|
| **A: Real crisis posts** | Tweets/posts during real disasters | HumAID, CrisisLexT26, Kaggle "NLP with Disaster Tweets" | Incident type (mapped), emergency vs. not |
| **B: Generated call-style reports** | Realistic 112-style reports in the call/SMS style | Generated with **Claude** (prompt and output format in [SCHEMA.md §3](SCHEMA.md#3-synthetic-generation-with-claude)) | **Everything**: type, severity, location, people, injuries, hazards, summary |

**Strategy:** train on **A + B**, demo on **B-style** reports, because the demo should look like real
dispatch work.

**Key insight:** when an LLM *generates* a synthetic report, it generates the *labels* too. So we get
fully labelled data for every field without manual annotation.

### 6.2 Incident types (schema v1)

8 classes. The full definitions, responders and SDG targets are in [SCHEMA.md §1.1](SCHEMA.md#11-incident_type-8-classes),
and the source mapping is in [DATASETS.md](DATASETS.md).

| Class | Mainly from |
|---|---|
| `FIRE` | HumAID wildfires + CrisisLexT26 fires/explosions + generated |
| `FLOOD` | HumAID + CrisisLexT26 + generated |
| `STORM_CYCLONE` | HumAID hurricanes/cyclones (largest share) + CrisisLexT26 typhoons + generated |
| `EARTHQUAKE_COLLAPSE` | HumAID + CrisisLexT26 (incl. Savar building collapse) + generated |
| `TRANSPORT_ACCIDENT` | CrisisLexT26 train/helicopter crashes + **mostly generated** (road) |
| `MEDICAL` | **Generated only** |
| `VIOLENCE_CRIME` | CrisisLexT26 bombing/shooting (small) + **mostly generated** |
| `NON_EMERGENCY` | Kaggle Disaster Tweets (`target == 0`) + CrisisLexT26 "Not related" + generated |

> **Known limitation to state openly:** public datasets cover disasters well but cover everyday
> emergencies (accidents, medical, crime) poorly, so those classes depend on generated data. This
> becomes "future work: train on real anonymised 112 call transcripts."

**Mapping HumAID to our types (watch out):**
- HumAID's labels describe **humanitarian need** (injured/dead, infrastructure damage, urgent requests, sympathy…),
  **not incident type**. Take the incident type from the **event name**, e.g. `kerala_floods_2018` → `FLOOD`.
- **Hurricanes/cyclones** are the biggest share of HumAID, so they get their own class, `STORM_CYCLONE`.
  Cap its size or use class weights so it doesn't dominate.
- Drop `sympathy_and_support` and `not_humanitarian` tweets. "Praying for Kerala" is neither an emergency report nor a
  "non-emergency" example.
- Clean URLs, @mentions, `RT` and `#` symbols.

**Hidden trap: the model learning style instead of meaning.** If FLOOD/FIRE come mostly from tweets and
TRANSPORT_ACCIDENT/MEDICAL mostly from call-style generated text, the model can learn "tweet style → flood". Scores
look high but the model is useless. **Fix:** every class gets plenty of call-style generated examples, and
we report scores **per source**.

### 6.3 Severity

- Scale **1.0–5.0** (1 = minor, 5 = life-threatening, many people).
- Comes only from generated data. Real tweets have no severity, so **the severity loss is skipped
  (masked) for those rows** during training.
- Bucketed for display: LOW (<2), MEDIUM (2–3), HIGH (3–4), CRITICAL (≥4).

### 6.4 Synthetic generation guidelines (ML1)

- About **3,000 reports**, balanced across classes. **Needs an API key** (free tiers of Gemini/Groq are
  enough); generating through a chat window is far too slow.
- **Don't ask for "3000 reports" in one go**: you'll get the same 50 reworded. Build a **grid** of
  type × severity × style × city × detail level (location given or missing, numbers given or not),
  and fill those values into the prompt, 10–20 reports per call.
- **Give the LLM a severity rubric** so scores are consistent:
  1 = minor, nobody hurt · 2 = minor injuries · 3 = serious injury or property at risk ·
  4 = life-threatening or several people hurt · 5 = deaths/mass casualties, people trapped, hazard spreading.
- Vary the style: panicked caller, calm bystander, SMS shorthand, typos, missing location, and vague
  reports ("something bad happened near the station").
- Vary severity deliberately inside each class (a minor kitchen fire vs. a building fire with people
  trapped).
- Ask the LLM to output the **report + its labels together as JSON**, with entity values copied
  **exactly** from the report text.
- Use Indian place names and contexts so the demo feels local.
- Remove near-duplicates before splitting.

### 6.5 Train / validation / test split

- **70 / 15 / 15**, stratified by class.
- Remove near-duplicates *across* splits (a retweet in train and in test inflates the scores).
- **Never train on the gold test set (below).**

### 6.6 Gold test set (the credibility piece)

Judges will ask "is your test data just synthetic?" Our answer combines:

| Method | What | Effort |
|---|---|---|
| **A. Official human-labelled test splits** | HumAID's own test split for type classification on real text | None |
| **B. LLM labels, second pass, human audit** | Claude labels real reports and re-reviews them; a person audits a random sample of 30 and we report the agreement rate (this is what we did) | ~30 min each for 2 people, done while models train |
| **C. Test on a different dataset** *(if time)* | Train on HumAID, test on CrisisLexT26 (different disasters) to show generalisation | Low |
| **D. Different generator for the test set** *(alternative)* | Generate synthetic test reports with a *different* LLM/prompt, so the model can't just learn one model's phrasing | Low |

**Plan: A + B, with C if time allows.** Always report gold-set and synthetic-set scores **separately**.

**ML1 hands over:** `train.csv`, `val.csv`, `test_synth.csv`, `gold.csv` with columns
`text, incident_type, severity (blank allowed), fields_json, source`.

### 6.7 Voice data

We **don't train Whisper**, so we need audio only for the **demo**, **testing on speech**, and one
**training trick**.

| Source | How | Use it for |
|---|---|---|
| **Teammate recordings** | Each person reads 10–15 call-style reports on a phone, some calm, some rushed, some with background noise | The most realistic voice test set + demo clips |
| **Text-to-speech** | Run 200–300 generated reports through `edge-tts` (includes Indian-English voices), mix in noise (sirens, traffic, crowds) from ESC-50 / MUSAN | A larger, reproducible voice test set |
| Public call recordings | No Indian 112 dataset exists; US 911 recordings are sensitive and a different context | **Skip**, mention as future work |

Target: about **50 human recordings + about 300 TTS clips**. Recordings stay out of git (`data/audio/` is ignored),
and only record teammates with their consent.

**The real problem: transcripts aren't clean text.** Whisper output has no punctuation, inconsistent casing, and
misheard words ("FC road" becomes "FC rode"). **Fix:** run about 300 generated reports through TTS and then Whisper,
and add those transcripts to the training data with their original labels (~15 min on Kaggle). Cheaper
alternative: randomly lowercase, strip punctuation and add typos to 20% of training text.

**Voice metrics:** word error rate (`jiwer`), type F1 typed vs. spoken, severity RMSE typed vs. spoken, and
audio-to-alert latency.

---

## 7. Models and training

### Model 0: Baseline (TF-IDF + Logistic Regression)
- Trains in seconds. It exists **only so we can show the transformer is better.**

### Model 1: DistilBERT multi-task
- `distilbert-base-uncased` with two heads on the `[CLS]` output:
  - Classification head → incident type (cross-entropy loss)
  - Regression head → severity (MSE loss, masked where there is no label)
- **Total loss** = `CE(type) + λ · MSE(severity)` (start with λ = 1)
- Class weights for rare classes.
- 3–5 epochs, early stopping on validation macro-F1, fixed random seed.
- Settings to start with: learning rate 2e-5, batch 32, max 128 tokens, fp16 is fine. Scale severity to 0–1 for
  training and back to 1–5 for reporting.
- Masked severity loss: rows with no severity contribute 0; divide by `max(count, 1)` so an all-unlabelled batch
  doesn't divide by zero.
- **Heatmap: use attention rollout, not the raw last layer.** The raw `[CLS]` attention of the last layer mostly
  lands on `[SEP]` and punctuation. Attention rollout (Abnar & Zuidema, 2020) combines all layers. Then drop
  special tokens, merge word pieces into words, and rescale. About 30 lines.
- **ML2 hands over:** `classify(text) -> {type, probs, severity, attention: [(word, score)]}`

### Model 2: Flan-T5-base fine-tuned
- Input: `"extract alert: <report text>"`
- **Output is a flat line format, not JSON**, because **T5's vocabulary has no `{` or `}`**:
  `location: FC road petrol pump | people: 3 | injuries: burns | hazards: fuel; smoke | summary: ...`
  A small Python parser turns it into JSON.
- **Train in fp32.** T5 often gives NaN losses in fp16. 3k examples × 5 epochs is still only ~30–45 min on a T4.
- Max input 256 tokens, max output 160, beam search with 4 beams at inference.
- Trained on the generated (B) data, which has all fields labelled.
- Outputs are validated with **Pydantic** (`people` → int, missing fields → null). If parsing fails: retry once,
  then fall back to rules.
- **Field metrics:** exact match for `people`; set-based P/R/F1 for `injuries`/`hazards`; token-overlap F1 for
  `location`; ROUGE-L for `summary`; % of outputs that parse.
- **ML3 hands over:** `extract(text) -> {location, people_affected, injuries, hazards, summary}`

### Whisper (speech → text), owned by BE2
- Not trained by us; it sits **in front of** the two models. They only ever see text.
- **`faster-whisper`** with `small.en` in int8: ~1–3 s per 15-second clip on a laptop CPU.
  The English-only model is more accurate than the multilingual one of the same size.
- `vad_filter=True`, since **Whisper invents text on silence or noise**.
- Flag low-confidence transcripts using `avg_logprob` and `no_speech_prob`.
- **Load the model once at server start**, never per request.
- Flow: `/transcribe` → transcript shown in an **editable box** (dispatcher fixes misheard names) → `/analyze`,
  the same route typed reports use. Keeping the two steps separate is what makes the human check possible and
  lets us measure what speech recognition costs.
- Used in 3 places: live in the app, once for data prep (TTS → Whisper transcripts), and in evaluation.

### Supporting pieces
- **geopy + Nominatim**: location text to lat/lon. Cache the results, and **hard-code fallback
  coordinates for demo locations** so a network failure can't break the demo.
- **Type → responders**: a simple lookup table (FIRE → fire brigade + ambulance, and so on).

### Compute
- Kaggle T4 GPU, 30 hrs free **per account**. ML2 and ML3 train in parallel on separate accounts.
- Expected: DistilBERT about 10–20 min per run, Flan-T5-base about 30–60 min per run.
- Inference runs on a laptop CPU in about 1–2 s per report.

---

## 8. Evaluation sheet → how we score full marks (50)

| Criterion | Marks | How we earn it |
|---|---|---|
| Problem Understanding & Relevance | 5 | Real user (dispatcher), real pain (triage under load), cited stats, clear scope |
| Innovation & Uniqueness | 5 | Full structured alert + attention explainability + voice + live queue/map (§4) |
| Technical Implementation | 10 | Two fine-tuned transformers, multi-task learning, baseline comparison, clean repo |
| Functionality / Working Prototype | 10 | Working end-to-end Streamlit app, text and voice in, alert + map out, handles bad input |
| SDG Implementation | 5 | Specific SDG *targets* mapped to features, shown in the app and on slides (§9) |
| Communication Skills | 5 | Everyone presents the part they built; rehearsed Q&A (§13) |
| Metrics (Precision, Recall, MSE, RMSE) | 5 | Full metrics table below, on the gold set, compared against the baseline |
| Presentation & Demo | 5 | Tight deck, live demo + backup video, one "wow" moment |

### Metrics we will report

| Task | Metrics |
|---|---|
| Incident type | **Precision, Recall, F1** (per class + macro), confusion matrix |
| Severity | **MSE, RMSE**, MAE, accuracy after bucketing |
| Field extraction (Flan-T5) | Precision / Recall / F1 for each field, JSON validity % |
| Summary | ROUGE-L |
| System | Latency per report |

**Emphasise recall on critical incidents**: missing a real emergency is worse than a false alarm.
Also show **2 failure examples** and why they failed. Honesty scores well with judges.

---

## 9. SDG mapping

| SDG target | How ResQPulse supports it |
|---|---|
| **3.6**: halve deaths and injuries from road traffic accidents | Faster triage of accident reports means faster ambulance dispatch |
| **3.d**: early warning and management of health risks | Severity-ranked medical alerts |
| **11.5**: reduce deaths and people affected by disasters | Structured, prioritised alerts during disaster report surges |
| **13.1**: strengthen resilience to climate-related hazards | Processes flood and cyclone crisis reports at scale |
| **16.1**: reduce all forms of violence | Faster police and ambulance dispatch for violence/crime reports |
| **16.6**: effective, accountable, transparent institutions | Explainable decisions + an audit log (JSON) of every alert |

Show these as badges in the app (for example, a TRANSPORT_ACCIDENT alert shows the SDG 3.6 badge).

---

## 10. The Streamlit app (screens)

1. **Report input**: text box, mic (`st.audio_input`) / audio upload, sample buttons (one per class), and an
   **editable transcript box** with a "please verify" warning for low-confidence speech
2. **Alert card**: type, severity bar, extracted fields, responders, summary, SDG badge, JSON download
3. **Explain tab**: attention heatmap over the report's words
4. **Dispatcher dashboard**: live priority queue (sorted by severity) and a map with pins coloured by severity
5. **Metrics page**: confusion matrix and scores table, live in the app

**Edge cases that must not crash the app:** empty input, non-emergency text ("is the mall open
today?"), very long text, unknown location, bad audio.

---

## 11. Team roles

| Person | Role | Owns |
|---|---|---|
| **ML1** | Data lead | Synthetic generation, mapping public data to our types, splits, gold set, evaluation report |
| **ML2** | Encoder lead | Baseline, DistilBERT multi-task training, attention heatmap extraction |
| **ML3** | Generator lead | Flan-T5 fine-tuning, JSON validation, fallback NER |
| **BE1** | API lead | FastAPI, model loading and inference pipeline, error handling |
| **BE2** | Services lead | Whisper, geocoding, alert store and priority queue, duplicate merge (stretch); helps verify the gold set |
| **FE** | UI lead | Streamlit screens, map, heatmap view, metrics page; owns the slide design |

**[DECIDE]** Adjust to individual strengths in the first hour.

---

## 12. 12-hour timeline

| Hours | What happens | Exit criterion |
|---|---|---|
| **0–1** | **Everyone:** lock incident types + JSON format, agree the API contract (request/response JSON), create repo + Kaggle notebooks, ML1 finalises the generation prompt | Incident types and API contract written in the repo |
| **1–3** | ML1 generates data · ML2 baseline + training code · ML3 Flan-T5 code on a seed set · BE1 FastAPI with **fake** responses · BE2 Whisper + geocoding · FE builds screens against the fake API | Frontend shows a (fake) alert end to end |
| **3–6** | Real training runs · backend plugs in real models · FE builds map + alert card | **Hour 6 milestone: full app works with real models** |
| **6–9** | Attention heatmap · gold-set evaluation + confusion matrix · JSON validation/fallback · BE2 verifies the gold set · metrics page | All metrics computed on the gold set |
| **9–10** | Bug fixes, polish, stretch features only if everything works | **Code freeze at hour 10** |
| **10–12** | Slides, record backup demo video, README, **two timed rehearsals** | Ready to present |

**Golden rule: a rough working version first, then improve.** The prototype is worth 10 marks. A great
model with a broken app scores badly.

---

## 13. Pitch outline and judge Q&A

### Deck (8–10 slides)
1. Hook: a real emergency where delay mattered, plus a stat
2. Problem and user: unstructured reports overwhelm dispatchers
3. Our solution: one architecture diagram
4. How attention works (one visual) and why a transformer fits
5. Data: sources, incident types, gold test set
6. Results: baseline vs. transformer, P/R/F1, MSE/RMSE, confusion matrix
7. **Live demo** (voice report → alert → heatmap → map)
8. SDG impact
9. Limitations and future work
10. Team

### Questions to rehearse

| Question | Our answer |
|---|---|
| Why not just use ChatGPT? | Cost per call, latency, needs internet, privacy of emergency data. Our small models run offline and free, and we measured their accuracy. |
| Is your test data synthetic? | No. We report on real tweets (HumAID test split, held-out CrisisLex crises and a 144-row gold set) separately from synthetic. The gold labels are Claude's, re-reviewed in a second pass and audited by a person on a 30-row sample ([x]% agreement). |
| Does attention really explain the decision? | It shows what the model focused on. It's an indicator, not a proof, and the dispatcher always makes the final decision. |
| What if the model is wrong? | Human-in-the-loop: the dispatcher confirms or edits every alert. Corrections can be logged for retraining. |
| Why regression for severity? | Severity is ordered (3 is between 2 and 4). Regression keeps that order, and we also report bucketed accuracy. |
| Why two models? | Each is best at its job (understanding vs. generating), they train in parallel, and each is a fallback for the other. |
| Real-world deployment? | Integrate with 112 ERSS, train on real anonymised transcripts, add Hindi/Marathi. |

---

## 14. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Synthetic data too repetitive, so the model overfits | Grid-based prompts, deduplicate, test on real gold data |
| Model learns writing style instead of meaning | Call-style examples for every class; report scores per source |
| Speech transcripts confuse the models | TTS → Whisper transcripts in training data; editable transcript in the app |
| Live microphone fails at the venue | Play a pre-recorded noisy clip as the main voice demo |
| Flan-T5 outputs broken JSON | Pydantic validation, retry, rule-based fallback |
| Training takes too long | Start with small subsets; DistilBERT is quick; parallel Kaggle accounts |
| Geocoding API fails during the demo | Cache + hard-coded demo coordinates |
| Integration breaks late | API contract fixed in hour 1; fake API from hour 1; code freeze at hour 10 |
| Live demo fails on stage | Pre-recorded backup video |

---

## 15. Open decisions for hour 0

- [x] Final incident types: 8 classes, schema v1 (§6.2, SCHEMA.md)
- [x] Synthetic data generated with Claude (needs an Anthropic API key; model choice is a budget call, see SCHEMA.md §3.4)
- [ ] Is preparation before the event allowed (downloading datasets, caching models on Kaggle, generating data)?
  It would save 2–3 hours.
- [ ] Teammates' consent to record voice clips
- [ ] Role assignments (§11)
- [ ] Which stretch features (duplicate merge?) we attempt if ahead of schedule

---

## 16. Project status (kept current)

Updated with every merged change. The full history is in [UPDATE.md](UPDATE.md).

| Part | Owner | Status | Notes |
|---|---|---|---|
| Repo, docs, schema v1 | – | ✅ Done | README, this brief, [SCHEMA.md](SCHEMA.md), [DATASETS.md](DATASETS.md) |
| Datasets downloaded + mapped | ML1 | ✅ Done (v0) | 37k rows in `data/processed/public_*.csv`; no MEDICAL, few VIOLENCE_CRIME rows yet |
| Synthetic reports (Claude) | ML1 | ✅ v2 done (710) | All 8 types, 67 to 134 each; test_synth is 107 rows |
| Gold test set | ML1 | ✅ 144 rows (Claude labels + second pass); 30-row human audit pending | See GOLD_REVIEW.md; 16% of event-mapped types were wrong |
| Baseline (TF-IDF + LR) | ML2 | ⏳ Not started | |
| DistilBERT classifier + attention | ML2 | ⏳ Not started | |
| Flan-T5 generator + fallback | ML3 | ⏳ Not started | |
| Whisper ASR | BE2 | ⏳ Not started | |
| FastAPI backend | BE1 | ⏳ Not started | |
| Streamlit dashboard | FE | ⏳ Not started | |
| Evaluation + metrics.json | ML1 | 🔶 Script built and tested on fake predictions; waiting for real CSVs | `scripts/evaluate.py`, formats in SCHEMA §8.1 |
| Slides + backup video | FE + all | ⏳ Not started | |

**Changes from the original plan** (record every change here, because judges like to hear *why* a plan changed):

| Date | Change | Why |
|---|---|---|
| 2026-10-16 | Added `STORM_CYCLONE` class | Hurricanes/cyclones are the largest share of HumAID; dropping them wasted real data |
| 2026-10-16 | `ROAD_ACCIDENT` → `TRANSPORT_ACCIDENT` | CrisisLexT26 has real train and helicopter crashes that fit only a broader class |
| 2026-10-16 | Claude chosen for synthetic data | Structured outputs guarantee valid labelled JSON for every report |
| 2026-10-16 | CrisisLexT26 split by crisis, not held out entirely | It holds the only real transport-accident and violence examples; 6 crises stay unseen as a generalisation test |
| 2026-10-16 | Speech-transcript augmentation cut; typo/lowercase noise instead | Only about 8 hours between starting and presenting |
| 2026-10-16 | Synthetic reports written directly by Claude in a Claude Code session, not through the API | No API key available; chat-session writing with a validator gives the same labelled data |
| 2026-10-16 | Public training rows capped at 1,200 per type; synthetic train rows repeated 4x | Keeps the call-style reports from being drowned out by 7,500 real tweets |

---

## 17. Presentation reading guide

**Read this on the day.** It follows the deck (§13) slide by slide. Each block says who speaks, what to say,
and which marks it earns. Anything in `[brackets]` is filled in from the final results (`reports/metrics.json`)
before the presentation. **Update this section whenever something we built changes the story.**

Target time: about 7 minutes of talk + 3 minutes of demo, then questions.

### Slide 1: Hook (≈30 s) · *Problem Understanding*
**Speaker:** [name]
> "[Cited statistic about emergency response delay or call volume.] When a disaster hits, control rooms get
> flooded with messages like this one: *'bhai there's a huge fire near the petrol pump on FC road, 2-3 people
> stuck inside...'*. Someone has to read it, work out what happened, how bad it is and where, and send the
> right help. Every minute spent doing that by hand is a minute lost."

### Slide 2: Problem and user (≈45 s) · *Problem Understanding*
**Speaker:** [name]
- Our user is the **112 dispatcher**. Reports arrive as unstructured text and calls, and during disasters
  they arrive in floods, many of them duplicates.
- Manual triage is slow, varies between operators, and leaves no machine-readable record.
- **We assist the dispatcher. We don't replace them**: every alert is confirmed by a human.

### Slide 3: Our solution (≈45 s) · *Innovation*
**Speaker:** [name]
> "ResQPulse turns a messy report, typed or spoken, into a structured, prioritised, explainable alert in about
> [latency] seconds."
- Point to the architecture: **Whisper hears it, DistilBERT understands it, Flan-T5 writes it up.**
- Our differentiators: a full alert, not just a label; attention-based explanations; a continuous severity
  score; voice input; a live priority queue and map; small models that run offline. [Add duplicate merging if built.]

### Slide 4: How attention works (≈45 s) · *Technical Implementation*
**Speaker:** [ML2]
- Every word looks at every other word and decides how much it matters (Q, K, V → softmax weights).
- We combine attention across all layers (**attention rollout**) to show which words drove the decision.
- Be honest: *"Attention shows what the model focused on. It's an indicator, not proof, which is why a human confirms every alert."*

### Slide 5: Data (≈45 s) · *Technical Implementation*
**Speaker:** [ML1]
- Real crisis posts: HumAID ([n] tweets, 13 disasters), CrisisLexT26 ([n] tweets, 26 crises), and Kaggle Disaster Tweets as negatives.
- [n] call-style reports generated with Claude, with every field labelled, covering everyday emergencies that no
  public dataset has.
- **Gold test set:** 144 real reports we never trained on, labelled by Claude with a second review pass and a 30-row human audit ([x]% agreement). Say clearly that it is Claude-labelled, not hand-labelled.
- 8 incident types; a severity rubric from 1 to 5.

### Slide 6: Results (≈60 s) · *Metrics*
**Speaker:** [ML2 / ML3]
| | Baseline | Ours |
|---|---|---|
| Incident type, macro F1 (gold) | [x] | [x] |
| Precision / Recall (gold) | [x] / [x] | [x] / [x] |
| Severity MSE / RMSE | – | [x] / [x] |
| Field extraction F1 | – | [x] |
| Voice: typed vs. spoken F1 | – | [x] vs. [x] (WER [x]%) |

- Point out **recall on critical incidents**: missing a real emergency costs more than a false alarm.
- Show the confusion matrix and **one failure case and why it failed**.

### Slide 7: Live demo (≈3 min) · *Functionality / Presentation & Demo*
**Driver:** [FE] · **Narrator:** [BE1]
1. Type a report → alert card: type, severity, location on the map, responders, summary.
2. Open the **Explain** tab → the attention heatmap. Say which words lit up and why that makes sense.
3. Play the **pre-recorded noisy voice clip** → the transcript appears, gets corrected if needed → alert.
4. Show the **priority queue**: the critical alert jumps to the top.
5. Type a non-emergency ("is the mall open today?") → *"No emergency detected"*.
6. If anything breaks, switch to the backup video without commentary.

### Slide 8: SDG impact (≈30 s) · *SDG Implementation*
**Speaker:** [name]
- 3.6 (road deaths) · 3.d (health risks) · 11.5 (disaster deaths) · 13.1 (climate resilience) · 16.1 (violence) · 16.6 (accountable institutions).
- Point out that the **SDG badge appears on each alert in the app**, not just on this slide.

### Slide 9: Limitations and future work (≈30 s) · *Problem Understanding / Communication*
**Speaker:** [name]
- Everyday emergencies rely on generated data → future work: real anonymised 112 transcripts.
- English only → Hindi, Marathi and Hinglish next (MuRIL, multilingual Whisper).
- Learning from dispatcher corrections (they are already logged); integration with 112 ERSS.

### Slide 10: Team (≈15 s)
Each person says their name and the one part they built.

### Before presenting: checklist
- [ ] Every `[bracket]` above is filled from `reports/metrics.json`
- [ ] Statistic on slide 1 has a cited source
- [ ] Demo laptop has the models, the cached geocodes and the voice clip available offline
- [ ] Backup video is on the laptop and on a phone
- [ ] Each speaker has rehearsed their part and the Q&A in §13

---

## Glossary

| Term | Meaning |
|---|---|
| **Transformer** | Neural network architecture built on attention; the basis of BERT, GPT and T5 |
| **Attention** | Mechanism that weights how much each word should focus on every other word |
| **Fine-tuning** | Further training a pre-trained model on our specific task |
| **Multi-task learning** | One model learning several tasks at once (type + severity) with shared layers |
| **Precision** | Of the alerts we labelled X, how many really were X |
| **Recall** | Of all the real X incidents, how many we caught |
| **F1** | Combines precision and recall into one score (their harmonic mean) |
| **MSE / RMSE** | Average squared error of severity predictions / its square root (in severity units) |
| **NER** | Named Entity Recognition: finding locations, people and similar things in text |
| **Gold set** | Held-out real reports with type, severity and fields; labels checked in a second pass and a human audit |
| **Synthetic data** | Data generated by an LLM instead of collected from the real world |
