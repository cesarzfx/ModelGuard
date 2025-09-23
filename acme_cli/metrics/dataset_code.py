from __future__ import annotations
from typing import Any, Dict

class DatasetAndCode:
    name = "dataset_and_code_score"

    def compute(self, url: str, meta: Dict[str, Any]) -> float:
        # Placeholder: if dataset/code linked
        return 1.0 if meta.get("has_dataset_and_code", False) else 0.3
