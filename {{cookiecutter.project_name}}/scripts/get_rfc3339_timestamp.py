#!/usr/bin/env python3
"""Get the current RFC3339 timestamp."""

import datetime

print(datetime.datetime.now(datetime.UTC).isoformat())
