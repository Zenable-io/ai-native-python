#!/usr/bin/env python3
"""Extract a cookiecutter template from a GitHub archive zip.

The top-level template directory in the zip contains NTFS-illegal characters
(pipe, double-quotes) from the Jinja2 expression in
``{{cookiecutter.project_name|replace(" ", "")}}``.  This script renames
**only** that top-level directory to the safe ``{{cookiecutter.project_name}}``
form while preserving nested cookiecutter directories like
``{{cookiecutter.project_slug}}`` so cookiecutter renders them correctly.

Usage:
    python extract_template_zip.py <zip_path> <dest_dir>

Prints the path to the extracted template root on stdout.
"""

import os
import sys
import zipfile


def extract(zip_path: str, dest: str) -> str:
    """Extract the zip, renaming only the top-level template directory."""
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            parts = info.filename.split("/")

            safe = []
            for i, part in enumerate(parts):
                # Index 0 is the repo root (e.g. ai-native-python-<sha>).
                # Index 1 is the template directory with NTFS-illegal chars.
                if i == 1 and "{{cookiecutter." in part:
                    safe.append("{{cookiecutter.project_name}}")
                else:
                    safe.append(part)

            target = os.path.join(dest, *[s for s in safe if s])

            if info.is_dir():
                os.makedirs(target, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with zf.open(info) as src, open(target, "wb") as dst:
                    dst.write(src.read())

    return os.path.join(dest, os.listdir(dest)[0])


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <zip_path> <dest_dir>", file=sys.stderr)
        sys.exit(1)
    print(extract(sys.argv[1], sys.argv[2]))
