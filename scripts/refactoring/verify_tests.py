#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path

# Base directory
BACKEND_TESTS_DIR = Path("backend/tests/systems")

def find_test_files():
    """Find all test files in the backend/tests/systems directory."""
    test_files = []
    for root, _, files in os.walk(BACKEND_TESTS_DIR):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                test_path = Path(root) / file
                test_files.append(test_path)
    return test_files

def run_pytest(test_file):
    """Run pytest on a specific test file."""
    print(f"Testing {test_file}...")
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", test_file, "-v"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print(f"✅ {test_file} passed!")
            return True
        else:
            print(f"❌ {test_file} failed!")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error running {test_file}: {e}")
        return False

def main():
    # Find all test files
    test_files = find_test_files()
    print(f"Found {len(test_files)} test files to verify")
    
    # Test each file
    passed = 0
    failed = 0
    
    for test_file in test_files:
        if run_pytest(test_file):
            passed += 1
        else:
            failed += 1
    
    print("\nVerification summary:")
    print(f"Total tests: {len(test_files)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {failed} tests failed!")

if __name__ == "__main__":
    main() 