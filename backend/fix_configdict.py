#!/usr/bin/env python3
"""
Script to add ConfigDict imports to all model files that use ConfigDict
"""

import os
import re
import subprocess

def get_files_using_configdict():
    """Get list of files that use ConfigDict"""
    result = subprocess.run([
        'grep', '-r', 'model_config.*ConfigDict', 'systems/', 
        '--include=*.py'
    ], capture_output=True, text=True, cwd='.')
    
    files = set()
    for line in result.stdout.splitlines():
        if 'test' not in line:  # Skip test files
            file_path = line.split(':')[0]
            files.add(file_path)
    
    return sorted(files)

def has_configdict_import(file_path):
    """Check if file already imports ConfigDict"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            # Check for existing ConfigDict import
            return 'ConfigDict' in content and ('from pydantic import' in content and 'ConfigDict' in content)
    except:
        return False

def add_configdict_import(file_path):
    """Add ConfigDict import to a file"""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Find pydantic imports
        pydantic_import_line = -1
        for i, line in enumerate(lines):
            if 'from pydantic import' in line and not line.strip().startswith('#'):
                pydantic_import_line = i
                break
        
        if pydantic_import_line >= 0:
            # Modify existing pydantic import
            current_import = lines[pydantic_import_line].strip()
            if 'ConfigDict' not in current_import:
                # Add ConfigDict to existing import
                if current_import.endswith(')'):
                    # Multi-line import
                    lines[pydantic_import_line] = current_import[:-1] + ', ConfigDict)\n'
                else:
                    # Single line import
                    lines[pydantic_import_line] = current_import.rstrip() + ', ConfigDict\n'
        else:
            # Add new import at top after other imports
            insert_index = 0
            for i, line in enumerate(lines):
                if line.startswith('from ') or line.startswith('import '):
                    insert_index = i + 1
                elif line.strip() == '':
                    continue
                else:
                    break
            
            lines.insert(insert_index, 'from pydantic import ConfigDict\n')
        
        # Write back to file
        with open(file_path, 'w') as f:
            f.writelines(lines)
        
        return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    files = get_files_using_configdict()
    
    fixed_count = 0
    for file_path in files:
        if not has_configdict_import(file_path):
            print(f"Adding ConfigDict import to {file_path}")
            if add_configdict_import(file_path):
                fixed_count += 1
            else:
                print(f"Failed to fix {file_path}")
        else:
            print(f"Skipping {file_path} (already has ConfigDict import)")
    
    print(f"\nFixed {fixed_count} files")

if __name__ == '__main__':
    main() 