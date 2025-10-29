# Contributing

To contribute to this project, please consider starting by [opening an issue](https://github.com/Zenable-io/ai-native-python/issues/new) to discuss the feature
and its design.

Once you are ready to submit your contribution, please fork the repository and open a pull request with your changes.

## Updating the dependencies

```bash
task update
```

## Running the tests

```bash
task test
```

## Creating a release

This project uses python-semantic-release for automated versioning. The version bump is determined automatically based on conventional commit messages:

- `fix:` commits bump patch version (0.1.0 -> 0.1.1)
- `feat:` commits bump minor version (0.1.1 -> 0.2.0)
- `BREAKING CHANGE:` in commit body bumps major version (0.2.0 -> 1.0.0)

To create a release:

```bash
# Create release (auto-determines version from commits)
task release

# Push the changes and tags
git push --follow-tags
```

Example commit messages:
```bash
# Patch release
git commit -m "fix: correct versioning reference in documentation"

# Minor release
git commit -m "feat: add support for multiple Python versions in template"

# Major release (use ! after type or BREAKING CHANGE in body)
git commit -m "feat!: remove CalVer support

BREAKING CHANGE: Projects now only use semantic versioning with python-semantic-release"
```

## Troubleshooting

If you're troubleshooting the results of any of the tasks, you can add `-v` to enable debug `task` logging, for instance:

```bash
task -v build
```

If you're troubleshooting a `pre-commit` failure, you can run pre-commit directly with more verbose output:

```bash
uv run pre-commit run --all-files --verbose
```
