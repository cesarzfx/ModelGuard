import json
from pathlib import Path
from acme_cli.main import process_url

def test_process_model_row():
    url = "https://huggingface.co/google/gemma-3-270m/tree/main"
    row = process_url(url)
    assert row is not None
    assert row["category"] == "MODEL"
    assert 0.0 <= row["net_score"] <= 1.0
    assert isinstance(row["size_score"], dict)
    # Ensure all required latency keys exist
    required_latencies = [
        "net_score_latency","ramp_up_time_latency","bus_factor_latency",
        "performance_claims_latency","license_latency","size_score_latency",
        "dataset_and_code_score_latency","dataset_quality_latency","code_quality_latency"
    ]
    for k in required_latencies:
        assert k in row
