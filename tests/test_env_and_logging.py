from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

CLI = [sys.executable, "-m", "src.main"]


def _run(env: dict[str, str]):
    e = os.environ.copy()
    e.update(env)
    return subprocess.run(CLI, env=e, capture_output=True, text=True)


def test_invalid_github_token_exits_nonzero():
    r = _run({"GITHUB_TOKEN": "bad token"})
    assert r.returncode != 0
    assert "invalid github token" in r.stderr.lower()


def test_invalid_log_dir_exits_nonzero(tmp_path: Path):
    bad = tmp_path / "nope" / "file.log"
    r = _run({"LOG_FILE": str(bad)})
    assert r.returncode != 0
    assert "invalid log path" in r.stderr.lower()


def test_log_level_zero_creates_blank(tmp_path: Path):
    f = tmp_path / "app.log"
    r = _run({"LOG_FILE": str(f), "LOG_LEVEL": "0"})
    assert f.exists()
    assert f.read_text(encoding="utf-8") == ""
    assert r.returncode == 0
