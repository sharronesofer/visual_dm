#!/usr/bin/env python3
"""
Script to fix ConfigDict syntax errors where opening braces don't have matching closing braces.
"""

import os
import re
from typing import List

def fix_configdict_syntax(file_path: str) -> bool:
    """Fix ConfigDict syntax errors in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern to find ConfigDict with incomplete closing braces
        # This matches: ConfigDict(key = {) and replaces with ConfigDict(key = {})
        pattern = r'model_config = ConfigDict\(([^=]+ = \{)\)'
        replacement = r'model_config = ConfigDict(\1})'
        content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def find_files_with_configdict_errors(project_root: str) -> List[str]:
    """Find all Python files that have ConfigDict syntax errors."""
    files_with_errors = []
    
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
                        # Look for ConfigDict with incomplete braces
                        if re.search(r'model_config = ConfigDict\([^}]*\{[^}]*\)', content):
                            files_with_errors.append(file_path)
                except (UnicodeDecodeError, PermissionError):
                    continue
    
    return files_with_errors

def main():
    project_root = os.getcwd()
    print(f"Scanning for files with ConfigDict syntax errors in {project_root}")
    
    files_with_errors = find_files_with_configdict_errors(project_root)
    print(f"Found {len(files_with_errors)} files with ConfigDict syntax errors")
    
    fixed_count = 0
    for file_path in files_with_errors:
        if fix_configdict_syntax(file_path):
            fixed_count += 1
    
    print(f"Fixed {fixed_count} files")

if __name__ == "__main__":
    main() 