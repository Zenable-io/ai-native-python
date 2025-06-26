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

    # Mock the argument parsing to avoid conflicts with pytest args
    with patch("{{ cookiecutter.project_slug }}.config.get_args_config") as mock_args:
        import logging

        mock_args.return_value = {"loglevel": logging.WARNING}

        with pytest.raises(NotImplementedError):
            main()


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
