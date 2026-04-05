#!/usr/bin/env python3
"""
Post-project generation hook
"""

import datetime
import hashlib
import json
import os
import pprint
import shutil
import subprocess
import sys
import tempfile
from collections import OrderedDict
from logging import basicConfig, getLogger
from pathlib import Path
from urllib.request import HTTPSHandler, build_opener

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
    # We no longer need this once https://github.com/docker/roadmap/issues/314 is available
    print("\n" + "=" * 70)
    print("IMPORTANT: Docker Hub Publishing Enabled")
    print("=" * 70)
    print("\nYou have enabled Docker Hub publishing for releases")
    print("Please ensure the following GitHub secrets are configured:")
    print("\n  • DOCKERHUB_USERNAME - Your Docker Hub username")
    print("  • DOCKERHUB_PAT - Your Docker Hub Personal Access Token")
    print("\nWithout these secrets, your releases will fail during the")
    print("Docker image publishing step")
    print("\nTo add these secrets:")
    print("1. Go to your GitHub repository settings")
    print("2. Navigate to Settings → Secrets and variables → Actions")
    print("3. Add the required secrets")
    print("=" * 70 + "\n")


def _find_zenable_binary() -> str | None:
    """Find the zenable binary in PATH or the default install location."""
    zenable_path = shutil.which("zenable")
    if zenable_path:
        return zenable_path

    # Check the default install location
    binary_name = "zenable.exe" if sys.platform == "win32" else "zenable"
    default_path = Path.home() / ".zenable" / "bin" / binary_name
    if default_path.is_file():
        return str(default_path)

    return None


ZENABLE_RELEASE_URL = "https://cli.zenable.app/zenable/latest"


_https_opener = build_opener(HTTPSHandler())


def _fetch_release_metadata() -> dict:
    """Fetch the Zenable CLI release metadata from cli.zenable.app."""
    with _https_opener.open(ZENABLE_RELEASE_URL, timeout=30) as resp:
        return json.loads(resp.read())


def _download_url(url: str) -> bytes:
    """Download a URL and return the raw bytes."""
    with _https_opener.open(url, timeout=60) as resp:
        return resp.read()


def _verify_checksum(data: bytes, expected_sha256: str) -> None:
    """Verify SHA-256 checksum of data against the expected value.

    Raises ValueError if the checksum does not match.
    """
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected_sha256:
        msg = f"Checksum mismatch: expected {expected_sha256}, got {actual}"
        raise ValueError(msg)


def _install_zenable_binary() -> bool:
    """Install the zenable CLI binary.

    Fetches the release metadata from cli.zenable.app/zenable/latest,
    downloads the appropriate installer for the current platform, verifies
    its SHA-256 checksum, then executes it non-interactively. The install
    script itself also performs cosign signature verification of the
    downloaded binary.

    Returns True if installation succeeded, False otherwise.
    """
    env = {**os.environ, "ZENABLE_YES": "1"}

    try:
        metadata = _fetch_release_metadata()

        if sys.platform == "win32":
            installer_key = "install.ps1"
        else:
            installer_key = "install.sh"

        install_url = metadata["installers"][installer_key]
        expected_checksum = metadata["installer_checksums"][installer_key]

        install_script = _download_url(install_url)
        _verify_checksum(install_script, expected_checksum)

        if sys.platform == "win32":
            # Write to a temp file because PowerShell's -Command - does not
            # reliably read scripts from stdin.
            tmp = tempfile.NamedTemporaryFile(suffix=".ps1", delete=False, mode="wb")
            tmp.write(install_script)
            tmp.close()
            cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", tmp.name]
            input_data = None
        else:
            cmd = ["bash"]
            input_data = install_script
            tmp = None

        result = subprocess.run(
            cmd,
            input=input_data,
            check=True,
            capture_output=True,
            timeout=120,
            env=env,
        )

        if tmp is not None:
            Path(tmp.name).unlink(missing_ok=True)
        if result.stdout:
            LOG.info("Zenable installer stdout: %s", result.stdout.decode("utf-8", errors="replace").strip())
        if result.stderr:
            LOG.info("Zenable installer stderr: %s", result.stderr.decode("utf-8", errors="replace").strip())
        return True
    except ValueError:
        LOG.warning("Zenable install script checksum verification failed")
        return False
    except Exception:
        LOG.warning("Failed to install the Zenable CLI binary")
        return False


def opportunistically_install_zenable_tools() -> None:
    """Opportunistically install the Zenable CLI and configure IDE integrations."""
    zenable_bin = _find_zenable_binary()

    if not zenable_bin:
        LOG.debug("Zenable CLI not found, attempting to install...")
        if not _install_zenable_binary():
            print("\n" + "=" * 70)
            print("NOTE: Skipped configuring the Zenable AI coding guardrails")
            print("=" * 70)
            print("\nTo set this up later, install the Zenable CLI:")
            print("\n  curl -fsSL https://cli.zenable.app/install.sh | bash")
            print("\nThen run: zenable install")
            print("=" * 70 + "\n")

            LOG.warning("Zenable CLI could not be installed.")
            return

        # The installer updates PATH for future shells/steps (e.g. via
        # GITHUB_PATH or the user's shell profile) but not the current
        # process.  Add the default install directory so we can find the
        # binary immediately.
        zenable_bin_dir = str(Path.home() / ".zenable" / "bin")
        os.environ["PATH"] = zenable_bin_dir + os.pathsep + os.environ.get("PATH", "")

        zenable_bin = _find_zenable_binary()
        if not zenable_bin:
            # Diagnostic: log what the installer actually created
            zenable_dir = Path.home() / ".zenable"
            if zenable_dir.exists():
                contents = [str(p.relative_to(zenable_dir)) for p in zenable_dir.rglob("*")]
                LOG.warning("Install dir %s contents: %s", zenable_dir, contents)
            else:
                LOG.warning("Install directory does not exist: %s", zenable_dir)
            LOG.warning("Current PATH: %s", os.environ.get("PATH", ""))
            LOG.warning("Zenable CLI was installed but could not be found in PATH or default location.")
            return

    # Zenable CLI is available, attempt to configure IDE integrations
    LOG.debug("Zenable CLI found at %s, configuring IDE integrations...", zenable_bin)
    try:
        subprocess.run([zenable_bin, "install"], check=True, timeout=60)
        print("\n" + "=" * 70)
        print("Successfully configured the Zenable AI coding guardrails 🚀")
        print("To start using it, just open the IDE of your choice, login, and you're all set 🤖")
        print("Learn more at https://docs.zenable.io")
        print("=" * 70 + "\n")
    except Exception:
        # Log the error but don't fail - this is opportunistic
        LOG.warning("Failed to configure the Zenable AI coding guardrails")
        print("\n" + "=" * 70)
        print("WARNING: Failed to configure the Zenable AI coding guardrails")
        print("=" * 70)
        print("You can retry it later by running:")
        print("\n  zenable install")
        print("\nTo report issues, please contact:")
        print("  • https://zenable.io/feedback")
        print("  • support@zenable.io")
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

        opportunistically_install_zenable_tools()

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
