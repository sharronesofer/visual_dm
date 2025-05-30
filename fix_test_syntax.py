#!/usr/bin/env python3
import os
import re
import glob

def find_test_files():
    """Find all Python test files that might have syntax issues"""
    patterns = [
        'backend/**/test_*.py',
        'backend/**/*_test.py',
        'backend/**/tests/*.py'
    ]
    
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern, recursive=True))
    
    return list(set(files))  # Remove duplicates

def fix_file(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Fix the most common syntax errors
        
        # Fix malformed try statements
        content = re.sub(r'try:\s*pass\s*\n', 'try:\n', content)
        content = re.sub(r'except\s+([^:]+):\s*pass\s*\n', r'except \1:\n', content)
        
        # Fix malformed function definitions
        content = re.sub(r'(\s*def\s+[^:]+):\s*pass\s*\n', r'\1:\n', content)
        content = re.sub(r'(\s*async\s+def\s+[^:]+):\s*pass\s*\n', r'\1:\n', content)
        
        # Fix malformed class definitions  
        content = re.sub(r'(\s*class\s+[^:]+):\s*pass\s*\n', r'\1:\n', content)
        
        # Fix malformed if/elif/else statements
        content = re.sub(r'(\s*if\s+[^:]+):\s*pass\s*\n', r'\1:\n', content)
        content = re.sub(r'(\s*elif\s+[^:]+):\s*pass\s*\n', r'\1:\n', content)
        content = re.sub(r'(\s*else):\s*pass\s*\n', r'\1:\n', content)
        
        # Fix malformed for/while loops
        content = re.sub(r'(\s*for\s+[^:]+):\s*pass\s*\n', r'\1:\n', content)
        content = re.sub(r'(\s*while\s+[^:]+):\s*pass\s*\n', r'\1:\n', content)
        
        # Fix malformed with statements
        content = re.sub(r'(\s*with\s+[^:]+):\s*pass\s*\n', r'\1:\n', content)
        
        # Fix comments with colons
        content = re.sub(r'(\s*#[^:]*?):\s*pass\s*\n', r'\1\n', content)
        
        # Fix duplicate pass statements
        content = re.sub(r'pass\s*\n\s*pass', 'pass', content)
        
        # Fix trailing colons in comments or strings
        content = re.sub(r'(\s*#.*?)\s*:\s*$', r'\1', content, flags=re.MULTILINE)
        
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f'Fixed: {file_path}')
        else:
            print(f'No changes needed: {file_path}')
            
    except Exception as e:
        print(f'Error fixing {file_path}: {e}')

if __name__ == "__main__":
    test_files = find_test_files()
    print(f"Found {len(test_files)} test files to check...")
    
    # Process files in batches
    import sys
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end = start + 30
    
    for file_path in test_files[start:end]:
        fix_file(file_path) 