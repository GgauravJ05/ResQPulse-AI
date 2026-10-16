# Gold set review guide

The gold set is the only test data where **real text has labels checked by a human**. Claude pre-labelled 146 real
tweets; your job is to check each row. About 10 seconds per row, 70 rows each.

**File:** `data/gold/gold_review.csv` → open it in Google Sheets or Excel (UTF-8).
**Split:** Gaurav reviews rows 2–74, BE2 reviews rows 75–147 (spreadsheet row numbers, header is row 1).

## What to do for each row

Read the `text` column, then check these columns:

| Column | Check | If wrong |
|---|---|---|
| `incident_type` | Is it the type of incident the **text reports**? | Pick the right one from the list below |
| `severity` | Does it match the rubric below? | Change the number (half points allowed) |
| `location` | Is it a place mentioned in the text, copied word for word? | Fix or clear it |
| `people_affected` | A number stated in the text (hurt, trapped, dead, evacuated). Empty if not stated | Fix or clear it |
| `injuries`, `hazards` | Phrases copied word for word from the text, separated by ` ; ` | Fix or clear |
| `summary` | One sentence that matches the text | Fix if misleading |

Then fill the **`verified`** column:

| Value | Meaning |
|---|---|
| `1` | Everything was correct, you changed nothing |
| `2` | You corrected something |
| `0` | Row is unusable (not English, unreadable). It will be dropped |

Use `notes` for doubts. **Don't leave `verified` empty**: empty rows are dropped.

## Types

`FIRE` · `FLOOD` · `STORM_CYCLONE` · `EARTHQUAKE_COLLAPSE` · `TRANSPORT_ACCIDENT` · `MEDICAL` · `VIOLENCE_CRIME` · `NON_EMERGENCY`

**The rule that matters most:** donations, relief logistics, housing offers, jokes, ads, rants, media commentary and
political comments are **NON_EMERGENCY**, even when they mention a disaster. A headline that *reports* the incident
(deaths, damage, a warning) keeps its incident type.

## Severity rubric

| Score | Meaning |
|---|---|
| 1 | Not an emergency, or nobody hurt and nothing at risk |
| 2 | Minor, or a follow-up/information post about an incident |
| 3 | One serious injury, damage, or a warning for people at risk |
| 4 | Life-threatening, many people hurt, or a major event unfolding |
| 5 | Deaths or mass casualties reported, people trapped |

Follow-up news about a past event (investigation, court, mourning) is **2–3**, not 5.

## When you're done

Save the sheet as `data/gold/gold_review.csv` (CSV UTF-8) and tell Gaurav. Then run:

```bash
.venv/bin/python scripts/build_gold.py finalize     # writes data/gold/gold.csv
```
