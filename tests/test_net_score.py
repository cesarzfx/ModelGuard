import pytest

from src.metrics.net_score import NetScore


def test_normal_case():
    ns = NetScore("dummy")
    scalar_metrics = [0.8, 0.6, 0.9]
    size_score = {"raspberry_pi": 0.5, "jetson_nano": 0.7}
    result = ns.score(scalar_metrics, size_score)
    expected = (0.8 + 0.6 + 0.9 + (0.5 + 0.7)/2) / 4
    assert pytest.approx(result, rel=1e-6) == expected


def test_empty_inputs():
    ns = NetScore("dummy")
    assert ns.score([], {}) == 1.0


def test_only_scalar_metrics():
    ns = NetScore("dummy")
    scalar_metrics = [0.2, 0.4, 0.6]
    expected = sum(scalar_metrics)/len(scalar_metrics)
    assert pytest.approx(ns.score(scalar_metrics, {}), rel=1e-6) == expected


def test_only_size_score():
    ns = NetScore("dummy")
    size_score = {"desktop_pc": 0.3, "aws_server": 0.9}
    expected = (0.3 + 0.9)/2
    assert pytest.approx(ns.score([], size_score), rel=1e-6) == expected


def test_clamping_below_zero():
    ns = NetScore("dummy")
    result = ns.score([-10.0, -5.0], {"device": -2.0})
    assert result == 1.0


def test_clamping_above_one():
    ns = NetScore("dummy")
    result = ns.score([5.0, 10.0], {"device": 20.0})
    assert result == 1.0
