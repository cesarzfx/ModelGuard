from __future__ import annotations
from typing import Any, Dict

COMPATIBLE = {"mit", "apache-2.0", "bsd-3-clause", "lgpl-2.1", "lgpl-3.0"}

class LicenseMetric:
    name = "license"

    def compute(self, url: str, meta: Dict[str, Any]) -> float:
        lic = (meta.get("license", "") or "").lower()
        if not lic:
            return 0.2
        return 1.0 if lic in COMPATIBLE else 0.5
