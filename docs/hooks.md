# Hooks

The AI-Native Python template uses hooks to automate setup tasks automatically.

## Cookiecutter Hooks

### Post-Generation Hook

The `post_gen_project.py` hook runs after project generation to:

1. Initialize the project as a Git repository
2. Create the project's initial commit
3. Set up GitHub remote (if credentials available)
4. Generate a fully up-to-date `uv.lock` file
5. Create an `.envrc` with API keys
6. Run `task init` to install dependencies
7. Push to GitHub and create an initial release

### Configuration

Environment variables can be set before running cookiecutter to modify hook behavior:

- `SKIP_GIT_PUSH=true` - Skip automatic Git push
- `RUN_POST_HOOK=false` - Skip the post-generation hook entirely (not recommended)
- `ZENABLE_API_KEY="..."` - Auto-populate API key in .envrc

For more environment variable options, see the [Optional Setup Guide](optional-setup.md#environment-variable-configuration).

## Pre-commit Hooks

Automatically run code quality checks before each commit.

### Installation

```bash
task init  # Installs pre-commit and sets up hooks, alongside setting up other project dependencies to get started
```

### Included Hooks

1. **Python** - Ruff for linting and formatting
2. **Security** - Trufflehog for secret detection
3. **File Checks** - JSON/YAML validation, large files, merge conflicts
4. **Spell Check** - Typos with custom dictionary
5. **Shell Scripts** - ShellCheck validation
6. **GitHub Actions** - Actionlint validation
7. **OpenAPI** - Schema validation

For the full list of hooks, see `{{cookiecutter.project_name|replace(" ", "")}}/.pre-commit-config.yaml`

### Configuration

Edit `.pre-commit-config.yaml` to customize:

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.8.6
  hooks:
    - id: ruff
      args: [--fix, --show-fixes]
```

### Adding Custom Hooks

```yaml
- repo: local
  hooks:
    - id: pytest-check
      name: pytest-check
      entry: pytest
      language: system
      pass_filenames: false
```
