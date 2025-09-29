# tests/test_logging_invalid_path.py
from pathlib import Path

import pytest

from src.logging_utils import setup_logging


def test_invalid_log_path_exits(tmp_path: Path, monkeypatch) -> None:
    bad = tmp_path / "no" / "nested" / "app.log"
    monkeypatch.setenv("LOG_FILE", str(bad))
    with pytest.raises(SystemExit) as exc:
        setup_logging()
    assert int(exc.value.code) == 2
