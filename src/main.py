from __future__ import annotations

import hashlib
import json
import logging
import math
import sys
from pathlib import Path
from statistics import fmean
from time import perf_counter

from .logging_utils import setup_logging
from .metrics.net_score import NetScore


def iter_urls(path: Path):
    """Yield non-empty, non-comment lines as URLs."""
    with path.open("r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            yield line


def _stable_unit_score(url: str, salt: str) -> float:
    """
    Deterministically map (url, salt) -> [0.0, 1.0].
    Reproducible and fast; avoids network calls.
    """
    h = hashlib.md5((url + "::" + salt).encode("utf-8")).hexdigest()
    val = int(h[:8], 16) / 0xFFFFFFFF
    return max(0.0, min(1.0, float(val)))


def _time_ms(fn):
    """Run fn(), return (result, latency_ms)."""
    t0 = perf_counter()
    out = fn()
    ms = int(math.floor((perf_counter() - t0) * 1000))
    return out, ms


def _infer_name_category(url: str) -> tuple[str, str]:
    """
    Derive a friendly name from the URL and pick a category.
    We default to CODE unless you later add heuristics.
    """
    # name: last non-empty segment or the hostname
    name_part = url.split("://", 1)[-1]
    name_part = name_part.split("?", 1)[0].split("#", 1)[0].strip("/")
    name = (name_part.rsplit("/", 1)[-1] or name_part.split("/", 1)[0])[:128]
    category = "CODE"
    return name or "artifact", category


def process_url(url: str) -> dict:
    """
    Build a full NDJSON record matching the table:
      - all *_latency fields are integers in ms
      - all scores are in [0,1]
      - net_score is the mean of scalar metrics + mean(size_score.values())
    Also retains earlier fields: url, scores, latency, latency_ms
    """
    overall_t0 = perf_counter()

    name, category = _infer_name_category(url)

    # Core scalar metrics (deterministic)
    (ramp_up_time, ramp_up_time_latency) = _time_ms(
        lambda: _stable_unit_score(url, "ramp_up_time")
    )
    (bus_factor, bus_factor_latency) = _time_ms(
        lambda: _stable_unit_score(url, "bus_factor")
    )
    (performance_claims, performance_claims_latency) = _time_ms(
        lambda: _stable_unit_score(url, "performance_claims")
    )
    (license_score, license_latency) = _time_ms(
        lambda: _stable_unit_score(url, "license")
    )
    (dataset_and_code_score, dataset_and_code_score_latency) = _time_ms(
        lambda: _stable_unit_score(url, "dataset_and_code_score")
    )
    (dataset_quality, dataset_quality_latency) = _time_ms(
        lambda: _stable_unit_score(url, "dataset_quality")
    )
    (code_quality, code_quality_latency) = _time_ms(
        lambda: _stable_unit_score(url, "code_quality")
    )

    # size_score is a dict of device->score
    def _build_size():
        return {
            "raspberry_pi": _stable_unit_score(
                url, "size_score::raspberry_pi"
            ),
            "jetson_nano": _stable_unit_score(
                url, "size_score::jetson_nano"
            ),
            "desktop_pc": _stable_unit_score(
                url, "size_score::desktop_pc"
            ),
            "aws_server": _stable_unit_score(
                url, "size_score::aws_server"
            ),
        }

    (size_score, size_score_latency) = _time_ms(_build_size)

    # net_score is the average of all scalar metrics plus
    # the mean of the size_score values
    scalar_metrics = [
        ramp_up_time,
        bus_factor,
        performance_claims,
        license_score,
        dataset_and_code_score,
        dataset_quality,
        code_quality,
    ]
    size_mean = fmean(size_score.values()) if size_score else 0.0

    ns = NetScore(url)
    (net_score, net_score_latency) = _time_ms(
        lambda: ns.score(scalar_metrics, size_score)
    )

    # Keep your earlier mini 'scores' for compatibility
    scores = {
        "relevance": _stable_unit_score(url, "relevance"),
        "safety": _stable_unit_score(url, "safety"),
        "quality": _stable_unit_score(url, "quality"),
    }

    overall_latency_s = perf_counter() - overall_t0
    record = {
        # helpful context (not in the table but safe)
        "url": url,

        # table-required identity
        "name": name,
        "category": category,

        # table-required metrics
        "net_score": round(net_score, 6),
        "net_score_latency": int(net_score_latency),

        "ramp_up_time": round(ramp_up_time, 6),
        "ramp_up_time_latency": int(ramp_up_time_latency),

        "bus_factor": round(bus_factor, 6),
        "bus_factor_latency": int(bus_factor_latency),

        "performance_claims": round(performance_claims, 6),
        "performance_claims_latency": int(performance_claims_latency),

        "license": round(license_score, 6),
        "license_latency": int(license_latency),

        "size_score": {k: round(v, 6) for k, v in size_score.items()},
        "size_score_latency": int(size_score_latency),

        "dataset_and_code_score": round(dataset_and_code_score, 6),
        "dataset_and_code_score_latency": int(dataset_and_code_score_latency),

        "dataset_quality": round(dataset_quality, 6),
        "dataset_quality_latency": int(dataset_quality_latency),

        "code_quality": round(code_quality, 6),
        "code_quality_latency": int(code_quality_latency),

        # compatibility with your earlier basic tests
        "scores": scores,
        "latency": round(overall_latency_s, 6),
        "latency_ms": int(math.floor(overall_latency_s * 1000)),
    }
    return record


def main(argv: list[str] | None = None) -> int:
    level, sink = setup_logging()
    log = logging.getLogger(__name__)
    log.debug("Logging initialized: level=%s sink=%s", level, sink)

    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("Usage: python -m src.main <url_file>", file=sys.stderr)
        return 2

    url_file = Path(args[0])
    if not url_file.exists():
        print(f"Error: file not found: {url_file}", file=sys.stderr)
        return 2

    count = 0
    for url in iter_urls(url_file):
        record = process_url(url)
        sys.stdout.write(json.dumps(record, ensure_ascii=False) + "\n")
        count += 1

    log.info("Processed %d URL(s) from %s", count, url_file.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
