#!/usr/bin/env python3
"""
{{ cookiecutter.project_name }} script entrypoint
"""

from {{ cookiecutter.project_slug }} import config

if __name__ == "__main__":
    log = config.setup_logging()
    raise NotImplementedError()
