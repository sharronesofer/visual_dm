#!/usr/bin/env python3

import os
import re
import shutil
from pathlib import Path
import subprocess
import sys

# Base directories
BACKEND_SYSTEMS_DIR = Path("backend/systems")
BACKEND_TESTS_DIR = Path("backend/tests/systems")

def find_test_files():
    """Find all test files in the backend/systems directory."""
    test_files = []
    for root, _, files in os.walk(BACKEND_SYSTEMS_DIR):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                source_path = Path(root) / file
                test_files.append(source_path)
    return test_files

def create_target_directory(source_file):
    """Create the target directory structure that mirrors the source."""
    rel_path = source_file.relative_to(BACKEND_SYSTEMS_DIR)
    # Get the directory part without the filename
    rel_dir = rel_path.parent
    target_dir = BACKEND_TESTS_DIR / rel_dir
    os.makedirs(target_dir, exist_ok=True)
    return target_dir / rel_path.name

def copy_and_remove_test_file(source_file, target_file):
    """Copy a test file from source to target and then remove the original."""
    # Create parent directories if they don't exist
    os.makedirs(target_file.parent, exist_ok=True)
    
    # Copy the file (imports should be fine as they're absolute)
    shutil.copy2(source_file, target_file)
    
    print(f"Copied: {source_file} -> {target_file}")
    
    # Automatically remove the original file (no prompt)
    os.remove(source_file)
    print(f"Removed: {source_file}")

def ensure_init_files(target_file):
    """Ensure that __init__.py files exist in all parent directories."""
    current_dir = target_file.parent
    # Go up to the BACKEND_TESTS_DIR
    while current_dir != BACKEND_TESTS_DIR.parent:
        init_file = current_dir / "__init__.py"
        if not init_file.exists():
            with open(init_file, 'w') as f:
                f.write("# Automatically created during test migration\n")
            print(f"Created __init__.py in {current_dir}")
        current_dir = current_dir.parent

def main():
    # Find all test files
    test_files = find_test_files()
    print(f"Found {len(test_files)} test files to move")
    
    # Move each test file
    for source_file in test_files:
        target_file = create_target_directory(source_file)
        ensure_init_files(target_file)
        copy_and_remove_test_file(source_file, target_file)
    
    print("Test migration completed!")
    print("Please verify that the tests still work in their new location.")

if __name__ == "__main__":
    main() 