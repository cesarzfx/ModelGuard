from __future__ import annotations
import logging, os

_SILENT = 100

def _parse_level(raw: str | None) -> int | None:
    if raw is None:
        return None
    v = raw.strip().lower()
    if v in {"0", "off", "none", "silent"}:
        return _SILENT
    if v == "1":
        return logging.INFO
    if v == "2" or v == "debug":
        return logging.DEBUG
    if v in {"info"}:
        return logging.INFO
    if v in {"warn", "warning"}:
        return logging.WARNING
    if v in {"error"}:
        return logging.ERROR
    if v in {"critical"}:
        return logging.CRITICAL
    return None

def setup_logging() -> None:
    path = os.environ.get("LOG_FILE")
    level = _parse_level(os.environ.get("LOG_LEVEL")) or _SILENT

    if path and level != _SILENT:
        logging.basicConfig(
            filename=path,
            level=level,
            format="%(asctime)s %(levelname)s %(message)s",
        )
    else:
        # quiet stdout by default; allow debug during dev
        logging.basicConfig(level=logging.CRITICAL)
