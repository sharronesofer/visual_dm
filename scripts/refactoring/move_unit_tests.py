#!/usr/bin/env python3

import os
import shutil
from pathlib import Path
import filecmp

# Base directories
SOURCE_DIR = Path("backend/tests/unit")
TARGET_DIR = Path("backend/tests/systems")

def find_test_files(directory):
    """Find all test files in the given directory."""
    test_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if (file.startswith("test_") and file.endswith(".py")) or file == "__init__.py":
                source_path = Path(root) / file
                test_files.append(source_path)
    return test_files

def create_target_path(source_file):
    """Create the target path based on the source file path."""
    rel_path = source_file.relative_to(SOURCE_DIR)
    if rel_path.parts[0] == "systems":
        # Remove the "systems" part from the path
        new_parts = rel_path.parts[1:]
        rel_path = Path(*new_parts)
    
    target_file = TARGET_DIR / rel_path
    os.makedirs(target_file.parent, exist_ok=True)
    return target_file

def copy_file(source_file, target_file):
    """Copy a file, creating a backup if needed."""
    if not target_file.exists():
        shutil.copy2(source_file, target_file)
        print(f"Copied: {source_file} -> {target_file}")
        return True
    
    # If target exists, compare contents
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

def main():
    # Find all test files
    test_files = find_test_files(SOURCE_DIR)
    print(f"Found {len(test_files)} files to move")
    
    # Copy each file
    for source_file in test_files:
        target_file = create_target_path(source_file)
        copy_file(source_file, target_file)
    
    print(f"\nAll unit tests have been moved to the systems directory.")
    print(f"You can now delete the unit directory if desired.")

if __name__ == "__main__":
    main() 