#!/usr/bin/env python3

import os
from pathlib import Path

# Base directories
BACKEND_SYSTEMS_DIR = Path("backend/systems")
BACKEND_TESTS_DIR = Path("backend/tests/systems")

def get_all_system_dirs():
    """Get all subdirectories from the backend/systems directory."""
    system_dirs = []
    for root, dirs, _ in os.walk(BACKEND_SYSTEMS_DIR):
        for dir_name in dirs:
            if dir_name != "__pycache__" and not dir_name.startswith("."):
                system_dirs.append(Path(root) / dir_name)
    return system_dirs

def create_mirrored_directory(system_dir):
    """Create a mirrored directory in the tests structure with __init__.py."""
    rel_path = system_dir.relative_to(BACKEND_SYSTEMS_DIR)
    target_dir = BACKEND_TESTS_DIR / rel_path
    
    # Create the directory if it doesn't exist
    if not target_dir.exists():
        os.makedirs(target_dir, exist_ok=True)
        print(f"Created directory: {target_dir}")
    
    # Ensure __init__.py exists
    init_file = target_dir / "__init__.py"
    if not init_file.exists():
        with open(init_file, 'w') as f:
            f.write("# Automatically created during test structure preparation\n")
        print(f"Created __init__.py in {target_dir}")

def main():
    # Ensure the base tests/systems directory exists with __init__.py
    os.makedirs(BACKEND_TESTS_DIR, exist_ok=True)
    base_init = BACKEND_TESTS_DIR / "__init__.py"
    if not base_init.exists():
        with open(base_init, 'w') as f:
            f.write("# Automatically created during test structure preparation\n")
        print(f"Created base __init__.py in {BACKEND_TESTS_DIR}")
    
    # Get all system directories
    system_dirs = get_all_system_dirs()
    print(f"Found {len(system_dirs)} system directories to mirror")
    
    # Create mirrored directories with __init__.py files
    for system_dir in system_dirs:
        create_mirrored_directory(system_dir)
    
    print("Test directory structure preparation completed!")

if __name__ == "__main__":
    main() 