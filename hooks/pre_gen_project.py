#!/usr/bin/env python3
"""
Pre-project generation hook for validation
"""

import re
import sys
from logging import basicConfig, getLogger

basicConfig(level="WARNING", format="%(levelname)s: %(message)s")
LOG = getLogger("pre_generation_hook")

# Cookiecutter variables
PROJECT_NAME = "{{ cookiecutter.project_name }}"
PROJECT_SLUG = "{{ cookiecutter.project_slug }}"


def validate_project_name() -> None:
    """Validate that project_name starts with an alphabetical character."""
    # Check if project_name starts with an alphabetical character
    if not re.match(r"^[a-zA-Z]", PROJECT_NAME):
        LOG.error(
            "Invalid project name '%s': Python project names must start with an alphabetical character (a-z or A-Z).",
            PROJECT_NAME,
        )
        sys.exit(1)


def validate_project_slug() -> None:
    """Validate that project_slug is a valid Python identifier."""
    # Check if project_slug is a valid Python identifier
    if not PROJECT_SLUG.isidentifier():
        LOG.error("Invalid project slug '%s': Must be a valid Python identifier.", PROJECT_SLUG)
        sys.exit(1)


if __name__ == "__main__":
    validate_project_name()
    validate_project_slug()
