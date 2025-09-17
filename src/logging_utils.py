from __future__ import annotations

import logging
import os
import sys


def _parse_level(env_val: str | None) -> str | None:
    """Return one of {'silent','debug','info','warning','error','critical'} or None."""
    if env_val is None:
        return None
    val = env_val.strip().lower()

    # numeric shortcuts per spec
    if val in {"0", "off", "none"}:
        return "silent"
    if val in {"1"}:
        return "info"
    if val in {"2"}:
        return "debug"

    # common names
    aliases = {
        "silent": "silent",
        "debug": "debug",
        "info": "info",
        "warn": "warning",
        "warning": "warning",
        "error": "error",
        "critical": "critical",
    }
    return aliases.get(val)


def setup_logging() -> tuple[str, str]:
    """
    Configure root logging from env:
      - LOG_LEVEL: 0/off/none/silent, 1/info, 2/debug, or standard names
      - LOG_FILE:  path to a file for logs; on failure, fall back to stderr

    Returns (effective_level_name, sink) where sink is 'stderr' or the file path.
    """
    level_name = _parse_level(os.getenv("LOG_LEVEL"))
    sink_desc = "stderr"

    root = logging.getLogger()
    # Remove any default handlers so we fully control sinks.
    for h in list(root.handlers):
        root.removeHandler(h)

    if level_name == "silent":
        # Disable logging entirely (no stdout pollution).
        root.setLevel(logging.CRITICAL + 1)
        root.addHandler(logging.NullHandler())
        return "silent", sink_desc

    # Map names to logging levels; default to WARNING if invalid/unspecified.
    name_to_level = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    level = name_to_level.get(level_name or "warning", logging.WARNING)

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    handler = None
    log_file = os.getenv("LOG_FILE")
    if log_file:
        try:
            handler = logging.FileHandler(log_file, encoding="utf-8")
            sink_desc = log_file
        except Exception:
            # If the file path is invalid/unwritable, quietly fall back to stderr.
            handler = logging.StreamHandler(stream=sys.stderr)
            sink_desc = "stderr"
    else:
        handler = logging.StreamHandler(stream=sys.stderr)
        sink_desc = "stderr"

    handler.setLevel(level)
    handler.setFormatter(fmt)
    root.addHandler(handler)
    root.setLevel(level)

    return logging.getLevelName(level).lower(), sink_desc
