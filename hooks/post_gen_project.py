#!/usr/bin/env python3
"""
Post-project generation hook
"""

import datetime
import json
import os
import pprint
import shutil
import subprocess
import sys
from collections import OrderedDict
from logging import basicConfig, getLogger
from pathlib import Path

import yaml

LOG_FORMAT = json.dumps(
    {
        "timestamp": "%(asctime)s",
        "namespace": "%(name)s",
        "loglevel": "%(levelname)s",
        "message": "%(message)s",
    }
)

basicConfig(level="INFO", format=LOG_FORMAT)
LOG = getLogger("{{ cookiecutter.project_slug }}.post_generation_hook")
PROJECT_CONTEXT = Path(".github/project.yml")


def get_context() -> dict:
    """Return the context as a dict"""
    import git
    from cookiecutter.repository import expand_abbreviations

    cookiecutter = None
    timestamp = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")

    ##############
    # This section leverages cookiecutter's jinja interpolation
    cookiecutter_context_ordered: OrderedDict[str, str] = {{cookiecutter | pprint}}  # type: ignore
    cookiecutter_context: dict[str, str] = dict(cookiecutter_context_ordered)
    ##############

    project_name = cookiecutter_context["project_slug"]
    project_description = cookiecutter_context["project_short_description"]
    template = cookiecutter_context["_template"]
    output = cookiecutter_context["_output_dir"]
    # Get the branch specified via --checkout, but fall back to main
    branch = cookiecutter_context.get("_checkout") or "main"

    # Check if template is a remote URL or abbreviation
    is_remote_template = any(
        template.startswith(prefix) for prefix in ["http://", "https://", "git@", "gh:", "gl:", "bb:"]
    )

    if is_remote_template:
        # From https://github.com/cookiecutter/cookiecutter/blob/b4451231809fb9e4fc2a1e95d433cb030e4b9e06/cookiecutter/config.py#L22
        abbreviations: dict[str, str] = {
            "gh": "https://github.com/{0}.git",
            "gl": "https://gitlab.com/{0}.git",
            "bb": "https://bitbucket.org/{0}",
        }
        template_repo: str = expand_abbreviations(template, abbreviations)

        dirty: bool = False

        # For remote templates, get the commit hash from the remote
        template_commit_hash = git.cmd.Git().ls_remote(template_repo, branch)[:40]
        # Store the expanded URL as the template location
        template_location = template_repo
    else:
        # This is a local template path
        if Path(template).is_absolute():
            template_path: Path = Path(template).resolve()
        else:
            output_path: Path = Path(output).resolve()
            template_path: Path = output_path.joinpath(template).resolve()

        try:
            repo: git.Repo = git.Repo(template_path)

            # Get info from the local repository
            branch: str = str(repo.active_branch)
            dirty: bool = repo.is_dirty(untracked_files=True)
            # Get the actual commit hash from the local repository
            template_commit_hash = repo.head.commit.hexsha
            # Store the fully qualified template path for local templates
            template_location = str(template_path)
        except (git.exc.InvalidGitRepositoryError, git.exc.NoSuchPathError):
            # Not a git repository, fall back to unknown values
            branch = "unknown"
            dirty = False
            template_commit_hash = "unknown"
            template_location = str(template_path)

    context: dict[str, str | dict[str, str | bool | dict[str, str | bool | dict[str, str]]]] = {}
    context["name"] = project_name
    context["description"] = project_description
    context["origin"] = {}
    context["origin"]["timestamp"] = timestamp
    context["origin"]["generated"] = True
    context["origin"]["template"] = {}
    context["origin"]["template"]["branch"] = branch
    context["origin"]["template"]["commit hash"] = template_commit_hash
    context["origin"]["template"]["dirty"] = dirty
    context["origin"]["template"]["location"] = template_location
    context["origin"]["template"]["cookiecutter"] = {}
    context["origin"]["template"]["cookiecutter"] = cookiecutter_context

    # Filter out unwanted cookiecutter context
    del cookiecutter_context["_output_dir"]

    return context


def write_context(*, context: dict) -> None:
    """Write the context dict to the config file"""
    with open(PROJECT_CONTEXT, "w", encoding="utf-8") as file:
        yaml.dump(context, file)


