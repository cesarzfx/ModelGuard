# src/main.py
from __future__ import annotations

import sys
from urllib.parse import urlparse

from src.logging_utils import setup_logging


def _name_from_url(url: str) -> str:
    """
    Extract a model/package name from a URL.
    Examples:
      https://huggingface.co/bert-base-uncased -> bert-base-uncased
      https://github.com/org/repo(.git)       -> repo
      https://pypi.org/project/black/         -> black
    """
    try:
        u = urlparse(url)
        path = (u.path or "").strip("/")
        if not path:
            return ""
        parts = [p for p in path.split("/") if p]
        name = parts[-1]
        if name.endswith(".git"):
            name = name[:-4]
        return name.lower()
    except Exception:
        return url.rstrip("/").split("/")[-1].lower()


def _early_env_exits() -> None:
    """Configure logging early; exits(2) if LOG_FILE is invalid."""
    setup_logging()


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint. Return 0 on success; non-zero on error."""
    argv = list(sys.argv[1:] if argv is None else argv)

    if "--just-init" in argv:
        try:
            _early_env_exits()
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
            return code
        return 0

    _early_env_exits()
    # TODO: existing CLI logic (return proper code)
    return 0


if __name__ == "__main__":
    sys.exit(main())
