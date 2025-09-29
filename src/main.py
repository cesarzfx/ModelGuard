from __future__ import annotations

import sys

from src.logging_utils import setup_logging


def _early_env_exits() -> None:
    # Make sure logging is configured; will exit(2) on bad LOG_FILE
    setup_logging()


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint. Return 0 on success; nonzero on error."""
    argv = list(sys.argv[1:] if argv is None else argv)

    # lightweight init path used by tests/CI
    if "--just-init" in argv:
        try:
            _early_env_exits()
        except SystemExit as e:
            return int(e.code)  # propagate non-zero exit
        return 0

    # normal startup
    _early_env_exits()

    # TODO: your actual CLI logic goes here. Make sure to return an int.
    # If you already compute a status code 'rc', return rc at the end.
    return 0


if __name__ == "__main__":
    sys.exit(main())
