#!/usr/bin/env python3

import os
import shutil
from pathlib import Path

# Base directories
BACKEND_DIR = Path("backend")
BACKEND_TESTS_DIR = Path("backend/tests")
BACKEND_SYSTEMS_DIR = Path("backend/systems")

def copy_test_configs():
    """Copy pytest configuration files to the appropriate directories."""
    # Copy pytest.ini to backend/tests if it doesn't exist
    source_pytest_ini = BACKEND_DIR / "pytest.ini"
    target_pytest_ini = BACKEND_TESTS_DIR / "pytest.ini"
    
    if source_pytest_ini.exists() and not target_pytest_ini.exists():
        shutil.copy2(source_pytest_ini, target_pytest_ini)
        print(f"Copied {source_pytest_ini} to {target_pytest_ini}")
    
    # Copy conftest.py to backend/tests/systems if it doesn't exist
    source_conftest = BACKEND_TESTS_DIR / "conftest.py"
    target_conftest = BACKEND_TESTS_DIR / "systems" / "conftest.py"
    
    if source_conftest.exists() and not target_conftest.exists():
        shutil.copy2(source_conftest, target_conftest)
        print(f"Copied {source_conftest} to {target_conftest}")
    
    # Look for any other conftest.py files in backend/systems and copy them to the corresponding location
    for root, _, files in os.walk(BACKEND_SYSTEMS_DIR):
        for file in files:
            if file == "conftest.py":
                source_path = Path(root) / file
                rel_path = source_path.relative_to(BACKEND_SYSTEMS_DIR)
                target_path = BACKEND_TESTS_DIR / "systems" / rel_path
                
                if not target_path.exists():
                    os.makedirs(target_path.parent, exist_ok=True)
                    shutil.copy2(source_path, target_path)
                    print(f"Copied {source_path} to {target_path}")

def ensure_empty_init_files():
    """Ensure that __init__.py files exist in all test directories."""
    for root, dirs, _ in os.walk(BACKEND_TESTS_DIR):
        for dir_name in dirs:
            if dir_name != "__pycache__" and not dir_name.startswith("."):
                init_file = Path(root) / dir_name / "__init__.py"
                if not init_file.exists():
                    with open(init_file, 'w') as f:
                        pass  # Create an empty file
                    print(f"Created empty __init__.py in {init_file.parent}")

def main():
    """Main function to fix test configuration files."""
    print("Fixing test configuration files...")
    
    # Copy test configuration files
    copy_test_configs()
    
    # Ensure __init__.py files exist in all test directories
    ensure_empty_init_files()
    
    print("\nTest configuration fix completed!")
    print("You may still need to manually update some test fixtures or paths.")

if __name__ == "__main__":
    main() 