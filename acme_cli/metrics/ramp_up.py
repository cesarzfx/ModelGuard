from __future__ import annotations
import hashlib
from typing import Any, Dict

class RampUp:
    name = "ramp_up_time"

    def compute(self, url: str, meta: Dict[str, Any]) -> float:
        # Placeholder heuristic: README length proxy via stable hash
        h = hashlib.md5((meta.get("readme_len_str","") + url).encode()).hexdigest()
        val = int(h[:8], 16) / 0xFFFFFFFF
        return val
