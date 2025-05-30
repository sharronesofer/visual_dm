#!/usr/bin/env python3

import os
import re
from pathlib import Path
import sys

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

def analyze_imports(file_path):
    """Analyze the imports in a file and suggest fixes."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Look for relative imports
    relative_imports = re.findall(r'from \.\.(.*?) import', content)
    relative_imports += re.findall(r'from \.(.*?) import', content)
    
    if relative_imports:
        print(f"\n{file_path}:")
        print("  Found relative imports that may need to be fixed:")
        for imp in relative_imports:
            print(f"  - from .{imp} import ...")
        
        # Try to determine the correct absolute import path
        module_path = file_path.relative_to(BACKEND_TESTS_DIR)
        parent_module = module_path.parent
        
        # Suggest possible fixes
        print("\n  Suggested fixes:")
        for imp in relative_imports:
            if '.' in imp:
                # For nested relative imports like ..utils.helpers
                parts = imp.split('.')
                if len(parts) > 1:
                    # Going up multiple levels
                    current_path = parent_module
                    levels_up = 0
                    while parts[0] == '' and len(parts) > 1:
                        parts.pop(0)
                        levels_up += 1
                        if len(current_path.parts) > levels_up:
                            current_path = current_path.parent
                    
                    suggested_import = f"backend.systems.{'.'.join(current_path.parts)}.{'.'.join(parts)}"
                    print(f"  - from {suggested_import} import ...")
            else:
                # For simple relative imports like .models or ..services
                if imp.startswith('.'):
                    # Going up one more level
                    if len(parent_module.parts) > 1:
                        suggested_import = f"backend.systems.{'.'.join(parent_module.parent.parts)}.{imp[1:]}"
                    else:
                        suggested_import = f"backend.systems.{imp[1:]}"
                else:
                    suggested_import = f"backend.systems.{'.'.join(parent_module.parts)}.{imp}"
                
                print(f"  - from {suggested_import} import ...")
        
        return True
    
    return False

def main():
    """Main function to analyze imports in test files."""
    test_files = find_test_files()
    print(f"Found {len(test_files)} test files to analyze.")
    
    # Analyze imports in each file
    files_with_relative_imports = 0
    for test_file in test_files:
        if analyze_imports(test_file):
            files_with_relative_imports += 1
    
    print(f"\nFound {files_with_relative_imports} files with relative imports that may need to be fixed.")

if __name__ == "__main__":
    main() 