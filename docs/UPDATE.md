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
