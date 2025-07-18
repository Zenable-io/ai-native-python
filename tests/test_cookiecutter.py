#!/usr/bin/env python3
"""
Test ai-native-python
"""

import copy
import itertools
import json
import os
import platform as plat
import re
import subprocess
import sys
from pathlib import Path

import git
import pytest
import yaml
from jinja2 import Template

LOCAL_PLATFORM = f"{plat.system().lower()}/{plat.machine()}"


def get_config() -> dict:
    """Generate all the config keys"""
    config_file = Path("./cookiecutter.json")
    with config_file.open(encoding="utf-8") as f:
        config = json.load(f)
    return config


def render_config(*, config: dict) -> dict:
    """Render the provided config"""
    rendered_config: dict[str, str | list] = {}
    for key, value in config.items():
        if isinstance(value, str):
            # Sanitize by removing the "cookiecutter." prefix
            sanitized_template = value.replace("cookiecutter.", "")
            template = Template(sanitized_template)
            rendered_config[key] = str(template.render(config))
        elif isinstance(value, list):
            rendered_config[key] = value
        else:
            sys.exit(1)
    return rendered_config


def get_supported_combinations() -> list:
    """Generate all supported combinations of options"""
    config = get_config()
    base_config = render_config(config=config)
    combinations = copy.deepcopy(base_config)

    # Make every str a list[str]
    for key, value in base_config.items():
        if isinstance(value, str):
            combinations[key] = [value]

    # Return all combinations of the config
    all_combinations: list[dict[str, list[str]]] = [
        dict(zip(combinations, v, strict=False)) for v in itertools.product(*combinations.values())
    ]

    # Remove unwanted keys (_copy_without_render is not currently used but may be in the future)
    supported_combinations: list[dict[str, list[str]]] = [
        {k: v for k, v in d.items() if k != "_copy_without_render"} for d in all_combinations
    ]
    return supported_combinations


@pytest.fixture
def context():
    """pytest fixture for context"""
    # Use the rendered defaults
    return get_supported_combinations()[0]


def _fixture_id(ctx):
    """Helper to get a user friendly test name from the parametrized context."""
    return ",".join(f"{key}:{value}" for key, value in ctx.items())


def build_files_list(root_dir):
    """
    Build a list containing absolute paths to the generated files, ignoring
    files under .git/
    """
    root_path = Path(root_dir)
    files = [str(file.absolute()) for file in root_path.glob("**/*") if file.is_file()]
    return list(filter(lambda f: ".git/" not in f, files))


def check_files(files):
    """Method to check all files have correct substitutions."""
    # Assert that no match is found in any of the files
    pattern = r"{{(\s?cookiecutter)[.](.*?)}}"
    re_obj = re.compile(pattern)
    for file in files:
        for line in open(file):
            match = re_obj.search(line)
            assert match is None, f"cookiecutter variable not replaced in {file}"


@pytest.mark.unit
@pytest.mark.parametrize(
    "context_override",
    get_supported_combinations(),
    ids=_fixture_id,
)
def test_supported_options(cookies, context_override):
    """
    Test all supported answer combinations
    """
    # Turn off the post generation hooks
    os.environ["RUN_POST_HOOK"] = "false"

    result = cookies.bake(extra_context=context_override)

    assert result.exit_code == 0
    assert result.exception is None
    assert result.project_path.name == context_override["project_name"]
    assert result.project_path.is_dir()

    files = build_files_list(str(result.project_path))
    assert files
    check_files(files)


@pytest.mark.integration
def test_update(cookies):
    """
    Test task update
    """
    # Turn on the post generation hooks but skip git push
    os.environ["RUN_POST_HOOK"] = "true"
    os.environ["SKIP_GIT_PUSH"] = "true"

    result = cookies.bake()
    project = result.project_path

    try:
        # First init the project just in case
        # Clean environment to avoid VIRTUAL_ENV conflicts
        env = os.environ.copy()
        env.pop("VIRTUAL_ENV", None)
        subprocess.run(
            ["task", "init"],
            capture_output=True,
            check=True,
            cwd=project,
            env=env,
        )

        # And then run a task update
        subprocess.run(
            ["task", "update"],
            capture_output=True,
            check=True,
            cwd=project,
            env=env,
        )
    except subprocess.CalledProcessError as error:
        pytest.fail(f"stdout: {error.stdout.decode('utf-8')}, stderr: {error.stderr.decode('utf-8')}")


@pytest.mark.integration
def test_autofix_hook(cookies, context):
    """
    Test the post-generation pre-commit autofix hook
    """
    # Turn on the post generation hooks but skip git push
    os.environ["RUN_POST_HOOK"] = "true"
    os.environ["SKIP_GIT_PUSH"] = "true"

    # If both work, autofix is expected (but not definitively proven) to be working
    for project_slug in ["aaaaaaaaaa", "zzzzzzzzzz"]:
        context["project_slug"] = project_slug
        result = cookies.bake(extra_context=context)
        project = result.project_path

        try:
            # First init the project
            # Clean environment to avoid VIRTUAL_ENV conflicts
            env = os.environ.copy()
            env.pop("VIRTUAL_ENV", None)
            subprocess.run(
                ["task", "init"],
                capture_output=True,
                check=True,
                cwd=project,
                env=env,
            )
            # Run linting (which will run pre-commit with auto-fixing allowed)
            # This may fail the first time if files need fixing
            process = subprocess.run(
                ["task", "lint"],
                capture_output=True,
                cwd=project,
                env=env,
            )
            # If it failed, run it again to verify fixes were applied
            if process.returncode != 0:
                subprocess.run(
                    ["task", "lint"],
                    capture_output=True,
                    check=True,
                    cwd=project,
                    env=env,
                )
        except subprocess.CalledProcessError as error:
            pytest.fail(f"stdout: {error.stdout.decode('utf-8')}, stderr: {error.stderr.decode('utf-8')}")


