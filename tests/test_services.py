"""Tests for the BE2 services: geocoding (offline), duplicate detection (fake embedder), ASR wiring. No network, no big models."""
import numpy as np

from src.services import deduplication as D
from src.services import geocoding as G


def _no_network(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("network disabled in tests")
    monkeypatch.setattr(G.geolocator, "geocode", boom)
    monkeypatch.setattr(G, "geocode_cache", {})


def test_known_places_resolve_offline(monkeypatch):
    _no_network(monkeypatch)
    for text in ["FC road", "near Lonavala exit", "Dadar station", "Kolkata Salt Lake", "Hyderabad Chandrayangutta"]:
        lat, lon, ok = G.geocode_location(text)
        assert ok and lat is not None and lon is not None, text


def test_unknown_place_never_raises(monkeypatch):
    _no_network(monkeypatch)
    assert G.geocode_location("somewhere nobody has heard of xyzzy") == (None, None, False)
    assert G.geocode_location("") == (None, None, False)
    assert G.geocode_location(None) == (None, None, False)


def test_geocode_name_used_by_the_api_exists():
    assert G.geocode_location is G.get_coordinates


def test_dedup_flags_a_near_copy_and_ignores_a_different_report(monkeypatch):
    vectors = {"fire at the market": np.array([1.0, 0.0]), "fire at the market please": np.array([0.99, 0.05]),
               "river is flooding": np.array([0.0, 1.0])}

    class FakeEmbedder:
        def encode(self, text):
            return vectors[text]

    monkeypatch.setattr(D, "_embedder", FakeEmbedder())
    monkeypatch.setattr(D, "embedding_store", {})
    first_id, emb = D.find_duplicate("fire at the market", {})
    assert first_id is None
    D.register_embedding("RQP-000001", emb)
    store = {"RQP-000001": object()}
    assert D.find_duplicate("fire at the market please", store)[0] == "RQP-000001"
    assert D.find_duplicate("river is flooding", store)[0] is None


def test_dedup_degrades_to_no_duplicates_when_the_model_is_missing(monkeypatch):
    monkeypatch.setattr(D, "_embedder", None)
    monkeypatch.setattr(D, "_unavailable", True)
    assert D.find_duplicate("anything", {"RQP-000001": object()}) == (None, None)
    D.register_embedding("RQP-000002", None)      # must not raise


def test_asr_module_exposes_the_function_the_api_imports():
    import importlib.util
    spec = importlib.util.find_spec("faster_whisper")
    if spec is None:                                  # whisper not installed on this machine: nothing to check
        return
    from src.asr import whisper
    assert whisper.transcribe is whisper.transcribe_bytes


def test_a_loose_word_overlap_must_not_pin_the_wrong_city(monkeypatch):
    # "expressway" appears in a gazetteer key, but Barrackpore Kalyani is nowhere near the Mumbai-Pune expressway
    _no_network(monkeypatch)
    assert G.geocode_location("Bus stop near Barrackpore Kalyani expressway") == (None, None, False)


def test_longest_place_name_wins(monkeypatch):
    _no_network(monkeypatch)
    kolhapur = G.OFFLINE_GAZETTEER["kolhapur"]
    lat, lon, ok = G.geocode_location("km 112 of Kolhapur-Pune highway")
    assert ok and (lat, lon) == kolhapur
