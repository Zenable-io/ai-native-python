#!/usr/bin/env python3
"""
Post-project generation hook
"""

import datetime
import json
import os
import pprint
import subprocess
import sys

# Used indirectly in the below Jinja2 block
from collections import OrderedDict  # pylint: disable=unused-import
from logging import basicConfig, getLogger
from pathlib import Path

import git
import yaml
from cookiecutter.repository import expand_abbreviations

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
    cookiecutter = None
    timestamp = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")

    ##############
    # This section leverages cookiecutter's jinja interpolation
    # pylint: disable-next=unhashable-member
    cookiecutter_context_ordered: OrderedDict[str, str] = {{cookiecutter | pprint}}  # type: ignore
    cookiecutter_context: dict[str, str] = dict(cookiecutter_context_ordered)

    project_name = cookiecutter_context["project_slug"]  # pylint: disable=unsubscriptable-object
    project_description = cookiecutter_context["project_short_description"]  # pylint: disable=unsubscriptable-object
    template = cookiecutter_context["_template"]  # pylint: disable=unsubscriptable-object
    output = cookiecutter_context["_output_dir"]  # pylint: disable=unsubscriptable-object
    ##############

    try:
        if Path(template).is_absolute():
            template_path: Path = Path(template).resolve()
        else:
            output_path: Path = Path(output).resolve()
            template_path: Path = output_path.joinpath(template)

        # IMPORTANT: If the specified template is remote (http/git/ssh) this SHOULD raise an exception. The remote logic is in the except block
        repo: git.Repo = git.Repo(template_path)

        # Expect this is a local template
        branch: str = str(repo.active_branch)
        dirty: bool = repo.is_dirty(untracked_files=True)
        template_commit_hash = git.cmd.Git().ls_remote(template_path, "HEAD")[:40]
    except (git.exc.InvalidGitRepositoryError, git.exc.NoSuchPathError):
        # This exception handling occurs every time the template repo is remote

        # From https://github.com/cookiecutter/cookiecutter/blob/b4451231809fb9e4fc2a1e95d433cb030e4b9e06/cookiecutter/config.py#L22
        abbreviations: dict[str, str] = {
            "gh": "https://github.com/{0}.git",
            "gl": "https://gitlab.com/{0}.git",
            "bb": "https://bitbucket.org/{0}",
        }
        template_repo: str = expand_abbreviations(template, abbreviations)

        # This currently assumes main until https://github.com/cookiecutter/cookiecutter/issues/1759 is resolved
        branch: str = "main"
        dirty: bool = False

        template_commit_hash = git.cmd.Git().ls_remote(template_repo, branch)[:40]

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
    context["origin"]["template"]["location"] = template
    context["origin"]["template"]["cookiecutter"] = {}
    context["origin"]["template"]["cookiecutter"] = cookiecutter_context

    # Filter out unwanted cookiecutter context
    del cookiecutter_context["_output_dir"]  # pylint: disable=unsubscriptable-object

    return context


def write_context(*, context: dict) -> None:
    """Write the context dict to the config file"""
    with open(PROJECT_CONTEXT, "w", encoding="utf-8") as file:
        yaml.dump(context, file)


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
        subprocess.run(["uv", "lock", "--upgrade"], check=True, capture_output=True, text=True)
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

        # Push the initial commit
        # TODO: Remove --force; just for testing
        subprocess.run(
            ["git", "push", "--set-upstream", "origin", "main", "--force"],
            capture_output=True,
            check=True,
        )

        # Cut an initial release
        subprocess.run(
            ["task", "release"],
            capture_output=True,
            check=True,
        )
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