@pytest.mark.integration
@pytest.mark.slow
def test_default_project(cookies):
    """
    Test a default project thoroughly
    """
    # Turn on the post generation hooks but skip git push
    os.environ["RUN_POST_HOOK"] = "true"
    os.environ["SKIP_GIT_PUSH"] = "true"

    result = cookies.bake()
    project = result.project_path

    repo = git.Repo(project)
    if repo.is_dirty(untracked_files=True):
        pytest.fail("Something went wrong with the project's post-generation hook")

    # Extract project_name and project_slug from cookiecutter.json
    config_file = Path("./cookiecutter.json")
    with config_file.open(encoding="utf-8") as f:
        generated_config = json.load(f)
        github_org = generated_config.get("github_org")
        project_name = generated_config.get("project_name")
        project_name_lower = project_name.lower()

        # Keep this logic aligned with the template's README.md
        # It's important that this has -s in the name to test the docker hub image name sanitization
        default_image_name = f"{github_org}/{project_name_lower}"
        default_image_name_and_tag = f"{default_image_name}:latest"

    try:
        env = os.environ.copy()
        env.pop("VIRTUAL_ENV", None)  # Clean VIRTUAL_ENV to avoid conflicts

        # Bootstrap the project and run the simplest checks first to optimize for a fast feedback loop
        subprocess.run(
            [
                "task",
                "-v",
                "init",
                "lint",
                "validate",
            ],
            capture_output=True,
            check=True,
            cwd=project,
            env=env,
        )

        # Ensure the project.yml is generated, and is valid YAML
        config_path = project / ".github" / "project.yml"
        with config_path.open(encoding="utf-8") as yaml_data:
            project_context = yaml.safe_load(yaml_data)
            assert project_context["origin"]["generated"]

        # Build and test each supported architecture individually
        for platform in ("linux/arm64", "linux/amd64"):
            env["PLATFORM"] = platform
            subprocess.run(
                ["task", "-v", "build", "test", "sbom", "vulnscan", "license-check"],
                capture_output=True,
                check=True,
                cwd=project,
                env=env,
            )

        # Do two releases to ensure they work; do not push the releases though
        for _ in range(2):
            subprocess.run(
                ["task", "-v", "release", "--", "--no-push", "--no-commit", "--no-tag", "--no-vcs-release"],
                capture_output=True,
                check=True,
                cwd=project,
                env=env,
            )

        # Ensure that --help exits 0
        subprocess.run(
            ["docker", "run", "--rm", default_image_name_and_tag, "--help"],
            capture_output=True,
            check=True,
            cwd=project,
        )

        # Ensure that --debug --verbose (mutually exclusive arguments) exits 2
        command: list[str] = [
            "docker",
            "run",
            "--rm",
            default_image_name_and_tag,
            "--debug",
            "--verbose",
        ]
        expected_exit: int = 2
        process = subprocess.run(
            command,
            capture_output=True,
            cwd=project,
        )
        if process.returncode != expected_exit:
            pytest.fail(
                f"Unexpected exit code when running {command}; expected {expected_exit}, received {process.returncode}"
            )

        # Clean the repo, perform a multi-platform build, and then run the sbom / vulnscan / license check tasks to ensure it all works
        # We cannot functionally test a multi-platform image without pushing it to a registry and then pulling it back down because they can't directly be
        # loaded into the docker daemon
        env["PLATFORM"] = "all"
        subprocess.run(
            [
                "task",
                "-v",
                "clean",
                "build",
                "sbom",
                "vulnscan",
                "license-check",
            ],
            capture_output=True,
            check=True,
            cwd=project,
            env=env,
        )
    except subprocess.CalledProcessError as error:
        print(f"\n=== STDOUT ===\n{error.stdout.decode('utf-8')}")
        print(f"\n=== STDERR ===\n{error.stderr.decode('utf-8')}")
        pytest.fail(f"Command failed with exit code {error.returncode}. See output above.")
    except (
        yaml.YAMLError,
        FileNotFoundError,
        PermissionError,
        IsADirectoryError,
        OSError,
    ) as exception:
        pytest.fail(exception)

    # Validate CI
    for filename in ["ci.yml"]:
        file_path = project / ".github" / "workflows" / filename
        with file_path.open(encoding="utf-8") as file:
            try:
                github_config = yaml.safe_load(file)
                # Ensure that the expected jobs exist
                for job in ["build", "test", "lint"]:
                    assert job in github_config["jobs"]
            except yaml.YAMLError as exception:
                pytest.fail(exception)
