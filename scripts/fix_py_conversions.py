#!/usr/bin/env python3
"""
Fix Python Conversion Issues

This script post-processes converted Python files to fix common issues
that may occur during TypeScript to Python conversion.

Usage:
  python fix_py_conversions.py --dir <directory_with_python_files>
"""

import os
import re
import sys
import argparse
from typing import List, Dict, Any, Optional

def fix_file(file_path: str, dry_run: bool = False) -> bool:
    """
    Fix common issues in a converted Python file.
    
    Args:
        file_path: Path to the Python file to fix
        dry_run: If True, don't write changes, just print what would be done
        
    Returns:
        True if changes were made, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # Fix common issues
        content = fix_nested_objects(content)
        content = fix_typescript_types(content)
        content = fix_trailing_chars(content)
        content = fix_self_refs(content)
        content = fix_imports(content)
        
        # Write the fixed content
        if content != original_content:
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Fixed: {file_path}")
            else:
                print(f"Would fix: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def fix_nested_objects(content: str) -> str:
    """Fix nested object type definitions."""
    # Replace patterns like:
    # dimensions: {
    #   width: number;
    #   height: number;
    # };
    # With: dimensions: Dict[str, float]
    
    # Match the start of a nested object
    nested_obj_pattern = r'(\w+):\s*{([^}]+)}'
    
    def replace_nested_obj(match):
        prop_name = match.group(1)
        obj_body = match.group(2)
        
        # Simple case - just make it a Dict
        if ':' in obj_body:
            return f"{prop_name}: Dict[str, Any]"
        return f"{prop_name}: Dict[str, Any]"
        
    return re.sub(nested_obj_pattern, replace_nested_obj, content)

def fix_typescript_types(content: str) -> str:
    """Fix TypeScript type annotations that were not correctly converted."""
    # Fix array types
    content = re.sub(r'(\w+):\s*(\w+)\[\]', r'\1: List[\2]', content)
    
    # Replace TypeScript primitive types
    ts_to_py_types = {
        'string': 'str',
        'number': 'float',
        'boolean': 'bool',
        'any': 'Any',
    }
    
    for ts_type, py_type in ts_to_py_types.items():
        content = re.sub(fr':\s*{ts_type}([;,\s)])', f': {py_type}\\1', content)
    
    return content

def fix_trailing_chars(content: str) -> str:
    """Remove trailing TypeScript syntax characters."""
    # Remove trailing semicolons
    content = re.sub(r';(\s*$)', r'\1', content, flags=re.MULTILINE)
    
    # Remove trailing percent signs (common converter error)
    content = re.sub(r'%(\s*$)', r'', content, flags=re.MULTILINE)
    
    return content

def fix_self_refs(content: str) -> str:
    """Fix self-references in type definitions."""
    # Pattern to find class definitions
    class_pattern = r'class (\w+)'
    class_names = re.findall(class_pattern, content)
    
    # Fix references to class types by adding quotes
    for name in class_names:
        # Only fix references that are type annotations 
        # (: TypeName), but not the class definition itself
        content = re.sub(fr'(:\s*)({name})([,\s])', r'\1\'\2\'\3', content)
    
    return content

def fix_imports(content: str) -> str:
    """Fix import statements and add necessary ones."""
    # First, remove duplicate imports
    lines = content.splitlines()
    seen_imports = set()
    new_lines = []
    
    for line in lines:
        if line.startswith(('import ', 'from ')) and line in seen_imports:
            continue
        new_lines.append(line)
        if line.startswith(('import ', 'from ')):
            seen_imports.add(line)
    
    content = '\n'.join(new_lines)
    
    # Now add any missing imports
    added_imports = set()
    
    # Check if we need Dict import
    if 'Dict[' in content:
        added_imports.add('Dict')
    
    # Check if we need List import
    if 'List[' in content:
        added_imports.add('List')
    
    # Check if we need Any import
    if 'Any' in content:
        added_imports.add('Any')
    
    # Check if we need Optional import
    if 'Optional[' in content:
        added_imports.add('Optional')
    
    # Check if we need Union import
    if 'Union[' in content:
        added_imports.add('Union')
    
    # Check if we need Enum import
    if 'class' in content and 'Enum)' in content:
        added_imports.add('from enum import Enum')
    
    # Add missing imports
    if added_imports:
        imports = []
        typing_imports = [imp for imp in added_imports if imp not in ('from enum import Enum')]
        
        if typing_imports:
            imports.append(f"from typing import {', '.join(sorted(typing_imports))}")
        
        # Add enum import if needed
        if 'from enum import Enum' in added_imports:
            imports.append('from enum import Enum')
        
        # Add the imports at the top of the file
        if imports:
            # Remove existing imports first to avoid duplication
            lines = content.splitlines()
            non_import_lines = []
            for line in lines:
                if not line.startswith(('import ', 'from ')):
                    non_import_lines.append(line)
            
            # Add new imports at the top
            content = '\n'.join(imports + [''] + non_import_lines)
    
    return content

def process_directory(directory: str, dry_run: bool = False) -> Dict[str, int]:
    """
    Process all Python files in a directory recursively.
    
    Args:
        directory: Directory to process
        dry_run: If True, don't write changes, just print what would be done
        
    Returns:
        Stats dictionary with counts of processed and fixed files
    """
    stats = {
        'processed': 0,
        'fixed': 0,
        'errors': 0
    }
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                stats['processed'] += 1
                
                try:
                    if fix_file(file_path, dry_run):
                        stats['fixed'] += 1
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    stats['errors'] += 1
    
    return stats

def main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description='Fix common issues in converted Python files')
    parser.add_argument('--dir', required=True, help='Directory containing Python files to fix')
    parser.add_argument('--dry-run', action='store_true', help='Don\'t write changes, just print what would be done')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.dir):
        print(f"Error: {args.dir} is not a directory")
        return 1
    
    stats = process_directory(args.dir, args.dry_run)
    
    print(f"\nProcessed {stats['processed']} files:")
    print(f"- Fixed: {stats['fixed']}")
    print(f"- Errors: {stats['errors']}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 