#!/usr/bin/env python3
"""
Integration tests for {{ cookiecutter.project_name }}
"""

import json
import tomllib
import os
import subprocess
from pathlib import Path

import pytest


@pytest.mark.integration
def test_project_tasks():
    """
    Test the project's task runner commands work together properly.

    This is an integration test that validates the project's build, test,
    and security scanning workflows work correctly.
    """
    project_root = Path(__file__).parent.parent

    try:
        # Test SBOM generation for local platform
        subprocess.run(
            ["task", "-v", "sbom"],
            capture_output=True,
            check=True,
            cwd=project_root,
        )

        # Verify SBOM files were created and are valid JSON
        sbom_files = list(project_root.glob("sbom.latest.*.json"))
        assert len(sbom_files) >= 3, (
            f"Expected at least 3 SBOM files, found {len(sbom_files)}"
        )

        # Validate each SBOM file is valid JSON
        for sbom_file in sbom_files:
            try:
                with open(sbom_file) as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in {sbom_file}: {e}")

        # Test vulnerability scanning
        subprocess.run(
            ["task", "-v", "vulnscan"],
            capture_output=True,
            # We don't check the exit of this because we aren't measuring that there are no vulns, but rather that vuln scan results are generated
            check=False,
            cwd=project_root,
        )

        # Verify vuln scan file was created and is valid JSON
        vuln_files = list(project_root.glob("vulns.latest.*.json"))
        assert len(vuln_files) >= 1, (
            f"Expected at least 1 vulnerability scan file, found {len(vuln_files)}"
        )

        # Validate each vuln scan file is valid JSON
        for vuln_file in vuln_files:
            try:
                with open(vuln_file) as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in {vuln_file}: {e}")

        # Test license checking
        subprocess.run(
            ["task", "-v", "license-check"],
            capture_output=True,
            check=True,
            cwd=project_root,
        )

        # Verify license check file was created and is valid JSON
        license_files = list(project_root.glob("license-check.latest.*.json"))
        assert len(license_files) >= 1, (
            f"Expected at least 1 license check file, found {len(license_files)}"
        )

        # Validate each license check file is valid JSON
        for license_file in license_files:
            try:
                with open(license_file) as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in {license_file}: {e}")

    except subprocess.CalledProcessError as error:
        pytest.fail(
            f"Command failed: {error.cmd}\nstdout: {error.stdout.decode('utf-8')}\nstderr: {error.stderr.decode('utf-8')}"
        )


@pytest.mark.integration
def test_docker_image():
    """
    Test that the Docker image builds and runs correctly.
    """
    project_root = Path(__file__).parent.parent
    image_name = "{{ cookiecutter.github_org }}/{{ cookiecutter.project_slug }}"

    pyproject_file = project_root / "pyproject.toml"

    with open(pyproject_file, "rb") as f:
        pyproject_data = tomllib.load(f)
        version = pyproject_data.get("project", {}).get("version", "0.0.0")

    try:
        # Test that --help works with version tag
        subprocess.run(
            ["docker", "run", "--rm", f"{image_name}:{version}", "--help"],
            capture_output=True,
            check=True,
            cwd=project_root,
        )

        # Test that --help works with latest tag
        subprocess.run(
            ["docker", "run", "--rm", f"{image_name}:latest", "--help"],
            capture_output=True,
            check=True,
            cwd=project_root,
        )

        # Test basic docker run without arguments (should raise NotImplementedError)
        process = subprocess.run(
            ["docker", "run", "--rm", f"{image_name}:latest"],
            capture_output=True,
            cwd=project_root,
        )
        assert process.returncode == 1, (
            f"Expected exit code 1, got: {process.returncode}"
        )
        assert "NotImplementedError" in process.stderr.decode(), (
            f"Expected NotImplementedError in stderr, got: {process.stderr.decode()}"
        )

        # Test that mutually exclusive arguments fail appropriately
        command = [
            "docker",
            "run",
            "--rm",
            f"{image_name}:latest",
            "--debug",
            "--verbose",
        ]
        expected_exit = 2
        process = subprocess.run(
            command,
            capture_output=True,
            cwd=project_root,
        )
        assert process.returncode == expected_exit, (
            f"Expected exit code {expected_exit} when running {command}, "
            f"but got {process.returncode}"
        )

        # Test running with environment variables
        process = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-e",
                "LOG_LEVEL=DEBUG",
                f"{image_name}:latest",
                "--help",
            ],
            capture_output=True,
            check=True,
            cwd=project_root,
        )
        assert process.returncode == 0, (
            f"Received an expected exit code of {process.returncode}"
        )
    except subprocess.CalledProcessError as error:
        pytest.fail(
            f"Command failed: {error.cmd}\nstdout: {error.stdout.decode('utf-8')}\nstderr: {error.stderr.decode('utf-8')}"
        )


@pytest.mark.integration
def test_multi_platform_build():
    """
    Test building for multiple platforms.

    This test is skipped in CI environments unless explicitly enabled.
    """
    project_root = Path(__file__).parent.parent

    try:
        # Test building for all supported platforms
        env = os.environ.copy()
        env["PLATFORM"] = "all"

        subprocess.run(
            ["task", "-v", "build"],
            capture_output=True,
            check=True,
            cwd=project_root,
            env=env,
        )

        # Test SBOM generation, vuln scanning, and license checks for each supported platforms
        for platform in ["linux/amd64", "linux/arm64"]:
            env["PLATFORM"] = platform
            subprocess.run(
                ["task", "-v", "sbom", "vulnscan", "license-check"],
                capture_output=True,
                check=True,
                cwd=project_root,
                env=env,
            )

            # Verify platform-specific files were created and are valid JSON
            platform_suffix = platform.replace("/", "_")
            sbom_file = project_root / f"sbom.latest.{platform_suffix}.syft.json"
            assert sbom_file.exists(), f"SBOM file for {platform} not found"

            # Validate SBOM is valid JSON
            try:
                with open(sbom_file) as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in {sbom_file}: {e}")

            vuln_file = project_root / f"vulns.latest.{platform_suffix}.json"
            assert vuln_file.exists(), (
                f"Vulnerability scan file for {platform} not found"
            )

            # Validate vuln scan is valid JSON
            try:
                with open(vuln_file) as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in {vuln_file}: {e}")

    except subprocess.CalledProcessError as error:
        pytest.fail(
            f"Command failed: {error.cmd}\nstdout: {error.stdout.decode('utf-8')}\nstderr: {error.stderr.decode('utf-8')}"
        )
