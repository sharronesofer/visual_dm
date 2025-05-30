#!/usr/bin/env python3

import os
import shutil
from pathlib import Path
import filecmp

# Source and target directories
SOURCE_DIR = Path("backend/tests/utils")
TARGET_DIR = Path("scripts/testing")

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

def find_test_files():
    """Find all test files in the source directory."""
    test_files = []
    for item in SOURCE_DIR.iterdir():
        if item.name.startswith("test_") and item.suffix == ".py" and item.is_file():
            test_files.append(item)
    return test_files

def move_all_files():
    """Move all test utility files to the target directory."""
    ensure_target_directory()
    
    test_files = find_test_files()
    print(f"Found {len(test_files)} test utility files to move")
    
    moved_count = 0
    for source_file in test_files:
        if move_file(source_file, TARGET_DIR):
            try:
                # Remove the original file
                os.remove(source_file)
                print(f"Removed original: {source_file}")
                moved_count += 1
            except Exception as e:
                print(f"Error removing {source_file}: {e}")
    
    return moved_count

def clean_up_utils_dir():
    """Clean up the utils directory if it's empty."""
    if not any(SOURCE_DIR.iterdir()):
        try:
            os.rmdir(SOURCE_DIR)
            print(f"Removed empty directory: {SOURCE_DIR}")
            return True
        except Exception as e:
            print(f"Error removing directory {SOURCE_DIR}: {e}")
            return False
    else:
        # Check if only __init__.py remains
        files = list(SOURCE_DIR.iterdir())
        if len(files) == 1 and files[0].name == "__init__.py":
            try:
                os.remove(files[0])
                os.rmdir(SOURCE_DIR)
                print(f"Removed __init__.py and empty directory: {SOURCE_DIR}")
                return True
            except Exception as e:
                print(f"Error cleaning up {SOURCE_DIR}: {e}")
                return False
        else:
            print(f"Directory not empty, keeping: {SOURCE_DIR}")
            return False

def main():
    """Main function."""
    print("Moving test utility files to scripts/testing directory...")
    moved_count = move_all_files()
    print(f"\nMoved {moved_count} test utility files.")
    
    if moved_count > 0:
        clean_up_utils_dir()
    
    # Warn about this script itself
    print("\nNote: Don't forget to move this script itself after it's done!")
    print("You can do this with: mv move_test_utils.py scripts/testing/")

if __name__ == "__main__":
    main() 