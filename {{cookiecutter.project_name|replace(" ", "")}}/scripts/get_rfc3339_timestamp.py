#!/usr/bin/env python3
"""Get the current RFC3339 timestamp."""

from datetime import datetime, timezone

print(datetime.now(timezone.utc).isoformat())