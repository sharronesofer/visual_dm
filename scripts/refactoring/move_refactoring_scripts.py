#!/usr/bin/env python3

import os
import shutil
from pathlib import Path
import filecmp
import sys

# Target directory for scripts
TARGET_DIR = Path("scripts/refactoring")

# Scripts to move from root directory
ROOT_SCRIPTS = [
    "categorize_tests.py",
    "fix_missing_data_files.py",
    "fix_missing_log_dir.py",
    "fix_singleton_instantiations.py",
    "fix_sqlalchemy_extend_existing.py",
    "fix_sqlalchemy_imports.py",
    "migrate_tests.py",
    "move_remaining_tests.py",
    "move_unit_tests.py",
    "update_imports.py",
    "verify_tests.py"
]

# Scripts to move from backend directory
BACKEND_SCRIPTS = [
    "fix_patches.py",
    "fix_paths.py",
    "fix_service.py"
]

def ensure_target_directory():
    """Ensure target directory exists."""
    os.makedirs(TARGET_DIR, exist_ok=True)

def move_file(source_path, target_dir):
    """Move a file to the target directory, creating backups if needed."""
    source_file = Path(source_path)
    target_file = target_dir / source_file.name
    
    # If target doesn't exist, simply copy
    if not target_file.exists():
        shutil.copy2(source_file, target_file)
        print(f"Copied: {source_file} -> {target_file}")
        return True
    
    # If target exists, compare and copy only if different
    try:
        if not filecmp.cmp(source_file, target_file, shallow=False):
            # Files are different, create a backup
            backup_file = target_file.with_suffix(f"{target_file.suffix}.bak")
            shutil.copy2(target_file, backup_file)
            print(f"Created backup: {backup_file}")
            
            # Copy the source file
            shutil.copy2(source_file, target_file)
            print(f"Updated: {source_file} -> {target_file}")
            return True
        else:
            print(f"Skipped (identical): {source_file}")
            return True
    except Exception as e:
        print(f"Error copying {source_file} to {target_file}: {e}")
        return False

def move_all_files():
    """Move all refactoring scripts to the target directory."""
    ensure_target_directory()
    
    moved_count = 0
    # Move files from root directory
    for script in ROOT_SCRIPTS:
        source_path = Path(script)
        if source_path.exists():
            if move_file(source_path, TARGET_DIR):
                try:
                    # Remove the original file
                    os.remove(source_path)
                    print(f"Removed original: {source_path}")
                    moved_count += 1
                except Exception as e:
                    print(f"Error removing {source_path}: {e}")
        else:
            print(f"Script not found: {source_path}")
    
    # Move files from backend directory
    for script in BACKEND_SCRIPTS:
        source_path = Path("backend") / script
        if source_path.exists():
            if move_file(source_path, TARGET_DIR):
                try:
                    # Remove the original file
                    os.remove(source_path)
                    print(f"Removed original: {source_path}")
                    moved_count += 1
                except Exception as e:
                    print(f"Error removing {source_path}: {e}")
        else:
            print(f"Script not found: {source_path}")
    
    return moved_count

def main():
    """Main function."""
    print("Moving refactoring scripts to scripts/refactoring directory...")
    moved_count = move_all_files()
    print(f"\nMoved {moved_count} refactoring scripts.")
    
    # Warn about this script itself
    print("\nNote: Don't forget to move this script itself after it's done!")
    print("You can do this with: mv move_refactoring_scripts.py scripts/refactoring/")

if __name__ == "__main__":
    main() 