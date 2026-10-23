# Kaggle Data Card: resqpulse-data

Paste-ready text for every field of the Kaggle dataset page
[kaggle.com/datasets/ggauravj05/resqpulse-data](https://www.kaggle.com/datasets/ggauravj05/resqpulse-data).
It describes the **public release** built by `make public-dataset` (`dist/kaggle/`, 7 files). Counts were taken from
that build on 2026-10-23.

Usability: **4.71 / 10** before this card; **10.00 / 10** after version 5 and the card were published on 2026-10-23.

---

## 0. Release status (2026-10-23)

Version 4 on Kaggle was the internal build: `train.csv`, `val.csv`, `test_public.csv`, `test_synth.csv` and
`gold_inputs.csv` included the text of HumAID, CrisisLexT26 and Kaggle Disaster Tweets posts, which those sources'
terms do not allow redistributing.

| Step | Status |
|---|---|
| Version 5 = exactly the 7 files in `dist/kaggle/`; none of the old files carried over | ✅ Done (uploaded on the website) |
| Licence MIT → CC BY 4.0; update frequency → Never | ✅ Done |
| Title, subtitle, description, 5 tags, provenance, all 7 file and 40 column descriptions | ✅ Done; usability 10.00 |
| Public "current version" pointer | ⏳ About 30 minutes after version 5 was Ready, the public API and logged-out page still pointed at version 4 (old title and file names, no preview). Since version 4 is now blocked, the unversioned download returns 403 until the pointer moves. Recheck with `kaggle datasets files ggauravj05/resqpulse-data`; if it is still stuck after a day, upload an unchanged version 6 or contact Kaggle support |
| Versions 1–4 (with tweet text) | ✅ Settings → Version Access = Only Latest Version Accessible. Checked logged out: `/versions/4` is a 404 page, version 1–4 downloads return 404, old files return 403, version 5 downloads the 7 clean files |
| Teammates' notebooks (`vanshborkar30/classifier-notebook`, `rugvedas/flan-t5-train`) | ⚠️ They read the old file names; tell them to pin version 4 privately or rebuild from the sources |
| Starter notebook from the owner's account | Not done |
| Description and provenance link to the public repo ([GgauravJ05/ResQPulse-AI](https://github.com/GgauravJ05/ResQPulse-AI)) | ✅ Done |
| Authors and coverage in the Metadata panel | Not filled (they don't count toward usability); values in §5 |

### Publishing with one command

`make kaggle-release` rebuilds `dist/kaggle/`, writes `dataset-metadata.json` from this card
(`scripts/make_kaggle_metadata.py`: title, subtitle, description, licence, tags, and every file and column description),
uploads the files as a new version and pushes the metadata. One-time setup:

1. `pip install kaggle`
2. kaggle.com → Settings → API → **Create New Token**, and save the downloaded `kaggle.json` to `~/.kaggle/`
   (`chmod 600 ~/.kaggle/kaggle.json`).

Edit this card, not the JSON: the JSON is regenerated on every release. Set the cover image, expected update frequency
and provenance (§1, §5) on the website once, since Kaggle's metadata file has no fields for them.

---

## 1. Header fields

| Field | Value |
|---|---|
| **Title** | ResQPulse: Emergency Reports to Structured Alerts |
| **Subtitle** | 710 labelled emergency call-style reports + 18.8k crisis-tweet labels |
| **Licence** | CC BY 4.0 (Attribution 4.0 International) |
| **Expected update frequency** | Never (fixed release; new versions only for label fixes) |
| **Cover image** | `docs/architecture_diagram.png` cropped to 1200×630 (Kaggle's image size), or a clean shot of one alert card from the dashboard |
| **Tags** | NLP, Text Classification, Text-To-Text Generation, Natural Disasters, India |

Kaggle allows at most 5 tags, chosen from its picker.

---

## 2. About Dataset (description, Markdown)

```markdown
**Turn messy emergency reports into structured alerts.** This dataset trains and evaluates models that read an
emergency report (a call transcript, SMS or WhatsApp message) and output an incident type, a severity score from 1 to 5,
and the key facts a dispatcher needs: location, people affected, injuries and hazards.

No public dataset of emergency calls with these labels exists, so we built one for **ResQPulse AI**
([GitHub](https://github.com/GgauravJ05/ResQPulse-AI)), made at the GenHack v1.0 Gen AI hackathon.

### What's inside

| Part | Rows | Text included? |
|---|---|---|
| Call-style reports, fully labelled (type, severity, fields, style) | 710 | Yes |
| Flan-T5 text-to-text pairs built from those reports | 497 / 106 / 107 (train / val / test) | Yes |
| Real crisis tweets: our labels by tweet ID | 18,788 | **No**, see below |
| Gold test set: 144 real tweets with full labels | 144 | **No**, IDs + labels |
| Human audit of the gold set | 30 | **No**, IDs + labels |

### The call-style reports

710 short reports (5 to 60 words, mean 27) written in the voice of people calling or messaging India's 112 emergency
line: panicked callers, calm bystanders, elderly callers, children, SMS shorthand, WhatsApp messages, official
reports and deliberately vague reports. They cover 8 incident types, 67 to 134 reports each, set in Indian cities,
highways and villages.

They were written by Claude (Anthropic) from a fixed generation grid (type × severity × style × city × detail level)
and then checked automatically:
- every `location`, `injuries` and `hazards` value appears **word for word** in the report text, so extraction can be
  scored by exact match;
- severity is within 1 to 5 and follows one rubric (below);
- near-duplicates are removed.

Synthetic data is not real data: real calls are longer and messier and code-switch between languages. Use the
real-tweet parts to check that a model transfers.

### Labels

**`incident_type` (8 classes):** `FIRE`, `FLOOD`, `STORM_CYCLONE`, `EARTHQUAKE_COLLAPSE`, `TRANSPORT_ACCIDENT`,
`MEDICAL`, `VIOLENCE_CRIME`, `NON_EMERGENCY` (questions, complaints, figurative use like "my phone is on fire", pranks).

**`severity` (1.0 to 5.0, half points allowed):**

| Score | Meaning |
|---|---|
| 1 | Minor, nobody hurt, no spreading risk |
| 2 | Minor injuries, or contained property damage |
| 3 | One serious injury, or lives at real risk |
| 4 | Life-threatening, or several people hurt |
| 5 | Deaths, mass casualties, people trapped, or a hazard spreading fast |

`NON_EMERGENCY` is always 1.0.

**`fields_json`:** `location` (verbatim or null), `people_affected` (integer or null; upper bound of a range),
`injuries` and `hazards` (lists of verbatim phrases), `summary` (one neutral sentence of at most 30 words).

### Getting the tweet text

The tweets come from **HumAID**, **CrisisLexT26** and **Kaggle Disaster Tweets**. Their terms do not allow
redistributing tweet text, so this dataset ships IDs and our labels only. IDs look like `humaid-<tweet id>`,
`crisislex-<tweet id>` and `kaggle_disaster-<row id>`. Download the sources and run `make data` then `make gold` in the
GitHub repo to rebuild the full splits with text.

### Baseline results (from the repo)

Incident type, macro F1, TF-IDF + logistic regression → DistilBERT:

| Test set | Baseline | DistilBERT |
|---|---|---|
| Gold: 144 real reports, human-audited labels | 0.56 | **0.77** |
| Call-style: 107 synthetic test reports | 0.87 | **0.96** |
| Real tweets: 7,755, including 6 crises never seen in training | 0.63 | **0.75** |

### Suggested uses

- Incident-type classification and severity regression (one model with two heads works well)
- Structured extraction / text-to-text generation (`*_flan.csv`)
- Testing whether models trained on tweets transfer to call-style text, and the other way round
- Small-data LLM fine-tuning and evaluation

### Citation

Jadhav, G., Borkar, V., Patil, R., Patil, A., Talekar, A., Singh, A. *ResQPulse AI: turning emergency reports into structured, prioritised,
explainable alerts* (2026). https://github.com/GgauravJ05/ResQPulse-AI

If you rebuild the tweet text, also cite HumAID (Alam et al., ICWSM 2021) and CrisisLexT26 (Olteanu et al., CSCW 2015).
```

---

## 3. File descriptions

| File | Description (paste into the file's "Description" box) |
|---|---|
| `synthetic_reports.csv` | 710 call-style emergency reports with text and every label: incident type, severity 1–5, extracted fields (JSON), writing style and split (497 train, 106 val, 107 test). The main file. |
| `train_flan.csv` | 497 text-to-text pairs for training a seq2seq extractor (Flan-T5). Same reports as the train split of `synthetic_reports.csv`. |
| `val_flan.csv` | 106 text-to-text pairs for validation. Same reports as the val split of `synthetic_reports.csv`. |
| `test_flan.csv` | 107 text-to-text pairs for testing. Same reports as the test split of `synthetic_reports.csv`. |
| `tweet_labels.csv` | Our incident-type labels and splits for 18,788 real crisis tweets from HumAID, CrisisLexT26 and Kaggle Disaster Tweets. IDs only, no text: rebuild it from the sources. |
| `gold_labels.csv` | The 144-report gold test set: real held-out tweets with full labels (type, severity, fields), drafted by an LLM and re-reviewed. IDs only, no text. |
| `gold_audit_labels.csv` | Human audit of 30 gold rows: the auditor agreed with all 30 labels. |

---

## 4. Column descriptions

### `synthetic_reports.csv`

| Column | Description |
|---|---|
| `id` | Unique ID, `synthetic-NNNNNN`. |
| `text` | The report as a caller or messenger would write it. 5–60 words. |
| `incident_type` | One of 8 classes: FIRE, FLOOD, STORM_CYCLONE, EARTHQUAKE_COLLAPSE, TRANSPORT_ACCIDENT, MEDICAL, VIOLENCE_CRIME, NON_EMERGENCY. |
| `severity` | 1.0–5.0, half points allowed, by the rubric in the description. NON_EMERGENCY is always 1.0. |
| `fields_json` | JSON object: location (verbatim or null), people_affected (int or null), injuries (list, verbatim), hazards (list, verbatim), summary (≤ 30 words). |
| `data_source` | Always `synthetic`. |
| `split` | `train`, `val` or `test`. |
| `style` | Writing style: panicked_caller, calm_bystander, sms_shorthand, whatsapp_message, elderly_caller, child_caller, official_report, vague_report. |
| `event` | Empty for synthetic reports (kept so all files share one schema). |
| `humanitarian_label` | Empty for synthetic reports (kept so all files share one schema). |

### `train_flan.csv`, `val_flan.csv`, `test_flan.csv`

| Column | Description |
|---|---|
| `id` | Report ID; joins to `synthetic_reports.csv`. |
| `input` | Model input: `extract alert: ` followed by the report text. |
| `target` | Flat output: `location: … \| people: … \| injuries: … \| hazards: … \| summary: …`. List items are joined with `; `, empty values are `none`. Flat text because T5's vocabulary has no `{` or `}`. |

### `tweet_labels.csv`

| Column | Description |
|---|---|
| `id` | `<source>-<original id>`: `humaid-<tweet id>`, `crisislex-<tweet id>`, or `kaggle_disaster-<row id in the competition's train.csv>`. |
| `incident_type` | Our label, mapped from the source event and its humanitarian or informativeness label. No MEDICAL tweets exist. |
| `data_source` | `humaid`, `crisislex` or `kaggle_disaster`. |
| `split` | `train`, `val` or `test`. CrisisLexT26 is split by crisis: 6 whole crises are in test only. |
| `event` | Source event or crisis name (39 events), e.g. `hurricane_harvey_2017`. Empty for Kaggle rows. |
| `humanitarian_label` | Original label from HumAID or CrisisLexT26, kept for analysis. Empty for Kaggle rows. |

### `gold_labels.csv`

| Column | Description |
|---|---|
| `id` | Tweet ID, same format as `tweet_labels.csv`. Every gold row is in the test split. |
| `incident_type` | Reviewed label (7 classes present; no MEDICAL). |
| `severity` | 1.0–5.0 by the same rubric. |
| `fields_json` | Same structure as in `synthetic_reports.csv`. |
| `data_source` | `crisislex` (102), `humaid` (32) or `kaggle_disaster` (10). |
| `split` | Always `gold`. |
| `style` | Empty (real tweets). |
| `event` | Source event or crisis name. |
| `humanitarian_label` | Original source label, where there is one. |

### `gold_audit_labels.csv`

| Column | Description |
|---|---|
| `id` | Gold row ID. |
| `incident_type` | Label under audit. |
| `severity` | Severity under audit. |
| `agree` | 1 if the human auditor agreed with the label, 0 if not. |
| `correct_type` | The auditor's type when they disagreed; empty otherwise. |
| `notes` | Auditor's note. |

---

## 5. Metadata panel

| Field | Value |
|---|---|
| **Authors** | Gaurav Jadhav (data lead), Vansh Borkar, Rugveda Patil, Aaryan Patil, Atharva Talekar, Agastya Singh. Add teammates with Kaggle accounts as collaborators. |
| **Coverage: temporal** | Tweets 2012–2019 (source events); synthetic reports written October 2026 |
| **Coverage: spatial** | Synthetic: India. Tweets: worldwide (39 events) |
| **DOI** | Optional: "Generate DOI" on Kaggle, then add it to CITATION.cff |

**Provenance → Sources:**
```
- ResQPulse synthetic reports: written for this project by Claude (Anthropic), October 2026. CC BY 4.0.
- HumAID events set 1 (Alam et al., ICWSM 2021): https://crisisnlp.qcri.org/humaid_dataset (IDs and our labels only)
- CrisisLexT26 (Olteanu et al., CSCW 2015): https://crisislex.org/data-collections.html (IDs and our labels only)
- Kaggle "NLP with Disaster Tweets": https://www.kaggle.com/competitions/nlp-getting-started (row IDs and our labels only)
```

**Provenance → Collection methodology:**
```
Synthetic reports: generated from a grid of incident type x target severity x writing style x Indian city x detail
level, then validated: extracted fields must appear verbatim in the text, severity must be 1-5, reports must be
5-90 words, and near-duplicates (TF-IDF cosine > 0.9) are removed.

Tweets: cleaned (URLs, @mentions and RT removed) and mapped to our 8 types from each source's event and
humanitarian/informativeness labels. Kaggle tweets with target = 0 became NON_EMERGENCY hard negatives. Classes are
capped at 1,200 training rows each. CrisisLexT26 is split by crisis, so 6 crises appear only in test.

Gold set: 144 held-out test tweets labelled by an LLM, reviewed a second time (16% of the event-mapped types were
corrected), and spot-checked by a human on 30 rows (30 of 30 agreed).

Full pipeline and schema: https://github.com/GgauravJ05/ResQPulse-AI (docs/SCHEMA.md, docs/DATASETS.md).
```
