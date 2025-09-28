"""
Additional tests for main module.
"""
import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from src.main import (
    _early_env_exits,
    _lat_ms,
    _print_ndjson,
    compute_all,
    main,
)


def test_lat_ms():
    """Test the _lat_ms function."""
    # Test with a small time difference
    assert _lat_ms(perf_counter() - 0.001) >= 1
    # Test with a larger time difference
    assert _lat_ms(perf_counter() - 1.5) >= 1


def test_print_ndjson(capsys):
    """Test _print_ndjson function."""
    rows = [
        {"name": "test1", "value": 1},
        {"name": "test2", "value": 2}
    ]
    _print_ndjson(rows)
    
    captured = capsys.readouterr()
    assert '{"name":"test1","value":1}' in captured.out
    assert '{"name":"test2","value":2}' in captured.out


def test_main_invalid_args():
    """Test main function with invalid arguments."""
    # Test with no arguments
    assert main([]) == 2
    
    # Test with non-existent file
    with tempfile.NamedTemporaryFile() as tmp:
        non_existent = tmp.name
    assert main(["program", non_existent]) == 2


def test_main_with_valid_file():
    """Test main function with a valid file."""
    # Create a temporary file with URLs
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
        tmp.write("https://example.com\n")
        tmp.flush()
        tmp_path = tmp.name
    
    # Mock compute_all to return a predefined result
    with mock.patch('src.main.compute_all') as mock_compute:
        mock_compute.return_value = [{"url": "https://example.com"}]
        
        # Mock _print_ndjson to avoid actual printing
        with mock.patch('src.main._print_ndjson'):
            result = main(["program", tmp_path])
            assert result == 0
    
    # Clean up
    os.unlink(tmp_path)


def test_main_with_exception():
    """Test main function when compute_all raises an exception."""
    # Create a temporary file with URLs
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
        tmp.write("https://example.com\n")
        tmp.flush()
        tmp_path = tmp.name
    
    # Mock compute_all to raise an exception
    with mock.patch('src.main.compute_all', side_effect=Exception("Test error")):
        result = main(["program", tmp_path])
        assert result == 1
    
    # Clean up
    os.unlink(tmp_path)


def test_early_env_exits_with_valid_token():
    """Test _early_env_exits with a valid GitHub token."""
    os.environ["GITHUB_TOKEN"] = "valid_token"
    assert _early_env_exits() is False
    os.environ.pop("GITHUB_TOKEN", None)


def test_early_env_exits_with_invalid_token(capsys):
    """Test _early_env_exits with an invalid GitHub token."""
    os.environ["GITHUB_TOKEN"] = "INVALID"
    result = _early_env_exits()
    assert result is True
    
    captured = capsys.readouterr()
    assert "Error: Invalid GitHub token" in captured.out
    assert "Error: Invalid GitHub token" in captured.err
    
    os.environ.pop("GITHUB_TOKEN", None)


# Import here to avoid circular import
from time import perf_counter
