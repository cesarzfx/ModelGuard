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


def setup_logging() -> bool:
    """Configure logging from LOG_LEVEL and LOG_FILE.

    Returns:
        True if LOG_FILE appears valid and is used; False if logging to stderr.
    Notes:
        - Do not exit here (main() decides for env tests).
        - Never log to stdout.
        - Support 'silent' (disable logger).
    """
    level = _parse_level(os.getenv("LOG_LEVEL"))

    # Silent mode disables the root logger.
    if level == _SILENT_SENTINEL:
        logging.getLogger().disabled = True
        return False

    handlers: list[logging.Handler] = []
    used_file = False
    log_file = os.getenv("LOG_FILE")

    if log_file:
        try:
            fh = logging.FileHandler(log_file, encoding="utf-8")
            handlers.append(fh)
            used_file = True
        except Exception:
            handlers.append(logging.StreamHandler(sys.stderr))
            used_file = False
    else:
        handlers.append(logging.StreamHandler(sys.stderr))

    logging.basicConfig(
        level=level or logging.INFO,
        handlers=handlers,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        force=True,
    )
    return used_file
