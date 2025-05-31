#!/usr/bin/env python3
"""
Script to fix malformed imports in the moved test files.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# Base paths
BACKEND_DIR = Path("backend")
TESTS_DIR = BACKEND_DIR / "tests" / "systems"

def fix_imports_in_file(file_path: Path) -> None:
    """Fix malformed import statements in test files."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix malformed imports step by step
        
        # 1. Fix doubled backend.systems imports
        content = re.sub(r'from backend\.systems\.([^.\s]+)\.([^.\s]+) import backend\.systems\.([^.\s]+)\.([^.\s]+)', 
                        r'from backend.systems.\1.\2 import \4', content)
        
        # 2. Fix imports that have backend.systems repeated
        content = re.sub(r'import backend\.systems\.([^.\s]+)\.backend\.systems\.([^.\s]+)', 
                        r'import backend.systems.\1.\2', content)
        
        # 3. Fix unittest import
        content = re.sub(r'import backend\.systems\.combat\.unittest', 
                        'import unittest', content)
        
        # 4. Fix uuid import
        content = re.sub(r'import backend\.systems\.combat\.uuid', 
                        'import uuid', content)
        
        # 5. Fix other standard library imports that got prefixed
        content = re.sub(r'from backend\.systems\.([^.\s]+)\.unittest', 
                        'from unittest', content)
        content = re.sub(r'from backend\.systems\.([^.\s]+)\.uuid', 
                        'from uuid', content)
        content = re.sub(r'from backend\.systems\.([^.\s]+)\.typing', 
                        'from typing', content)
        content = re.sub(r'from backend\.systems\.([^.\s]+)\.pytest', 
                        'import pytest', content)
        
        # 6. Fix relative imports that became absolute
        content = re.sub(r'from backend\.systems\.([^.\s]+)\. import', 
                        r'from backend.systems.\1 import', content)
        content = re.sub(r'from backend\.systems\.([^.\s]+)\.\. import', 
                        r'from backend.systems import', content)
        
        # 7. Fix class imports with doubled module names
        content = re.sub(r'from backend\.systems\.([^.\s]+)\.([^.\s]+) import backend\.systems\.\1\.([^.\s]+)', 
                        r'from backend.systems.\1.\2 import \3', content)
        
        # 8. Fix any remaining backend.systems.system.backend.systems patterns
        content = re.sub(r'backend\.systems\.([^.\s]+)\.backend\.systems\.([^.\s]+)', 
                        r'backend.systems.\1.\2', content)
        
        # 9. Clean up import lines that start imports incorrectly
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Skip empty lines that just contain import statements
            if line.strip() == 'import':
                continue
            
            # Fix lines that start with just the module name but should be imports
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', line.strip()) and 'def ' not in line and 'class ' not in line:
                continue
                
            fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        # 10. Ensure pytest import is at the top if there are test functions
        if ('def test_' in content or 'class Test' in content) and 'import pytest' not in content:
            lines = content.split('\n')
            # Find the first import line
            import_index = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    import_index = i
                    break
            lines.insert(import_index, 'import pytest')
            content = '\n'.join(lines)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed imports in {file_path}")
            return True
        else:
            print(f"- No changes needed in {file_path}")
            return False
            
    except Exception as e:
        print(f"✗ Error fixing imports in {file_path}: {e}")
        return False

def main():
    """Fix imports in all moved test files."""
    print("Fixing malformed imports in moved test files...")
    print("=" * 60)
    
    # List of specific files we moved that need fixing
    moved_files = [
        "combat/test_combat_integration.py",
        "combat/test_combat_state_management.py", 
        "magic/test_magic.py",
        "rumor/test_rumor.py",
        "events/test_event_bus.py",
        "events/test_event_dispatcher_core.py",
        "character/test_event_dispatcher.py",
        "character/test_world_state_manager.py",
        "character/test_character.py",
        "events/test_event_dispatcher.py",
        "events/test_event_manager.py",
        "events/test_dispatcher.py",
    ]
    
    fixed_count = 0
    
    for file_path in moved_files:
        full_path = TESTS_DIR / file_path
        if full_path.exists():
            print(f"\nProcessing: {file_path}")
            if fix_imports_in_file(full_path):
                fixed_count += 1
        else:
            print(f"⚠ File not found: {full_path}")
    
    print("\n" + "=" * 60)
    print(f"Import fixing complete! Fixed {fixed_count} files.")
    print("\nNext step: Run 'cd backend && python -m pytest tests/systems/ -v' to test")

if __name__ == "__main__":
    main() 