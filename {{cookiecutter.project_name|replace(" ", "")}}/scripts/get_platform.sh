#!/usr/bin/env bash
set -euo pipefail

# Always use linux for container builds
os="linux"
arch="$(uname -m)"

# Inspired by https://github.com/containerd/containerd/blob/e0912c068b131b33798ae45fd447a1624a6faf0a/platforms/database.go#L76
case ${arch} in
  # AMD64
  x86_64)  echo "${os}/amd64" ;;
  amd64)   echo "${os}/amd64" ;;

  # ARM64
  aarch64) echo "${os}/arm64" ;;
  arm64)   echo "${os}/arm64" ;;

  *) echo "Unsupported architecture: $arch" && exit 1 ;;
esac
