"""Write dist/kaggle/dataset-metadata.json from docs/KAGGLE_DATACARD.md, so the Kaggle page and the card never drift.

The card is the single source of truth. This reads its header table (title, subtitle, tags), the Markdown description
in §2, the file descriptions in §3 and the column descriptions in §4, and writes the metadata file the Kaggle CLI
uploads with `kaggle datasets version` / `kaggle datasets metadata --update`.

Kaggle's metadata file has no fields for the cover image, expected update frequency or provenance: set those on the
website (values are in the card's §1 and §5).

Run from the repo root after `make public-dataset`:  python scripts/make_kaggle_metadata.py
"""
import json
import re
import sys
from pathlib import Path

CARD = Path("docs/KAGGLE_DATACARD.md")
OUT = Path("dist/kaggle")
DATASET_ID = "ggauravj05/resqpulse-data"
LICENSE = "CC-BY-4.0"
NUMERIC_COLUMNS = {"severity", "agree"}


def cells(line: str) -> list[str]:
    """Split one Markdown table row into cells, keeping escaped pipes (\\|) inside a cell."""
    parts = re.split(r"(?<!\\)\|", line.strip().strip("|"))
    return [p.strip().replace("\\|", "|") for p in parts]


def table_after(text: str, start: int) -> list[list[str]]:
    """Rows of the first Markdown table after `start`, without the header and separator rows."""
    lines = text[start:].splitlines()
    rows, in_table = [], False
    for line in lines:
        if line.startswith("|"):
            in_table = True
            rows.append(cells(line))
        elif in_table:
            break
    return rows[2:]


def unquote(cell: str) -> str:
    return cell.strip("`*").strip()


def main() -> None:
    card = CARD.read_text(encoding="utf-8")
    if not OUT.exists():
        sys.exit(f"{OUT}/ is missing: run `make public-dataset` first")

    header = {unquote(k): v for k, v in table_after(card, card.index("## 1. Header fields"))}
    description = re.search(r"## 2\..*?```markdown\n(.*?)\n```", card, re.S).group(1)
    file_desc = {unquote(f): d for f, d in table_after(card, card.index("## 3. File descriptions"))}

    columns: dict[str, list[dict]] = {}
    for m in re.finditer(r"^### (.+)$", card[card.index("## 4. Column descriptions"):], re.M):
        names = re.findall(r"`([^`]+\.csv)`", m.group(1))
        pos = card.index("## 4. Column descriptions") + m.end()
        fields = [{"name": unquote(c), "description": d, "type": "numeric" if unquote(c) in NUMERIC_COLUMNS else "string"}
                  for c, d in table_after(card, pos)]
        for name in names:
            columns[name] = fields

    files = sorted(p.name for p in OUT.glob("*.csv"))
    missing = [f for f in files if f not in file_desc or f not in columns]
    if missing:
        sys.exit(f"the card has no file or column descriptions for: {', '.join(missing)}")

    metadata = {
        "id": DATASET_ID,
        "title": header["Title"],
        "subtitle": header["Subtitle"],
        "description": description,
        "isPrivate": False,
        "licenses": [{"name": LICENSE}],
        "keywords": [t.strip().lower() for t in header["Tags"].split(",")],
        "resources": [{"path": f, "description": file_desc[f], "schema": {"fields": columns[f]}} for f in files],
    }
    (OUT / "dataset-metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT}/dataset-metadata.json: {len(files)} files, "
          f"{sum(len(columns[f]) for f in files)} column descriptions")


if __name__ == "__main__":
    main()
