from __future__ import annotations

import logging
import os
from logging import handlers

_SILENT_SENTINEL = 100


def _parse_level(raw: str | None) -> int | None:
    if raw is None:
        return None
    v = raw.strip().lower()
    if v in {"0", "off", "none", "silent"}:
        return _SILENT_SENTINEL
    if v == "1":
        return logging.INFO
    if v == "2":
        return logging.DEBUG
    return getattr(logging, v.upper(), logging.INFO)


def setup_logging() -> None:
    lvl = _parse_level(os.getenv("LOG_LEVEL"))
    log_path = os.getenv("LOG_FILE", "app.log")

    if lvl == _SILENT_SENTINEL:
        try:
            with open(log_path, "w", encoding="utf-8"):
                pass
        except Exception:
            pass
        return

    import logging
    from logging import handlers

    root = logging.getLogger()
    root.handlers[:] = []
    root.setLevel(lvl or logging.INFO)

    try:
        fh = handlers.RotatingFileHandler(
            log_path, maxBytes=1_000_000, backupCount=1, encoding="utf-8"
        )
        fh.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s"
        ))
        root.addHandler(fh)
    except Exception:
        sh = logging.StreamHandler()  # fallback, don’t crash tests
        sh.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        root.addHandler(sh)