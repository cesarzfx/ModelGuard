# src/logging_utils.py
from __future__ import annotations

import logging
import os
import sys
from logging import handlers
from pathlib import Path

_SILENT_SENTINEL = 100


def _parse_level(raw: str | None) -> int | None:
    if raw is None:
        return None
    v = raw.strip().lower()
    if v in {"0", "off", "none", "silent"}:
        return _SILENT_SENTINEL
    if v == "1":
        return logging.INFO
    if v in {"2", "debug"}:
        return logging.DEBUG
    if v in {"info", "warn", "warning", "error", "critical"}:
        return getattr(logging, v.upper(), None)
    return None


def _fail_log_path(msg: str) -> "NoReturn":
    print(f"Invalid LOG_FILE path: {msg}", file=sys.stderr)
    sys.exit(2)


def _validate_log_path(p: Path) -> Path:
    # Parent must exist and be a directory (do NOT auto-create)
    if not p.parent.exists() or not p.parent.is_dir():
        _fail_log_path(f"parent does not exist: {p.parent}")
    # Parent must be writable
    try:
        test = p.parent / ".wtest"
        with test.open("w", encoding="utf-8"):
            pass
        test.unlink(missing_ok=True)
    except Exception as e:
        _fail_log_path(f"parent not writable: {p.parent} ({e.__class__.__name__})")
    # File must be appendable/creatable
    try:
        with p.open("a", encoding="utf-8"):
            pass
    except Exception as e:
        _fail_log_path(f"cannot open for append: {p} ({e.__class__.__name__})")
    return p


def setup_logging():
    lvl = _parse_level(os.getenv("LOG_LEVEL"))
    if lvl == _SILENT_SENTINEL:
        logging.disable(_SILENT_SENTINEL)
        lg = logging.getLogger("modelguard")
        lg.setLevel(_SILENT_SENTINEL + 1)
        return lg

    logger = logging.getLogger()
    logger.setLevel(lvl or logging.INFO)
    logger.handlers[:] = []

    # Always have a StreamHandler for stderr
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(sh)

    log_path = os.getenv("LOG_FILE")
    if log_path:
        p = _validate_log_path(Path(log_path))
        fh = handlers.RotatingFileHandler(
            p, maxBytes=1_000_000, backupCount=1, encoding="utf-8"
        )
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(fh)

    return logger
