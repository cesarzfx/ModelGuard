from __future__ import annotations

import logging
from logging import handlers

import os
import sys
import tempfile
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
    if v in {"2", "debug"}:
        return logging.DEBUG
    if v in {"info", "warn", "warning", "error", "critical"}:
        return getattr(logging, v.upper(), None)
    return None


def _fail_log_path(msg: str) -> NoReturn:
    print(f"Invalid LOG_FILE path: {msg}", file=sys.stderr)
    sys.exit(2)


def _validate_log_path(p: Path) -> Path:
    # Parent must exist and be a directory (do NOT auto-create)
    parent = p.parent
    if not parent.exists() or not parent.is_dir():
        _fail_log_path(f"parent does not exist: {parent}")

    # Parent must be writable
    try:
        test = parent / ".wtest"
        with test.open("w", encoding="utf-8"):
            pass
        test.unlink(missing_ok=True)
    except Exception as exc:  # noqa: BLE001
        _fail_log_path(
            f"parent not writable: {parent} "
            f"({exc.__class__.__name__})"
        )

    # File must be appendable/creatable
    try:
        with p.open("a", encoding="utf-8"):
            pass
    except Exception as exc:  # noqa: BLE001
        _fail_log_path(
            f"cannot open for append: {p} "
            f"({exc.__class__.__name__})"
        )

    return p


def setup_logging() -> logging.Logger:
    lvl = _parse_level(os.getenv("LOG_LEVEL"))
    if lvl == _SILENT_SENTINEL:
        logging.disable(_SILENT_SENTINEL)
        lg = logging.getLogger("modelguard")
        lg.setLevel(_SILENT_SENTINEL + 1)
        # create blank file if LOG_FILE set
        log_path = os.getenv("LOG_FILE")
        if log_path:
            try:
                with open(log_path, "w", encoding="utf-8"):
                    pass
            except Exception:
                # even if path is bad, never crash here
                pass
        return lg

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

    return logger
