from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler

_SILENT = 100  # sentinel for "no logging, but create/truncate file"


def _parse_level(raw: str | None) -> int | None:
    if not raw:
        return None
    v = raw.strip().lower()
    if v in {"0", "off", "none", "silent"}:
        return _SILENT
    if v == "1":
        return logging.INFO
    if v == "2":
        return logging.DEBUG
    return getattr(logging, v.upper(), logging.INFO)


def setup_logging() -> None:
    lvl = _parse_level(os.getenv("LOG_LEVEL"))
    log_path = os.getenv("LOG_FILE", "app.log")

    if lvl == _SILENT:
        # Create/truncate the file but attach no handlers
        try:
            with open(log_path, "w", encoding="utf-8"):
                pass
        except Exception:
            # Even if path is bad, never crash
            pass
        return

    root = logging.getLogger()
    root.handlers[:] = []
    root.setLevel(lvl or logging.INFO)

    try:
        fh = RotatingFileHandler(
            log_path,
            maxBytes=1_000_000,
            backupCount=1,
            encoding="utf-8",
        )
        fh.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s: %(message)s"
            )
        )
        root.addHandler(fh)
    except Exception:
        # If file handler fails (bad path), fall back to STDERR
        sh = logging.StreamHandler()
        sh.setFormatter(
            logging.Formatter("%(levelname)s: %(message)s")
        )
        root.addHandler(sh)
