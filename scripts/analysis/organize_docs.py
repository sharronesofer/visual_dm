#!/usr/bin/env python3

import os
import shutil
from pathlib import Path
import filecmp
import re

# Files to move with their destinations
FILES_TO_MOVE = {
    # Move development bible to root
    "docs/Development_Bible_Reorganized_Final.md": "./development_bible.md",
    
    # Migration and refactoring summaries to docs/refactoring
    "MIGRATION_SUMMARY.md": "docs/refactoring/migration_summary.md",
    "REFACTORING_SUMMARY.md": "docs/refactoring/refactoring_summary.md",
    "REORGANIZATION_SUMMARY.md": "docs/refactoring/reorganization_summary.md",
    "VDM_REORGANIZATION_SUMMARY.md": "docs/refactoring/vdm_reorganization_summary.md",
    "TEST_MIGRATION_README.md": "docs/refactoring/test_migration_readme.md",
    
    # System documentation
    "# Custom TTRPG System Rules Reference.md": "docs/systems/ttrpg_system_rules_reference.md",
    "POI_MEMORY_SYSTEM_v2.md": "docs/systems/poi_memory_system_v2.md",
    "VisualDM_LootSystem_Roadmap.md": "docs/systems/loot_system_roadmap.md",
}

# Files to keep in place (don't move these)
FILES_TO_KEEP = [
    "README.md",           # Keep README in root
    "requirements-dev.txt" # Keep requirements in root
]

def ensure_directory(file_path):
    """Ensure the directory for the file exists."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def copy_file(source, destination):
    """Copy a file to the destination, creating the directory if needed."""
    ensure_directory(destination)
    
    # If destination doesn't exist, simply copy
    if not os.path.exists(destination):
        shutil.copy2(source, destination)
        print(f"Copied: {source} -> {destination}")
        return True
    
    # If destination exists, compare and copy only if different
    try:
        if not filecmp.cmp(source, destination, shallow=False):
            # Files are different, create a backup
            backup_file = f"{destination}.bak"
            shutil.copy2(destination, backup_file)
            print(f"Created backup: {backup_file}")
            
            # Copy the source file
            shutil.copy2(source, destination)
            print(f"Updated: {source} -> {destination}")
            return True
        else:
            print(f"Skipped (identical): {source}")
            return True
    except Exception as e:
        print(f"Error copying {source} to {destination}: {e}")
        return False

def remove_file(file_path):
    """Remove a file."""
    try:
        os.remove(file_path)
        print(f"Removed original: {file_path}")
        return True
    except Exception as e:
        print(f"Error removing {file_path}: {e}")
        return False

def organize_files():
    """Organize documentation files by moving them to appropriate locations."""
    moved_count = 0
    
    # Process the files that need to be moved
    for source, destination in FILES_TO_MOVE.items():
        if os.path.exists(source):
            if copy_file(source, destination):
                if remove_file(source):
                    moved_count += 1
        else:
            print(f"Source file not found: {source}")
    
    return moved_count

def find_other_docs():
    """Find other documentation files that might need organizing."""
    print("\nOther documentation files that might need organizing:")
    
    # Find markdown files in the root directory that we didn't explicitly handle
    root_docs = []
    for item in os.listdir('.'):
        if item.endswith(('.md', '.txt')) and item not in FILES_TO_KEEP and item != 'organize_docs.py':
            if os.path.isfile(item) and item not in [os.path.basename(dest) for dest in FILES_TO_MOVE.values()]:
                root_docs.append(item)
    
    if root_docs:
        print("\nMarkdown/Text files in root directory:")
        for doc in root_docs:
            print(f"  - {doc}")
    else:
        print("No additional documentation files found in root directory.")

def main():
    """Main function."""
    print("Organizing documentation files...")
    moved_count = organize_files()
    print(f"\nMoved {moved_count} documentation files.")
    
    find_other_docs()
    
    print("\nNote: Don't forget to move this script when you're done!")
    print("You can do this with: mv organize_docs.py scripts/refactoring/")

if __name__ == "__main__":
    main() 