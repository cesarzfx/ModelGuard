from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class Metric(ABC):
    def _as_path(self, path_or_url: str) -> Optional[Path]:
        p = Path(path_or_url)
        return p if p.exists() else None

    def _stable_unit_score(self, path_or_url: str, metric_name: str) -> float:
        """
        Returns a stable placeholder score for non-local paths or unsupported cases.
        This avoids random output and makes results predictable for URLs.
        """
        fallback_scores = {
            "availability": 0.2,
            "bus_factor": 0.2,
            "code_quality": 0.2,
            "dataset_quality": 0.5,
            "license": 0.0,
            "performance_claims": 0.0,
            "ramp_up": 0.05,
        }
        return fallback_scores.get(metric_name, 0.0)
