#!/usr/bin/env python3
"""
Script to fix specific syntax errors in test files.

Targets the malformed import pattern where typing imports are incorrectly 
placed inside other import blocks.
"""

import os
import re
import glob
from pathlib import Path

def fix_malformed_imports(file_path: Path):
    """Fix malformed import statements in a file."""
    try:
        content = file_path.read_text()
        original_content = content
        
        # Pattern: multi-line import with typing imports in wrong place
        # Example:
        # from module import (
        # from typing import Type
        #     RealImport,
        # )
        
        # Find and fix this pattern
        pattern = r'(from [^\n]+ import \()\s*\n(from typing import [^\n]+)\s*\n([^)]*\))'
        
        def fix_import_block(match):
            import_start = match.group(1)  # "from module import ("
            typing_import = match.group(2)  # "from typing import backend.systems."
            rest_imports = match.group(3)   # "    RealImport,\n)"
            
            # Return the import block without the typing import
            return import_start + "\n" + rest_imports
        
        # Apply the fix
        fixed_content = re.sub(pattern, fix_import_block, content, flags=re.MULTILINE)
        
        # If we made changes, try to compile to check syntax
        if fixed_content != original_content:
            try:
                compile(fixed_content, str(file_path), 'exec')
                file_path.write_text(fixed_content)
                print(f"✅ Fixed {file_path.name}")
                return True
            except SyntaxError as e:
                print(f"⚠️  Still has syntax error after fix: {file_path.name} - {e}")
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Fix syntax errors in all test files."""
    # Get backend root
    script_dir = Path(__file__).parent
    backend_root = script_dir.parent
    tests_root = backend_root / "tests" / "systems"
    
    print("🔧 Fixing syntax errors in test files...")
    
    # Find all Python test files
    test_files = glob.glob(str(tests_root / "**" / "*.py"), recursive=True)
    
    fixed_count = 0
    for test_file in test_files:
        if fix_malformed_imports(Path(test_file)):
            fixed_count += 1
    
    print(f"\n🎉 Fixed {fixed_count} files!")
    
    # Run a quick test to see improvement
    print("\n📊 Testing collection improvement...")
    os.chdir(backend_root)
    result = os.system("python -m pytest tests/systems/ --collect-only 2>&1 | grep -c 'ERROR'")

if __name__ == "__main__":
    main() 