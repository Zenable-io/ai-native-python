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
{% if cookiecutter.dockerhub_subscription != 'none' %}
## Docker Hub Publishing

{% if cookiecutter.dockerhub_subscription in ['team', 'business'] %}
Docker Hub OIDC requires a Team or Business subscription. Releases authenticate with short-lived tokens. [Create a Docker Hub OIDC
connection](https://docs.docker.com/enterprise/security/oidc-connections/create-manage/) for this repository, then add these GitHub Actions variables:

- `DOCKERHUB_ORGANIZATION`: Docker Hub organization name
- `DOCKERHUB_OIDC_CONNECTIONID`: OIDC connection ID from Docker Hub

The Docker Hub connection ruleset must allow this GitHub repository to write to the target image repository. Personal Docker Hub accounts are not supported.
{% else %}
Releases authenticate with Docker Hub credentials. Add these GitHub Actions secrets:

- `DOCKERHUB_USERNAME`: Docker Hub username
- `DOCKERHUB_PAT`: Docker Hub Personal Access Token
{% endif %}
{% endif %}

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

## FAQs

For frequently asked questions including release workflow troubleshooting, see our [FAQ documentation](./FAQ.md).

_This project was generated with 🤟 by [Zenable](https://zenable.io)_
