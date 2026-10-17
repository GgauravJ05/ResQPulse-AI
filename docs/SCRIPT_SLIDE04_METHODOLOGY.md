# Speaking script: Slide 04, Methodology and Measurable Impact

Deck: `docs/ResQPulse_AI_GenHack.pptx`, slide 04 of 07. About **90 seconds**.
Speak in plain sentences. **→** marks where to point on the slide.

---

## Opening (5 s)

> "This slide shows **how we built it** on the left, and **what it achieves** on the right."

---

## Left side: Methodology

### 1. Data → point at step 1

> "First, data. No public dataset of real emergency calls exists, so we combined two sources.
> **Real disaster tweets** from three public datasets, HumAID, CrisisLexT26 and Kaggle, about 37,000 after cleaning, teach the model what real disasters look like.
> Then **710 call-style reports that we generated**, written the way people actually talk on a 112 call.
> Every report follows one fixed format: **8 incident types** and a **severity from 1 to 5**."

### 2. Train → step 2

> "Second, training. We fine-tuned **DistilBERT**, a small Transformer, with **two outputs**: one picks the incident type, the other gives the severity score.
> We also fine-tuned **Flan-T5** to write the details: location, people, injuries, hazards and a summary.
> And we built a simple **word-counting baseline**, TF-IDF with logistic regression, to prove the Transformer actually adds value."

### 3. Serve → step 3

> "Third, how it runs live. If it's a call, **Whisper** turns the voice into text.
> **DistilBERT** classifies it and shows which words it focused on, using attention.
> **Flan-T5** extracts the details, and if its answer is incomplete, it retries, then falls back to rules, so we always get an answer.
> Finally we **put it on the map**, suggest which responders to send, and **flag duplicate reports** of the same incident."

### 4. Evaluate → step 4

> "Fourth, testing, done honestly. One script scores everything on data the models **never saw**: 107 call-style reports, 7,755 real tweets, including **6 disasters the model never saw at all**, and **144 real reports whose labels a person checked**."

### 5. Human in the loop → step 5

> "And fifth, the AI **assists**, it doesn't decide. The dispatcher confirms, dispatches or dismisses every alert, and each correction is saved so the model can learn from it later."

---

## Right side: Measurable Impact

> "Now the results, all on real reports the model never saw, compared with the baseline."

| Point at | Say |
|---|---|
| **91%** | "It catches **91% of real emergencies**. The word-counting baseline caught 71%." |
| **98%** | "Most important: for the **most severe** reports, it keeps **98%**. It missed only **one out of 56**. The baseline missed 14 of them, a quarter." |
| **0.77** | "Overall quality, measured by macro F1, is **0.77 against 0.56**. That means it's balanced across all emergency types, not just the common ones." |
| **0.75** | "For severity, it's on average **0.75 points off on a 1-to-5 scale**, usually less than one point from the true urgency." |
| **~3 s** | "And it does all this in **about 3 seconds per report, on an ordinary laptop, fully offline**. No cloud needed, even if the internet goes down during a disaster." |

---

## Closing line (5 s)

> "So: honest data, a model that clearly beats the baseline where it matters most, severe emergencies, and a human always in control."

---

## 45-second version (if short on time)

> "We trained on real disaster tweets plus 710 call-style reports we generated, all labelled with 8 incident types and a severity from 1 to 5. DistilBERT classifies the type and severity; Flan-T5 writes the details; Whisper handles voice calls. We tested only on data the model never saw, including 144 human-checked real reports. It catches **91%** of emergencies against 71% for a baseline, keeps **98%** of the most severe ones, and runs in about **3 seconds on a laptop, offline**. A dispatcher confirms every alert."

---

## Likely follow-up questions on this slide

**"What does 'masked MSE' mean?"**
> "Severity is only labelled on our call-style reports, not on tweets. 'Masked' means the severity error is counted only on reports that have a severity label, so tweets don't confuse it."

**"What's attention rollout?"**
> "It combines the attention from all the model's layers to show which words most influenced the decision. That's the yellow heatmap in our app."

**"Why generate reports?"**
> "No public dataset of real emergency calls exists. Tweets are news-style, but real calls are short and panicked, so we generated that style. We still test on real reports so the numbers stay honest."

**"What's the people-count rule?"**
> "Flan-T5 sometimes writes '1 person' by default. We keep the number only if the text actually mentions people, like 'my mother' or '3 people', otherwise we leave it empty."

**"What is TF-IDF?"**
> "Term Frequency–Inverse Document Frequency. It scores each word by how often it appears in a report and how rare it is across all reports. Our baseline feeds those scores into logistic regression. It only counts words, so it shows what DistilBERT gains by understanding context."

**"Why is it called 'macro' F1?"**
> "We compute F1 for each incident type separately and then average, so rare types like violent crime count as much as common ones."

---

## Numbers to remember

| Number | Meaning |
|---|---|
| 37,000 | Real tweets after cleaning |
| 710 | Generated call-style reports |
| 8 / 1–5 | Incident types / severity scale |
| 107 · 7,755 · 144 | Call-style test · real tweet test · human-checked gold set |
| 6 | Disasters held out completely |
| 91% vs 71% | Emergencies caught, ours vs baseline |
| 98% vs 75% | Severe reports kept (missed 1 of 56; baseline missed 14) |
| 0.77 vs 0.56 | Macro F1 on real reports |
| 0.75 (MSE 0.57) | Severity RMSE on call-style reports |
| ~3 s | Per report, laptop, offline |

Source of every number: `reports/results.md`. More detail: `docs/EVALUATION_PREP.md`.
