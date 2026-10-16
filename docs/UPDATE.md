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
