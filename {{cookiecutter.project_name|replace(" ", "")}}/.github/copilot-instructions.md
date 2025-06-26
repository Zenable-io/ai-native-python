# GitHub Copilot Instructions for {{ cookiecutter.project_name }}

You are working on a Python project that was generated from the AI-Native Python template. This project follows modern Python development best practices.

## Context

- **Project**: {{ cookiecutter.project_name }}
- **Description**: {{ cookiecutter.project_short_description }}
- **Company**: {{ cookiecutter.company_name }}
- **Python Version**: {{ cookiecutter.python_version }}+
- **Package Manager**: uv and uvx (not pip, poetry, or pipx)

## Code Conventions

1. **Imports**: Use absolute imports only
2. **Type Hints**: Always include type hints for function parameters and return values
3. **Docstrings**: Use Google-style docstrings for all public functions and classes
4. **Error Handling**: Raise specific exceptions with descriptive messages
5. **Path Handling**: Use pathlib.Path instead of os.path
6. **Logging**: Use the logging module, never print()

## Project Structure

```
{{ cookiecutter.project_slug }}/    # Main package directory
tests/                              # Test files
docker/                             # Docker configuration
docs/                               # Documentation
.github/workflows/                  # CI/CD pipelines
```

## Testing Requirements

- Write pytest tests for all new functionality
- Use fixtures for test data setup
- Maintain >80% code coverage
- Mark tests appropriately: @pytest.mark.unit or @pytest.mark.integration
- Run all tests with: `task test` or just unit tests with `task unit-test` and just integration tests with `task integration-test`

## Development Workflow

1. Create feature branches for all changes
2. Write tests before implementing features
3. Run `task build test` before committing
4. Use conventional commits (feat:, fix:, docs:, etc.)
5. Open pull requests for code review

## Task Automation

Common tasks are automated via Taskfile:

- `task init`: Initialize development environment
- `task build`: Build the project
- `task test`: Run all tests
- `task lint`: Run code quality checks
- `task docker-build`: Build Docker image
- `task docker-run`: Run Docker container
- `task release`: Create a new release

## Security Considerations

- Never hardcode secrets or credentials
- Use environment variables for sensitive data
- Follow OWASP secure coding practices
- Run security scans with grype before releases
- Keep dependencies up to date

## When Suggesting Code

1. Check existing patterns in the codebase first
2. Look for NotImplementedError placeholders to implement
3. Ensure compatibility with uv package manager
4. Follow the established project structure
5. Include appropriate error handling
6. Add tests for new functionality
7. Update documentation as needed

## Common Patterns

```python
# Path handling
from pathlib import Path
project_root = Path(__file__).parent.parent

# Logging setup
import logging
logger = logging.getLogger(__name__)

# Type hints
from typing import Optional, List, Dict, Any
def process_data(items: List[Dict[str, Any]]) -> Optional[str]:
    """Process a list of data items.

    Args:
        items: List of dictionaries containing data.

    Returns:
        Processed result or None if no data.
    """
    ...

# Error handling
class {{ cookiecutter.project_slug.replace('_', ' ').title().replace(' ', '') }}Error(Exception):
    """Base exception for {{ cookiecutter.project_name }}."""
    pass
```

## Dependencies

- Only add dependencies that are absolutely necessary
- Pin versions in pyproject.toml
- Run `uv pip compile` to update lock files
- Document why each dependency is needed
