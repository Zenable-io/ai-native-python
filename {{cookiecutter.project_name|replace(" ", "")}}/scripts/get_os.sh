#!/usr/bin/env bash
set -euo pipefail

case "$(uname -s)" in
  Darwin) echo "darwin" ;;
  Linux) echo "linux" ;;
  *) echo "Unsupported OS" && exit 1 ;;
esac
