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


def setup_logging() -> tuple[str, str]:
    """Configure logging from LOG_LEVEL and LOG_FILE.

    Returns a pair (level_name, sink) where sink is 'stderr' or a path.
    """
    parsed = _parse_level(os.getenv("LOG_LEVEL"))
    level = logging.WARNING if parsed is None else parsed

    # Reset handlers so we control sinks deterministically.
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)

    log_file = os.getenv("LOG_FILE")
    try:
        if log_file:
            handler: logging.Handler = logging.FileHandler(
                log_file, encoding="utf-8"
            )
            sink_desc = log_file
        else:
            handler = logging.StreamHandler(stream=sys.stderr)
            sink_desc = "stderr"
    except OSError:
        handler = logging.StreamHandler(stream=sys.stderr)
        sink_desc = "stderr"

    fmt = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    handler.setFormatter(fmt)

    # Silent mode: attach a handler but raise the root level above CRITICAL.
    if level == _SILENT_SENTINEL:
        root.addHandler(handler)
        root.setLevel(logging.CRITICAL + 1)
        return "silent", sink_desc

    handler.setLevel(level)
    root.addHandler(handler)
    root.setLevel(level)

    return logging.getLevelName(level).lower(), sink_desc
