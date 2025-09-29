import os
import pytest
from pathlib import Path
from src.logging_utils import setup_logging

def test_invalid_log_path_exits(tmp_path, monkeypatch):
    bad = tmp_path / "no" / "nested" / "app.log"
    monkeypatch.setenv("LOG_FILE", str(bad))
    with pytest.raises(SystemExit) as e:
        setup_logging()
    assert int(e.value.code) == 2
