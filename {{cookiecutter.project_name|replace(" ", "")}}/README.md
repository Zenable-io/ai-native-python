# {{ cookiecutter.project_name }}

[![CI](https://github.com/{{ cookiecutter.github_org }}/{{ cookiecutter.project_name }}/actions/workflows/commit.yml/badge.svg)](https://github.com/{{ cookiecutter.github_org }}/{{ cookiecutter.project_name }}/actions/workflows/commit.yml)

Welcome to {{ cookiecutter.project_name }}

## Getting Started

First, you need to ensure you have `brew`, `task`, `docker`, `git`, and `uv` installed locally, and the `docker` daemon is running.

Then, you can setup your local environment via:

```bash
# Install the dependencies
task init

# Build the image
task build

# Run the image
docker run {{ cookiecutter.github_org }}/{{ cookiecutter.project_name | lower }}:0.0.0 --help
```

If you'd like to build all of the supported docker images, you can set the `PLATFORM` env var to `all` like this:

```bash
PLATFORM=all task build
```

You can also specify a single platform of either `linux/arm64` or `linux/amd64`

## Optional setup

If you'd like to be able to run `task license-check` locally, you will need to install `grant` and ensure it's in your `PATH`.

## Troubleshooting

If you're troubleshooting the results of any of the tasks, you can add `-v` to enable debug `task` logging, for instance:

```bash
task -v build
```

## Automated Dependency Management

This project is configured with automated dependency management:

- **Dependabot**: Automatically creates pull requests for Python, GitHub Actions, and Docker dependency updates
- **Renovate**: Provides more advanced dependency update management with grouping and scheduling capabilities

Both tools are pre-configured and will start working once the repository is pushed to GitHub.

## Development Containers

This project includes Dev Container support for consistent development environments.

### Quick Start with VS Code

1. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Open this project in VS Code
3. Click "Reopen in Container" when prompted, or use the command palette: `Dev Containers: Reopen in Container`

### Alternative: Attach to Running Container

If you prefer to manage the container manually:

```bash
# Build and start the development container
task dev-container

# Check container status
task dev-container-status

# Access the container shell
task dev-container-shell

# Run a specific command in the container
task dev-container-exec CMD="python --version"

# Stop the container when done
task dev-container-stop
```

To attach from VS Code: Use command palette `Dev Containers: Attach to Running Container` and select `{{ cookiecutter.project_slug }}-dev`.

### What's Included

The development container provides:
- Python {{ cookiecutter.python_version }}+ with all project dependencies
- Development tools: uv, Task, pre-commit, git
- VS Code extensions for Python development
- Live code editing with proper volume mounts
- All dependencies installed (including dev dependencies)

For more details, see [.devcontainer/README.md](.devcontainer/README.md).

## FAQs

For frequently asked questions including release workflow troubleshooting, see our [FAQ documentation](./FAQ.md).

_This project was generated with 🤟 by [Zenable](https://zenable.io)_
