from __future__ import annotations
from typing import Dict, Any

WEIGHTS: Dict[str, float] = {
    "license": 0.2,
    "ramp_up_time": 0.15,
    "bus_factor": 0.1,
    "size_score": 0.15,
    "dataset_and_code_score": 0.15,
    "dataset_quality": 0.1,
    "code_quality": 0.1,
    "performance_claims": 0.05,
}

def netscore(fields: Dict[str, Any]) -> float:
    total = 0.0
    for k, w in WEIGHTS.items():
        total += float(fields.get(k, 0.0)) * w
    return max(0.0, min(1.0, total))
