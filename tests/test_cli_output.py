from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CLI = [sys.executable, "-m", "src.main"]


def test_help_flag_works():
    r = subprocess.run(CLI + ["--help"], capture_output=True, text=True)
    assert r.returncode == 0
    assert "usage" in (r.stdout.lower() + r.stderr.lower())


def test_iter_urls_and_processed_count(tmp_path: Path):
    urls = tmp_path / "u.txt"
    urls.write_text("# c1\nhttp://a\n\n# c2\nhttps://b\n", encoding="utf-8")
    r = subprocess.run(CLI + ["--urls", str(urls)],
                       capture_output=True, text=True)
    assert r.returncode == 0
    assert "processed: 2" in (r.stdout + r.stderr).lower()
