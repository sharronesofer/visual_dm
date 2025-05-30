#!/usr/bin/env python3
"""
Script to fix ConfigDict imports across all files that use it.
"""

import os
import re
from pathlib import Path
from typing import List

def needs_configdict_import(file_path: str) -> bool:
    """Check if a file uses ConfigDict but doesn't import it."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if ConfigDict is used
    if 'model_config = ConfigDict' not in content:
        return False
    
    # Check if ConfigDict is already imported
    if 'from pydantic import ConfigDict' in content or 'ConfigDict' in content.split('model_config = ConfigDict')[0]:
        return False
    
    return True

def add_configdict_import(file_path: str) -> bool:
    """Add ConfigDict import to a file that needs it."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the pydantic import line and add ConfigDict
    lines = content.split('\n')
    modified = False
    
    for i, line in enumerate(lines):
        if line.startswith('from pydantic import') and 'ConfigDict' not in line:
            # Add ConfigDict to the import
            if line.endswith('BaseModel'):
                lines[i] = line.replace('BaseModel', 'BaseModel, ConfigDict')
                modified = True
                break
            elif 'BaseModel' in line:
                # More complex import, add after
                import_block_end = i
                # Find end of import block
                while import_block_end + 1 < len(lines) and (lines[import_block_end + 1].startswith(' ') or lines[import_block_end + 1].startswith('try:') or lines[import_block_end + 1] == ''):
                    import_block_end += 1
                
                # Add the try/except block after the import
                try_except_block = [
                    '',
                    'try:',
                    '    from pydantic import ConfigDict',
                    'except ImportError:',
                    '    # Fallback for older Pydantic versions',
                    '    class ConfigDict:',
                    '        def __init__(self, **kwargs):',
                    '            pass'
                ]
                
                lines[import_block_end + 1:import_block_end + 1] = try_except_block
                modified = True
                break
    
    # If no pydantic import found, add it
    if not modified:
        # Find a good place to add the import
        for i, line in enumerate(lines):
            if line.startswith('from') or line.startswith('import'):
                continue
            # Insert before the first non-import line
            try_except_block = [
                'try:',
                '    from pydantic import ConfigDict',
                'except ImportError:',
                '    # Fallback for older Pydantic versions',
                '    class ConfigDict:',
                '        def __init__(self, **kwargs):',
                '            pass',
                ''
            ]
            lines[i:i] = try_except_block
            modified = True
            break
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        return True
    
    return False

def find_files_with_configdict(project_root: str) -> List[str]:
    """Find all Python files that use ConfigDict."""
    files_with_configdict = []
    
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
                        if 'model_config = ConfigDict' in content:
                            files_with_configdict.append(file_path)
                except (UnicodeDecodeError, PermissionError):
                    continue
    
    return files_with_configdict

def main():
    project_root = os.getcwd()
    print(f"Scanning for files with ConfigDict usage in {project_root}")
    
    files_with_configdict = find_files_with_configdict(project_root)
    print(f"Found {len(files_with_configdict)} files using ConfigDict")
    
    fixed_count = 0
    for file_path in files_with_configdict:
        if needs_configdict_import(file_path):
            print(f"Fixing {file_path}")
            if add_configdict_import(file_path):
                fixed_count += 1
            else:
                print(f"  Failed to fix {file_path}")
        else:
            print(f"Skipping {file_path} (already has import)")
    
    print(f"Fixed {fixed_count} files")

if __name__ == "__main__":
    main() 