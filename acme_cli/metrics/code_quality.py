from __future__ import annotations
from typing import Any, Dict

class CodeQuality:
    name = "code_quality"

    def compute(self, url: str, meta: Dict[str, Any]) -> float:
        return 0.7
