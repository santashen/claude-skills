#!/usr/bin/env python3
"""
Claude Skills & Commands Sync Script

This script syncs the skills and commands from this repository to your
Claude Code configuration directory across different operating systems.
"""

import os
import sys
import shutil
import platform
import argparse
from pathlib import Path


def get_claude_config_path():
    """
    Get the Claude Code configuration directory based on the OS.

    Returns:
        Path: The path to the Claude Code configuration directory.
    """
    system = platform.system()
    home = Path.home()

    if system == "Windows":
        # Windows: %APPDATA%\Claude\
        config_path = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming")) / "Claude"
    elif system == "Darwin":
        # macOS: ~/Library/Application Support/Claude/
        config_path = home / "Library" / "Application Support" / "Claude"
    else:
        # Linux: ~/.config/Claude/
        config_path = home / ".config" / "Claude"

    return config_path


def supports_symlink():
    """
    Check if the platform supports symlinks and we have permission to create them.

    Returns:
        bool: True if symlinks are supported, False otherwise.
    """
    system = platform.system()

    # Check if we're on Windows and developer mode is enabled
    if system == "Windows":
        try:
            # Try to create a temporary symlink
            temp_path = Path(os.getcwd()) / "temp_symlink_test"
            temp_path.symlink_to(Path(os.getcwd()))
            temp_path.unlink()
            return True
        except (OSError, NotImplementedError):
            return False

    # Unix-like systems generally support symlinks
    return True


def sync_directory(source_dir, target_dir, use_symlink=True, force_copy=False):
    """
    Sync a directory from source to target.

    Args:
        source_dir: Path to the source directory.
        target_dir: Path to the target directory.
        use_symlink: Whether to use symlinks if available.
        force_copy: Force copy even if symlinks are available.

    Returns:
        dict: Statistics about the sync operation.
    """
    source = Path(source_dir).resolve()
    target = Path(target_dir).resolve()

    if not source.exists():
        return {"status": "error", "message": f"Source directory not found: {source}"}

    stats = {"linked": 0, "copied": 0, "skipped": 0, "errors": 0}
    errors = []

    # Ensure target parent directory exists
    target.parent.mkdir(parents=True, exist_ok=True)

    # Handle the target directory
    if target.exists():
        if target.is_symlink():
            print(f"  Removing existing symlink: {target}")
            target.unlink()
        elif target.is_dir():
            # Check if it's already synced (contains same files)
            existing_files = set(str(f.name) for f in target.iterdir() if f.is_file())
            source_files = set(str(f.name) for f in source.iterdir() if f.is_file())

            if existing_files == source_files and not force_copy:
                print(f"  Target already synced: {target}")
                return {"status": "already_synced", **stats}

    # Decide whether to use symlink or copy
    use_link = use_symlink and supports_symlink() and not force_copy

    if use_link:
        try:
            if target.exists():
                shutil.rmtree(target)
            target.symlink_to(source)
            print(f"  Created symlink: {target} -> {source}")
            stats["linked"] = 1
        except OSError as e:
            print(f"  Symlink failed, falling back to copy: {e}")
            use_link = False

    if not use_link:
        # Copy mode
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)
        print(f"  Copied directory: {source} -> {target}")
        stats["copied"] = 1

    return {"status": "success", **stats}


def sync_commands(source_dir, target_dir, use_symlink=True, force_copy=False):
    """
    Sync individual command files from source to target.

    Args:
        source_dir: Path to the source commands directory.
        target_dir: Path to the target commands directory.
        use_symlink: Whether to use symlinks if available.
        force_copy: Force copy even if symlinks are available.

    Returns:
        dict: Statistics about the sync operation.
    """
    source = Path(source_dir).resolve()
    target = Path(target_dir).resolve()

    if not source.exists():
        return {"status": "error", "message": f"Source directory not found: {source}"}

    stats = {"linked": 0, "copied": 0, "skipped": 0, "errors": 0}

    # Ensure target directory exists
    target.mkdir(parents=True, exist_ok=True)

    # Decide whether to use symlink or copy
    use_link = use_symlink and supports_symlink() and not force_copy

    for source_file in source.iterdir():
        if source_file.is_file():
            target_file = target / source_file.name

            try:
                # Remove existing target if it exists
                if target_file.exists():
                    if target_file.is_symlink():
                        target_file.unlink()
                    else:
                        target_file.unlink()

                if use_link:
                    target_file.symlink_to(source_file)
                    print(f"  Linked: {source_file.name}")
                    stats["linked"] += 1
                else:
                    shutil.copy2(source_file, target_file)
                    print(f"  Copied: {source_file.name}")
                    stats["copied"] += 1

            except Exception as e:
                print(f"  Error syncing {source_file.name}: {e}")
                stats["errors"] += 1

    return {"status": "success", **stats}


def main():
    parser = argparse.ArgumentParser(
        description="Sync Claude skills and commands to local configuration"
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Force copy instead of using symlinks"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--config-path",
        type=str,
        help="Custom Claude config path (auto-detected by default)"
    )

    args = parser.parse_args()

    # Get the repository root
    repo_root = Path(__file__).parent.resolve()
    skills_dir = repo_root / "skills"
    commands_dir = repo_root / "commands"

    # Get Claude config path
    claude_config = Path(args.config_path) if args.config_path else get_claude_config_path()

    print(f"Claude Code config path: {claude_config}")
    print(f"Repository root: {repo_root}")
    print(f"Symlink support: {supports_symlink()}")
    print()

    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        print()

    # Sync skills
    print("Syncing skills...")
    target_skills = claude_config / "skills"
    if not args.dry_run:
        sync_directory(skills_dir, target_skills, use_symlink=not args.copy, force_copy=args.copy)
    else:
        print(f"  Would sync: {skills_dir} -> {target_skills}")
    print()

    # Sync commands
    print("Syncing commands...")
    target_commands = claude_config / "commands"
    if not args.dry_run:
        sync_commands(commands_dir, target_commands, use_symlink=not args.copy, force_copy=args.copy)
    else:
        print(f"  Would sync: {commands_dir} -> {target_commands}")
    print()

    if not args.dry_run:
        print("Sync complete!")
        print("\nTo use your custom skills and commands, restart Claude Code.")
    else:
        print("Dry run complete. Use without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
