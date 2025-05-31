#!/usr/bin/env python3
"""
Fix syntax errors in test files caused by corrupted line continuation characters.
Improved version for Task 28 implementation.
"""

import os
import re
from pathlib import Path

def fix_corrupted_test_file(file_path):
    """Fix corrupted syntax in a Python test file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # The corruption pattern is \1:\n\1 which should be replaced with proper Python syntax
        
        # Step 1: Fix class definitions
        # Pattern: \1:\n\1    pass followed by docstring indicates a class
        content = re.sub(
            r'\\1:\n\\1\s+pass\s*\n\s*"""Test suite for [^"]*"""\s*\n',
            'class TestEconomyManager:\n    """Test suite for economy_manager module."""\n    \n',
            content
        )
        
        # Step 2: Fix method definitions  
        # Pattern: \1:\n\1    pass followed by method docstring
        def replace_method(match):
            docstring = match.group(1)
            # Extract method name from docstring
            if "Set up test fixtures" in docstring:
                return '    def setUp(self):\n        """Set up test fixtures before each test method."""\n        pass\n    \n'
            elif "Clean up after" in docstring:
                return '    def tearDown(self):\n        """Clean up after each test method."""\n        pass\n\n\n'
            elif "Test " in docstring:
                # Extract test name from docstring
                test_desc = docstring.replace("Test ", "").replace(".", "").strip()
                method_name = "test_" + test_desc.lower().replace(" ", "_").replace("-", "_")
                return f'    def {method_name}(self):\n        """{docstring}"""\n'
            else:
                return f'    def test_method(self):\n        """{docstring}"""\n'
        
        content = re.sub(
            r'\\1:\n\\1\s+pass\s*\n\s*"""([^"]+)"""\s*\n',
            replace_method,
            content
        )
        
        # Step 3: Fix remaining \1: patterns that are standalone
        content = re.sub(r'\\1:\n\\1\s+pass\s*\n', '', content)
        
        # Step 4: Fix try/except blocks that got corrupted
        content = re.sub(
            r'\\1:\n\\1\s+',
            '        try:\n            ',
            content
        )
        
        # Step 5: Clean up any remaining \1 patterns
        content = re.sub(r'\\1:\n\\1\s*', '', content)
        content = re.sub(r'\\1:', '', content)
        
        # Step 6: Fix indentation issues
        lines = content.split('\n')
        fixed_lines = []
        in_try_block = False
        
        for i, line in enumerate(lines):
            # Handle try blocks that need proper except clauses
            if 'try:' in line and i + 1 < len(lines):
                fixed_lines.append(line)
                in_try_block = True
            elif in_try_block and ('pytest.skip' in line or 'except' in line):
                if 'except' not in line:
                    # Add except clause before pytest.skip
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(' ' * (indent - 4) + 'except Exception as e:')
                fixed_lines.append(line)
                in_try_block = False
            else:
                fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        # Step 7: Ensure proper class structure
        if 'class Test' not in content and 'def test_' in content:
            # Add a basic test class if missing
            lines = content.split('\n')
            import_end = 0
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('#') and not line.startswith('import') and not line.startswith('from') and not line.startswith('"""'):
                    import_end = i
                    break
            
            class_def = '\n\nclass TestModule:\n    """Test class for module."""\n'
            lines.insert(import_end, class_def)
            content = '\n'.join(lines)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def scan_and_fix_all_corrupted_files():
    """Scan all test files and fix the specific corruption pattern."""
    tests_dir = Path("tests/systems")
    fixed_count = 0
    error_count = 0
    
    print("Scanning for corrupted test files...")
    
    for test_file in tests_dir.rglob("*.py"):
        if test_file.name.startswith('__'):
            continue
            
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file has the corruption pattern
            if '\\1:' in content:
                print(f"Found corrupted file: {test_file}")
                if fix_corrupted_test_file(test_file):
                    fixed_count += 1
                    print(f"  -> Fixed {test_file}")
                else:
                    error_count += 1
                    print(f"  -> Could not fix {test_file}")
                    
        except Exception as e:
            print(f"Error processing {test_file}: {e}")
            error_count += 1
    
    print(f"\nSummary: Fixed {fixed_count} files, {error_count} files had errors")
    return fixed_count, error_count

def main():
    """Main function to fix test syntax errors."""
    print("TASK 28: Fixing Corrupted Test Files (v2)")
    print("=" * 50)
    
    # Change to backend directory
    os.chdir(Path(__file__).parent)
    
    # Scan and fix all corrupted files
    fixed_count, error_count = scan_and_fix_all_corrupted_files()
    
    if fixed_count > 0:
        print(f"\n✅ Fixed {fixed_count} corrupted test files")
    
    if error_count > 0:
        print(f"⚠️  {error_count} files had errors during fixing")
    
    # Test if we can now collect tests without syntax errors
    print("\nTesting test collection after fixes...")
    import subprocess
    import sys
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/systems", 
            "--collect-only", "-q"
        ], capture_output=True, text=True, timeout=60)
        
        output = result.stdout + result.stderr
        syntax_errors = len([line for line in output.split('\n') if 'unexpected character after line continuation character' in line])
        
        print(f"Remaining corruption errors after fix: {syntax_errors}")
        
        if syntax_errors == 0:
            print("✅ All corruption syntax errors fixed!")
        else:
            print(f"⚠️  {syntax_errors} corruption errors still remain")
            
    except Exception as e:
        print(f"Error testing collection: {e}")

if __name__ == "__main__":
    main() 