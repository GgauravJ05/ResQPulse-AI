# Datasets and Model Links

Everything the team needs to download, with what each file contains and how it maps to our labels.
All links were checked on 2026-10-16. Labels and enums referenced here are defined in [SCHEMA.md](SCHEMA.md).

> **Never commit downloaded data.** `data/raw/` and `data/processed/` are git-ignored. Upload raw data to a
> private Kaggle Dataset so every teammate's notebook can attach it.

---

## 1. Text datasets (A: real crisis posts)

### 1.1 HumAID (main real-text source)

| | |
|---|---|
| Page | https://crisisnlp.qcri.org/humaid_dataset |
| **Download: events set 1 (with tweet text)** | https://crisisnlp.qcri.org/data/humaid/HumAID_data_events_set1_47K.tar.gz (2.6 MB) |
| Event-type split (tweet IDs + labels only) | https://crisisnlp.qcri.org/data/humaid/HumAID_data_event_type.tar.gz |
| All combined (tweet IDs + labels only) | https://crisisnlp.qcri.org/data/humaid/HumAID_data_all_combined.tar.gz |
| Events set 2 (29k tweets, incl. Kerala floods 2018) | Requires a Google Form on the HumAID page. Optional. |
| Alternate host | https://doi.org/10.7910/DVN/A7NVF7 (Harvard Dataverse) |
| Paper | Alam et al., *HumAID: Human-Annotated Disaster Incidents Data from Twitter*, ICWSM 2021 |
| Terms | Released under Twitter/X terms (tweet ID, text, label). Use for research; don't republish the tweets. |

**Use set 1.** It is the only file with tweet text that downloads without a form. Each event folder has
`<event>_train.tsv`, `_dev.tsv` and `_test.tsv`, about 43k rows in total.

**Columns (tab-separated):** `tweet_id`, `tweet_text`, `class_label`

**Events in set 1 → our `incident_type`:**

| Event folder | `incident_type` |
|---|---|
| `canada_wildfires_2016`, `greece_wildfires_2018` | `FIRE` |
| `srilanka_floods_2017`, `maryland_floods_2018` | `FLOOD` |
| `hurricane_harvey_2017`, `hurricane_irma_2017`, `hurricane_maria_2017`, `hurricane_matthew_2016`, `cyclone_idai_2019` | `STORM_CYCLONE` |
| `ecuador_earthquake_2016`, `italy_earthquake_aug_2016`, `kaikoura_earthquake_2016`, `puebla_mexico_earthquake_2017` | `EARTHQUAKE_COLLAPSE` |

> Note: in the archive, `greece_wildfires_2018` and `maryland_floods_2018` are nested inside the
> `hurricane_matthew_2016/` folder. Map by **file name**, not by parent folder.

**`class_label` filter:** HumAID labels describe humanitarian need, not incident type. Keep only rows that read like
a report of the incident:

| Keep | Drop |
|---|---|
| `injured_or_dead_people`, `infrastructure_and_utility_damage`, `requests_or_urgent_needs`, `missing_or_found_people`, `displaced_people_and_evacuations`, `caution_and_advice` | `sympathy_and_support`, `not_humanitarian`, `dont_know_cant_judge`, `other_relevant_information`, `rescue_volunteering_or_donation_effort` |

Keep the original `class_label` in the `humanitarian_label` column (see SCHEMA.md §2). It's useful for analysis.

**Splits:** keep HumAID's own `test` files as part of the **gold set** (human-labelled, never trained on).

### 1.2 CrisisLexT26 (covers accidents, violence and explosions with real text)

| | |
|---|---|
| Page | https://crisislex.org/data-collections.html |
| **Download** | https://github.com/sajao/CrisisLex/blob/master/releases/CrisisLexT26-v1.0.zip?raw=true (4.6 MB) |
| Content | ~28k tweets, ~1,000 per crisis, 26 crises from 2012–2013 |
| Paper | Olteanu et al., *What to Expect When the Unexpected Happens*, CSCW 2015 |

**File:** `CrisisLexT26/<crisis>/<crisis>-tweets_labeled.csv`

**Columns (comma-separated, note the leading spaces):**
`Tweet ID`, ` Tweet Text`, ` Information Source`, ` Information Type`, ` Informativeness`

**Crisis → our `incident_type`:**

| Crisis folder | `incident_type` |
|---|---|
| `2012_Colorado_wildfires`, `2013_Australia_bushfire`, `2013_Brazil_nightclub_fire`, `2012_Venezuela_refinery`, `2013_West_Texas_explosion` | `FIRE` |
| `2012_Philipinnes_floods`, `2013_Alberta_floods`, `2013_Colorado_floods`, `2013_Manila_floods`, `2013_Queensland_floods`, `2013_Sardinia_floods` | `FLOOD` |
| `2012_Typhoon_Pablo`, `2013_Typhoon_Yolanda` | `STORM_CYCLONE` |
| `2012_Italy_earthquakes`, `2012_Costa_Rica_earthquake`, `2012_Guatemala_earthquake`, `2013_Bohol_earthquake`, `2013_Savar_building_collapse` | `EARTHQUAKE_COLLAPSE` |
| `2013_Lac_Megantic_train_crash`, `2013_Spain_train_crash`, `2013_NY_train_crash`, `2013_Glasgow_helicopter_crash` | `TRANSPORT_ACCIDENT` |
| `2013_Boston_bombings`, `2013_LA_airport_shootings` | `VIOLENCE_CRIME` |
| `2013_Russia_meteor`, `2013_Singapore_haze` | drop (no matching type) |

