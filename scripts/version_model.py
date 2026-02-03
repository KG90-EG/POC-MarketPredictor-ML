#!/usr/bin/env python3
"""
Model Version Management Script (FR-004 Phase 2).

Manages model versions with proper archiving and metadata tracking.

Features:
    - Automatic versioning with semantic versioning
    - Production/staging/archive structure
    - Metadata tracking (metrics, timestamp, git commit)
    - Version comparison
    - Safe promotion workflow

Usage:
    # Promote model to staging
    python scripts/version_model.py promote --model model_20250127.bin --to staging

    # Promote staging to production
    python scripts/version_model.py promote --from staging --to production

    # Archive current production
    python scripts/version_model.py archive --keep 5

    # List all versions
    python scripts/version_model.py list

    # Show version info
    python scripts/version_model.py info --version v1.2.3

Exit Codes:
    0: Success
    1: Operation failed
    2: Model not found
    3: Invalid arguments
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Project root
ROOT_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT_DIR / "models"
PRODUCTION_DIR = MODELS_DIR / "production"
STAGING_DIR = MODELS_DIR / "staging"
ARCHIVE_DIR = MODELS_DIR / "archive"

# Exit codes
EXIT_SUCCESS = 0
EXIT_OPERATION_FAILED = 1
EXIT_MODEL_NOT_FOUND = 2
EXIT_INVALID_ARGS = 3


def ensure_directories() -> None:
    """Create model directory structure."""
    for dir_path in [PRODUCTION_DIR, STAGING_DIR, ARCHIVE_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)


def get_git_commit() -> str:
    """Get current git commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT_DIR
        )
        return result.stdout.strip()[:8] if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def compute_checksum(file_path: Path) -> str:
    """Compute SHA256 checksum of model file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()[:16]


def get_next_version(current_version: str | None, bump: str = "patch") -> str:
    """
    Get next semantic version.

    Args:
        current_version: Current version string (e.g., "v1.2.3")
        bump: Version bump type ("major", "minor", "patch")

    Returns:
        Next version string
    """
    if not current_version:
        return "v1.0.0"

    # Parse version
    version = current_version.lstrip("v")
    parts = version.split(".")
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

    if bump == "major":
        return f"v{major + 1}.0.0"
    elif bump == "minor":
        return f"v{major}.{minor + 1}.0"
    else:  # patch
        return f"v{major}.{minor}.{patch + 1}"


def load_metadata(model_dir: Path) -> dict | None:
    """Load metadata for a model directory."""
    metadata_file = model_dir / "metadata.json"
    if metadata_file.exists():
        with open(metadata_file) as f:
            return json.load(f)
    return None


def save_metadata(model_dir: Path, metadata: dict) -> None:
    """Save metadata to model directory."""
    metadata_file = model_dir / "metadata.json"
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2, default=str)


def create_model_metadata(
    model_path: Path, version: str, metrics: dict | None = None, description: str = ""
) -> dict:
    """Create metadata for a model."""
    return {
        "version": version,
        "created_at": datetime.utcnow().isoformat(),
        "git_commit": get_git_commit(),
        "checksum": compute_checksum(model_path),
        "file_size_bytes": model_path.stat().st_size,
        "metrics": metrics or {},
        "description": description,
        "source_file": model_path.name,
    }


def cmd_promote(args: argparse.Namespace) -> int:
    """Promote model to staging or production."""
    ensure_directories()

    # Determine source
    if args.model:
        source_path = MODELS_DIR / args.model
        if not source_path.exists():
            print(f"Error: Model not found: {source_path}")
            return EXIT_MODEL_NOT_FOUND
    elif args.source == "staging":
        source_path = STAGING_DIR / "model.bin"
        if not source_path.exists():
            print("Error: No model in staging")
            return EXIT_MODEL_NOT_FOUND
    else:
        print("Error: Must specify --model or --from staging")
        return EXIT_INVALID_ARGS

    # Determine destination
    if args.to == "staging":
        dest_dir = STAGING_DIR
    elif args.to == "production":
        dest_dir = PRODUCTION_DIR
        # Archive current production first
        if (PRODUCTION_DIR / "model.bin").exists():
            cmd_archive(argparse.Namespace(keep=10))
    else:
        print(f"Error: Invalid destination: {args.to}")
        return EXIT_INVALID_ARGS

    # Get current version for production
    current_metadata = load_metadata(dest_dir)
    current_version = current_metadata.get("version") if current_metadata else None

    # Bump version
    new_version = get_next_version(current_version, args.bump)

    # Load metrics from training results if available
    metrics = {}
    results_file = MODELS_DIR / "training_results.json"
    if results_file.exists():
        with open(results_file) as f:
            results = json.load(f)
            metrics = results.get("metrics", {})

    # Create metadata
    metadata = create_model_metadata(
        source_path,
        new_version,
        metrics=metrics,
        description=args.description or f"Promoted to {args.to}",
    )

    # Copy model
    dest_model = dest_dir / "model.bin"
    shutil.copy2(source_path, dest_model)
    save_metadata(dest_dir, metadata)

    # Also maintain backward-compatible prod_model.bin
    if args.to == "production":
        legacy_path = MODELS_DIR / "prod_model.bin"
        shutil.copy2(source_path, legacy_path)

    print(f"✓ Promoted {source_path.name} to {args.to}")
    print(f"  Version: {new_version}")
    print(f"  Checksum: {metadata['checksum']}")

    return EXIT_SUCCESS


def cmd_archive(args: argparse.Namespace) -> int:
    """Archive current production model."""
    ensure_directories()

    prod_model = PRODUCTION_DIR / "model.bin"
    prod_metadata = load_metadata(PRODUCTION_DIR)

    if not prod_model.exists():
        print("No production model to archive")
        return EXIT_SUCCESS

    # Create archive name
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    version = prod_metadata.get("version", "unknown") if prod_metadata else "unknown"
    archive_name = f"model_{version}_{timestamp}"
    archive_path = ARCHIVE_DIR / archive_name

    # Create archive directory
    archive_path.mkdir(parents=True, exist_ok=True)

    # Copy model and metadata
    shutil.copy2(prod_model, archive_path / "model.bin")
    if prod_metadata:
        prod_metadata["archived_at"] = datetime.utcnow().isoformat()
        save_metadata(archive_path, prod_metadata)

    print(f"✓ Archived production model to {archive_name}")

    # Cleanup old archives
    if args.keep:
        archives = sorted(ARCHIVE_DIR.iterdir(), reverse=True)
        for old_archive in archives[args.keep :]:
            if old_archive.is_dir():
                shutil.rmtree(old_archive)
                print(f"  Removed old archive: {old_archive.name}")

    return EXIT_SUCCESS


def cmd_list(args: argparse.Namespace) -> int:
    """List all model versions."""
    ensure_directories()

    print("\n=== Model Versions ===\n")

    # Production
    print("PRODUCTION:")
    prod_meta = load_metadata(PRODUCTION_DIR)
    if prod_meta:
        print(f"  Version: {prod_meta.get('version', 'unknown')}")
        print(f"  Created: {prod_meta.get('created_at', 'unknown')[:19]}")
        print(f"  Accuracy: {prod_meta.get('metrics', {}).get('accuracy', 'N/A')}")
    else:
        print("  No production model")

    # Staging
    print("\nSTAGING:")
    staging_meta = load_metadata(STAGING_DIR)
    if staging_meta:
        print(f"  Version: {staging_meta.get('version', 'unknown')}")
        print(f"  Created: {staging_meta.get('created_at', 'unknown')[:19]}")
        print(f"  Accuracy: {staging_meta.get('metrics', {}).get('accuracy', 'N/A')}")
    else:
        print("  No staging model")

    # Archives
    print("\nARCHIVE:")
    if ARCHIVE_DIR.exists():
        archives = sorted(ARCHIVE_DIR.iterdir(), reverse=True)
        if archives:
            for archive in archives[:5]:  # Show last 5
                meta = load_metadata(archive)
                if meta:
                    print(
                        f"  {meta.get('version', archive.name)}: {meta.get('created_at', '')[:19]}"
                    )
            if len(archives) > 5:
                print(f"  ... and {len(archives) - 5} more")
        else:
            print("  No archived models")
    else:
        print("  No archived models")

    # Standalone models
    print("\nSTANDALONE MODELS:")
    standalone = list(MODELS_DIR.glob("model_*.bin"))
    if standalone:
        for model in sorted(standalone, reverse=True)[:5]:
            print(f"  {model.name}")
        if len(standalone) > 5:
            print(f"  ... and {len(standalone) - 5} more")
    else:
        print("  No standalone models")

    return EXIT_SUCCESS


def cmd_info(args: argparse.Namespace) -> int:
    """Show detailed version info."""
    ensure_directories()

    # Find version
    version = args.version

    # Check production
    prod_meta = load_metadata(PRODUCTION_DIR)
    if prod_meta and prod_meta.get("version") == version:
        metadata = prod_meta
        location = "production"
    elif prod_meta and version == "production":
        metadata = prod_meta
        location = "production"
    else:
        # Check staging
        staging_meta = load_metadata(STAGING_DIR)
        if staging_meta and staging_meta.get("version") == version:
            metadata = staging_meta
            location = "staging"
        elif staging_meta and version == "staging":
            metadata = staging_meta
            location = "staging"
        else:
            # Check archives
            for archive in ARCHIVE_DIR.iterdir():
                meta = load_metadata(archive)
                if meta and meta.get("version") == version:
                    metadata = meta
                    location = f"archive/{archive.name}"
                    break
            else:
                print(f"Version not found: {version}")
                return EXIT_MODEL_NOT_FOUND

    print(f"\n=== Model Version: {metadata.get('version', 'unknown')} ===\n")
    print(f"Location:    {location}")
    print(f"Created:     {metadata.get('created_at', 'unknown')}")
    print(f"Git Commit:  {metadata.get('git_commit', 'unknown')}")
    print(f"Checksum:    {metadata.get('checksum', 'unknown')}")
    print(f"Size:        {metadata.get('file_size_bytes', 0) / 1024:.1f} KB")
    print(f"Description: {metadata.get('description', '')}")

    metrics = metadata.get("metrics", {})
    if metrics:
        print("\nMetrics:")
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.4f}")
            else:
                print(f"  {key}: {value}")

    return EXIT_SUCCESS


def cmd_compare(args: argparse.Namespace) -> int:
    """Compare two model versions."""
    ensure_directories()

    # Load metadata for both versions
    v1_meta = None
    v2_meta = None

    for version, target in [(args.version1, "v1"), (args.version2, "v2")]:
        if version == "production":
            meta = load_metadata(PRODUCTION_DIR)
        elif version == "staging":
            meta = load_metadata(STAGING_DIR)
        else:
            # Check archives
            for archive in ARCHIVE_DIR.iterdir():
                m = load_metadata(archive)
                if m and m.get("version") == version:
                    meta = m
                    break
            else:
                meta = None

        if target == "v1":
            v1_meta = meta
        else:
            v2_meta = meta

    if not v1_meta:
        print(f"Version not found: {args.version1}")
        return EXIT_MODEL_NOT_FOUND
    if not v2_meta:
        print(f"Version not found: {args.version2}")
        return EXIT_MODEL_NOT_FOUND

    print(f"\n=== Comparison: {args.version1} vs {args.version2} ===\n")

    # Compare metrics
    print(f"{'Metric':<15} {'V1':>12} {'V2':>12} {'Diff':>12}")
    print("-" * 51)

    v1_metrics = v1_meta.get("metrics", {})
    v2_metrics = v2_meta.get("metrics", {})

    all_metrics = set(v1_metrics.keys()) | set(v2_metrics.keys())
    for metric in sorted(all_metrics):
        v1_val = v1_metrics.get(metric, 0)
        v2_val = v2_metrics.get(metric, 0)
        if isinstance(v1_val, float) and isinstance(v2_val, float):
            diff = v2_val - v1_val
            sign = "+" if diff > 0 else ""
            print(f"{metric:<15} {v1_val:>12.4f} {v2_val:>12.4f} {sign}{diff:>11.4f}")

    return EXIT_SUCCESS


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Model version management", formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # promote command
    promote_parser = subparsers.add_parser("promote", help="Promote model")
    promote_parser.add_argument("--model", help="Model file to promote")
    promote_parser.add_argument("--from", dest="source", help="Source stage (staging)")
    promote_parser.add_argument(
        "--to", required=True, choices=["staging", "production"], help="Destination stage"
    )
    promote_parser.add_argument(
        "--bump", default="patch", choices=["major", "minor", "patch"], help="Version bump type"
    )
    promote_parser.add_argument("--description", help="Version description")

    # archive command
    archive_parser = subparsers.add_parser("archive", help="Archive production model")
    archive_parser.add_argument("--keep", type=int, default=10, help="Number of archives to keep")

    # list command
    subparsers.add_parser("list", help="List all versions")

    # info command
    info_parser = subparsers.add_parser("info", help="Show version info")
    info_parser.add_argument("--version", required=True, help="Version to show")

    # compare command
    compare_parser = subparsers.add_parser("compare", help="Compare versions")
    compare_parser.add_argument("version1", help="First version")
    compare_parser.add_argument("version2", help="Second version")

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()

    if args.command == "promote":
        return cmd_promote(args)
    elif args.command == "archive":
        return cmd_archive(args)
    elif args.command == "list":
        return cmd_list(args)
    elif args.command == "info":
        return cmd_info(args)
    elif args.command == "compare":
        return cmd_compare(args)
    else:
        print("No command specified. Use --help for usage.")
        return EXIT_INVALID_ARGS


if __name__ == "__main__":
    sys.exit(main())
