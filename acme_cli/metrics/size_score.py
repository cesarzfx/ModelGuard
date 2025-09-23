from __future__ import annotations
from typing import Any, Dict

class SizeScore:
    name = "size_score"

    def compute(self, url: str, meta: Dict[str, Any]) -> float:
        # Not used directly; we emit object in main. Return average for NetScore.
        ss = meta.get("size_score", {
            "raspberry_pi": 0.3,
            "jetson_nano": 0.5,
            "desktop_pc": 0.8,
            "aws_server": 1.0,
        })
        meta["size_score"] = ss
        return sum(ss.values()) / len(ss)