**`Informativeness` filter:**
- `Related and informative` → keep with the crisis's type
- `Not related` → `NON_EMERGENCY` (off-topic tweets caught by crisis keywords, which make good hard negatives)
- `Related - but not informative` → drop

**Best use:** **cross-dataset test** (train on HumAID + synthetic, test on CrisisLexT26) to show the model generalises.
Its accident and violence tweets can also top up those classes in training, but if you train on them, use a
**crisis-level split** so the same crisis never appears in both train and test.

### 1.3 Kaggle "Natural Language Processing with Disaster Tweets"

| | |
|---|---|
| Page | https://www.kaggle.com/competitions/nlp-getting-started |
| Download | Join the competition, then the Data tab, or `kaggle competitions download -c nlp-getting-started` |
| Files | `train.csv` (labelled), `test.csv` (unlabelled, ignore), `sample_submission.csv` |
| Columns | `id`, `keyword`, `location`, `text`, `target` (1 = real disaster, 0 = not) |

**Use only `target == 0` rows → `NON_EMERGENCY`.** They are tweets that use disaster words without describing
a real emergency ("my phone is on fire 🔥"), which are ideal hard negatives. `target == 1` rows have no
incident type, so skip them (or use the `keyword` column if you have spare time).

---

## 2. Synthetic call-style reports (B)

Generated by **Claude** following SCHEMA.md §3. Nothing to download. ML1 runs `scripts/generate_reports.py`
(to be written) with an Anthropic API key in `.env`.

---

## 3. Audio (voice demo and evaluation)

| Resource | Link | Use | Licence |
|---|---|---|---|
| **edge-tts** (text-to-speech) | https://github.com/rany2/edge-tts (`pip install edge-tts`) | Turn ~300 synthetic reports into speech. Run `edge-tts --list-voices` and pick `en-IN` voices if listed. | Open-source tool (uses Microsoft's online TTS service; needs internet) |
| **ESC-50** (environmental sounds) | https://github.com/karolpiczak/ESC-50 (~600 MB zip) | Background noise: `siren`, `car_horn`, `crackling_fire`, `rain`, `engine`, crowd sounds. 2,000 five-second clips, 50 classes. | CC BY-NC 3.0 (non-commercial: fine for a hackathon) |
| **MUSAN** (music, speech, noise) | https://www.openslr.org/17/ (11 GB) | Optional extra noise. **Too big to download during the event.** Use ESC-50 unless it's already downloaded. | CC BY 4.0 |
| Teammate recordings | Recorded on phones | Most realistic voice test set and demo clips. **Consent required. Never commit them** (`data/audio/` is ignored). | — |

---

## 4. Pretrained models (Hugging Face)

| Model | Link | Role |
|---|---|---|
| DistilBERT base uncased | https://huggingface.co/distilbert/distilbert-base-uncased | Classifier backbone (ML2) |
| Flan-T5 base | https://huggingface.co/google/flan-t5-base | Field generator (ML3) |
| BERT base NER | https://huggingface.co/dslim/bert-base-NER | Fallback location/entity extractor (ML3) |
| faster-whisper small.en | https://huggingface.co/Systran/faster-whisper-small.en | Speech to text (BE2). Library: https://github.com/SYSTRAN/faster-whisper |
| faster-whisper small (multilingual) | https://huggingface.co/Systran/faster-whisper-small | Only if Hindi/Marathi is added later |

On Kaggle, turn **Internet on** in notebook settings so these download, or attach them as Kaggle Models.

---

## 5. Quick download commands

```bash
mkdir -p data/raw && cd data/raw

# HumAID set 1 (text) + event-type split
curl -L -o humaid_set1.tar.gz https://crisisnlp.qcri.org/data/humaid/HumAID_data_events_set1_47K.tar.gz
tar xzf humaid_set1.tar.gz

# CrisisLexT26
curl -L -o crisislex_t26.zip "https://github.com/sajao/CrisisLex/blob/master/releases/CrisisLexT26-v1.0.zip?raw=true"
unzip -q crisislex_t26.zip

# Kaggle Disaster Tweets (needs ~/.kaggle/kaggle.json and joining the competition first)
kaggle competitions download -c nlp-getting-started && unzip -q nlp-getting-started.zip -d kaggle_disaster

# ESC-50 noise clips
curl -L -o esc50.zip https://github.com/karoldvl/ESC-50/archive/master.zip
unzip -q esc50.zip
```

## 6. Expected class coverage

| `incident_type` | HumAID set 1 | CrisisLexT26 | Kaggle | Synthetic (Claude) |
|---|---|---|---|---|
| `FIRE` | ✅ wildfires | ✅ fires, explosions | | ✅ |
| `FLOOD` | ✅ | ✅ | | ✅ |
| `STORM_CYCLONE` | ✅ (largest share) | ✅ | | ✅ |
| `EARTHQUAKE_COLLAPSE` | ✅ | ✅ | | ✅ |
| `TRANSPORT_ACCIDENT` | | ✅ (rail/air) | | ✅ **main source** (road) |
| `MEDICAL` | | | | ✅ **only source** |
| `VIOLENCE_CRIME` | | ✅ (small) | | ✅ **main source** |
| `NON_EMERGENCY` | | ✅ "Not related" | ✅ `target == 0` | ✅ |

**Class balance:** HumAID's storm class will be far larger than the others. Cap each class at roughly the size of
the smallest well-covered class (e.g. 2,000–3,000 rows) **or** use class weights. Don't let storms dominate.
