from __future__ import annotations
from typing import Any, Dict

class PerformanceClaims:
    name = "performance_claims"

    def compute(self, url: str, meta: Dict[str, Any]) -> float:
        # Placeholder: claims present flag in meta
        return 1.0 if meta.get("has_eval_table", False) else 0.4
