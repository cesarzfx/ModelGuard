# src/logging_utils.py
from __future__ import annotations

import logging
import os
import sys

# Define a sentinel value for "silent" mode that is safely above any
# standard logging level (CRITICAL is 50).
_SILENT_SENTINEL = 100


def _parse_level(raw: str | None) -> int | None:
    """Map an environment variable string to a logging level integer.

    This function provides user-friendly shortcuts for setting the log level.

    Args:
        raw: The raw string from the LOG_LEVEL environment variable.

    Returns:
        The corresponding logging level constant (e.g., logging.INFO),
        the silent sentinel value, or None if the input is empty.
    """
    if not raw:
        return None

    val = raw.strip().lower()

    # Numeric and special string mappings
    if val in {"0", "off", "none", "silent"}:
        return _SILENT_SENTINEL
    if val == "1":
        return logging.INFO
    if val == "2":
        return logging.DEBUG

    # Standard logging level names
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
    # Determine the logging level, defaulting to WARNING for clean output.
    parsed_level = _parse_level(os.getenv("LOG_LEVEL"))
    level = logging.WARNING if parsed_level is None else parsed_level

    # Reset handlers to ensure our configuration is the only one active.
    # This prevents duplicate log messages if this function is called multiple times.
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)

    log_file = os.getenv("LOG_FILE")

    # --- Robustly determine the log handler ---
    if log_file:
        try:
            # If a log file is specified, attempt to use it.
            handler: logging.Handler = logging.FileHandler(
                log_file, encoding="utf-8"
            )
            sink_desc = log_file
        except OSError as e:
            # If the log file cannot be opened, it's a critical configuration
            # error. Print a message to stderr and exit.
            print(
                f"Error: cannot open log file '{log_file}': {e}",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        # If no log file is specified, default to logging to the console.
        handler = logging.StreamHandler(stream=sys.stderr)
        sink_desc = "stderr"

    # --- Configure formatter and apply handler ---
    log_format = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
    )
    handler.setFormatter(log_format)

    # Special handling for "silent" mode.
    if level == _SILENT_SENTINEL:
        root.addHandler(handler)
        # Set the root level higher than any possible message to suppress all output.
        root.setLevel(logging.CRITICAL + 1)
        return "silent", sink_desc

    # For standard levels, apply the level to both the handler and the root logger.
    handler.setLevel(level)
    root.addHandler(handler)
    root.setLevel(level)

    return logging.getLevelName(level).lower(), sink_desc