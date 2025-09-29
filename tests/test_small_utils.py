from __future__ import annotations

from src.metrics._calibrate import _clamp, _affine_into


def test_clamp_bounds():
    assert _clamp(-1.0, 0.0, 1.0) == 0.0
    assert _clamp(2.0, 0.0, 1.0) == 1.0
    assert _clamp(0.5, 0.0, 1.0) == 0.5


def test_affine_into_basic():
    assert 0.0 <= _affine_into(0.5, 0.2, 0.8) <= 1.0
