#!/usr/bin/env python3
"""
Fix test imports and remaining references after moving modules
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
            print(f"Fixed test imports in: {file_path}")
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    # Define replacements for test files and scripts
    replacements = {
        # Test file error messages
        r'Module backend\.systems\.auth_user': 'Module backend.infrastructure.auth.auth_user',
        r'Module backend\.systems\.models': 'Module backend.infrastructure.shared.models',
        r'Module backend\.systems\.repositories': 'Module backend.infrastructure.repositories',
        r'Module backend\.systems\.shared': 'Module backend.infrastructure.shared',
        r'Module backend\.systems\.llm': 'Module backend.infrastructure.llm',
        
        # Script references
        r'"backend\.systems\.auth_user': '"backend.infrastructure.auth.auth_user',
        r"'backend\.systems\.auth_user": "'backend.infrastructure.auth.auth_user",
        r'backend\.systems\.shared\.database': 'backend.infrastructure.shared.database',
        r'backend\.systems\.shared\.models': 'backend.infrastructure.shared.models',
        r'backend\.systems\.shared\.utils': 'backend.infrastructure.shared.utils',
        r'backend\.systems\.shared\.repositories': 'backend.infrastructure.shared.repositories',
        r'backend\.systems\.shared\.base': 'backend.infrastructure.shared.base',
        r'backend\.systems\.shared\.config': 'backend.infrastructure.shared.config',
        r'backend\.systems\.shared\.services': 'backend.infrastructure.shared.services',
        
        # Validation script references
        r"'backend\.systems\.auth_user'": "'backend.infrastructure.auth.auth_user'",
        r"'backend\.systems\.shared'": "'backend.infrastructure.shared'",
        r"'backend\.systems\.llm'": "'backend.infrastructure.llm'",
        
        # Import statements in test files
        r'from systems\.shared\.database\.base': 'from backend.infrastructure.shared.database.base',
        r'from systems\.shared\.repositories': 'from backend.infrastructure.shared.repositories',
    }
    
    # Find all Python files in backend, scripts, and tests
    for directory in ['backend', 'scripts']:
        if os.path.exists(directory):
            dir_path = Path(directory)
            for py_file in dir_path.rglob('*.py'):
                if '__pycache__' not in str(py_file):
                    fix_imports_in_file(py_file, replacements)

if __name__ == "__main__":
    main() 