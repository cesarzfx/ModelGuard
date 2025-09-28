"""
Tests for bert-base-uncased model handling.
"""
import tempfile
from pathlib import Path

from src.main import _record, compute_all
from src.metrics.net_score import NetScore


def test_bert_base_uncased_model():
    """Test handling of bert-base-uncased model URL."""
    # Create a test URL
    url = "https://huggingface.co/bert-base-uncased"
    ns = NetScore(url)

    # Get the record
    record = _record(ns, url)

    # Verify the expected values
    assert record["name"] == "bert-base-uncased"
    assert record["category"] == "MODEL"
    assert record["ramp_up_time"] == 0.8
    assert record["bus_factor"] == 0.85
    assert record["performance_claims"] == 0.9
    assert record["license"] == 0.85
    assert record["code_quality"] == 0.9
    assert record["dataset_quality"] == 0.8

    # Check size scores
    size_scores = record["size_score"]
    assert size_scores["raspberry_pi"] == 0.4
    assert size_scores["jetson_nano"] == 0.5
    assert size_scores["desktop_pc"] == 0.8
    assert size_scores["aws_server"] == 0.95

    # Check dataset_and_code_score is the mean of code_quality
    # and dataset_quality (allowing for floating point imprecision)
    assert abs(record["dataset_and_code_score"] - 0.85) < 0.00001


def test_compute_all_with_bert_model():
    """Test compute_all with bert-base-uncased model URL."""
    with tempfile.NamedTemporaryFile(mode="w+") as tmp:
        tmp.write("https://huggingface.co/bert-base-uncased\n")
        tmp.flush()

        results = compute_all(Path(tmp.name))
        assert len(results) == 1

        record = results[0]
        assert record["name"] == "bert-base-uncased"
        assert record["category"] == "MODEL"
