"""
Tests for bert-base-uncased model URL formats.
"""

from src.main import _record
from src.metrics.net_score import NetScore


def test_bert_base_uncased_additional_urls():
    """Test handling of bert-base-uncased model with different URL formats."""
    # Test different URL formats that might be used
    urls = [
        "https://huggingface.co/bert-base-uncased",
        "https://huggingface.co/models/bert-base-uncased",
        "bert-base-uncased",
        "/path/to/bert-base-uncased",
        "http://some-url/bert-base-uncased/model",
    ]

    for url in urls:
        ns = NetScore(url)
        record = _record(ns, url)

        # Verify key properties for all URL formats
        assert record["name"] == "bert-base-uncased"
        assert record["category"] == "MODEL"
        assert record["ramp_up_time"] == 0.8
        assert abs(record["dataset_and_code_score"] - 0.85) < 0.00001
