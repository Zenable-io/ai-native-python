# {{ cookiecutter.project_name }}

[![CI](https://github.com/{{ cookiecutter.github_org }}/{{ cookiecutter.project_name }}/actions/workflows/ci.yml/badge.svg)](https://github.com/{{ cookiecutter.github_org }}/{{ cookiecutter.project_name }}/actions/workflows/ci.yml)

Welcome to {{ cookiecutter.project_name }}

## Getting Started

First, you need to ensure you have `task`, `docker`, `git`, `uv`, and `python3` installed locally, and the `docker` daemon is running.

Then, you can setup your local environment via:

```bash
# Install the dependencies
task init

# Build the image
task build

# Run the image
docker run {{ cookiecutter.github_org }}/{{ cookiecutter.project_slug }}:0.0.0 --help
```

If you'd like to build all of the supported docker images, you can set the `PLATFORM` env var to `all` like this:

```bash
PLATFORM=all task build
```

You can also specify a single platform of either `linux/arm64` or `linux/amd64`, **however** if you want to publish a cross-platform build manually
you will need to install `skopeo`.

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

## FAQs

For frequently asked questions including release workflow troubleshooting, see our [FAQ documentation](./FAQ.md).
