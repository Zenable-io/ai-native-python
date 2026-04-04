#!/usr/bin/env python3
"""Extract __version__ from the project's __init__.py without importing it.

This avoids import-mechanism issues (namespace packages, venv state, etc.)
that can occur cross-platform.  The script locates the file relative to its
own position in the repo so it works regardless of the caller's CWD.
"""

import os
import pathlib
import re
import sys

FALLBACK = "0.0.0"


def _debug(msg: str) -> None:
    if os.environ.get("ZENABLE_LOGLEVEL", "").upper() == "DEBUG":
        print(f"get_version: {msg}", file=sys.stderr)


def main() -> None:
    if len(sys.argv) < 2:
        print(FALLBACK)
        sys.exit(0)

    project_slug = sys.argv[1]

    # Resolve relative to this script's location (scripts/ -> project root)
    script_dir = pathlib.Path(__file__).resolve().parent
    project_root = script_dir.parent
    init_file = project_root / "src" / project_slug / "__init__.py"

    _debug(f"cwd={os.getcwd()}")
    _debug(f"script_dir={script_dir}")
    _debug(f"project_root={project_root}")
    _debug(f"init_file={init_file} exists={init_file.exists()}")

    if not init_file.exists():
        _debug(f"init file not found, falling back to {FALLBACK}")
        print(FALLBACK)
        sys.exit(0)

    text = init_file.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*"(.+?)"', text)
    if match:
        print(match.group(1))
    else:
        _debug(f"no __version__ found in {init_file}, falling back to {FALLBACK}")
        print(FALLBACK)


if __name__ == "__main__":
    main()
