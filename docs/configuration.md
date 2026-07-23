# Configuration Guide

This guide covers the configuration options available in the AI-Native Python cookiecutter template.

[← Back to Documentation Index](index.md)

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

| Variable                 | Description                                         | Default | Options                                  |
| ------------------------ | --------------------------------------------------- | ------- | ---------------------------------------- |
| `python_version`         | Minimum Python version                              | "3.13"  | "3.11", "3.12", "3.13"                   |
| `dockerhub_subscription` | Docker Hub plan; `none` disables image publishing   | "none"  | "none", "personal", "team", "business"   |
| `public`                 | Make repository public                              | "yes"   | "yes", "no"                              |
| `license`                | Project license                                     | "NONE"  | "NONE", "MIT", "BSD-3-Clause"            |

## Post-Generation Configuration

After your project is generated, you are able to make any changes you'd like. Here are some common modifications:

### Environment Variables

Set environment variables for development:

```bash
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

#### Docker Hub Authentication

The `dockerhub_subscription` choice controls publishing and authentication:

- **None:** Docker Hub publishing is not generated.
- **Personal:** Add `DOCKERHUB_USERNAME` and `DOCKERHUB_PAT` as GitHub Actions secrets.
- **Team or Business:** [Create a Docker Hub OIDC connection](https://docs.docker.com/enterprise/security/oidc-connections/create-manage/) whose ruleset grants the
  generated repository write access. Add `DOCKERHUB_ORGANIZATION` and `DOCKERHUB_OIDC_CONNECTIONID` as GitHub Actions variables.

Personal subscriptions use the standard Docker Hub login. Team and Business subscriptions exchange the GitHub identity token for a short-lived Docker Hub token.
The generated README and setup reminder describe only the selected authentication path.
