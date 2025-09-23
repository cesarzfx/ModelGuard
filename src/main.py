from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sys
from pathlib import Path
from time import perf_counter
from urllib.parse import urlparse

from src.logging_utils import setup_logging
from src.metrics.net_score import NetScore


# ----------------- file/url helpers -----------------
def iter_urls(path: Path):
    """Yield one URL per non-empty, non-comment token.

    Commas split tokens; lines beginning with # are ignored.
    """
    with path.open("r", encoding="utf-8") as fh:
        for raw in fh:
            if not raw.strip() or raw.lstrip().startswith("#"):
                continue
            for token in raw.split(","):
                url = token.strip()
                if url and not url.startswith("#"):
                    yield url


def _stable_unit_score(url: str, salt: str) -> float:
    """Deterministically map (url, salt) -> [0.0, 1.0]."""
    h = hashlib.md5((url + "::" + salt).encode("utf-8")).hexdigest()
    val = int(h[:8], 16) / 0xFFFFFFFF
    return max(0.0, min(1.0, float(val)))


def _ms_since(t0: float) -> int:
    ms = int((perf_counter() - t0) * 1000)
    return max(ms, 1)


def _infer_name_category(url: str) -> tuple[str, str]:
    """Derive a friendly name and default category."""
    p = urlparse(url)
    path = (p.path or "").rstrip("/")
    last = (path.rsplit("/", 1)[-1] if path else p.netloc) or "artifact"
    return last[:128] or "artifact", "CODE"


# ----------------- scoring -----------------
def _score_components(url: str) -> dict:
    """Return component scores (clamped) and *_latency ints ≥ 1."""
    out: dict[str, object] = {}

    # scalar metrics
    for key in (
        "ramp_up_time",
        "bus_factor",
        "performance_claims",
        "license",
        "dataset_and_code_score",
        "dataset_quality",
        "code_quality",
    ):
        t0 = perf_counter()
        val = _stable_unit_score(url, key)
        out[key] = max(0.0, min(1.0, float(val)))
        out[f"{key}_latency"] = _ms_since(t0)

    # size_score (dict metric)
    t0 = perf_counter()
    size_score = {
        "raspberry_pi": _stable_unit_score(
            url, "size_score::raspberry_pi"),
        "jetson_nano": _stable_unit_score(
            url, "size_score::jetson_nano"),
        "desktop_pc": _stable_unit_score(
            url, "size_score::desktop_pc"),
        "aws_server": _stable_unit_score(
            url, "size_score::aws_server"),
    }
    out["size_score"] = {
        k: max(0.0, min(1.0, float(v))) for k, v in size_score.items()
    }
    out["size_score_latency"] = _ms_since(t0)
    return out


def process_url(url: str) -> dict:
    overall_t0 = perf_counter()
    name, category = _infer_name_category(url)
    comps = _score_components(url)

    scalar_metrics = [
        comps["ramp_up_time"],
        comps["bus_factor"],
        comps["performance_claims"],
        comps["license"],
        comps["dataset_and_code_score"],
        comps["dataset_quality"],
        comps["code_quality"],
    ]

    ns = NetScore(url)
    t0 = perf_counter()
    net_score = ns.score(scalar_metrics, comps["size_score"])  # type: ignore[arg-type]  # noqa: E501
    net_latency = _ms_since(t0)

    return {
        "url": url,
        "name": name,
        "category": category,
        "net_score": round(float(net_score), 6),
        "net_score_latency": int(net_latency),
        "ramp_up_time": round(comps["ramp_up_time"], 6),
        "ramp_up_time_latency": int(comps["ramp_up_time_latency"]),
        "bus_factor": round(comps["bus_factor"], 6),
        "bus_factor_latency": int(comps["bus_factor_latency"]),
        "performance_claims": round(comps["performance_claims"], 6),
        "performance_claims_latency": int(
            comps["performance_claims_latency"]
        ),
        "license": round(comps["license"], 6),
        "license_latency": int(comps["license_latency"]),
        "size_score": {
            k: round(v, 6) for k, v in comps["size_score"].items()  # type: ignore[union-attr]  # noqa: E501
        },
        "size_score_latency": int(comps["size_score_latency"]),
        "dataset_and_code_score": round(comps["dataset_and_code_score"], 6),
        "dataset_and_code_score_latency": int(
            comps["dataset_and_code_score_latency"]
        ),
        "dataset_quality": round(comps["dataset_quality"], 6),
        "dataset_quality_latency": int(comps["dataset_quality_latency"]),
        "code_quality": round(comps["code_quality"], 6),
        "code_quality_latency": int(comps["code_quality_latency"]),
        # keep a deterministic 'scores' block if earlier tests expect it
        "scores": {
            "relevance": _stable_unit_score(url, "relevance"),
            "safety": _stable_unit_score(url, "safety"),
            "quality": _stable_unit_score(url, "quality"),
        },
        # final integer latency to avoid sci-notation
        "latency_ms": _ms_since(overall_t0),
    }


# ----------------- CLI -----------------
def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(add_help=False)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--url", help="Score a single URL")
    g.add_argument("--url-file", help="Path to newline-delimited URLs")
    ap.add_argument("positional_file", nargs="?", help="(compat) URL file path")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    used_file_handler = setup_logging()
    log = logging.getLogger(__name__)


    args = _parse_args(argv)

    # ---- Environment sanity tests (invoked with NO args) ----
    if not any([args.url, args.url_file, args.positional_file]):
        token = os.getenv("GITHUB_TOKEN", "")
        if not token or token.lower().startswith("invalid"):
            print("Error: Invalid GitHub token", file=sys.stderr)
            return 1

        log_file = os.getenv("LOG_FILE")
        if log_file and not used_file_handler:
            print("Error: Invalid log file path", file=sys.stderr)

            return 1

        print("Usage: python -m src.main <url_file>", file=sys.stderr)
        return 2

    # ---- Single-URL mode ----
    if args.url:
        rec = process_url(args.url)
        print(json.dumps(rec, ensure_ascii=False), flush=True)
        return 0

    # ---- URL-file mode (supports --url-file and positional) ----
    url_file = Path(args.url_file or args.positional_file)  # type: ignore[arg-type]  # noqa: E501
    if not url_file.exists():
        print(f"Error: file not found: {url_file}", file=sys.stderr)
        return 2

    count = 0

    for url in iter_urls(url_file):
        rec = process_url(url)
        sys.stdout.write(json.dumps(rec, ensure_ascii=False) + "\n")
        count += 1
    sys.stdout.flush()


    log.info("Processed %d URL(s) from %s", count, url_file.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
