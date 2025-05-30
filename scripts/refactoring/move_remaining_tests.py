#!/usr/bin/env python3

import os
import shutil
from pathlib import Path
import filecmp

SOURCE_DIR = Path("tests/backend")
TARGET_DIR = Path("backend/tests")

def find_test_files(directory):
    """Find all test files in the given directory."""
    test_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if (file.startswith("test_") and file.endswith(".py")) or file in ["conftest.py", "README.md", "__init__.py"]:
                source_path = Path(root) / file
                test_files.append(source_path)
    return test_files

def create_target_directory(source_file, source_base, target_base):
    """Create the target directory structure that mirrors the source."""
    rel_path = source_file.relative_to(source_base)
    target_file = target_base / rel_path
    os.makedirs(target_file.parent, exist_ok=True)
    return target_file

def compare_and_copy_file(source_file, target_file):
    """Compare files and copy only if different or target doesn't exist."""
    if not target_file.exists():
        shutil.copy2(source_file, target_file)
        print(f"Copied: {source_file} -> {target_file}")
        return True
    
    # If target exists, compare contents
    try:
        if not filecmp.cmp(source_file, target_file, shallow=False):
            # Files are different, create a backup of the target file
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
        print(f"Error comparing {source_file} and {target_file}: {e}")
        return False

def ensure_init_files(target_file):
    """Ensure that __init__.py files exist in all parent directories."""
    current_dir = target_file.parent
    while current_dir != TARGET_DIR.parent:
        init_file = current_dir / "__init__.py"
        if not init_file.exists():
            with open(init_file, 'w') as f:
                f.write("# Automatically created during test migration\n")
            print(f"Created __init__.py in {current_dir}")
        current_dir = current_dir.parent

def main():
    # Find all test files
    test_files = find_test_files(SOURCE_DIR)
    print(f"Found {len(test_files)} files to move")
    
    # Track success for each file
    successful_moves = 0
    
    # Move each test file
    for source_file in test_files:
        target_file = create_target_directory(source_file, SOURCE_DIR, TARGET_DIR)
        ensure_init_files(target_file)
        if compare_and_copy_file(source_file, target_file):
            successful_moves += 1
    
    print(f"\nSuccessfully processed {successful_moves}/{len(test_files)} files")
    print("Migration of remaining tests completed!")

if __name__ == "__main__":
    main() 