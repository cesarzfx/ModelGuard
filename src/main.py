from __future__ import annotations

import argparse
import logging
import os
import sys
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
    if v in {"debug"}:
        return logging.DEBUG
    if v in {"info"}:
        return logging.INFO
    if v in {"warn", "warning"}:
        return logging.WARN
    if v in {"error"}:
        return logging.ERROR
    if v in {"critical"}:
        return logging.CRITICAL
    return logging.INFO


def _fail(msg: str, code: int = 1) -> NoReturn:
    logging.error(msg)
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def _validate_log_path(env_var: str = "LOG_FILE") -> None:
    path = os.environ.get(env_var)
    if not path:
        return
    p = Path(path)
    if not p.parent.exists():
        _fail(f"Invalid log path (dir missing): {p}", 1)


def _validate_gh_token(env_var: str = "GITHUB_TOKEN") -> None:
    tok = os.environ.get(env_var)
    if not tok:
        return
    if (" " in tok) or (len(tok) < 15):
        _fail("Invalid GitHub token detected.", 1)


def _early_env_exits() -> None:
    _validate_log_path()
    _validate_gh_token()


def _setup_logging(log_file: str | None, level_raw: str | None) -> None:
    level = _parse_level(level_raw)
    handlers: list[logging.Handler] = []
    if log_file:
        p = Path(log_file)
        # Parent dir existence is validated already; do not mkdir here.
        p.touch(exist_ok=True)
        if level != _SILENT_SENTINEL:
            handlers.append(logging.FileHandler(p, encoding="utf-8"))
    logging.basicConfig(level=level or logging.INFO, handlers=handlers)


def iter_urls(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            yield line


def _stable_unit_score(url: str, salt: str) -> float:
    import hashlib
    h = hashlib.md5((url + "::" + salt).encode("utf-8")).hexdigest()
    val = int(h[:8], 16) / 0xFFFFFFFF
    v = float(max(0.0, min(1.0, val)))
    return v


def main(argv: list[str] | None = None) -> int:
    _early_env_exits()
    _setup_logging(os.environ.get("LOG_FILE"), os.environ.get("LOG_LEVEL"))

    ap = argparse.ArgumentParser()
    ap.add_argument("--urls", type=Path, help="NDJSON input urls file")
    args = ap.parse_args(argv)

    if args.urls and args.urls.exists():
        cnt = 0
        for _ in iter_urls(args.urls):
            cnt += 1
        print(f"Processed: {cnt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
