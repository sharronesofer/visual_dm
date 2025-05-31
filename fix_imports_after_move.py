#!/usr/bin/env python3
"""
Fix imports after moving infrastructure folders from systems to infrastructure
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path, replacements):
    """Fix imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for old_import, new_import in replacements.items():
            content = re.sub(old_import, new_import, content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed imports in: {file_path}")
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    # Define import replacements
    replacements = {
        # Auth user imports
        r'from backend\.systems\.auth_user': 'from backend.infrastructure.auth.auth_user',
        r'import backend\.systems\.auth_user': 'import backend.infrastructure.auth.auth_user',
        
        # Models imports  
        r'from backend\.systems\.models': 'from backend.infrastructure.shared.models',
        r'import backend\.systems\.models': 'import backend.infrastructure.shared.models',
        
        # Repositories imports
        r'from backend\.systems\.repositories': 'from backend.infrastructure.repositories',
        r'import backend\.systems\.repositories': 'import backend.infrastructure.repositories',
        
        # Shared imports
        r'from backend\.systems\.shared': 'from backend.infrastructure.shared',
        r'import backend\.systems\.shared': 'import backend.infrastructure.shared',
        
        # LLM imports
        r'from backend\.systems\.llm': 'from backend.infrastructure.llm',
        r'import backend\.systems\.llm': 'import backend.infrastructure.llm',
    }
    
    # Find all Python files
    backend_dir = Path('backend')
    
    for py_file in backend_dir.rglob('*.py'):
        if '__pycache__' not in str(py_file):
            fix_imports_in_file(py_file, replacements)
    
    # Also check test files and scripts
    for directory in ['scripts', 'tests']:
        if os.path.exists(directory):
            dir_path = Path(directory)
            for py_file in dir_path.rglob('*.py'):
                if '__pycache__' not in str(py_file):
                    fix_imports_in_file(py_file, replacements)

if __name__ == "__main__":
    main() 