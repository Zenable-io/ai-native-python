# AI-Native Python

Give your vibe coding the perfect starting point with this paved-road repo generator so Cursor (or any AI) can learn by example—no verbose prompts needed.

## Features

- 🚀 Modern Python development with `uv`
- 🧪 Automated testing with `pytest`
- 🔍 Code quality checks with `pre-commit` hooks (`ruff`, `pyright`, etc.)
- 🔐 Security scanning with SBOM generation (`syft`), vulnerability scanning (`grype`), and license checks (`grant`)
- 🤖 Automated dependency updates with Dependabot and Renovate
- 📦 Multi-platform Docker builds
- 🔄 Automated versioning and releasing with `python-semantic-release`

For FAQs including release workflow troubleshooting, see our [FAQ documentation](./FAQ.md).

## Getting Started

Create an empty remote Git repository that aligns with name of the project you'd like to create. Once it exists, you can continue.

```bash
# Install the prerequisites
brew install uv go-task

# Initialize your project with *either* HTTP or SSH
# HTTP
uv run cookiecutter gh:zenable-io/ai-native-python
# SSH example
#uv run cookiecutter git+ssh://git@github.com/zenable-io/ai-native-python.git
```

This will push the initial commit and run a release of your project; ensure that this succeeds before adding business logic to ensure you have a solid
foundation.

Then, configure any required repository settings such as rulesets/branch protections. This can be done via Infrastructure as Code (IaC) or manually, but
ostensibly by this point your repository is aligned with your organizational practices and you're ready to start adding features.

Consider a tool like OpenSSF [allstar](https://github.com/ossf/allstar) to monitor and alert or mitigate on your behalf.

```bash
# Enter the project directory
cd $(ls -td * | head -1)

# Initialize the repository
task init

# Checkout a new branch for your initial content
git checkout -b initial-content

# Check for `NotImplementedError`s and address them as a part of adding your business logic
grep -r NotImplementedError *
```

## Optional setup

If you'd like to support license file checking locally, you will need to install `grant` and put it in your `PATH`

## Version Control System support

Currently this project only supports projects hosted on GitHub.
