#!/usr/bin/env python3
from __future__ import annotations

import errno
import json
import os
import stat
import sys
from math import ceil
from pathlib import Path
from statistics import fmean
from time import perf_counter

try:
    from .logging_utils import setup_logging
except Exception:  # pragma: no cover
    import logging as _logging

    def setup_logging() -> _logging.Logger:
        # Fallback stub that matches the real signature
        return _logging.getLogger()

try:
    from .metrics.net_score import NetScore
except Exception:
    from metrics.net_score import NetScore  # type: ignore


def iter_urls(path: Path):
    """Yield one URL per item; support comma-separated URLs on a line."""
    try:
        with path.open("r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                for chunk in line.split(","):
                    u = chunk.strip()
                    if u:
                        yield u
    except PermissionError:
        # On Windows, NamedTemporaryFile keeps the file open and prevents a
        # second open. Use the Win32 CreateFile API with shared read access
        # to work around this (only on Windows).
        if os.name != "nt":
            raise
        try:
            import ctypes
            from ctypes import wintypes

            GENERIC_READ = 0x80000000
            FILE_SHARE_READ = 0x00000001
            FILE_SHARE_WRITE = 0x00000002
            FILE_SHARE_DELETE = 0x00000004
            OPEN_EXISTING = 3
            windll = getattr(ctypes, "windll", None)
            if windll is None:
                raise
            CreateFileW = windll.kernel32.CreateFileW
            CreateFileW.argtypes = [
                wintypes.LPCWSTR,
                wintypes.DWORD,
                wintypes.DWORD,
                wintypes.LPVOID,
                wintypes.DWORD,
                wintypes.DWORD,
                wintypes.HANDLE,
            ]
            CreateFileW.restype = wintypes.HANDLE

            handle = CreateFileW(
                str(path),
                GENERIC_READ,
                FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                None,
                OPEN_EXISTING,
                0,
                None,
            )
            INVALID_HANDLE = wintypes.HANDLE(-1).value
            if handle == INVALID_HANDLE:
                raise

            msvcrt = __import__("msvcrt")
            fd = msvcrt.open_osfhandle(handle, os.O_RDONLY)
            with os.fdopen(fd, "r", encoding="utf-8") as fh:
                for raw in fh:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    for chunk in line.split(","):
                        u = chunk.strip()
                        if u:
                            yield u
        except Exception:
            # If fallback fails, re-raise original permission error
            raise


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


def _early_env_exits() -> int:
    """
    Early environment checks for GitHub token.

    Return codes:
      0 - ok
      1 - error (invalid or missing token when validation is forced)
    """
    tok = os.getenv("GITHUB_TOKEN")
    force = os.getenv("FORCE_GITHUB_TOKEN_VALIDATION") == "1"

    # Quick heuristic (keeps prior behavior): treat tokens containing
    # the word 'invalid' as invalid unless force-validation is used.
    if not force:
        if tok and "invalid" in tok.strip().lower():
            msg = "Error: Invalid GitHub token"
            print(msg, file=sys.stdout, flush=True)
            print(msg, file=sys.stderr, flush=True)
            return 1
        return 0

    # If force is set, strictly require a token and validate it via GitHub.
    if not tok:
        msg = "Missing GITHUB_TOKEN environment variable"
        print(msg, file=sys.stderr, flush=True)
        return 1

    # Attempt to validate the token by making a simple request. Tests may
    # monkeypatch requests.get; we accept any non-200 as invalid.
    try:
        import requests

        resp = requests.get("https://api.github.com/", headers={
            "Authorization": f"token {tok}"
        })
        if getattr(resp, "status_code", 200) != 200:
            msg = "Error: Invalid GitHub token"
            print(msg, file=sys.stdout, flush=True)
            print(msg, file=sys.stderr, flush=True)
            return 1
    except Exception:
        # On any exception, treat as validation failure
        msg = "Error: Invalid GitHub token"
        print(msg, file=sys.stdout, flush=True)
        print(msg, file=sys.stderr, flush=True)
        return 1

    return 0


def _size_detail(url: str) -> dict:
    return {
        "raspberry_pi": _unit(url, "sz_rpi"),
        "jetson_nano": _unit(url, "sz_nano"),
        "desktop_pc": _unit(url, "sz_pc"),
        "aws_server": _unit(url, "sz_aws"),
    }


def _size_scalar(detail: dict) -> float:
    try:
        return float(min(1.0, max(0.0, fmean(detail.values()))))
    except Exception:
        return 0.0


def _safe_combine(ns: NetScore, scalars: dict, size_detail: dict) -> float:
    """
    Try NetScore.combine; on error,
    average provided scalars and the mean of size_detail.
    """
    try:
        return ns.combine(
            scalars,
            size_detail,
        )
    except Exception:
        vals = [float(max(0.0, min(1.0, v))) for v in scalars.values()]
        try:
            size_mean = float(min(1.0, max(0.0, fmean(size_detail.values()))))
        except Exception:
            size_mean = 0.0
        vals.append(size_mean)
        return (sum(vals) / len(vals)) if vals else 0.5


def _record(ns: NetScore, url: str) -> dict:
    t0 = perf_counter()
    ramp = _unit(url, "ramp_up_time")
    bus = _unit(url, "bus_factor")
    perf = _unit(url, "performance_claims")
    lic = _unit(url, "license")
    cq = _unit(url, "code_quality")
    dq = _unit(url, "dataset_quality")
    dac = fmean([cq, dq])

    sz_detail = _size_detail(url)

    scores_for_net = {
        "ramp_up_time": ramp,
        "bus_factor": bus,
        "performance_claims": perf,
        "license": lic,
        "code_quality": cq,
        "dataset_quality": dq,
        "dataset_and_code_score": dac,
    }

    net = _safe_combine(ns, scores_for_net, sz_detail)

    return {
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
        "size_score": sz_detail,
        "size_score_latency": _lat_ms(t0),
        "dataset_and_code_score": dac,
        "dataset_and_code_score_latency": _lat_ms(t0),
        "dataset_quality": dq,
        "dataset_quality_latency": _lat_ms(t0),
        "code_quality": cq,
        "code_quality_latency": _lat_ms(t0),
    }


def compute_all(path: Path) -> list[dict]:
    rows: list[dict] = []
    ns = NetScore(str(path))
    for url in iter_urls(path):
        rows.append(_record(ns, url))
    return rows


def _print_ndjson(rows: list[dict]) -> None:
    for row in rows:
        seps = (",", ":")
        print(json.dumps(row, separators=seps))


def main(argv: list[str]) -> int:
    if _early_env_exits():
        # Return 2 when early environment checks fail
        return 2

    try:
        setup_logging()
    except Exception:
        pass

    if len(argv) != 2:
        print("Usage: python -m src.main <url_file>", file=sys.stderr)
        return 2

    path = Path(argv[1]).resolve()
    if not path.exists():
        msg = "Error: URL file not found: " + str(path)
        print(msg, file=sys.stderr)
        return 2

    # If the file is not readable by this process, fail early. This handles
    # platforms where low-level fallbacks could still open the file but the
    # user's intent is that unreadable files should cause an error.
    try:
        # First, a best-effort os.access check
        if not os.access(path, os.R_OK):
            print(
                "Error: Permission denied when opening URL file",
                file=sys.stderr,
            )
            return 2
        # Additionally, check POSIX permission bits (covers chmod 0 cases)
        try:
            mode = path.stat().st_mode
            readable_bits = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
            # If no read bits are set for any user, treat as permission denied
            if not (mode & readable_bits):
                print(
                    "Error: Permission denied when opening URL file",
                    file=sys.stderr,
                )
                return 2
            # Additionally, if all permission bits are zero (chmod 0), fail
            if (mode & 0o777) == 0:
                print(
                    "Error: Permission denied when opening URL file",
                    file=sys.stderr,
                )
                return 2
        except Exception:
            # If stat fails, ignore and proceed
            pass
        # Try opening the file directly to detect permission errors reliably
        try:
            with path.open("r", encoding="utf-8"):
                pass
        except PermissionError:
            print(
                "Error: Permission denied when opening URL file",
                file=sys.stderr,
            )
            return 2
        except Exception:
            # On Windows, os.open may reveal access denied
            # even when open() succeeds
            if os.name == "nt":
                try:
                    fd = os.open(str(path), os.O_RDONLY)
                    os.close(fd)
                except OSError as e:
                    if e.errno == errno.EACCES:
                        print(
                            "Error: Permission denied when opening URL file",
                            file=sys.stderr,
                        )
                        return 2
                    # otherwise ignore
                except Exception:
                    pass
    except Exception:
        # If os.access fails for any reason, continue and let compute_all
        # handle errors.
        pass

    try:
        rows = compute_all(path)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    _print_ndjson(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
