#!/usr/bin/env python3
"""
Fix NPC test import paths to use canonical backend.systems.npc imports.

This script fixes imports in NPC test files to follow the canonical structure
as required by Development_Bible.md.
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path: Path) -> bool:
    """Fix imports in a single test file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix import patterns
        patterns = [
            # systems.npc.* -> backend.systems.npc.*
            (r'import systems\.npc\.', 'import backend.systems.npc.'),
            (r'from systems\.npc\.', 'from backend.systems.npc.'),
            
            # Handle specific test file patterns that might exist
            (r'import systems\.npc$', 'import backend.systems.npc'),
            (r'from systems\.npc import', 'from backend.systems.npc import'),
        ]
        
        for old_pattern, new_pattern in patterns:
            content = re.sub(old_pattern, new_pattern, content)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed imports in {file_path}")
            return True
        else:
            print(f"No changes needed in {file_path}")
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix all NPC test imports."""
    # Find all NPC test files
    test_dirs = [
        Path("tests/systems/npc/"),
        Path("tests/")  # Check root for any misplaced NPC tests
    ]
    
    files_fixed = 0
    total_files = 0
    
    for test_dir in test_dirs:
        if test_dir.exists():
            # Find all Python test files mentioning NPC
            for file_path in test_dir.rglob("*npc*.py"):
                if file_path.is_file():
                    total_files += 1
                    if fix_imports_in_file(file_path):
                        files_fixed += 1
    
    print(f"\nFixed imports in {files_fixed} out of {total_files} NPC test files.")

if __name__ == "__main__":
    main() 