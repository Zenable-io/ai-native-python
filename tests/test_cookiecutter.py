#!/usr/bin/env python3
"""
Test cookiecutter-python
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
    with open(config_file) as file_object:
        config = json.load(file_object)
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
    Test all supported cookiecutter-python answer combinations
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
def test_autofix_hook(cookies, context):
    """
    Test the post-generation pre-commit autofix hook of cookiecutter-python
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
def test_default_project(cookies):
    """
    Test a default cookiecutter-python project thoroughly
    """
    # Turn on the post generation hooks but skip git push
    os.environ["RUN_POST_HOOK"] = "true"
    os.environ["SKIP_GIT_PUSH"] = "true"

    result = cookies.bake()
    project = result.project_path

    repo = git.Repo(project)
    if repo.is_dirty(untracked_files=True):
        pytest.fail("Something went wrong with the project's post-generation hook")

    try:
        # Build all supported architectures to ensure it succeeds; we cannot test it because multi-platform builds can't be loaded into the docker daemon, but
        # we will load and test the same-platform image later
        env = os.environ.copy()
        env.pop("VIRTUAL_ENV", None)  # Clean VIRTUAL_ENV to avoid conflicts
        env["PLATFORM"] = "all"
        subprocess.run(
            [
                "task",
                "-v",
                "init",
                "lint",
                "validate",
                "build",
                "sbom",
                "vulnscan",
            ],
            capture_output=True,
            check=True,
            cwd=project,
            env=env,
        )

        # Build and test each supported architecture individually (should be mostly cached)
        for platform in ("linux/arm64", "linux/amd64"):
            env["PLATFORM"] = platform
            subprocess.run(
                ["task", "-v", "build", "test", "sbom", "vulnscan"],
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

        default_image = "zenable-io/todo:latest"

        # Ensure that --help exits 0
        subprocess.run(
            ["docker", "run", "--rm", default_image, "--help"],
            capture_output=True,
            check=True,
            cwd=project,
        )

        # Ensure that --debug --verbose (mutually exclusive arguments) exits 2
        command: list[str] = [
            "docker",
            "run",
            "--rm",
            default_image,
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

        # Ensure the project.yml is generated, and is valid YAML
        config_path = project / ".github" / "project.yml"
        with config_path.open(encoding="utf-8") as yaml_data:
            project_context = yaml.safe_load(yaml_data)
            assert project_context["origin"]["generated"]
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
