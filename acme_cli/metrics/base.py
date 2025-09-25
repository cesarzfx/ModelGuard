from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Dict, Any, Tuple, List
from ..util.timer import time_ms

class Metric(Protocol):
    name: str
    def compute(self, url: str, meta: Dict[str, Any]) -> float: ...

@dataclass
class Measured:
    name: str
    score: float
    latency_ms: int

def run_metrics(url: str, meta: Dict[str, Any], metrics: List[Metric]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for m in metrics:
        score, ms = time_ms(lambda: m.compute(url, meta))
        out[m.name] = float(max(0.0, min(1.0, score)))
        out[f"{m.name}_latency"] = int(ms)
    return out
