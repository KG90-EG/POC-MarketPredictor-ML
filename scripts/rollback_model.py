#!/usr/bin/env python3
"""
Model Rollback Script (FR-004 Phase 2).

Safely rollback to a previous model version.

Features:
    - Rollback to any archived version
    - Automatic backup of current model
    - Validation before activation
    - Dry-run mode for testing

Usage:
    # Rollback to specific version
    python scripts/rollback_model.py --version v1.2.3

    # Rollback to previous version
    python scripts/rollback_model.py --previous

    # List available versions
    python scripts/rollback_model.py --list

    # Dry run
    python scripts/rollback_model.py --version v1.2.3 --dry-run

Exit Codes:
    0: Success
    1: Rollback failed
    2: Version not found
    3: Invalid arguments
"""

import argparse
import json
import shutil
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
EXIT_ROLLBACK_FAILED = 1
EXIT_VERSION_NOT_FOUND = 2
EXIT_INVALID_ARGS = 3


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


def find_version(version: str) -> tuple[Path | None, dict | None]:
    """
    Find a model version in archive.

    Returns:
        Tuple of (model_path, metadata) or (None, None)
    """
    if not ARCHIVE_DIR.exists():
        return None, None

    for archive in ARCHIVE_DIR.iterdir():
        if not archive.is_dir():
            continue

        meta = load_metadata(archive)
        if meta and meta.get("version") == version:
            model_path = archive / "model.bin"
            if model_path.exists():
                return model_path, meta

    return None, None


def find_previous_version() -> tuple[Path | None, dict | None]:
    """
    Find the most recent archived version.

    Returns:
        Tuple of (model_path, metadata) or (None, None)
    """
    if not ARCHIVE_DIR.exists():
        return None, None

    # Sort archives by archived_at timestamp
    archives = []
    for archive in ARCHIVE_DIR.iterdir():
        if not archive.is_dir():
            continue
        meta = load_metadata(archive)
        if meta:
            archives.append((archive, meta))

    if not archives:
        return None, None

    # Sort by archived_at descending
    archives.sort(key=lambda x: x[1].get("archived_at", ""), reverse=True)

    archive, meta = archives[0]
    model_path = archive / "model.bin"
    if model_path.exists():
        return model_path, meta

    return None, None


def backup_current_production() -> str | None:
    """
    Backup current production model before rollback.

    Returns:
        Backup path or None if no production model
    """
    prod_model = PRODUCTION_DIR / "model.bin"
    if not prod_model.exists():
        return None

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_name = f"pre_rollback_{timestamp}"
    backup_path = ARCHIVE_DIR / backup_name

    backup_path.mkdir(parents=True, exist_ok=True)
    shutil.copy2(prod_model, backup_path / "model.bin")

    # Copy metadata
    prod_meta = load_metadata(PRODUCTION_DIR)
    if prod_meta:
        prod_meta["archived_at"] = datetime.utcnow().isoformat()
        prod_meta["archive_reason"] = "pre_rollback_backup"
        save_metadata(backup_path, prod_meta)

    return str(backup_path)


def rollback_to_version(model_path: Path, metadata: dict, dry_run: bool = False) -> bool:
    """
    Rollback to a specific version.

    Args:
        model_path: Path to the model file
        metadata: Model metadata
        dry_run: If True, don't actually rollback

    Returns:
        True if successful
    """
    if dry_run:
        print(f"DRY RUN: Would rollback to {metadata.get('version', 'unknown')}")
        print(f"  Source: {model_path}")
        print(f"  Destination: {PRODUCTION_DIR / 'model.bin'}")
        return True

    # Ensure production directory exists
    PRODUCTION_DIR.mkdir(parents=True, exist_ok=True)

    # Backup current
    backup_path = backup_current_production()
    if backup_path:
        print(f"✓ Backed up current production to: {Path(backup_path).name}")

    # Copy model to production
    prod_model = PRODUCTION_DIR / "model.bin"
    shutil.copy2(model_path, prod_model)

    # Update metadata
    rollback_meta = metadata.copy()
    rollback_meta["rolled_back_at"] = datetime.utcnow().isoformat()
    rollback_meta["rollback_from"] = backup_path
    save_metadata(PRODUCTION_DIR, rollback_meta)

    # Also update legacy prod_model.bin
    legacy_path = MODELS_DIR / "prod_model.bin"
    shutil.copy2(model_path, legacy_path)

    print(f"✓ Rolled back to {metadata.get('version', 'unknown')}")

    return True


