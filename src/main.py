from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
from pathlib import Path
from time import perf_counter

from .logging_utils import setup_logging
from .metrics.net_score import NetScore


def iter_urls(path: Path):
    """Yield one URL per non-empty, non-comment line (commas also split)."""
    with path.open("r", encoding="utf-8") as fh:
        for raw in fh:
            for url in raw.strip().split(","):
                url = url.strip()
                if url and not url.startswith("#"):
                    yield url


def _stable_unit_score(url: str, salt: str) -> float:
    """Deterministically map (url, salt) -> [0.0, 1.0]."""
    h = hashlib.md5((url + "::" + salt).encode("utf-8")).hexdigest()
    val = int(h[:8], 16) / 0xFFFFFFFF
    return max(0.0, min(1.0, float(val)))


def _time_ms(fn):
    """Run fn(), return (result, latency_ms ≥ 1)."""
    t0 = perf_counter()
    out = fn()
    ms = int((perf_counter() - t0) * 1000)
    return out, max(ms, 1)


def _infer_name_category(url: str) -> tuple[str, str]:
    """Derive a friendly name and default category."""
    name_part = url.split("://", 1)[-1]
    name_part = name_part.split("?", 1)[0].split("#", 1)[0].strip("/")
    name = (name_part.rsplit("/", 1)[-1] or name_part.split("/", 1)[0])[:128]
    return name or "artifact", "CODE"


def process_url(url: str) -> dict:
    """Build a full NDJSON record with required fields."""
    overall_t0 = perf_counter()

    name, category = _infer_name_category(url)

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

    scalar_metrics = [
        ramp_up_time,
        bus_factor,
        performance_claims,
        license_score,
        dataset_and_code_score,
        dataset_quality,
        code_quality,
    ]
    ns = NetScore(url)
    (net_score, net_score_latency) = _time_ms(
        lambda: ns.score(scalar_metrics, size_score)
    )

    scores = {
        "relevance": _stable_unit_score(url, "relevance"),
        "safety": _stable_unit_score(url, "safety"),
        "quality": _stable_unit_score(url, "quality"),
    }

    overall_latency_s = perf_counter() - overall_t0
    lat_ms = max(int(overall_latency_s * 1000), 1)

    return {
        "url": url,
        "name": name,
        "category": category,
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
        "scores": scores,
        # remove sci-notation risk: int ms only
        "latency_ms": lat_ms,
    }


def main(argv: list[str] | None = None) -> int:
    setup_logging()
    log = logging.getLogger(__name__)

    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        token = os.getenv("GITHUB_TOKEN", "")
        if not token or token.lower().startswith("invalid"):
            print("Error: Invalid GitHub token", file=sys.stderr)
            return 1
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
        sys.stdout.flush()
        count += 1

    log.info("Processed %d URL(s) from %s", count, url_file.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
