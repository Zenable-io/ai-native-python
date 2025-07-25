# CI/CD Workflows

The AI-Native Python template includes GitHub Actions workflows for automated testing, security scanning, and release management.

[← Back to Documentation Index](index.md)

## Included Workflows

### CI Pipeline (`.github/workflows/ci.yml`)

Runs on every push and pull request:

1. **Linting** - Python (Ruff), YAML/JSON, shell scripts, GitHub Actions
2. **Testing** - Unit and integration tests with >80% coverage requirement, as well as docker builds on each supported platform
3. **Security** - Vulnerability scanning (Grype), SBOM generation (Syft), secret detection

### Release Pipeline (`.github/workflows/release.yml`)

Automates semantic versioning and publishing:

1. Analyzes commit messages to determine version bump
2. Updates version in `pyproject.toml`
3. Generates changelog
4. Creates GitHub release
5. Pushes Docker images to Docker Hub (if enabled)

### PR Validation (`.github/workflows/pr.yml`)

Ensures pull request quality:

- Validates PR title follows conventional commit format
- Checks all commit messages
- Look for deprecations or warnings and adds them to the finalizer

## Configuration

For GitHub Actions configuration and required secrets, see the [Configuration Guide](configuration.md#post-generation-configuration).

### Dependency Updates

The generated project includes multiple dependency update mechanisms. See the [Configuration Guide](configuration.md#post-generation-configuration) for details
on customizing these tools.

## Customization

Add new workflows in `.github/workflows/` for specific needs like deployment or scheduled tasks.
