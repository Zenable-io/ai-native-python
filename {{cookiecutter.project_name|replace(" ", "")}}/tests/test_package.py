#!/usr/bin/env python3
"""
Test package metadata and imports
"""

import pytest

from {{ cookiecutter.project_slug }} import (
    __maintainer__,
    __project_name__,
    __version__,
{%- if cookiecutter.license != 'NONE' %}
    __license__,
{%- endif %}
{%- if cookiecutter.license == 'NONE' %}
    __copyright__,
{%- endif %}
)


@pytest.mark.unit
def test_package_metadata():
    """Test that package metadata is accessible."""

    assert __maintainer__ == "{{ cookiecutter.company_name }}"
    assert __project_name__ == "{{ cookiecutter.project_slug }}"
    assert __version__ is not None
    assert isinstance(__version__, str)
{%- if cookiecutter.license == 'MIT' %}
    assert __license__ == "MIT"
{%- elif cookiecutter.license == 'BSD-3' %}
    assert __license__ == "BSD-3-Clause"
{%- elif cookiecutter.license == 'NONE' %}
    assert __copyright__.startswith("(c) {{ cookiecutter.company_name }}")
{%- endif %}
