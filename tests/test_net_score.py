import pytest

from src.metrics.net_score import NetScore

def test_normal_case():
    ns = NetScore("dummy")
    scalar_metrics = {
        "availability": 0.8,
        "bus_factor": 0.6,
        "code_quality": 0.9,
    }
    size_score = {"raspberry_pi": 0.5, "jetson_nano": 0.7}
    # Only keys present in weights will be used
    result = ns.combine(scalar_metrics, size_score)
    # You may need to update the expected value based on weights
    assert 0.0 <= result <= 1.0

def test_empty_inputs():
    ns = NetScore("dummy")
    assert ns.combine({}, {}) == 0.0

def test_only_scalar_metrics():
    ns = NetScore("dummy")
    scalar_metrics = {
        "availability": 0.2,
        "bus_factor": 0.4,
        "code_quality": 0.6,
    }
    assert 0.0 <= ns.combine(scalar_metrics, {}) <= 1.0

def test_only_size_score():
    ns = NetScore("dummy")
    size_score = {"desktop_pc": 0.3, "aws_server": 0.9}
    assert 0.0 <= ns.combine({}, size_score) <= 1.0

def test_clamping_below_zero():
    ns = NetScore("dummy")
    result = ns.combine({"availability": -10.0}, {"device": -2.0})
    assert result == 0.0

def test_clamping_above_one():
    ns = NetScore("dummy")
    result = ns.combine({"availability": 5.0}, {"device": 20.0})
    assert 0.0 <= result <= 1.0  # Accept any value in [0, 1]
