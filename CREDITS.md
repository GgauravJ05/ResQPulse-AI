# Credits and third-party notices

ResQPulse AI stands on open datasets, open models and open-source software. This file credits each one and states
how it may be used. The project's own code is under the [MIT licence](LICENSE); see [Licensing](#licensing-summary)
for data.

---

## Datasets

| Dataset | Authors / host | How we used it | Terms |
|---|---|---|---|
| **HumAID** (events set 1) | Alam, Qazi, Imran, Ofli — Qatar Computing Research Institute (CrisisNLP). [crisisnlp.qcri.org/humaid_dataset](https://crisisnlp.qcri.org/humaid_dataset) | Real disaster tweets, mapped to our 8 incident types | [CrisisNLP terms of use](https://crisisnlp.qcri.org/terms-of-use.html): research use; share tweet IDs, not text |
| **CrisisLexT26** | Olteanu, Vieweg, Castillo. [crisislex.org](https://crisislex.org/data-collections.html) | Real crisis tweets from 26 events; 6 events held out as unseen-crisis tests | See the CrisisLex site |
| **Natural Language Processing with Disaster Tweets** | Kaggle (data originally from Figure Eight). [kaggle.com/competitions/nlp-getting-started](https://www.kaggle.com/competitions/nlp-getting-started) | Non-disaster tweets used as NON_EMERGENCY negatives | Kaggle competition rules |
| **ResQPulse synthetic reports** (ours) | This project; generated with Claude (Anthropic) and validated automatically | 710 call-style reports with full labels | CC BY 4.0 |

**Tweet text is not redistributed here.** This repository contains only tweet **IDs and our labels**
(`data/gold/gold_labels.csv`, and the public dataset release). Rebuild the text from the original datasets with the
scripts described in the README.

## Pre-trained models

| Model | Source | Use | Licence |
|---|---|---|---|
| `distilbert-base-uncased` | Sanh et al., Hugging Face | Fine-tuned incident-type + severity classifier | Apache-2.0 |
| `google/flan-t5-base` | Chung et al., Google | Fine-tuned alert-field generator | Apache-2.0 |
| Whisper `small.en` via `faster-whisper` (`Systran/faster-whisper-small.en`) | Radford et al., OpenAI; CTranslate2 conversion by SYSTRAN | Speech-to-text (not fine-tuned) | MIT |
| `sentence-transformers/all-MiniLM-L6-v2` | Reimers & Gurevych, sentence-transformers | Duplicate-report detection | Apache-2.0 |

## Software

| Library / tool | Use | Licence |
|---|---|---|
| PyTorch | Training and inference | BSD-3-Clause |
| Hugging Face Transformers | Model loading, fine-tuning, generation | Apache-2.0 |
| sentence-transformers | Sentence embeddings | Apache-2.0 |
| faster-whisper / CTranslate2 | Fast CPU speech recognition | MIT |
| scikit-learn | TF-IDF + logistic-regression baseline, metrics | BSD-3-Clause |
| pandas, NumPy | Data processing | BSD-3-Clause |
| rouge-score | Summary evaluation | Apache-2.0 |
| FastAPI, Uvicorn, Pydantic | Backend API | MIT / BSD-3-Clause / MIT |
| Streamlit | Dashboard | Apache-2.0 |
| Folium, Leaflet, streamlit-folium | Incident map | MIT / BSD-2-Clause / MIT |
| geopy | Geocoding client | MIT |
| rapidfuzz | Fuzzy place matching | MIT |
| pydub, FFmpeg | Audio decoding and resampling | MIT / LGPL |
| python-pptx | Building the hackathon deck | MIT |

## Services, fonts and map data

| Item | Use | Terms |
|---|---|---|
| OpenStreetMap / Nominatim | Geocoding places not in our offline gazetteer | Data © OpenStreetMap contributors, [ODbL](https://www.openstreetmap.org/copyright); [Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/) |
| Esri World Gray Canvas | Map background tiles | Tiles © Esri, per Esri's terms of use (attribution shown on the map) |
| Figtree, JetBrains Mono | Dashboard typefaces (served locally from `app/static/fonts/`) | SIL Open Font License 1.1 (licence files included) |
| Claude (Anthropic) | Generating the synthetic training reports; drafting the gold-set labels, which a person then audited | Used offline; never called at run time |
| Kaggle (T4 GPUs) | Model training | Kaggle terms |

## Research this project builds on

- Vaswani et al., *Attention Is All You Need*, NeurIPS 2017.
- Sanh, Debut, Chaumond, Wolf, *DistilBERT, a distilled version of BERT*, arXiv:1910.01108, 2019.
- Chung et al., *Scaling Instruction-Finetuned Language Models*, arXiv:2210.11416, 2022.
- Radford et al., *Robust Speech Recognition via Large-Scale Weak Supervision*, arXiv:2212.04356, 2022.
- Abnar & Zuidema, *Quantifying Attention Flow in Transformers*, ACL 2020 (attention rollout).
- Reimers & Gurevych, *Sentence-BERT*, EMNLP 2019.
- Alam, Qazi, Imran, Ofli, *HumAID: Human-Annotated Disaster Incidents Data from Twitter with Deep Learning Benchmarks*, ICWSM 2021.
- Olteanu, Vieweg, Castillo, *What to Expect When the Unexpected Happens: Social Media Communications Across Crises*, CSCW 2015.

---

## Licensing summary

| Part | Licence |
|---|---|
| Source code (everything outside `data/`, `docs/hackathon/` and `app/static/fonts/`) | [MIT](LICENSE) |
| Our synthetic reports (`data/raw/synthetic/`) and our labels (`data/gold/*_labels.csv`) | CC BY 4.0 |
| Fonts in `app/static/fonts/` | SIL OFL 1.1 (see the included licence files) |
| Third-party tweets | Not included; governed by each source dataset's terms |
| `docs/hackathon/` (event template and deck) | The template belongs to the event organisers; included for reference only |
