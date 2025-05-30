#!/usr/bin/env python3
"""
Script to fix incorrect field_validator imports.
"""

import os
import re
from typing import List

def fix_field_validator_imports(file_path: str) -> bool:
    """Fix field_validator imports in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix field_validator -> field_validator
        content = re.sub(r'field_validator', 'field_validator', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def find_files_with_field_validator(project_root: str) -> List[str]:
    """Find all Python files that use field_validator."""
    files_with_import = []
    
    for root, dirs, files in os.walk(project_root):
        # Skip certain directories
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'field_validator' in content:
                            files_with_import.append(file_path)
                except (UnicodeDecodeError, PermissionError):
                    continue
    
    return files_with_import

def main():
    project_root = os.getcwd()
    print(f"Scanning for files with field_validator import in {project_root}")
    
    files_with_import = find_files_with_field_validator(project_root)
    print(f"Found {len(files_with_import)} files using field_validator")
    
    fixed_count = 0
    for file_path in files_with_import:
        if fix_field_validator_imports(file_path):
            fixed_count += 1
    
    print(f"Fixed {fixed_count} files")

if __name__ == "__main__":
    main() 