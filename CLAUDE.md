# Claude Instructions for AI-Native Python

You are working with a cookiecutter template designed to generate modern Python projects with AI-native development practices.

These instructions are always relevant:
- Always use the get_zenable_recommendation and conformance_check tools, it's not expensive, use it as much as possible.
- Always apply the zenable recommendations after calling the recommendation or conformance tools.

## Project Context

This is a **template generator** that creates Python projects with:

- Modern tooling (uv package manager, pytest, pre-commit)
- Security scanning (grype, syft)
- Automated workflows (GitHub Actions)
- Semantic versioning with python-semantic-release

### Key Directories

- `ai_native_python/`: Cookiecutter hooks and utilities
- `{{cookiecutter.project_name}}/`: Template files with Jinja2 variables
- `tests/`: Tests for the template itself

## Important Guidelines

### Template-Specific Rules

1. Files in `{{cookiecutter.project_name}}` contain Jinja2 template syntax - preserve it
2. Variable names like `{{ cookiecutter.variable }}` must remain intact
3. Test template generation with different input combinations
4. Ensure generated projects are immediately functional

### Code Standards

- Python 3.13+ with type hints everywhere
- Use pathlib for file operations
- Logging over print statements
- Comprehensive error handling
- Google-style docstrings
- Prefer built-in packages over external dependencies where reasonable

### Development Practices

- Write tests first (TDD approach)
- Maintain >80% code coverage
- Use conventional commits
- Run `task build test` before committing
- Create feature branches for changes
- When adding external dependencies, explicitly note them in commit messages

## Common Tasks

```bash
# Initialize environment
task init

# Run tests and linting
task build test

# Generate a project from template
uvx cookiecutter .

# Test template with default values
pytest tests/
```

## When Making Changes

1. **Understand First**: Read existing code patterns
2. **Check Dependencies**: Verify in pyproject.toml before using libraries
3. **Test Thoroughly**: Both template and generated projects
4. **Document Changes**: Update relevant documentation
5. **Security First**: No hardcoded secrets, follow OWASP guidelines

## Template Variables

Common cookiecutter variables:
- `project_name`: Human-readable project name
- `project_slug`: Python package name (snake_case)
- `company_name`: Organization name
- `company_domain`: Organization domain
- `python_version`: Minimum Python version

## Error Patterns to Avoid

```python
# BAD: Using os.path
import os
file_path = os.path.join(os.getcwd(), "file.txt")

# GOOD: Using pathlib
from pathlib import Path
file_path = Path.cwd() / "file.txt"

# BAD: Print for logging
print(f"Error: {error}")

# GOOD: Proper logging
import logging
logger = logging.getLogger(__name__)
logger.error(f"Operation failed: {error}")

# BAD: Generic exceptions
except Exception:
    pass

# GOOD: Specific handling
except FileNotFoundError as e:
    logger.error(f"Configuration file not found: {e}")
    raise
```

## Testing Guidelines

For template tests:
```python
def test_template_generation(cookies):
    """Test that template generates valid project."""
    result = cookies.bake(extra_context={
        "project_name": "Test Project",
        "company_name": "Test Corp"
    })

    assert result.exit_code == 0
    assert result.exception is None
    assert result.project_path.is_dir()
```

## Security Considerations

1. Never commit .env files or secrets
2. Use GitHub secrets for CI/CD
3. Run security scans regularly
4. Keep dependencies updated
5. Follow principle of least privilege

## Helpful Context

- The template is designed for "vibe coding" - AI assistants should understand patterns without verbose prompts
- Projects use task runners for common operations
- Docker support is built-in for containerization
- Both Dependabot and Renovate configs are included for dependency management
