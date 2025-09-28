"""
Tests for the metrics module functionality and edge cases.
"""
import pytest
from pathlib import Path

from src.metrics.metric import Metric
from src.metrics.base_metric import BaseMetric


class TestBaseMetric(BaseMetric):
    """A concrete implementation of BaseMetric for testing."""
    pass


def test_base_metric_methods():
    """Test that base metric methods have expected return types."""
    metric = TestBaseMetric()
    
    assert metric._is_git_repo(Path(".")) is False
    assert metric._git() is None
    assert metric._count_lines(Path(".")) == 0
    assert metric._saturating_scale(0.5, knee=0.5, max_x=1.0) == 0.0
    assert metric._clamp01(1.5) == 0.0
    assert metric._read_text(Path(".")) == ""
    assert metric._glob() == []
    assert metric._as_path("nonexistent") is None
    assert 0.0 <= metric._stable_unit_score("key", "salt") <= 1.0


def test_metric_stable_unit_score():
    """Test the stable unit score method in the Metric class."""
    class TestMetric(Metric):
        pass
    
    metric = TestMetric()
    
    # Test known metrics
    assert metric._stable_unit_score("url", "availability") == 0.2
    assert metric._stable_unit_score("url", "bus_factor") == 0.2
    assert metric._stable_unit_score("url", "code_quality") == 0.2
    assert metric._stable_unit_score("url", "dataset_quality") == 0.5
    assert metric._stable_unit_score("url", "license") == 0.0
    assert metric._stable_unit_score("url", "performance_claims") == 0.0
    assert metric._stable_unit_score("url", "ramp_up") == 0.05
    
    # Test unknown metric
    assert metric._stable_unit_score("url", "unknown_metric") == 0.0


def test_metric_as_path():
    """Test the _as_path method in the Metric class."""
    class TestMetric(Metric):
        pass
    
    metric = TestMetric()
    
    # Non-existent path
    assert metric._as_path("/path/that/does/not/exist") is None
    
    # Existing path (current directory should exist)
    import os
    current_dir = os.getcwd()
    path_obj = metric._as_path(current_dir)
    assert path_obj is not None
    assert isinstance(path_obj, Path)
    assert path_obj.exists()


def test_early_env_exits():
    """Test the _early_env_exits function with environment variables."""
    import os
    from src.main import _early_env_exits
    
    # Test with valid token
    os.environ["GITHUB_TOKEN"] = "valid_token"
    assert _early_env_exits() is False
    
    # Test with invalid token
    os.environ["GITHUB_TOKEN"] = "INVALID"
    assert _early_env_exits() is True
    
    # Clean up
    os.environ.pop("GITHUB_TOKEN", None)