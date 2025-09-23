from __future__ import annotations
import hashlib
from typing import Any, Dict

class BusFactor:
    name = "bus_factor"

    def compute(self, url: str, meta: Dict[str, Any]) -> float:
        # Placeholder: stable mapping from url -> [0,1]
        h = hashlib.md5(url.encode()).hexdigest()
        return int(h[8:16], 16) / 0xFFFFFFFF
