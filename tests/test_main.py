"""
Tests for the main module, combining unit tests and integration tests
to ensure full coverage of command-line behavior.
"""
import subprocess
import sys
import json
from pathlib import Path

import pytest

# Assuming 'src' is in the project root, this allows importing from it.
# You may need to adjust your project structure or PYTHONPATH if this fails.
from src.main import (
    _name_from_url,
    _record,
    _size_detail,
    _size_scalar,
    _unit,
    iter_urls,
)

# Define the path to the script to make tests cleaner
SCRIPT_PATH = Path("src/main.py")

# --- Command-Line and Environment Tests (for Coverage) ---

def test_no_arguments():
    """Tests if the script exits with code 2 when no arguments are given."""
    result = subprocess.run(
        [sys.executable, SCRIPT_PATH], capture_output=True, text=True
    )
    assert result.returncode == 2
    assert "Usage: python -m src.main <url_file>" in result.stderr

def test_nonexistent_file():
    """Tests if the script exits with code 2 for a file that doesn't exist."""
    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, "nonexistent_file.txt"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "Error: URL file not found" in result.stderr

def test_missing_github_token(monkeypatch):
    """Tests if the script exits with code 1 if GITHUB_TOKEN is not set."""
    # Temporarily remove the GITHUB_TOKEN for this test
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    # This env var forces the token validation to run even under pytest
    monkeypatch.setenv("FORCE_GITHUB_TOKEN_VALIDATION", "1")

    # We need a dummy file to get past the initial file check
    with open("dummy_file.txt", "w") as f:
        f.write("test")

    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, "dummy_file.txt"],
        capture_output=True,
        text=True,
    )
    # Clean up the dummy file
    Path("dummy_file.txt").unlink()

    assert result.returncode == 1
    assert "Error: Invalid GitHub token" in result.stderr

def test_happy_path(tmp_path, monkeypatch):
    """Tests the script's main success case with a valid file."""
    # Set a dummy GitHub token so the check passes
    monkeypatch.setenv("GITHUB_TOKEN", "dummy_token_for_testing")

    # Create a temporary file with some URLs
    url_file = tmp_path / "urls.txt"
    urls_to_test = [
        "https://github.com/user1/repo1",
        "https://github.com/user2/a-model-repo",
    ]
    url_file.write_text("\n".join(urls_to_test))

    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, str(url_file)],
        capture_output=True,
        text=True,
    )

    # Check for successful exit and no errors
    assert result.returncode == 0
    assert result.stderr == ""

    # Check that the output is valid NDJSON
    lines = result.stdout.strip().split("\n")
    assert len(lines) == len(urls_to_test)
    for line in lines:
        data = json.loads(line)  # Will raise an error if not valid JSON
        assert "url" in data
        assert "net_score" in data
        assert "category" in data

# --- Unit Tests (from your original file) ---

def test_name_from_url():
    """Test extracting name from URL."""
    assert _name_from_url("https://github.com/user/repo") == "repo"
    assert _name_from_url("https://github.com/user/repo/") == "repo"
    assert _name_from_url("") == "artifact"

def test_unit_function():
    """Test the _unit function returns values between 0 and 1."""
    url = "https://example.com"
    salt = "test_salt"
    result = _unit(url, salt)
    assert 0.0 <= result <= 1.0

def test_size_detail():
    """Test the _size_detail function returns expected keys."""
    url = "https://example.com"
    detail = _size_detail(url)
    expected_keys = {"raspberry_pi", "jetson_nano", "desktop_pc", "aws_server"}
    assert set(detail.keys()) == expected_keys
    assert all(0.0 <= v <= 1.0 for v in detail.values())

def test_size_scalar():
    """Test the _size_scalar function."""
    # Test normal case (mean is clamped)
    detail = {"a": 0.1, "b": 0.3, "c": 0.5}
    assert _size_scalar(detail) == 0.3

    # Test empty dict
    assert _size_scalar({}) == 0.0

def test_record_structure(monkeypatch):
    """Test the _record function generates expected keys."""
    # Mock NetScore to isolate the _record function
    class MockNetScore:
        def combine(self, scores, sizes):
            return 0.5

    # Set a dummy token to pass the check inside _record
    monkeypatch.setenv("GITHUB_TOKEN", "dummy_token_for_testing")
    
    url = "https://example.com"
    ns = MockNetScore()
    record = _record(ns, url)

    expected_keys = {
        "url", "name", "category", "net_score", "net_score_latency",
        "ramp_up_time", "ramp_up_time_latency", "bus_factor",
        "bus_factor_latency", "performance_claims",
        "performance_claims_latency", "license", "license_latency",
        "size_score", "size_score_latency", "dataset_and_code_score",
        "dataset_and_code_score_latency", "dataset_quality",
        "dataset_quality_latency", "code_quality", "code_quality_latency"
    }
    assert set(record.keys()) == expected_keys
    assert record["url"] == url
    assert record["name"] == "example.com"
    assert record["category"] == "CODE"

def test_iter_urls(tmp_path):
    """Test the iter_urls function correctly ignores comments and blank lines."""
    file_content = "https://a.com\n# Comment\n\nhttps://b.com"
    url_file = tmp_path / "test_urls.txt"
    url_file.write_text(file_content)
    
    urls = list(iter_urls(url_file))
    assert urls == ["https://a.com", "https://b.com"]

