# Testing Guide

This document covers two distinct testing contexts:

1. **Template Tests** - Tests for the AI-Native Python cookiecutter template itself (i.e. this repository)
2. **Generated Project Tests** - Tests included in projects created from this template (i.e. projects rendered after running `cookiecutter`)

## Template Tests

These tests ensure the cookiecutter template works correctly and generates valid projects.

### Running Template Tests

```bash
# From this repository
task test               # Run all template tests with coverage
task unit-test          # Run unit tests only
task integration-test   # Run integration tests only
```

### What Template Tests Cover

- **Generation Validation**: Tests with various input combinations to ensure valid project generation
- **Hook Execution**: Verifies post-generation hooks run correctly
- **File Structure**: Confirms all expected files are created
- **End-to-End**: Full test of the default parameter answers including:
  - Project initialization
  - Dependency installation
  - Running generated project's test suite and linters

## Generated Project Tests

Every project created from this template includes a complete testing setup.

### Features Included

- **100% Coverage**: Template provides tests for the initial `main.py` and module code
- **Pytest Configuration**: Pre-configured in `pyproject.toml`
- **Coverage Requirements**: 80% minimum enforced in CI/CD

### Running Tests in Generated Projects

```bash
# From the generated project root
task test                     # Run all tests with coverage
pytest tests/unit -v         # Run unit tests only
pytest tests/integration -v  # Run integration tests only
```

### Writing Tests in Generated Projects

Generated projects use pytest with:

- Parametrized tests for multiple scenarios
- Markers for test categorization (`@pytest.mark.unit`, `@pytest.mark.integration`)
- Mocking for external dependencies

## CI/CD Integration

The above tests are a part of what's automatically executed in the CI pipeline. For complete details on test automation and workflow configuration, see the
[CI/CD Guide](ci-cd.md#ci-pipeline-githubworkflowsciyml).
