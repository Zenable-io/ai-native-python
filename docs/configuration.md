# Configuration Guide

This guide covers the configuration options available in the AI-Native Python cookiecutter template.

## Cookiecutter Variables

When generating a new project, you'll be prompted for the following configuration options:

### Basic Project Information

| Variable                    | Description                      | Default        | Example                     |
| --------------------------- | -------------------------------- | -------------- | --------------------------- |
| `project_name`              | Human-readable project name      | (required)     | "My Awesome Project"        |
| `project_slug`              | Python package name (snake_case) | Auto-generated | "my_awesome_project"        |
| `project_short_description` | Brief project description        | (required)     | "A tool for awesome things" |

### Organization Details

| Variable                        | Description                     | Default    | Example     |
| ------------------------------- | ------------------------------- | ---------- | ----------- |
| `company_name`                  | Your organization's name        | (required) | "Acme Corp" |
| `company_domain`                | Your organization's domain      | (required) | "acme.com"  |
| `github_org`                    | GitHub organization or username | (required) | "acme-corp" |
| `project_owner_github_username` | Project owner's GitHub username | (required) | "johndoe"   |

### Technical Options

| Variable         | Description                  | Default | Options                       |
| ---------------- | ---------------------------- | ------- | ----------------------------- |
| `python_version` | Minimum Python version       | "3.13"  | "3.11", "3.12", "3.13"        |
| `dockerhub`      | Enable Docker Hub publishing | "no"    | "yes", "no"                   |
| `public`         | Make repository public       | "yes"   | "yes", "no"                   |
| `license`        | Project license              | "NONE"  | "NONE", "MIT", "BSD-3-Clause" |

## Post-Generation Configuration

After your project is generated, you are able to make any changes you'd like. Here are some common modifications:

### Environment Variables

Create or modify the `.envrc` file in your project root:

```bash
# API Keys
export ZENABLE_API_KEY="your-api-key-here"

# Development settings
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
export UV_PYTHON_PREFERENCE="only-system"
```

### Task Configuration

The `Taskfile.yml` in your project defines common development tasks. You can customize anything you'd like, such as:

- Python versions
- Linting and cleanup tasks
- Build configurations

Example task customization:

```yaml
vars:
  IMAGE_NAME: "abc123"    # Change the name of the docker image
  PYTHON_VERSION: "3.13"  # Change default Python version
```

### Pre-commit Hooks

For detailed information about pre-commit hooks configuration and available hooks, see the [Hooks Guide](hooks.md#pre-commit-hooks).

### GitHub Actions Configuration

For detailed information about CI/CD workflows and customization options, see the [CI/CD Guide](ci-cd.md).

#### Required Secrets

If you enabled Docker Hub publishing:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_PAT`

These will be printed as a reminder after project generation.
