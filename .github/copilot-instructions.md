# GitHub Copilot Instructions for AI-Native Python Paved Road

You are working on a cookiecutter template for creating AI-native Python projects. This template provides a modern Python development setup with best practices
built-in.

## Context

- This is a **template generator**, not a regular Python project
- Files in `{{cookiecutter.project_name}}` directory contain Jinja2 template variables
- The project uses `uv` as the package manager (not pip or poetry)
- Python 3.13+ is the minimum requirement
- The template uses python-semantic-release for automated versioning

## Code Conventions

1. **Imports**: Use absolute imports only
2. **Type Hints**: Always include type hints for function parameters and return values
3. **Docstrings**: Use Google-style docstrings for all public functions and classes
4. **Error Handling**: Raise specific exceptions with descriptive messages
5. **Path Handling**: Use pathlib.Path instead of os.path
6. **Logging**: Use the logging module, never print()

## File Patterns

- `*.py`: Python source files
- `*.toml`: Configuration files (pyproject.toml, etc.)
- `*.yml`: GitHub Actions workflows
- `*.md`: Documentation files
- `*.j2`: Jinja2 templates (if any)

## Testing Requirements

- Write pytest tests for all new functionality, but run all tests with: `task test`
- You can also run just unit tests with `task unit-test` and just integration tests with `task integration-test`
- Use fixtures for test data setup and place it in `tests/conftest.py`
- Maintain >80% code coverage
- Mark tests appropriately: @pytest.mark.unit or @pytest.mark.integration

## Task Automation

Common tasks are automated via Taskfile:

- `task init`: Initialize development environment
- `task build`: Build the project
- `task test`: Run all tests
- `task lint`: Run code quality checks
- `task clean`: Remove any build artifacts or temporary files

## Security Considerations

- Never hardcode secrets or credentials
- Use environment variables for sensitive data
- Follow OWASP secure coding practices
- Run security scans with grype before releases

## When Suggesting Code

1. Check existing patterns in the codebase first
2. Ensure compatibility with uv package manager
3. Follow the established project structure
4. Include appropriate error handling
5. Add tests for new functionality
6. Update documentation as needed

## Template-Specific Guidelines

When working with cookiecutter templates:

- Preserve Jinja2 syntax in template files
- Use proper escaping for template variables
- Test template generation with various inputs
- Ensure generated projects are functional

## Common Patterns

```python
# Path handling
from pathlib import Path
project_root = Path(__file__).parent.parent

# Logging setup
import logging
logger = logging.getLogger(__name__)

# Type hints
from typing import Optional, List, Dict
def process_data(items: List[Dict[str, Any]]) -> Optional[str]:
    ...
```
