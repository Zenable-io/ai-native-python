#!/usr/bin/env python3
"""Get the Docker platform string for the current machine.

Always uses 'linux' as the OS since container builds target Linux.
"""

import platform
import sys

# Always use linux for container builds
os_name = "linux"
machine = platform.machine().lower()

# Inspired by https://github.com/containerd/containerd/blob/e0912c068b131b33798ae45fd447a1624a6faf0a/platforms/database.go#L76
arch_map = {
    # AMD64
    "x86_64": "amd64",
    "amd64": "amd64",
    # ARM64
    "aarch64": "arm64",
    "arm64": "arm64",
}

if machine not in arch_map:
    print(f"Unsupported architecture: {machine}", file=sys.stderr)
    sys.exit(1)

print(f"{os_name}/{arch_map[machine]}")