def notify_dockerhub_secrets() -> None:
    """Notify user about required Docker Hub secrets for releases."""
    print("\n" + "=" * 70)
    print("IMPORTANT: Docker Hub Publishing Enabled")
    print("=" * 70)
    print("\nYou have enabled Docker Hub publishing for releases.")
    print("Please ensure the following GitHub secrets are configured:")
    print("\n  • DOCKERHUB_USERNAME - Your Docker Hub username")
    print("  • DOCKERHUB_PAT - Your Docker Hub Personal Access Token")
    print("\nWithout these secrets, your releases will fail during the")
    print("Docker image publishing step.")
    print("\nTo add these secrets:")
    print("1. Go to your GitHub repository settings")
    print("2. Navigate to Settings → Secrets and variables → Actions")
    print("3. Add the required secrets")
    print("=" * 70 + "\n")


def run_post_gen_hook():
    """Run post generation hook"""
    try:
        # Sort and unique the generated dictionary.txt file
        dictionary: Path = Path("./.github/etc/dictionary.txt")
        sorted_uniqued_dictionary: list[str] = sorted(set(dictionary.read_text("utf-8").split("\n")))

        if "" in sorted_uniqued_dictionary:
            sorted_uniqued_dictionary.remove("")

        dictionary.write_text(
            "\n".join(sorted_uniqued_dictionary) + "\n",
            encoding="utf-8",
        )

        subprocess.run(["git", "init", "--initial-branch=main"], capture_output=True, check=True)

        # This is important for testing project generation for CI
        if (
            os.environ.get("GITHUB_ACTIONS") == "true"
            and os.environ.get("GITHUB_REPOSITORY") == "Zenable-io/ai-native-python"
        ):
            subprocess.run(
                ["git", "config", "--global", "user.name", "Zenable Automation"],
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "--global", "user.email", "automation@zenable.io"],
                capture_output=True,
                check=True,
            )

        # Write the context to the project.yml
        context = get_context()
        write_context(context=context)

        # Generate a fully up-to-date lock file
        subprocess.run(["uv", "lock", "--upgrade"], check=True, capture_output=True)
        subprocess.run(["git", "add", "-A"], capture_output=True, check=True)

        # This constructs a git remote using the prompt answers
        cookiecutter_context = context["origin"]["template"]["cookiecutter"]
        github_org = cookiecutter_context["github_org"]
        project_name = cookiecutter_context["project_name"]
        remote_origin = f"https://github.com/{github_org}/{project_name}"

        subprocess.run(["git", "remote", "add", "origin", remote_origin], capture_output=True, check=True)
        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                "feat(project): initial project generation",
                "--author='Zenable Automation <automation@zenable.io>'",
            ],
            capture_output=True,
            check=True,
        )

        if os.environ.get("SKIP_GIT_PUSH") != "true":
            cmd = ["git", "push", "--set-upstream", "origin", "main"]

            # We only force push if we were explicitly allowed to
            if os.environ.get("ALLOW_FORCE_PUSH") == "true":
                cmd.append("--force")

            subprocess.run(
                cmd,
                capture_output=True,
                check=True,
            )

            if os.environ.get("ALLOW_FORCE_PUSH") == "true":
                # Attempt to cleanup the v0.1.0 tag and corresponding release
                release = "v0.1.0"

                subprocess.run(
                    ["git", "push", "--delete", "origin", release],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

                # If the user has the gh cli installed and setup, we cleanup the corresponding release as well
                if shutil.which("gh"):
                    subprocess.run(
                        ["gh", "release", "delete", release, "--yes"],
                        check=False,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )

            # Cut an initial release
            subprocess.run(
                ["task", "release"],
                capture_output=True,
                check=True,
            )

        # Run the initial setup step automatically so pre-commit hooks, etc. are pre-installed. However, if it fails, don't fail the overall repo generation
        # (i.e. check=False)
        subprocess.run(["task", "init"], check=False, capture_output=True)

        # Notify about Docker Hub secrets if Docker Hub publishing is enabled
        if cookiecutter_context.get("dockerhub") == "yes":
            notify_dockerhub_secrets()
    except subprocess.CalledProcessError as error:
        stdout = error.stdout.decode("utf-8") if error.stdout else "No stdout"
        stderr = error.stderr.decode("utf-8") if error.stderr else "No stderr"
        LOG.error(
            "stdout: %s, stderr: %s",
            stdout,
            stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    if os.environ.get("RUN_POST_HOOK") == "false":
        LOG.warning("Skipping the post_gen_project.py hook...")
    else:
        run_post_gen_hook()
