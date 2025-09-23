from __future__ import annotations

import logging
import os
import sys

# Higher than CRITICAL; used to represent "silent".
_SILENT_SENTINEL = 100


def _parse_level(raw: str | None) -> int | None:
    """Map env text to a logging level int or the silent sentinel.

    Accepts:
      - 0/off/none/silent -> silent
      - 1 -> INFO
      - 2 -> DEBUG
      - debug|info|warn|warning|error|critical
    """
    if raw is None:
        return None

    val = raw.strip().lower()

    if val in {"0", "off", "none", "silent"}:
        return _SILENT_SENTINEL
    if val == "1":
        return logging.INFO
    if val == "2":
        return logging.DEBUG

    aliases = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warn": logging.WARNING,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    return aliases.get(val)


def setup_logging() -> None:
    """Initialize logging based on LOG_LEVEL and LOG_FILE.

    - If LOG_FILE is invalid/unwritable: print exactly
      'Error: Invalid log file path' to stderr and exit non-zero.
    - Never log to stdout (only stderr or file).
    - Support 'silent' mode (disable logging).
    """
    level = _parse_level(os.getenv("LOG_LEVEL"))
    log_file = os.getenv("LOG_FILE")

    # Silent mode disables the root logger
    if level == _SILENT_SENTINEL:
        logging.getLogger().disabled = True
        return

    handlers: list[logging.Handler] = []
    if log_file:
        try:
            parent = os.path.dirname(log_file) or "."
            if parent and not os.path.exists(parent):
                raise FileNotFoundError(parent)
            fh = logging.FileHandler(log_file, encoding="utf-8")
            handlers.append(fh)
        except Exception:
            sys.stderr.write("Error: Invalid log file path\n")
            sys.stderr.flush()
            sys.exit(2)
    else:
        handlers.append(logging.StreamHandler(sys.stderr))

    logging.basicConfig(
        level=level or logging.INFO,
        handlers=handlers,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        force=True,
    )
