"""Sanity tests for src/eval/metrics.py. Run:  .venv/bin/python tests/test_metrics.py   (or pytest)"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.eval.metrics import (  # noqa: E402
    classification_metrics, critical_recall, extraction_metrics, parses_ok, set_prf, severity_metrics, token_f1,
)


def close(a, b, tol=1e-9):
    return math.isclose(a, b, abs_tol=tol)


def test_perfect_classification():
    y = ["FIRE", "FLOOD", "NON_EMERGENCY", "FIRE"]
    m = classification_metrics(y, y)
    assert close(m["accuracy"], 1.0) and close(m["macro_f1"], 1.0)
    assert close(m["emergency_recall"], 1.0) and close(m["false_alarm_rate"], 0.0)


def test_macro_ignores_absent_classes():
    # MEDICAL never occurs in y_true: it must not drag the macro average down
    m = classification_metrics(["FIRE", "FLOOD"], ["FIRE", "FLOOD"])
    assert close(m["macro_f1"], 1.0) and "MEDICAL" not in m["classes_evaluated"]


def test_known_precision_recall():
    # FIRE: 1 of 2 true found, 1 of 1 predicted correct -> P=1.0 R=0.5 ; FLOOD: P=0.5 R=1.0
    m = classification_metrics(["FIRE", "FIRE", "FLOOD"], ["FIRE", "FLOOD", "FLOOD"])
    assert close(m["per_class"]["FIRE"]["precision"], 1.0) and close(m["per_class"]["FIRE"]["recall"], 0.5)
    assert close(m["per_class"]["FLOOD"]["precision"], 0.5) and close(m["per_class"]["FLOOD"]["recall"], 1.0)


def test_missed_emergency_and_false_alarm():
    m = classification_metrics(["FIRE", "FIRE", "NON_EMERGENCY", "NON_EMERGENCY"],
                               ["NON_EMERGENCY", "FIRE", "FIRE", "NON_EMERGENCY"])
    assert close(m["emergency_recall"], 0.5) and close(m["false_alarm_rate"], 0.5)


def test_critical_recall():
    assert close(critical_recall(["FIRE", "FIRE"], ["FIRE", "NON_EMERGENCY"], [5.0, 4.0]), 0.5)
    assert critical_recall(["FIRE"], ["FIRE"], [2.0]) is None


def test_severity():
    m = severity_metrics([1.0, 3.0, 5.0], [2.0, 3.0, 4.0])
    assert close(m["mse"], 2 / 3) and close(m["rmse"], math.sqrt(2 / 3)) and close(m["mae"], 2 / 3)
    assert close(m["within_one"], 1.0)
    # predictions outside 1-5 are clipped before scoring
    assert close(severity_metrics([5.0], [9.0])["mae"], 0.0)


def test_token_f1():
    assert close(token_f1("FC road", "fc road"), 1.0)
    assert close(token_f1(None, None), 1.0) and close(token_f1("a", None), 0.0)
    assert 0 < token_f1("petrol pump on FC road", "FC road") < 1


def test_set_prf_exact_and_lenient():
    m = set_prf([["bleeding from the head"]], [["bleeding"]])
    assert close(m["f1"], 0.0)
    m = set_prf([["bleeding from the head"]], [["bleeding from head"]], lenient=True)
    assert close(m["f1"], 1.0)
    assert close(set_prf([[]], [[]])["f1"], 0.0)   # nothing to find, nothing found: no score either way


def test_parse_check():
    ok = "location: x | people: 1 | injuries: none | hazards: none | summary: y"
    assert parses_ok(ok) and not parses_ok("garbage output")


def test_extraction_perfect():
    f = {"location": "FC road", "people_affected": 3, "injuries": ["burns"], "hazards": ["smoke"], "summary": "Fire."}
    m = extraction_metrics([f], [f], raw_outputs=["location: a | people: 1 | injuries: b | hazards: c | summary: d"])
    assert close(m["location_exact"], 1.0) and close(m["people_exact_match"], 1.0)
    assert close(m["injuries"]["f1"], 1.0) and close(m["summary_rougeL"], 1.0) and close(m["parse_rate"], 1.0)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok  ", t.__name__)
    print(f"{len(tests)} tests passed")
