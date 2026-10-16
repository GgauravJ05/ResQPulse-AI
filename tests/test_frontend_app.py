"""Drives the real Streamlit app with Streamlit's test harness (no browser, no backend needed)."""
import re
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app" / "streamlit_app.py")
SCREENS = ["Report Input", "Alert Card", "Attention Heatmap",
           "Dispatcher Dashboard", "Model Metrics"]


def _app():
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    return at


def _goto(at, screen):
    return at.radio(key="nav_screen_selection").set_value(screen).run()


def test_every_screen_renders_without_errors():
    at = _app()
    for screen in SCREENS:
        _goto(at, screen)
        assert not at.exception, f"{screen}: {[e.value for e in at.exception]}"


def test_starts_in_mock_mode_when_no_backend_is_reachable():
    # the live default only applies when /health answers; with nothing listening the page must still work
    at = _app()
    if at.session_state["mock_mode"] is False:
        pytest.skip("a backend is running on this machine, so the app (correctly) started in live mode")
    assert at.session_state["mock_mode"] is True


def test_heatmap_stretches_contrast_across_the_report():
    at = _app()
    at.session_state["current_alert"] = {
        "alert_id": "RQP-000001", "incident_type": "FIRE", "severity": 4.0, "severity_label": "CRITICAL",
        "explanation": {"attention": [["Fire", 1.0], ["in", 0.84], ["a", 0.75], ["flat", 0.55], ["trapped", 0.62], ["everywhere", 0.95]]},
    }
    _goto(at, "Attention Heatmap")
    html = " ".join(m.value for m in at.markdown)
    alphas = [float(x) for x in re.findall(r"background-color: rgba\(255, 204, 0, ([0-9.]+)\)", html)]
    assert len(alphas) == 6
    assert max(alphas) - min(alphas) > 0.6          # raw rollout scores span only 0.55 to 1.0; they must be stretched
    assert "indicator, not proof" in html


def test_heatmap_escapes_html_in_words():
    at = _app()
    at.session_state["current_alert"] = {
        "alert_id": "RQP-000002", "incident_type": "FIRE", "severity": 3.0, "severity_label": "HIGH",
        "explanation": {"attention": [["<script>alert(1)</script>", 0.9], ["fire", 0.5]]},
    }
    _goto(at, "Attention Heatmap")
    html = " ".join(m.value for m in at.markdown)
    assert "<script>" not in html and "&lt;script&gt;" in html


def test_flat_html_has_no_blank_lines_or_indentation():
    from app.components import _flat
    out = _flat("""
        <div>
            <!-- note -->

            <span>x</span>
        </div>
    """)
    assert out == "<div>\n<span>x</span>\n</div>"
