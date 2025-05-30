#!/usr/bin/env python3
"""
Script to fix common syntax errors in Python files.
Specifically targets:
1. Improperly indented import statements in try blocks
2. Missing except/finally blocks
3. Misplaced imports in function bodies
"""

import os
import re
import sys
from pathlib import Path

def fix_misplaced_imports_in_functions(content):
    """Fix import statements that are placed incorrectly within function bodies."""
    lines = content.split('\n')
    fixed_lines = []
    imports_to_move = []
    in_function = False
    function_indent = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        current_indent = len(line) - len(line.lstrip())
        
        # Check if we're entering a function
        if stripped.startswith(('def ', 'async def ')):
            in_function = True
            function_indent = current_indent
            fixed_lines.append(line)
            continue
        
        # Check if we're exiting a function (unindent to function level or less)
        if in_function and stripped and current_indent <= function_indent:
            in_function = False
            function_indent = 0
        
        # If we're in a function and find an import, mark it for moving
        if in_function and stripped.startswith(('from ', 'import ')):
            # Skip the import line, save it to move to top
            imports_to_move.append(stripped)
            continue
        
        fixed_lines.append(line)
    
    # Add collected imports at the top (after existing imports)
    if imports_to_move:
        # Find where to insert imports (after existing imports and docstring)
        insert_index = 0
        for i, line in enumerate(fixed_lines):
            stripped = line.strip()
            if (stripped.startswith(('"""', "'''")) or 
                stripped.startswith(('from ', 'import ')) or
                not stripped or stripped.startswith('#')):
                insert_index = i + 1
            else:
                break
        
        # Insert imports with proper formatting
        for imp in imports_to_move:
            fixed_lines.insert(insert_index, imp)
            insert_index += 1
        
        # Add blank line after imports
        if imports_to_move and insert_index < len(fixed_lines):
            fixed_lines.insert(insert_index, '')
    
    return '\n'.join(fixed_lines)

def fix_indented_imports(content):
    """Fix imports that should be indented within try blocks."""
    lines = content.split('\n')
    fixed_lines = []
    in_try_block = False
    try_indent = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Detect try block start
        if stripped.startswith('try:'):
            in_try_block = True
            try_indent = len(line) - len(line.lstrip())
            fixed_lines.append(line)
            continue
        
        # Detect except/finally - exit try block
        if stripped.startswith(('except', 'finally')) and in_try_block:
            in_try_block = False
            fixed_lines.append(line)
            continue
        
        # If we're in a try block and find an import at wrong indentation
        if in_try_block and stripped.startswith(('from ', 'import ')):
            current_indent = len(line) - len(line.lstrip())
            expected_indent = try_indent + 4  # Standard Python indentation
            
            if current_indent != expected_indent:
                # Fix the indentation
                fixed_line = ' ' * expected_indent + stripped
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)
            continue
        
        # For non-import lines in try block, check if they're at wrong indentation
        if in_try_block and stripped and not stripped.startswith('#'):
            current_indent = len(line) - len(line.lstrip())
            expected_indent = try_indent + 4
            
            # Only fix obvious cases where the line should be indented
            if current_indent < expected_indent and not stripped.startswith(('except', 'finally', 'else')):
                fixed_line = ' ' * expected_indent + stripped
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)
            continue
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_file(file_path):
    """Fix syntax errors in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        content = original_content
        
        # Apply fixes
        content = fix_misplaced_imports_in_functions(content)
        content = fix_indented_imports(content)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_syntax_errors.py <directory>")
        sys.exit(1)
    
    directory = Path(sys.argv[1])
    if not directory.exists():
        print(f"Directory {directory} does not exist")
        sys.exit(1)
    
    files_fixed = 0
    
    # Find all Python files
    for py_file in directory.rglob("*.py"):
        if fix_file(py_file):
            files_fixed += 1
            print(f"Fixed: {py_file}")
    
    print(f"\nFixed {files_fixed} files")

if __name__ == "__main__":
    main() 