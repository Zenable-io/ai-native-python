#!/usr/bin/env python3
"""Cross-platform cleanup of build artifacts, cache files, and temp files."""

import glob
import shutil
import sys
from pathlib import Path


def main() -> int:
    """Remove build artifacts, cache directories, and temporary files."""
    root = Path(".")

    # Paths to remove (may be files or directories)
    for name in [".pytest_cache", "htmlcov", ".coverage", "dist", "build"]:
        path = root / name
        if path.is_dir():
            shutil.rmtree(path)
        elif path.is_file():
            path.unlink()

    # Glob patterns for directories
    for path in glob.glob("*.egg-info"):
        shutil.rmtree(path)

    # Glob patterns for files
    for pattern in [
        "sbom.*.json",
        "vulns.*.json",
        "license-check.*.json",
        "{{ cookiecutter.github_org }}_{{ cookiecutter.project_slug }}_*_*.tar",
    ]:
        for path in glob.glob(pattern):
            Path(path).unlink()

    # Recursively remove __pycache__ directories
    for path in root.rglob("__pycache__"):
        if path.is_dir():
            shutil.rmtree(path)

    # Recursively remove .pyc files
    for path in root.rglob("*.pyc"):
        path.unlink()

    return 0


if __name__ == "__main__":
    sys.exit(main())
