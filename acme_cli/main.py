from __future__ import annotations
import sys, json, logging
from pathlib import Path
from typing import Any, Dict

from .logging_utils import setup_logging
from .urls import iter_urls, classify
from .ndjson import dump_line
from .hf_api import get_model_meta
from .repo_analysis import analyze_repo
from .metrics.base import run_metrics
from .metrics.ramp_up import RampUp
from .metrics.bus_factor import BusFactor
from .metrics.license import LicenseMetric
from .metrics.size_score import SizeScore
from .metrics.dataset_code import DatasetAndCode
from .metrics.dataset_quality import DatasetQuality
from .metrics.code_quality import CodeQuality
from .metrics.perf_claims import PerformanceClaims
from .scoring import netscore

METRICS = [
    LicenseMetric(),
    RampUp(),
    BusFactor(),
    SizeScore(),
    DatasetAndCode(),
    DatasetQuality(),
    CodeQuality(),
    PerformanceClaims(),
]

def process_url(url: str) -> Dict[str, Any] | None:
    name, category = classify(url)
    # Only emit NDJSON for MODEL
    if category != "MODEL":
        return None
    meta = get_model_meta(url)
    meta.update(analyze_repo(url))

    fields: Dict[str, Any] = {"name": name, "category": category}
    # Run metrics and capture per-metric latencies
    fields.update(run_metrics(url, meta, METRICS))

    # size_score is object; ensure present and add latency captured already
    size_obj = meta.get("size_score") or {
        "raspberry_pi": 0.3, "jetson_nano": 0.5, "desktop_pc": 0.8, "aws_server": 1.0
    }
    fields["size_score"] = size_obj  # already added size_score score in metrics

    # Net score
    fields["net_score"] = netscore(fields)
    # Sum of metric latencies as a rough proxy for net_score_latency
    fields["net_score_latency"] = sum(
        int(v) for k, v in fields.items() if k.endswith("_latency") and k != "net_score_latency"
    )
    return fields

def main(argv: list[str]) -> int:
    setup_logging()
    if len(argv) != 1:
        print("Usage: python -m acme_cli.main <URL_FILE>", file=sys.stderr)
        return 1
    url_file = Path(argv[0])
    if not url_file.exists():
        print(f"URL file not found: {url_file}", file=sys.stderr)
        return 1
    for url in iter_urls(url_file):
        row = process_url(url)
        if row is not None:
            print(dump_line(row))
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
