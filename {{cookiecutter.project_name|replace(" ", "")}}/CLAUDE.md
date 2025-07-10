# Claude Instructions for {{ cookiecutter.project_name }}

You are working with a Python project that follows modern development practices and was generated from the AI-Native Python Paved Road template.

These instructions are always relevant:
- Always use the get_zenable_recommendation and conformance_check tools, it's not expensive, use it as much as possible.
- Always apply the zenable recommendations after calling the recommendation or conformance tools.

## Project Information

- **Name**: {{ cookiecutter.project_name }}
- **Package**: {{ cookiecutter.project_slug }}
- **Description**: {{ cookiecutter.project_short_description | replace('"', '\\"') | replace("'", "\\\\'") }}
- **Organization**: {{ cookiecutter.company_name }} ({{ cookiecutter.company_domain }})
- **Python Version**: {{ cookiecutter.python_version }}+

## Technology Stack

- **Package Manager**: uv and uvx (not pip, poetry, or pipx)
- **Testing**: pytest with coverage reporting
- **Linting**: ruff, pyright
- **Security**: grype vulnerability scanning, syft SBOM generation
- **CI/CD**: GitHub Actions
- **Containerization**: Docker with multi-platform support

## Project Structure

```
{{ cookiecutter.project_slug }}/    # Main package code
├── __init__.py                     # Package initialization
├── __main__.py                     # CLI entry point
└── ...                             # Your modules

tests/                              # Test suite
├── unit/                           # Unit tests
├── integration/                    # Integration tests
└── conftest.py                     # pytest fixtures

docker/                             # Docker configuration
docs/                               # Documentation
.github/workflows/                  # CI/CD pipelines
```

## Development Workflow

### Initial Setup

```bash
task init                # Set up development environment
```

### Daily Development

```bash
task build              # Build the project
task test               # Run all tests
task lint               # Check code quality
task format             # Auto-format code
```

### Before Committing

1. Run `task build test` to ensure everything passes
2. Use conventional commits: `feat:`, `fix:`, `docs:`, `chore:`, etc.
3. Write descriptive commit messages
4. When adding external dependencies, explicitly note them in commit messages

## Code Guidelines

### Style Rules

1. **Imports**: Always use absolute imports
2. **Type Hints**: Required for all function signatures
3. **Docstrings**: Google-style for all public APIs
4. **Line Length**: Maximum 120 characters
5. **Naming**: snake_case for functions/variables, PascalCase for classes
6. **Dependencies**: Prefer built-in packages over external dependencies where reasonable

### Best Practices

```python
# GOOD: Type hints and docstrings
from typing import List, Optional

def process_items(items: List[str], filter_empty: bool = True) -> Optional[List[str]]:
    """Process a list of items with optional filtering.

    Args:
        items: List of strings to process.
        filter_empty: Whether to remove empty strings.

    Returns:
        Processed list or None if all items filtered.

    Raises:
        ValueError: If items is not a list.
    """
    if not isinstance(items, list):
        raise ValueError("items must be a list")

    # Implementation here
    ...

# GOOD: Using pathlib
from pathlib import Path

config_path = Path(__file__).parent / "config.yml"
with config_path.open() as f:
    config = yaml.safe_load(f)

# GOOD: Proper logging
import logging

logger = logging.getLogger(__name__)
logger.info("Processing started")

# GOOD: Context managers
with open("data.txt") as f:
    data = f.read()
```

## Testing Requirements

1. Write tests for all new functionality
2. Use pytest fixtures for test setup
3. Maintain >80% code coverage
4. Mark tests appropriately:
   ```python
   @pytest.mark.unit
   def test_calculation():
       ...

   @pytest.mark.integration
   def test_api_call():
       ...
   ```

## Security Guidelines

1. **Never hardcode secrets** - use environment variables
2. **Validate all inputs** - especially from external sources
3. **Use parameterized queries** - prevent SQL injection
4. **Keep dependencies updated** - check with `task security-scan`
5. **Follow OWASP guidelines** - for web-facing code

## Common Patterns

### Configuration Management
```python
from pathlib import Path
import yaml

def load_config(config_file: Path) -> dict:
    """Load configuration from YAML file."""
    with config_file.open() as f:
        return yaml.safe_load(f)
```

### Error Handling
```python
class {{ cookiecutter.project_slug.replace('_', ' ').title().replace(' ', '') }}Error(Exception):
    """Base exception for {{ cookiecutter.project_name }}."""
    pass

class ConfigurationError({{ cookiecutter.project_slug.replace('_', ' ').title().replace(' ', '') }}Error):
    """Raised when configuration is invalid."""
    pass

# Usage
try:
    config = load_config(config_path)
except FileNotFoundError:
    raise ConfigurationError(f"Config file not found: {config_path}")
```

### CLI Entry Points
```python
import argparse
import logging
import sys

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="{{ cookiecutter.project_short_description }}"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    try:
        # Your main logic here
        pass
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error occurred")
        sys.exit(1)
```

## Task Reference

- `task init`: Initialize development environment
- `task build`: Build the project
- `task test`: Run tests with coverage
- `task lint`: Run all linters
- `task format`: Auto-format code
- `task security-scan`: Check for vulnerabilities
- `task docker-build`: Build Docker image
- `task docker-run`: Run in Docker container
- `task release`: Create a release

## Important Notes

1. Look for `NotImplementedError` markers - these indicate where you need to add business logic
2. All public APIs must have comprehensive docstrings
3. Keep dependencies minimal - justify each addition
4. Follow {{ cookiecutter.company_name }} coding standards
5. Update tests when modifying functionality
6. Prefer built-in Python packages over external dependencies where reasonable
7. When adding new external dependencies, explicitly mention them in commit messages

## Getting Help

- Check existing code patterns first
- Review test cases for usage examples
- Consult the main README.md for project overview
- Use logging liberally for debugging