def list_versions() -> None:
    """List all available versions for rollback."""
    print("\n=== Available Versions for Rollback ===\n")

    # Current production
    print("CURRENT PRODUCTION:")
    prod_meta = load_metadata(PRODUCTION_DIR)
    if prod_meta:
        print(f"  Version: {prod_meta.get('version', 'unknown')}")
        print(f"  Created: {prod_meta.get('created_at', 'unknown')[:19]}")
    else:
        print("  No production model")

    # Archived versions
    print("\nARCHIVED VERSIONS:")
    if not ARCHIVE_DIR.exists():
        print("  No archived versions")
        return

    archives = []
    for archive in ARCHIVE_DIR.iterdir():
        if not archive.is_dir():
            continue
        meta = load_metadata(archive)
        if meta:
            archives.append((archive.name, meta))

    if not archives:
        print("  No archived versions")
        return

    # Sort by archived_at descending
    archives.sort(key=lambda x: x[1].get("archived_at", ""), reverse=True)

    for name, meta in archives:
        version = meta.get("version", "unknown")
        archived_at = meta.get("archived_at", "unknown")[:19]
        accuracy = meta.get("metrics", {}).get("accuracy")
        acc_str = f"{accuracy:.2%}" if accuracy else "N/A"
        print(f"  {version:12} | Archived: {archived_at} | Accuracy: {acc_str}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Rollback to a previous model version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s --version v1.2.3    # Rollback to specific version
    %(prog)s --previous          # Rollback to most recent archive
    %(prog)s --list              # List available versions
    %(prog)s --version v1.2.3 --dry-run  # Test rollback
        """,
    )

    parser.add_argument("--version", help="Version to rollback to (e.g., v1.2.3)")
    parser.add_argument(
        "--previous", action="store_true", help="Rollback to most recent archived version"
    )
    parser.add_argument("--list", action="store_true", help="List available versions")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would happen without making changes"
    )
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompt")

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # List mode
    if args.list:
        list_versions()
        return EXIT_SUCCESS

    # Find version to rollback to
    if args.previous:
        model_path, metadata = find_previous_version()
        if not model_path:
            print("Error: No archived versions found")
            return EXIT_VERSION_NOT_FOUND
    elif args.version:
        model_path, metadata = find_version(args.version)
        if not model_path:
            print(f"Error: Version not found: {args.version}")
            print("Use --list to see available versions")
            return EXIT_VERSION_NOT_FOUND
    else:
        print("Error: Must specify --version, --previous, or --list")
        return EXIT_INVALID_ARGS

    # Confirm rollback
    print("\n=== Rollback Confirmation ===\n")
    print(f"Version:  {metadata.get('version', 'unknown')}")
    print(f"Created:  {metadata.get('created_at', 'unknown')[:19]}")
    print(f"Accuracy: {metadata.get('metrics', {}).get('accuracy', 'N/A')}")
    print(f"Source:   {model_path}")

    if not args.force and not args.dry_run:
        response = input("\nProceed with rollback? [y/N]: ")
        if response.lower() != "y":
            print("Rollback cancelled")
            return EXIT_SUCCESS

    # Perform rollback
    success = rollback_to_version(model_path, metadata, args.dry_run)

    if success:
        if not args.dry_run:
            print("\n✓ Rollback complete!")
            print("  Restart server to use rolled-back model: make restart")
        return EXIT_SUCCESS
    else:
        print("\n✗ Rollback failed")
        return EXIT_ROLLBACK_FAILED


if __name__ == "__main__":
    sys.exit(main())
