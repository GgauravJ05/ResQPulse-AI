# Speaking script: my part (tech stack, architecture, how it works, metrics, live demo)

About **6 to 7 minutes** in total. Plain sentences; **→** means point or click.
Slides: `docs/hackathon/ResQPulse_AI_GenHack.pptx` (slide 03 tech stack and architecture, slide 05 results).
App: **http://localhost:8501** (check the top-right pill says **LIVE · REAL MODELS**).

| Part | Time | Show |
|---|---|---|
| 1. Tech stack | ~45 s | Slide 03, left |
| 2. System architecture | ~60 s | Slide 03, right (or `docs/architecture_diagram.png`) |
| 3. How it works (one report's journey) | ~60 s | Same diagram |
| 4. Model metrics | ~90 s | Slide 05, then the Model Metrics screen |
| 5. Live demo | ~3 min | The app |

---

## 1. Tech stack (~45 s) → slide 03, left card

> "Here's what we built it with. Everything is open source and runs on one laptop."

| Layer | Say |
|---|---|
| **Frontend** | "The dashboard is **Streamlit**, a Python web framework, with a **Folium** map for incident locations." |
| **Backend** | "The backend is **FastAPI** in Python. It receives each report, runs the models and returns the alert as JSON." |
| **AI models** | "Three Transformer models from **Hugging Face**, run with **PyTorch**: **DistilBERT** to classify the incident and score severity, **Flan-T5** to extract the details, and **Whisper** to turn voice into text. A small model called **MiniLM** detects duplicate reports." |
| **Training** | "We fine-tuned DistilBERT and Flan-T5 on free **Kaggle T4 GPUs**. For comparison, a **scikit-learn** baseline: TF-IDF with logistic regression." |
| **Storage** | "Alerts are kept in memory and logged to files, including every dispatcher correction." |
| **Maps** | "Locations go through an offline list of Indian cities first, then OpenStreetMap if needed." |

> "No paid APIs and no cloud. That matters, because during a disaster the internet may be down."

---

## 2. System architecture (~60 s) → slide 03, right card (or the architecture diagram)

> "This is how the pieces connect." → follow the boxes left to right

1. → **Typed report / Voice call**
   > "A report comes in two ways: typed text, or a voice call. Voice first goes through **Whisper**, which turns speech into text. The dispatcher can correct the transcript."
2. → **DistilBERT** and **Flan-T5** (the two red boxes)
   > "The text goes to **two models at the same time**. **DistilBERT** decides *what* happened, which of 8 incident types, and *how bad*, a severity from 1 to 5. It also gives the attention scores for the explanation. **Flan-T5** writes the *details*: location, number of people, injuries, hazards and a one-line summary."
3. → **FastAPI**
   > "The **FastAPI backend** combines both into one alert. It finds the location on the map, suggests responders, tags the UN goals, checks for duplicates, and logs everything."
4. → **Streamlit dashboard**
   > "Finally the **dashboard** shows the alert card, the heatmap, the priority queue and the map, where the dispatcher confirms, dispatches or dismisses."

> "All of this, the boxes inside the frame, runs **offline on one laptop**."

---

## 3. How it works: one report's journey (~60 s)

> "Let me follow one real example through the system."

Report: *"Accident on the Mumbai-Pune expressway near Lonavala exit, a truck hit two cars, one man is not moving, there is a lot of blood and traffic is blocked."*

1. **DistilBERT** reads it and gives probabilities for the 8 types. → *Transport accident, 99.7%.* Its second output gives severity → *4.4 out of 5, Critical.*
2. **Attention** shows which words mattered → *accident, not moving, blood.*
3. **Flan-T5** writes one line:
   `location: Mumbai-Pune expressway near Lonavala exit | people: 1 | injuries: not moving; lot of blood | hazards: traffic blocked | summary: …`
   > "Flan-T5 can't write JSON directly, so it writes this simple line, and our code turns it into fields."
4. **Backend** adds the rest → map coordinates, responders (**ambulance, traffic police**), UN goal **SDG 3.6 road safety**, duplicate check.
5. **Dashboard** → the alert jumps to the **top of the queue** because it's critical.

> "Total time: about **3 seconds**, on a laptop. And a person always makes the final call."

**If they ask what each model outputs:**
- DistilBERT: incident type (8 classes) + severity (1–5) + attention weights. It does **not** produce JSON.
- Flan-T5: 5 fields (location, people, injuries, hazards, summary) as one text line.
- Our FastAPI code: combines everything and returns the **one final JSON alert**.

---

## 4. Model metrics (~90 s) → slide 05, then the Model Metrics screen

**Set it up first (10 s):**
> "We tested only on data the models **never saw**, and always against a **baseline**, a simple word-counting model, TF-IDF with logistic regression. The most important test is **144 real reports with human-checked labels**."

**Incident type** → the table:
> "On those 144 real reports, our model is right **75%** of the time against **59%** for the baseline. The combined quality score, macro F1, is **0.77 vs 0.56**. Precision, meaning 'when it says fire, is it really fire', goes from 0.61 to 0.76. Recall, meaning 'of all real fires, how many it caught', goes from 0.59 to 0.79."

**Safety** → the four tiles:
> "For an emergency system, these matter most. It catches **91% of real emergencies**; the baseline caught 71%. Of the **56 most severe reports**, it dismissed only **one**; the baseline dismissed **14**. Our honest weakness is **false alarms, 38%**: some ordinary posts that mention a disaster get flagged. We accept that, because a false alarm costs seconds, a missed emergency costs a life, and a human checks every alert."

**Severity** → severity table:
> "Severity is a number, so we measure how far off it is. On call-style reports, the error, **RMSE, is 0.75** on a 1-to-5 scale, and **87%** of the time it's within one point."

**Extraction** → Flan-T5 table:
> "Flan-T5 gives a readable answer **100%** of the time and finds the location about **80%** right on call-style reports."

**Confusion matrix** → bottom pictures:
> "The diagonal is correct answers. Look at **violent crime**: the baseline sent **15 of 17** crime reports to 'no emergency'. Ours got **15 of 17** right. Word-counting misses context; the Transformer understands it."

---

## 5. Live demo (~3 min) → the app

Before starting: one report already sent (models warm), queue reasonably clean.

1. **Report Input** → click **Transport Accident** → **Analyze Report**
   > "One click, and in about three seconds we have a structured alert."
2. Sidebar → **Alert Card**
   > "Type and ID at the top, severity on the right. The **severity ruler**: 4.4 of 5. On the right, the **evidence**: location with coordinates, people affected, model confidence, response time, and the **UN goal** this supports. Below, injuries, hazards and the responders to send."
3. Sidebar → **Attention Heatmap**
   > "These yellow words are what the model focused on: the darker, the more it mattered. It's an **indicator, not proof**, which is why a human confirms. Underneath, the probability for each incident type."
4. **Voice**: back to **Report Input** → upload `demo_assets/noisy_phone_report.wav` → **Transcribe Audio Now**
   > "This is a noisy phone-quality call. Whisper transcribes it, and it heard 'Lonavala' as 'La Navalan'." → fix the word in the box → **Analyze Report**
   > "The dispatcher can always correct the transcript before it becomes an alert."
5. **Duplicate**: analyse the same incident reworded, e.g. *"Truck crashed into two cars at Lonavala exit, one man bleeding, road blocked"*
   > "A second caller reporting the same accident: it's flagged as a **possible duplicate**, so ten calls about one incident don't become ten alerts."
6. Sidebar → **Dispatcher Dashboard**
   > "The queue, **most severe first**, and the map with each incident coloured by severity." → click **Dispatch** on the top alert
   > "The dispatcher confirms, dispatches or dismisses, and every action is logged."
7. **Non-emergency**: Report Input → type *"is the mall open today?"* → Analyze
   > "And a normal question is recognised as **no emergency**, so it never clutters the queue."
8. Sidebar → **Model Metrics** (only if time): "and these are the numbers I just explained."

**If something breaks:** stay calm. "The first request after a restart takes a few seconds," or switch to the slides and narrate. Restart commands are in `docs/hackathon/EVALUATION_PREP.md`, section 11.

---

## Likely questions on my part

**"Why FastAPI and Streamlit?"**
> "Both are Python, so the models, backend and dashboard share one language. FastAPI is fast and gives automatic validation and JSON; Streamlit let us build a working dashboard quickly."

**"Why DistilBERT and not BERT?"**
> "It's about 40% smaller and 60% faster while keeping most of BERT's accuracy, so it runs on a laptop CPU."

**"Why three separate models and not one big LLM?"**
> "Small, specialised models run offline, fast and cheaply, and keep emergency data private. One big LLM would need the cloud or a large GPU."

**"Does it work without internet?"**
> "Yes, all the AI runs offline. We tested it with the internet blocked. Only the map background tiles and looking up brand-new place names need a connection."

**"How fast is it?"**
> "About 2 to 4 seconds per report on a laptop CPU, after a one-time warm-up of about 6 seconds."

**"What's in the JSON alert?"**
> "Alert ID, status, incident type and confidence, severity and its label, location with coordinates, people affected, injuries, hazards, summary, responders, SDG targets, duplicate flag and the attention words."

**"How do you know the baseline comparison is fair?"**
> "Both models were trained on the same training data and scored by the same script on exactly the same test reports."

**"What's macro F1 / RMSE?"**
> "Macro F1 averages the precision–recall balance across all incident types equally, so rare ones count. RMSE is the typical size of the severity error, in severity points."

---

## Numbers to remember

| Number | Meaning |
|---|---|
| 8 / 1–5 | Incident types / severity scale |
| 144 | Real reports with checked labels (gold set) |
| 75% vs 59% | Accuracy, ours vs baseline (gold) |
| 0.77 vs 0.56 | Macro F1 (gold) |
| 91% vs 71% | Emergencies caught |
| 1 vs 14 (of 56) | Severe reports dismissed |
| 38% | False alarms (our weakness) |
| 0.75 / 87% | Severity RMSE / within one point (call-style) |
| 100% / ~80% | Flan-T5 parse rate / location F1 (call-style) |
| 15 vs 2 (of 17) | Violent crime correct, ours vs baseline |
| ~3 s | Per report, laptop, offline |

Sources: `reports/results.md`, `reports/metrics.json`. More: `docs/hackathon/EVALUATION_PREP.md`.
