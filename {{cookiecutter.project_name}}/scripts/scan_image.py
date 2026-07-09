#!/usr/bin/env python
"""Handle SBOM generation, vulnerability scanning, and license checking for container images.

This script supports both single-platform and multi-platform OCI images.
For multi-platform images (OCI index), it extracts and scans each platform separately.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)

    if result.returncode != 0 and check:
        print(f"Command failed with exit code {result.returncode}")
        print(f"STDERR: {result.stderr}")
        print(f"STDOUT: {result.stdout}")
        raise subprocess.CalledProcessError(
            result.returncode, cmd, result.stdout, result.stderr
        )

    return result


def get_platform_suffix(platform: str) -> str:
    """Convert platform string to file suffix."""
    if platform == "all":
        return "all"
    return platform.replace("/", "_")


def find_image_tar(image_name: str, platform: str) -> str:
    """Find the appropriate image tar file based on platform.

    Args:
        image_name: The image name (e.g., "org/repo")
        platform: The platform specification

    Returns:
        Path to the image tar file
    """
    image_name_normalized = image_name.replace("/", "_")
    platform_suffix = get_platform_suffix(platform)

    # Look for the expected tar file
    tar_file = f"{image_name_normalized}_latest_{platform_suffix}.tar"

    if not Path(tar_file).exists():
        # If platform-specific tar doesn't exist, check for "all" platform tar
        all_tar = f"{image_name_normalized}_latest_all.tar"
        if Path(all_tar).exists() and platform != "all":
            print(f"Note: Using multi-platform image {all_tar} for {platform}")
            return all_tar

        # Try to find any matching tar file
        pattern = f"{image_name_normalized}_latest_*.tar"
        matching_files = list(Path.cwd().glob(pattern))
        if matching_files:
            print(f"Warning: Expected {tar_file} not found, using {matching_files[0]}")
            return str(matching_files[0])
        else:
            raise FileNotFoundError(f"No image tar file found matching {pattern}")

    return tar_file


def should_output_to_stdout() -> bool:
    """Determine if we should output to stdout (CI environment)."""
    # In GitHub Actions, we want to tee output
    return os.environ.get("GITHUB_ACTIONS") == "true"


def extract_oci_layout(index_tar: str) -> Path:
    """Extract the OCI archive to a directory for easier manipulation.

    Args:
        index_tar: Path to the OCI archive tar file

    Returns:
        Path to the extracted directory
    """
    # Create a temporary directory
    extract_dir = Path(tempfile.mkdtemp(prefix="oci_extract_"))

    try:
        # Extract the tar file
        with tarfile.open(index_tar, "r") as tar:
            tar.extractall(extract_dir, filter="data")
    except Exception:
        # Clean up on failure
        shutil.rmtree(extract_dir, ignore_errors=True)
        raise

    return extract_dir


def _read_manifest_file(oci_dir: Path, digest: str) -> dict | None:
    """Read a manifest file from the OCI directory."""
    manifest_path = oci_dir / "blobs" / digest.replace(":", "/")
    if not manifest_path.exists():
        return None

    with open(manifest_path) as f:
        return json.load(f)


def _is_attestation_manifest(manifest: dict) -> bool:
    """Check if a manifest is an attestation manifest."""
    media_type = manifest.get("mediaType", "")
    return (
        "attestation" in media_type
        or manifest.get("annotations", {}).get("vnd.docker.reference.type")
        == "attestation-manifest"
    )


def _extract_platforms_from_manifest(
    oci_dir: Path, manifest: dict, seen_platforms: set
) -> list[str]:
    """Extract platforms from a manifest, handling nested indexes."""
    platforms = []

    for child in manifest.get("manifests", []):
        if _is_attestation_manifest(child):
            continue

        platform = child.get("platform", {})
        os_name = platform.get("os", "")
        arch = platform.get("architecture", "")

        # If we have a valid platform, add it
        if os_name and arch and os_name != "unknown" and arch != "unknown":
            platform_str = f"{os_name}/{arch}"
            if platform_str not in seen_platforms:
                platforms.append(platform_str)
                seen_platforms.add(platform_str)

        # If platform is unknown/missing, check if it's a nested index
        elif "digest" in child:
            child_manifest = _read_manifest_file(oci_dir, child["digest"])
            if (
                child_manifest
                and child_manifest.get("mediaType")
                == "application/vnd.oci.image.index.v1+json"
            ):
                # Recursively extract platforms from nested index
                nested_platforms = _extract_platforms_from_manifest(
                    oci_dir, child_manifest, seen_platforms
                )
                platforms.extend(nested_platforms)

    return platforms


def get_platforms_from_oci_index(oci_dir: Path) -> list[str]:
    """Get the list of platforms from an OCI index.

    Args:
        oci_dir: Path to the extracted OCI directory

    Returns:
        List of platform strings (e.g., ["linux/amd64", "linux/arm64"])
    """

    # Read the index.json to find available manifests
    index_file = oci_dir / "index.json"
    if not index_file.exists():
        print(f"Warning: No index.json found in {oci_dir}")
        return []

    with open(index_file) as f:
        index_data = json.load(f)

    platforms = []
    seen_platforms = set()  # To avoid duplicates

    # Process each manifest in the index
    for manifest in index_data.get("manifests", []):
        if _is_attestation_manifest(manifest):
            continue

        # Check if this is tagged as "latest" (our main image)
        annotations = manifest.get("annotations", {})
        ref_name = annotations.get("org.opencontainers.image.ref.name", "")
        if ref_name and ref_name != "latest":
            continue

        # Read the actual manifest
        if "digest" not in manifest:
            continue

        manifest_data = _read_manifest_file(oci_dir, manifest["digest"])
        if not manifest_data:
            continue

        # If it's an image index, extract platforms from it
        if manifest_data.get("mediaType") == "application/vnd.oci.image.index.v1+json":
            index_platforms = _extract_platforms_from_manifest(
                oci_dir, manifest_data, seen_platforms
            )
            platforms.extend(index_platforms)

    return platforms if platforms else ["linux/amd64", "linux/arm64"]  # Fallback


def extract_platform_from_index(index_tar: str, platform: str, output_tar: str) -> None:
    """Extract a specific platform from a multi-platform OCI index.

    Args:
        index_tar: Path to the multi-platform OCI index tar file
        platform: Platform to extract (e.g., "linux/amd64")
        output_tar: Path for the extracted platform-specific tar
    """
    os_name, arch = platform.split("/")

    # Extract the OCI archive to work with the directory layout
    oci_dir = extract_oci_layout(index_tar)

    try:
        # Use skopeo to copy from the OCI directory layout
        # When buildx creates multi-platform images, they're stored with tags like "latest"
        cmd = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{Path.cwd()}:/src",
            "-v",
            f"{oci_dir}:/oci",
            "-w",
            "/src",
            "quay.io/skopeo/stable:latest",
            "copy",
            "--override-arch",
            arch,
            "--override-os",
            os_name,
            "oci:/oci:latest",  # buildx typically tags as "latest"
            f"oci-archive:{output_tar}",
        ]

        run_command(cmd)
    finally:
        # Clean up the extracted directory
        shutil.rmtree(oci_dir, ignore_errors=True)


def generate_sboms(image_tar: str, platform_suffix: str) -> None:
    """Generate SBOMs in multiple formats using syft.

    Args:
        image_tar: Path to the OCI image tar file
        platform_suffix: Suffix for output files (e.g., "linux_amd64")
    """
    formats = {
        "syft-json": f"sbom.latest.{platform_suffix}.syft.json",
        "spdx-json": f"sbom.latest.{platform_suffix}.spdx.json",
        "cyclonedx-json": f"sbom.latest.{platform_suffix}.cyclonedx.json",
    }

    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{Path.cwd()}:/src",
        "-w",
        "/src",
        "anchore/syft:latest",
        f"oci-archive:{image_tar}",
    ]

    for fmt, output in formats.items():
        cmd.extend(["-o", f"{fmt}={output}"])

    result = run_command(cmd, check=False)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)

    # In CI, also print to stdout
    if should_output_to_stdout():
        print(result.stdout)

    print(f"SBOMs generated: {', '.join(formats.values())}")


def scan_vulnerabilities(sbom_file: str, platform_suffix: str) -> None:
    """Scan for vulnerabilities using grype.

    Args:
        sbom_file: Path to the SBOM file
        platform_suffix: Suffix for output files
    """
    output_file = f"vulns.latest.{platform_suffix}.json"

    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{Path.cwd()}:/src",
        "-w",
        "/src",
        "anchore/grype:latest",
        f"sbom:{sbom_file}",
        "-o",
        "json",
    ]

    result = run_command(cmd, check=False)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)

    # Write to file
    with open(output_file, "w") as f:
        f.write(result.stdout)

    # In CI, also print to stdout
    if should_output_to_stdout():
        print(result.stdout)

    print(f"Vulnerability scan complete: {output_file}")


def check_licenses(sbom_file: str, platform_suffix: str) -> None:
    """Check license compliance using grant.

    Args:
        sbom_file: Path to the SPDX SBOM file
        platform_suffix: Suffix for output files
    """
    output_file = f"license-check.latest.{platform_suffix}.json"
    config_file = ".github/.grant.yml"

    if not Path(config_file).exists():
        raise FileNotFoundError(f"Grant config file {config_file} not found")

    cmd = ["grant", "check", sbom_file, "--config", config_file, "-o", "json"]

    result = run_command(cmd, check=False)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        # Don't exit on grant errors, just warn

    # Write to file
    with open(output_file, "w") as f:
        f.write(result.stdout)

    # In CI, also print to stdout
    if should_output_to_stdout():
        print(result.stdout)

    print(f"License check complete: {output_file}")


def process_platform(
    image_tar: str,
    platform: str,
    platform_suffix: str,
    operations: list[str],
    cleanup: bool = False,
) -> None:
    """Process a single platform: generate SBOM, scan vulns, check licenses.

    Args:
        image_tar: Path to the OCI image tar file
        platform: Platform string (e.g., "linux/amd64")
        platform_suffix: Suffix for output files
        operations: List of operations to perform ("sbom", "vulnscan", "license-check")
        cleanup: Whether to clean up extracted tar files
    """
    print(f"\nProcessing platform: {platform}")

    if "sbom" in operations:
        print(f"Generating SBOMs for platform {platform}...")
        generate_sboms(image_tar, platform_suffix)

    if "vulnscan" in operations:
        sbom_file = f"sbom.latest.{platform_suffix}.syft.json"
        if Path(sbom_file).exists():
            print(f"Scanning vulnerabilities for platform {platform}...")
            scan_vulnerabilities(sbom_file, platform_suffix)
        else:
            raise FileNotFoundError(
                f"SBOM file {sbom_file} not found for vulnerability scan"
            )

    if "license-check" in operations:
        sbom_file = f"sbom.latest.{platform_suffix}.spdx.json"
        if Path(sbom_file).exists():
            print(f"Checking licenses for platform {platform}...")
            check_licenses(sbom_file, platform_suffix)
        else:
            raise FileNotFoundError(
                f"SBOM file {sbom_file} not found for license check"
            )

    if cleanup and image_tar.endswith("_extracted.tar"):
        Path(image_tar).unlink()
        print(f"Cleaned up extracted tar: {image_tar}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Handle SBOM generation and scanning for container images"
    )
    parser.add_argument(
        "operation",
        choices=["sbom", "vulnscan", "license-check"],
        help="Operation to perform",
    )
    parser.add_argument(
        "--platform",
        required=True,
        help="Platform specification (e.g., 'linux/amd64', 'all')",
    )
    parser.add_argument(
        "--image-name", required=True, help="Image name (e.g., 'org/repo')"
    )

    args = parser.parse_args()

    # Normalize image name for file paths
    image_name_normalized = args.image_name.replace("/", "_")

    if args.platform == "all":
        # Multi-platform: extract and process each platform
        try:
            image_tar = find_image_tar(args.image_name, args.platform)
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        # Extract the OCI archive to discover platforms
        oci_dir = extract_oci_layout(image_tar)

        try:
            # Discover platforms from the OCI index
            platforms = get_platforms_from_oci_index(oci_dir)
            print(f"Found platforms in image: {', '.join(platforms)}")

            for platform in platforms:
                platform_suffix = platform.replace("/", "_")
                extracted_tar = (
                    f"{image_name_normalized}_latest_{platform_suffix}_extracted.tar"
                )

                try:
                    # Extract platform from index
                    print(
                        f"\nExtracting platform {platform} from multi-platform image..."
                    )

                    # Use skopeo to copy from the OCI directory layout
                    os_name, arch = platform.split("/")
                    cmd = [
                        "docker",
                        "run",
                        "--rm",
                        "-v",
                        f"{Path.cwd()}:/src",
                        "-v",
                        f"{oci_dir}:/oci",
                        "-w",
                        "/src",
                        "quay.io/skopeo/stable:latest",
                        "copy",
                        "--override-arch",
                        arch,
                        "--override-os",
                        os_name,
                        "oci:/oci:latest",
                        f"oci-archive:{extracted_tar}",
                    ]

                    run_command(cmd)

                    # Process the extracted platform
                    process_platform(
                        extracted_tar,
                        platform,
                        platform_suffix,
                        [args.operation],
                        cleanup=True,
                    )
                except Exception:
                    # Clean up extracted tar on error
                    if Path(extracted_tar).exists():
                        Path(extracted_tar).unlink()
                    raise
        finally:
            # Clean up the extracted directory
            shutil.rmtree(oci_dir, ignore_errors=True)

        print(f"\n{args.operation} complete for all platforms")
    else:
        # Single platform: process directly
        try:
            image_tar = find_image_tar(args.image_name, args.platform)
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        # Check if we got a multi-platform tar when asking for a specific platform
        if image_tar.endswith("_all.tar") and args.platform != "all":
            # Need to extract the specific platform from the multi-platform image
            platform_suffix = get_platform_suffix(args.platform)
            extracted_tar = (
                f"{image_name_normalized}_latest_{platform_suffix}_extracted.tar"
            )

            print(f"Extracting platform {args.platform} from multi-platform image...")
            try:
                extract_platform_from_index(image_tar, args.platform, extracted_tar)

                # Process the extracted platform
                process_platform(
                    extracted_tar,
                    args.platform,
                    platform_suffix,
                    [args.operation],
                    cleanup=True,
                )
            except Exception:
                # Clean up extracted tar on error
                if Path(extracted_tar).exists():
                    Path(extracted_tar).unlink()
                raise
        else:
            # Process single platform image directly
            platform_suffix = get_platform_suffix(args.platform)
            process_platform(
                image_tar, args.platform, platform_suffix, [args.operation]
            )


if __name__ == "__main__":
    main()
