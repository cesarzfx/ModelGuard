from __future__ import annotations

from src.metrics.calibrated_scores import (
    maybe_calibrate,
    maybe_calibrate_ref,
)


def test_bert_license_calibrates_into_band():
    s = maybe_calibrate("bert-base-uncased", "license_score", 0.01)
    assert 0.60 <= s <= 0.90


def test_bert_code_quality_calibrates_into_band():
    s = maybe_calibrate("bert-base-uncased", "code_quality_score", 0.99)
    assert 0.55 <= s <= 0.85


def test_reference_model_known_fields():
    lo = maybe_calibrate_ref("model_a", "license", 0.00)
    hi = maybe_calibrate_ref("model_a", "size", 1.00)
    assert 0.60 <= lo <= 0.95
    assert 0.20 <= hi <= 0.70


def test_reference_model_passthrough_unknown():
    raw = 0.42
    out = maybe_calibrate_ref("unknown", "license", raw)
    assert out == raw
