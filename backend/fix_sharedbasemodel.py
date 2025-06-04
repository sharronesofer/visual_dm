#!/usr/bin/env python3
"""
Script to add SharedBaseModel imports to all files that inherit from it
"""

import os
import re
import subprocess

def get_files_using_sharedbasemodel():
    """Get list of files that inherit from SharedBaseModel"""
    result = subprocess.run([
        'grep', '-r', 'class.*SharedBaseModel', 'infrastructure/', 'systems/',
        '--include=*.py'
    ], capture_output=True, text=True, cwd='.')
    
    files = set()
    for line in result.stdout.splitlines():
        if 'test' not in line and 'shared/models/models.py' not in line:  # Skip tests and the definition file
            file_path = line.split(':')[0]
            files.add(file_path)
    
    return sorted(files)

def has_sharedbasemodel_import(file_path):
    """Check if file already imports SharedBaseModel properly"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            # Check for existing SharedBaseModel import in various forms
            patterns = [
                r'from.*SharedBaseModel',
                r'import.*SharedBaseModel',
                r'BaseModel as SharedBaseModel'  # Arc pattern
            ]
            for pattern in patterns:
                if re.search(pattern, content):
                    return True
            return False
    except:
        return False

def add_sharedbasemodel_import(file_path):
    """Add SharedBaseModel import to a file"""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Find where to insert the import
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith('from backend.infrastructure'):
                insert_index = i + 1
            elif line.startswith('from ') or line.startswith('import '):
                if 'backend' not in line:
                    continue
                insert_index = i + 1
            elif line.strip() == '' and insert_index > 0:
                continue
            elif line.strip() != '' and insert_index > 0:
                break
        
        # Add the import
        import_line = 'from backend.infrastructure.shared.models import SharedBaseModel\n'
        lines.insert(insert_index, import_line)
        
        # Write back to file
        with open(file_path, 'w') as f:
            f.writelines(lines)
        
        return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    files = get_files_using_sharedbasemodel()
    
    fixed_count = 0
    for file_path in files:
        if not has_sharedbasemodel_import(file_path):
            print(f"Adding SharedBaseModel import to {file_path}")
            if add_sharedbasemodel_import(file_path):
                fixed_count += 1
            else:
                print(f"Failed to fix {file_path}")
        else:
            print(f"Skipping {file_path} (already has SharedBaseModel import)")
    
    print(f"\nFixed {fixed_count} files")

if __name__ == '__main__':
    main() 