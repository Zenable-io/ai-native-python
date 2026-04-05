#!/usr/bin/env python3
"""
Test main.py module
"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.mark.unit
def test_main_import():
    """Test that main.py can be imported without executing"""
    import main  # noqa: F401


@pytest.mark.unit
def test_main_function():
    """Test that main() raises NotImplementedError"""
    from main import main

    with patch("sys.argv", ["main"]):
        with pytest.raises(NotImplementedError):
            main()


@pytest.mark.unit
def test_main_version():
    """Test that --version prints the version and exits"""
    from main import main

    with patch("sys.argv", ["main", "--version"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0


@pytest.mark.unit
def test_main_as_script():
    """Test that main.py raises NotImplementedError when run as a script"""
    main_path = Path(__file__).parent.parent / "src" / "main.py"

    result = subprocess.run(
        [sys.executable, str(main_path)],
        capture_output=True,
        text=True,
    )

    # Should exit with code 1 due to NotImplementedError
    assert result.returncode == 1
    assert "NotImplementedError" in result.stderr


@pytest.mark.unit
def test_main_as_script_version():
    """Test that --version works when run as a script"""
    main_path = Path(__file__).parent.parent / "src" / "main.py"

    result = subprocess.run(
        [sys.executable, str(main_path), "--version"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "0.0.0" in result.stdout
