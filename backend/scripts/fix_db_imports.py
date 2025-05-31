#!/usr/bin/env python3
"""
Fix database import issues by replacing get_db_session with get_db
"""

import os
import re

def fix_db_imports(file_path):
    """Fix database imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix import statements
        content = re.sub(
            r'from backend\.infrastructure\.database import get_db_session',
            'from backend.infrastructure.database import get_db',
            content
        )
        
        # Fix function calls
        content = re.sub(
            r'get_db_session\(\)',
            'get_db()',
            content
        )
        
        # Fix next() calls
        content = re.sub(
            r'next\(get_db_session\(\)\)',
            'next(get_db())',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed database imports in {file_path}")
            return True
        else:
            print(f"⏭️  No changes needed for {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix all database imports"""
    backend_dir = '/Users/Sharrone/Visual_DM/backend'
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk(backend_dir):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files to check")
    
    fixed_count = 0
    for file_path in python_files:
        if fix_db_imports(file_path):
            fixed_count += 1
    
    print(f"\n✅ Fixed database imports in {fixed_count} files")

if __name__ == "__main__":
    main() 