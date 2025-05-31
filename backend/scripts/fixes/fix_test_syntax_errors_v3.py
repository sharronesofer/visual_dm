#!/usr/bin/env python3
"""
Final comprehensive fix for test syntax errors.
Handles all corruption patterns including \n\1 and remaining \1: patterns.
"""

import os
import re
from pathlib import Path

def fix_all_corruption_patterns(file_path):
    """Fix all corruption patterns in a Python test file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern 1: Fix \n\1    pass patterns
        content = re.sub(r'\\n\\1\s+pass\s*\n', '', content)
        
        # Pattern 2: Fix remaining \1: patterns  
        content = re.sub(r'\\1:\s*\n', '', content)
        
        # Pattern 3: Fix standalone \1 patterns
        content = re.sub(r'\\1\s+', '', content)
        
        # Pattern 4: Fix try/except blocks that are malformed
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith('#'):
                fixed_lines.append(line)
                i += 1
                continue
            
            # Handle malformed try blocks
            if 'try:' in line and i + 1 < len(lines):
                next_line = lines[i + 1] if i + 1 < len(lines) else ""
                
                # If next line doesn't start with proper indentation or except, fix it
                if next_line.strip() and not next_line.startswith('    ') and not 'except' in next_line:
                    fixed_lines.append(line)
                    fixed_lines.append('        try:')
                    i += 1
                    continue
            
            # Handle lines that should be class definitions
            if ('"""Test suite for' in line or 'Test class for' in line) and i > 0:
                prev_line = lines[i - 1] if i > 0 else ""
                if not prev_line.strip().startswith('class'):
                    # Extract class name from docstring
                    if 'Test suite for' in line:
                        module_name = line.split('Test suite for ')[1].split(' ')[0].replace('.', '')
                        class_name = f"Test{module_name.title().replace('_', '')}"
                    else:
                        class_name = "TestModule"
                    
                    fixed_lines.append(f"class {class_name}:")
                    fixed_lines.append(line)
                    i += 1
                    continue
            
            # Handle lines that should be method definitions
            if line.strip().startswith('"""Test ') and i > 0:
                prev_line = lines[i - 1] if i > 0 else ""
                if not prev_line.strip().startswith('def '):
                    # Extract method name from docstring
                    test_desc = line.replace('"""Test ', '').replace('."""', '').replace(' ', '_').lower()
                    method_name = f"test_{test_desc}"
                    fixed_lines.append(f"    def {method_name}(self):")
                    fixed_lines.append(line)
                    i += 1
                    continue
            
            # Handle setUp/tearDown methods
            if 'Set up test fixtures' in line and i > 0:
                prev_line = lines[i - 1] if i > 0 else ""
                if not prev_line.strip().startswith('def '):
                    fixed_lines.append('    def setUp(self):')
                    fixed_lines.append(line)
                    i += 1
                    continue
            
            if 'Clean up after' in line and i > 0:
                prev_line = lines[i - 1] if i > 0 else ""
                if not prev_line.strip().startswith('def '):
                    fixed_lines.append('    def tearDown(self):')
                    fixed_lines.append(line)
                    i += 1
                    continue
            
            fixed_lines.append(line)
            i += 1
        
        content = '\n'.join(fixed_lines)
        
        # Final cleanup: ensure proper structure
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
        
        # Ensure proper indentation for methods
        lines = content.split('\n')
        fixed_lines = []
        in_class = False
        
        for line in lines:
            if line.strip().startswith('class '):
                in_class = True
                fixed_lines.append(line)
            elif in_class and line.strip().startswith('def ') and not line.startswith('    '):
                # Fix method indentation
                fixed_lines.append('    ' + line.strip())
            elif in_class and line.strip().startswith('"""') and not line.startswith('        '):
                # Fix docstring indentation
                fixed_lines.append('        ' + line.strip())
            else:
                fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def scan_and_fix_remaining_corruption():
    """Scan all test files and fix remaining corruption patterns."""
    tests_dir = Path("tests/systems")
    fixed_count = 0
    error_count = 0
    
    print("Scanning for remaining corruption patterns...")
    
    for test_file in tests_dir.rglob("*.py"):
        if test_file.name.startswith('__'):
            continue
            
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file has any corruption patterns
            if '\\n\\1' in content or '\\1:' in content or '\\1 ' in content:
                print(f"Found remaining corruption in: {test_file}")
                if fix_all_corruption_patterns(test_file):
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
    """Main function to fix remaining test syntax errors."""
    print("TASK 28: Final Corruption Fix (v3)")
    print("=" * 50)
    
    # Change to backend directory
    os.chdir(Path(__file__).parent)
    
    # Scan and fix remaining corrupted files
    fixed_count, error_count = scan_and_fix_remaining_corruption()
    
    if fixed_count > 0:
        print(f"\n✅ Fixed {fixed_count} additional corrupted test files")
    
    if error_count > 0:
        print(f"⚠️  {error_count} files had errors during fixing")
    
    # Test if we can now collect tests without syntax errors
    print("\nTesting test collection after final fixes...")
    import subprocess
    import sys
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/systems", 
            "--collect-only", "-q"
        ], capture_output=True, text=True, timeout=60)
        
        output = result.stdout + result.stderr
        syntax_errors = len([line for line in output.split('\n') if 'unexpected character after line continuation character' in line])
        total_errors = len([line for line in output.split('\n') if 'ERROR' in line or 'error' in line.lower()])
        
        print(f"Remaining corruption errors after final fix: {syntax_errors}")
        print(f"Total collection errors: {total_errors}")
        
        if syntax_errors == 0:
            print("✅ All corruption syntax errors fixed!")
        else:
            print(f"⚠️  {syntax_errors} corruption errors still remain")
            
    except Exception as e:
        print(f"Error testing collection: {e}")

if __name__ == "__main__":
    main() 