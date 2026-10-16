"""Flan-T5 text format for the generator (docs/SCHEMA.md §4).

T5's vocabulary has no { or } tokens, so the target is a flat line instead of JSON:
    location: X | people: 3 | injuries: a; b | hazards: x; y | summary: ...
`none` stands for null / empty.
"""
from typing import Optional

PREFIX = "extract alert: "
_KEYS = ["location", "people", "injuries", "hazards", "summary"]


def format_input(text: str) -> str:
    return PREFIX + text


def format_target(fields: dict) -> str:
    def join(items):
        items = [str(i).replace("|", ",").replace(";", ",") for i in (items or [])]
        return "; ".join(items) if items else "none"

    people = fields.get("people_affected")
    parts = [
        f"location: {fields.get('location') or 'none'}",
        f"people: {people if people is not None else 'none'}",
        f"injuries: {join(fields.get('injuries'))}",
        f"hazards: {join(fields.get('hazards'))}",
        f"summary: {str(fields.get('summary') or 'none').replace('|', ',')}",
    ]
    return " | ".join(parts)


def parse_target(line: str) -> dict:
    """Inverse of format_target. Unknown or missing keys fall back to empty values; never raises."""
    raw = {}
    for part in str(line).split(" | "):
        key, sep, value = part.partition(": ")
        if sep and key.strip() in _KEYS:
            raw[key.strip()] = value.strip()

    def items(value: Optional[str]) -> list:
        if not value or value.lower() == "none":
            return []
        return [v.strip() for v in value.split(";") if v.strip()]

    def text(value: Optional[str]) -> Optional[str]:
        return None if not value or value.lower() == "none" else value

    people = raw.get("people", "")
    return {
        "location": text(raw.get("location")),
        "people_affected": int(people) if people.isdigit() else None,
        "injuries": items(raw.get("injuries")),
        "hazards": items(raw.get("hazards")),
        "summary": text(raw.get("summary")) or "",
    }
