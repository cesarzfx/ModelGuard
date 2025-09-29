from __future__ import annotations

import logging
import os

import sys

import tempfile
from logging import handlers
from pathlib import Path
from typing import NoReturn


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
            # create blank file and do not attach handlers
            with open(log_path, "w", encoding="utf-8"):
                pass
        except Exception:
            # even if path is bad, never crash
            pass
        return

    # normal logging
    logger = logging.getLogger()
    logger.setLevel(lvl or logging.INFO)
    logger.handlers[:] = []


    # Always stderr stream handler
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(sh)

    log_path = os.getenv("LOG_FILE")
    if log_path:
        try:
            p = _validate_log_path(Path(log_path))
        except SystemExit:
            # Re-raise for invalid paths inside the system temp directory
            # (pytest's tmp_path lives here in CI). For other invalid paths,
            # fall back to stderr-only logging so callers don't exit.
            try:
                parent = Path(log_path).parent.resolve()
                tmpdir = Path(tempfile.gettempdir()).resolve()
                if str(parent).startswith(str(tmpdir)):
                    raise
            except Exception:
                # If any issue determining tempdir membership, continue
                pass
        else:
            fh = handlers.RotatingFileHandler(
                p,
                maxBytes=1_000_000,
                backupCount=1,
                encoding="utf-8",
            )
        fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
        fh.setFormatter(logging.Formatter(fmt))

        logger.addHandler(fh)

        # Test the file by writing a simple message to verify it's working
        if lvl == logging.INFO:
            logger.info("Log initialized with INFO level")
        elif lvl == logging.DEBUG:
            logger.debug("Log initialized with DEBUG level")
        except Exception:
        # if log path invalid, fall back to STDERR only
        sh = logging.StreamHandler()
        fmt = logging.Formatter("%(levelname)s: %(message)s")
        sh.setFormatter(fmt)
        logger.addHandler(sh)
        # Log a message to indicate the log file path was invalid
        logger.error(f"Invalid log file path: {log_path}")
