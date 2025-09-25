from __future__ import annotations
from typing import Any, Dict

class DatasetQuality:
    name = "dataset_quality"

    def compute(self, url: str, meta: Dict[str, Any]) -> float:
        return 0.6
