#!/usr/bin/env python3
"""
{{ cookiecutter.project_name }} script entrypoint
"""

import argparse

from {{ cookiecutter.project_slug }} import __version__, config


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="{{ cookiecutter.project_short_description | replace('"', '\\"') | replace("'", "\\\\'") }}")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.parse_args()

    log = config.setup_logging()
    log.debug("Logging initialized with level: %s", log.level)

    raise NotImplementedError()


if __name__ == "__main__":
    main()
