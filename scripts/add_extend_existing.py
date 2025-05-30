#!/usr/bin/env python3
"""
Add 'extend_existing=True' to all SQLAlchemy model classes.

This script scans Python files for SQLAlchemy model classes (those inheriting from Base)
and adds an __table_args__ dictionary with 'extend_existing': True if not already present.
It handles several common patterns for defining table_args.
"""

import os
import re
import sys
import argparse
from pathlib import Path

# Regular expressions to find model classes and their __table_args__
CLASS_PATTERN = re.compile(r'class\s+(\w+)\s*\(\s*(?:\w+\s*,\s*)*(?:Base|CoreBaseModel)\s*\):\s*')
TABLENAME_PATTERN = re.compile(r'__tablename__\s*=\s*[\'"](\w+)[\'"]')
TABLE_ARGS_PATTERN = re.compile(r'__table_args__\s*=\s*({.*?}|\([^)]*\))', re.DOTALL)
EXTEND_EXISTING_PATTERN = re.compile(r'[\'"]extend_existing[\'"]\s*:\s*True')

def find_python_files(directory):
    """Find all Python files in the given directory."""
    return list(Path(directory).glob('**/*.py'))

def process_file(file_path, dry_run=False):
    """Process a Python file to add extend_existing=True to all model classes."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for model classes
    model_classes = CLASS_PATTERN.finditer(content)
    modified = False
    
    for match in model_classes:
        class_name = match.group(1)
        class_start = match.start()
        
        # Find the end of the class definition
        # This is a simplified approach; a proper parser would be better
        next_class = CLASS_PATTERN.search(content, class_start + 1)
        class_end = next_class.start() if next_class else len(content)
        
        class_content = content[class_start:class_end]
        
        # Skip if it doesn't have a __tablename__ (not a table model)
        if not TABLENAME_PATTERN.search(class_content):
            continue
        
        # Check if __table_args__ already exists
        table_args_match = TABLE_ARGS_PATTERN.search(class_content)
        
        if table_args_match:
            # Check if extend_existing is already in __table_args__
            if EXTEND_EXISTING_PATTERN.search(table_args_match.group(1)):
                print(f"  ✓ {class_name} already has extend_existing=True")
                continue
                
            # Table args exists but doesn't have extend_existing
            args_str = table_args_match.group(1)
            if args_str.startswith('{'):
                # Dictionary format
                if args_str.strip() == '{}':
                    # Empty dict
                    new_args = "{'extend_existing': True}"
                else:
                    # Add to existing dict
                    new_args = args_str[:-1].strip() + ", 'extend_existing': True}"
            elif args_str.startswith('('):
                # Tuple format with items and dict
                if '{}' in args_str:
                    # Tuple with empty dict at the end
                    new_args = args_str.replace('{}', "{'extend_existing': True}")
                elif not args_str.strip().endswith(')'):
                    # Malformed tuple
                    print(f"  ⚠ Warning: Malformed __table_args__ in {class_name}, skipping")
                    continue
                else:
                    # Check if the last item is a dict
                    if re.search(r'{\s*[\'"][a-zA-Z_]+[\'"]\s*:', args_str):
                        # There's already a dict, add to it
                        new_args = args_str[:-1].strip() + ", 'extend_existing': True})"
                    else:
                        # Add a dict to the tuple
                        new_args = args_str[:-1].strip() + ", {'extend_existing': True})"
            else:
                print(f"  ⚠ Warning: Unrecognized __table_args__ format in {class_name}, skipping")
                continue
                
            # Replace the table args
            updated_content = content[:table_args_match.start(1)] + new_args + content[table_args_match.end(1):]
            content = updated_content
            modified = True
            print(f"  ✓ Updated __table_args__ in {class_name}")
            
        else:
            # No __table_args__, add it after __tablename__
            tablename_match = TABLENAME_PATTERN.search(class_content)
            if not tablename_match:
                print(f"  ⚠ Warning: Class {class_name} looks like a model but has no __tablename__, skipping")
                continue
                
            indent = re.match(r'(\s*)', content[tablename_match.start():].split('\n')[0]).group(1)
            insert_pos = class_start + tablename_match.end()
            
            # Find the line end
            line_end = content.find('\n', insert_pos)
            if line_end == -1:
                line_end = len(content)
                
            # Insert after the line
            new_args = f"\n{indent}__table_args__ = {{'extend_existing': True}}"
            updated_content = content[:line_end] + new_args + content[line_end:]
            content = updated_content
            modified = True
            print(f"  ✓ Added __table_args__ to {class_name}")
    
    if modified and not dry_run:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
        
    return False

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Add extend_existing=True to all SQLAlchemy models')
    parser.add_argument('directory', help='Directory to scan for Python files')
    parser.add_argument('--dry-run', action='store_true', help='Print what would be changed without modifying files')
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a valid directory")
        return 1
        
    python_files = find_python_files(args.directory)
    modified_files = 0
    
    print(f"Found {len(python_files)} Python files to process")
    for file_path in python_files:
        print(f"Processing {file_path}")
        if process_file(file_path, args.dry_run):
            modified_files += 1
    
    mode = "Would modify" if args.dry_run else "Modified"
    print(f"\n{mode} {modified_files} files")
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 