from __future__ import annotations

import logging
import os
import sys


def _parse_level(env_val: str | None) -> str | None:
    """Return one of {'silent','debug','info','warning','error','critical'}
    or None.
    """
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
    """Configure root logging from env.

    Env:
      - LOG_LEVEL: 0/off/none/silent, 1/info, 2/debug, or standard names
      - LOG_FILE:  path to a file for logs; on failure, fall back to stderr

    Returns:
        (effective_level_name, sink) where sink is 'stderr'
        or the file path.
    """
    raw_level = os.getenv("LOG_LEVEL")
    level = _parse_level(raw_level) or logging.INFO

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    root: logging.Logger = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)

    log_file = os.getenv("LOG_FILE")

    # >>> Changed types here: use the common base class, never None
    handler: logging.Handler
    if log_file:
        try:
            handler = logging.FileHandler(log_file, encoding="utf-8")
            sink_desc = f"file:{log_file}"
        except OSError:
            handler = logging.StreamHandler(stream=sys.stderr)
            sink_desc = "stderr"
    else:
        handler = logging.StreamHandler(stream=sys.stderr)
        sink_desc = "stderr"
    # <<<

    handler.setLevel(level)
    handler.setFormatter(fmt)
    root.addHandler(handler)

    # Treat "silent" (100) as higher than CRITICAL so nothing emits
    effective_level = level if level != 100 else logging.CRITICAL + 1
    root.setLevel(effective_level)

    return logging.getLevelName(effective_level).lower(), sink_desc
