#!/usr/bin/env python3
"""
Fix internal imports within moved modules
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
            print(f"Fixed internal imports in: {file_path}")
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    # Fix internal imports within auth_user module
    auth_user_dir = Path('backend/infrastructure/auth/auth_user')
    if auth_user_dir.exists():
        auth_replacements = {
            r'from backend\.systems\.auth_user\.': 'from backend.infrastructure.auth.auth_user.',
            r'import backend\.systems\.auth_user\.': 'import backend.infrastructure.auth.auth_user.',
        }
        
        for py_file in auth_user_dir.rglob('*.py'):
            if '__pycache__' not in str(py_file):
                fix_imports_in_file(py_file, auth_replacements)
    
    # Fix internal imports within llm module
    llm_dir = Path('backend/infrastructure/llm')
    if llm_dir.exists():
        llm_replacements = {
            r'from backend\.systems\.llm\.': 'from backend.infrastructure.llm.',
            r'import backend\.systems\.llm\.': 'import backend.infrastructure.llm.',
        }
        
        for py_file in llm_dir.rglob('*.py'):
            if '__pycache__' not in str(py_file):
                fix_imports_in_file(py_file, llm_replacements)
    
    # Fix imports in shared models
    shared_models_dir = Path('backend/infrastructure/shared/models')
    if shared_models_dir.exists():
        shared_replacements = {
            r'from backend\.systems\.models\.': 'from backend.infrastructure.shared.models.',
            r'import backend\.systems\.models\.': 'import backend.infrastructure.shared.models.',
        }
        
        for py_file in shared_models_dir.rglob('*.py'):
            if '__pycache__' not in str(py_file):
                fix_imports_in_file(py_file, shared_replacements)

if __name__ == "__main__":
    main() 