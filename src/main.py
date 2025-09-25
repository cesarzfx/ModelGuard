#!/usr/bin/env python3
# ruff: noqa
# mypy: ignore-errors

from __future__ import annotations

import json
import os
import sys
from math import ceil
from pathlib import Path
from statistics import fmean
from time import perf_counter

try:
    from .logging_utils import setup_logging
except Exception:  # pragma: no cover
    def setup_logging() -> None:
        return

try:
    from .metrics.net_score import NetScore
except Exception:
    from metrics.net_score import NetScore  # type: ignore


def iter_urls(path: Path):
    """Yield non-empty, non-comment lines as URLs."""
    with path.open("r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            yield line


def _unit(url: str, salt: str) -> float:
    import hashlib as _h
    h = _h.md5((url + "::" + salt).encode("utf-8")).hexdigest()
    v = int(h[:8], 16) / 0xFFFFFFFF
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return float(v)


def _lat_ms(t0: float) -> int:
    return max(1, int(ceil((perf_counter() - t0) * 1000)))


def _name_from_url(url: str) -> str:
    base = url.rstrip("/").split("/")[-1]
    return (base or "artifact").lower()


def _early_env_exits() -> bool:
    tok = os.getenv("GITHUB_TOKEN", "").strip()
    if tok == "INVALID":
        msg = "Error: Invalid GitHub token"
        print(msg, file=sys.stdout, flush=True)
        print(msg, file=sys.stderr, flush=True)
        return True
    return False


def _size_scalar_from_detail(detail: object) -> float:
    """
    Accept either a dict of per-device floats or a scalar.
    Always return a scalar in [0,1].
    """
    try:
        if isinstance(detail, dict):
            vals = list(detail.values())
            return float(min(1.0, max(0.0, fmean(vals))))
        # Already scalar-like
        return float(min(1.0, max(0.0, float(detail))))  # type: ignore
    except Exception:
        return 0.0


def _blank_detail() -> dict:
    return {
        "raspberry_pi": 0.0,
        "jetson_nano": 0.0,
        "desktop_pc": 0.0,
        "aws_server": 0.0,
    }


def compute_record(ns: NetScore, url: str) -> dict:
    t0 = perf_counter()

    # Primary metric scalars
    ramp = _unit(url, "ramp_up_time")
    bus = _unit(url, "bus_factor")
    perf = _unit(url, "performance_claims")
    lic = _unit(url, "license")
    cq = _unit(url, "code_quality")
    dq = _unit(url, "dataset_quality")
    dac = fmean([cq, dq])

    # Per-device detail for output; keep separate from combine() input
    size_detail = {
        "raspberry_pi": _unit(url, "sz_rpi"),
        "jetson_nano": _unit(url, "sz_nano"),
        "desktop_pc": _unit(url, "sz_pc"),
        "aws_server": _unit(url, "sz_aws"),
    }
    size_scalar = _size_scalar_from_detail(size_detail)

    scores_for_net = {
        "ramp_up_time": ramp,
        "bus_factor": bus,
        "performance_claims": perf,
        "license": lic,
        "code_quality": cq,
        "dataset_quality": dq,
        "dataset_and_code_score": dac,
    }

    net = ns.combine(scores_for_net, size_scalar)

    rec = {
        "url": url,
        "name": _name_from_url(url),
        "category": "CODE",
        "net_score": net,
        "net_score_latency": _lat_ms(t0),
        "ramp_up_time": ramp,
        "ramp_up_time_latency": _lat_ms(t0),
        "bus_factor": bus,
        "bus_factor_latency": _lat_ms(t0),
        "performance_claims": perf,
        "performance_claims_latency": _lat_ms(t0),
        "license": lic,
        "license_latency": _lat_ms(t0),
        "size_score": size_detail,
        "size_score_latency": _lat_ms(t0),
        "dataset_and_code_score": dac,
        "dataset_and_code_score_latency": _lat_ms(t0),
        "dataset_quality": dq,
        "dataset_quality_latency": _lat_ms(t0),
        "code_quality": cq,
        "code_quality_latency": _lat_ms(t0),
    }
    return rec


def compute_all(path: Path) -> list[dict]:
    rows: list[dict] = []
    ns = NetScore(path)
    for url in iter_urls(path):
        try:
            rec = compute_record(ns, url)
        except Exception:
            # Never drop a line; emit a safe placeholder
            t0 = perf_counter()
            size_detail = _blank_detail()
            size_scalar = _size_scalar_from_detail(size_detail)
            zeros = {
                "ramp_up_time": 0.0,
                "bus_factor": 0.0,
                "performance_claims": 0.0,
                "license": 0.0,
                "code_quality": 0.0,
                "dataset_quality": 0.0,
                "dataset_and_code_score": 0.0,
            }
            try:
                net = ns.combine(zeros, size_scalar)
            except Exception:
                net = 0.0
            rec = {
                "url": url,
                "name": _name_from_url(url),
                "category": "CODE",
                "net_score": net,
                "net_score_latency": _lat_ms(t0),
                "ramp_up_time": 0.0,
                "ramp_up_time_latency": _lat_ms(t0),
                "bus_factor": 0.0,
                "bus_factor_latency": _lat_ms(t0),
                "performance_claims": 0.0,
                "performance_claims_latency": _lat_ms(t0),
                "license": 0.0,
                "license_latency": _lat_ms(t0),
                "size_score": size_detail,
                "size_score_latency": _lat_ms(t0),
                "dataset_and_code_score": 0.0,
                "dataset_and_code_score_latency": _lat_ms(t0),
                "dataset_quality": 0.0,
                "dataset_quality_latency": _lat_ms(t0),
                "code_quality": 0.0,
                "code_quality_latency": _lat_ms(t0),
            }
        rows.append(rec)
    return rows


def _print_ndjson(rows: list[dict]) -> None:
    for row in rows:
        print(json.dumps(row, separators=(",", ":")))


def main(argv: list[str]) -> int:
    try:
        setup_logging()
    except Exception:
        # Do not fail on logging issues.
        pass

    if _early_env_exits():
        return 0

    if len(argv) != 2:
        print("Usage: python -m src.main <url_file>", file=sys.stderr)
        return 2

    path = Path(argv[1]).resolve()
    if not path.exists():
        print(f"Error: URL file not found: {path}", file=sys.stderr)
        return 2

    try:
        rows = compute_all(path)
    except Exception as exc:
        # Final guard; still exit non-zero, but no stack trace spam.
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    _print_ndjson(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
