#!/usr/bin/env python3
"""
Cleanup script for world_state refactoring.

This script removes old directories and files that have been consolidated
during the refactoring of the world_state module.
"""
import os
import shutil
import sys
from pathlib import Path

# Directories to be removed
DIRS_TO_REMOVE = [
    "repositories",
    "schemas",
    "services",
    "models",
    "routers",
    "tick_utils"
]

def run_cleanup():
    """Run the cleanup process."""
    # Get the base directory
    base_dir = Path(__file__).parent
    print(f"Base directory: {base_dir}")
    
    # Check each directory and remove
    for dir_name in DIRS_TO_REMOVE:
        dir_path = base_dir / dir_name
        
        if dir_path.exists():
            print(f"Removing directory: {dir_path}")
            try:
                shutil.rmtree(dir_path)
                print(f"✅ Successfully removed {dir_path}")
            except Exception as e:
                print(f"❌ Error removing {dir_path}: {str(e)}")
        else:
            print(f"⚠️ Directory does not exist: {dir_path}")
    
    print("\nCleanup completed!\n")
    print("The world_state directory has been refactored to use the following structure:")
    print("  core/       - Core types, manager, and events")
    print("  mods/       - Mod handling and synchronization")
    print("  events/     - Event handlers for world state events")
    print("  api/        - FastAPI router for HTTP endpoints")
    print("  utils/      - Utility functions for world state operations")

if __name__ == "__main__":
    # Confirm before proceeding
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        run_cleanup()
    else:
        print("This script will remove the following directories from the world_state module:")
        for dir_name in DIRS_TO_REMOVE:
            print(f"  - {dir_name}")
        print("\nThese directories have been consolidated as part of the refactoring process.")
        print("Make sure you have committed any important changes before proceeding.")
        
        confirm = input("\nProceed with cleanup? (y/n): ")
        if confirm.lower() in ["y", "yes"]:
            run_cleanup()
        else:
            print("Cleanup cancelled.") 