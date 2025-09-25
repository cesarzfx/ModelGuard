from statistics import mean
from typing import Dict


class NetScore:
    """
    Weighted composite score.

    Default weights (sum to 1):
      availability:         0.10
      bus factor:           0.15
      code quality:         0.20
      dataset quality:      0.05
      license:              0.10
      performance claims:   0.10
      ramp up:              0.15
      size (aggregate):     0.15
    """

    def __init__(self, url_or_path: str):
        self.target = url_or_path
        self.weights = {
            "availability": 0.10,
            "bus_factor": 0.15,
            "code_quality": 0.20,
            "dataset_quality": 0.05,
            "license": 0.10,
            "performance_claims": 0.10,
            "ramp_up": 0.15,
            "size": 0.15,
        }

    def combine(self, scores: Dict[str, float], size_scores: Dict[str, float]) -> float:
        size_val = mean(size_scores.values()) if size_scores else 0.0
        total = 0.0
        wsum = 0.0
        for name, w in self.weights.items():
            if name == "size":
                val = size_val
            else:
                val = scores.get(name, 0.0)
            total += w * max(0.0, min(1.0, float(val)))
            wsum += w
        result = total / wsum if wsum > 0 else 0.0
        return max(0.0, min(1.0, result))  # Clamp final result
