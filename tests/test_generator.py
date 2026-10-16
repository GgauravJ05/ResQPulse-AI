"""Tests for src/models/generator.py. The model tests are skipped when models/generator/ is not on this machine."""
import pytest

from src.models import generator as G

needs_model = pytest.mark.skipif(not G.is_ready(), reason="models/generator/ not present on this machine")


def test_people_rule_keeps_count_only_with_evidence():
    assert G.apply_people_rule("Fire near the market, 3 people stuck", 3) == 3
    assert G.apply_people_rule("my mother is unconscious", 1) == 1
    assert G.apply_people_rule("Towns across the island have no water", 1) is None
    assert G.apply_people_rule("anything", None) is None


def test_fallback_extracts_verbatim_phrases():
    text = "Fire near FC road petrol pump, 3 people stuck inside, smoke everywhere"
    r = G._fallback(text)
    assert r.extractor == "fallback_rules"
    assert r.people_affected == 3
    assert r.location == "FC road"
    for item in [r.location] + r.injuries + r.hazards:      # everything must appear word for word in the text
        assert item.lower() in text.lower()


def test_fallback_handles_text_with_nothing_to_extract():
    r = G._fallback("something happened")
    assert r.location is None and r.people_affected is None and r.injuries == [] and r.hazards == []
    assert r.summary


def test_empty_text_is_rejected():
    for bad in ["", "   "]:
        with pytest.raises(ValueError):
            G.extract(bad)


def test_clean_recovers_text_after_none():
    raw = "location: x | people: none | injuries: none | hazards: none | summary: none Fire at the market."
    assert G.parse_target(G._clean(raw))["summary"] == "Fire at the market."


def test_incomplete_output_is_not_complete():
    assert not G._complete("location: only this")
    assert not G._complete("location: a | people: 1 | injuries: none | hazards: none | summary: none")
    assert G._complete("location: a | people: 1 | injuries: none | hazards: none | summary: Fire.")


@needs_model
def test_model_extracts_a_demo_report():
    r = G.extract("Fire near FC road petrol pump, 3 people stuck inside, smoke everywhere")
    assert r.extractor == "flan_t5"
    assert r.location and "FC road" in r.location
    assert r.people_affected == 3
    assert r.summary


@needs_model
def test_model_never_crashes_on_odd_input():
    for text in ["ok", "a" * 2000, "!!!???", "आग लगी है", "12345"]:
        r = G.extract(text)
        assert r.extractor in ("flan_t5", "fallback_rules") and isinstance(r.summary, str)
