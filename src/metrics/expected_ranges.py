# src/metrics/expected_ranges.py
from __future__ import annotations

# Put expected bands here so we don't ship external data files.
EXPECTED: dict = {
    "packages": {
        "bert-base-uncased": {
            "license_score": [0.60, 0.90],
            "code_quality_score": [0.55, 0.85],
        }
    },
    "reference_models": {
        # Use the model keys your pipeline emits; keep at least one
        # example so tests can assert calibration.
        "model_a": {
            "ramp_up": [0.40, 0.80],
            "bus_factor": [0.50, 0.90],
            "license": [0.60, 0.95],
            "correctness": [0.45, 0.85],
            "maintainability": [0.50, 0.90],
            "testing": [0.30, 0.80],
            "usage": [0.40, 0.90],
            "size": [0.20, 0.70],
        }
    },
}
