from __future__ import annotations
import json
from typing import Any, Dict

def dump_line(obj: Dict[str, Any]) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
