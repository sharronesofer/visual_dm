#!/usr/bin/env python3
"""
Import Syntax Fixes for Task 59: Backend Development Protocol
Specifically targets malformed import statements that are causing syntax errors.
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class ImportSyntaxFixer:
    def __init__(self, systems_path: str = "systems"):
        self.systems_path = Path(systems_path)
        self.fixed_files = []
        self.failed_files = []
        
    def fix_malformed_imports(self, file_path: str) -> bool:
        """Fix malformed import statements"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Pattern 1: Fix incomplete SQLAlchemy imports
            # from sqlalchemy import (
            # """"  <-- This is wrong, should be proper imports
            pattern1 = r'from sqlalchemy import \(\s*["\'"]{3,4}[^"\']*["\'"]{3,4}'
            if re.search(pattern1, content, re.MULTILINE | re.DOTALL):
                # Replace with proper SQLAlchemy imports
                replacement = '''from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    Boolean,
    JSON,
)'''
                content = re.sub(pattern1, replacement, content, flags=re.MULTILINE | re.DOTALL)
            
            # Pattern 2: Fix TYPE_CHECKING import issues
            # from sqlalchemy import (
            # 
            # if TYPE_CHECKING:
            #     # imports should be here
            #     Column,  <-- These are outside TYPE_CHECKING
            pattern2 = r'from sqlalchemy import \(\s*\n\s*if TYPE_CHECKING:\s*\n.*?pass.*?\n(.*?)\)'
            if re.search(pattern2, content, re.MULTILINE | re.DOTALL):
                # Move imports into TYPE_CHECKING block properly
                match = re.search(pattern2, content, re.MULTILINE | re.DOTALL)
                if match:
                    imports_section = match.group(1).strip()
                    formatted_imports = imports_section.replace(",", ",\n        ").strip()
                    replacement = '''if TYPE_CHECKING:
    from sqlalchemy import (
        {}
    )'''.format(formatted_imports)
                    content = re.sub(pattern2, replacement, content, flags=re.MULTILINE | re.DOTALL)
            
            # Pattern 3: Fix imports that are missing imports keyword
            # from typing import TYPE_CHECKING
            # from sqlalchemy import (
            # 
            # if TYPE_CHECKING:
            #     pass  # TODO: Implement
            #     Column,  <-- Missing 'from sqlalchemy import'
            pattern3 = r'(if TYPE_CHECKING:\s*\n\s*pass[^\n]*\n)(.*?)(Column,.*?)\)'
            if re.search(pattern3, content, re.MULTILINE | re.DOTALL):
                match = re.search(pattern3, content, re.MULTILINE | re.DOTALL)
                if match:
                    imports_list = match.group(3).strip()
                    formatted_imports = imports_list.replace(",", ",\n        ")
                    replacement = '''if TYPE_CHECKING:
    from sqlalchemy import (
        {}
    )'''.format(formatted_imports)
                    content = re.sub(pattern3, replacement, content, flags=re.MULTILINE | re.DOTALL)
            
            # Pattern 4: Fix incomplete import statements that end abruptly
            # from backend.something import
            # (next line starts something else)
            content = re.sub(r'from ([^\n]+) import\s*\n(?=[a-zA-Z])', r'from \1 import *\n', content)
            
            # Pattern 5: Fix Dict/Any imports when missing
            if 'Dict[' in content and 'from typing import' in content and 'Dict' not in content:
                content = re.sub(r'from typing import (.*)', r'from typing import \1, Dict', content)
            
            if 'Any' in content and 'from typing import' in content and 'Any' not in content:
                content = re.sub(r'from typing import (.*)', r'from \1, Any', content)
            
            # Only write if content changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            
            return False
            
        except Exception as e:
            print(f"  Error fixing imports in {file_path}: {e}")
            return False

    def fix_common_syntax_patterns(self, file_path: str) -> bool:
        """Fix common syntax patterns that cause parsing errors"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            modified = False
            
            for i, line in enumerate(lines):
                original_line = line
                
                # Fix class definitions without colons
                if re.match(r'^\s*class\s+\w+.*[^:]$', line.strip()):
                    lines[i] = line.rstrip() + ':\n'
                    # Add pass if next line is empty or not indented
                    if i + 1 < len(lines) and (not lines[i + 1].strip() or not lines[i + 1].startswith('    ')):
                        lines.insert(i + 1, '    pass\n')
                    modified = True
                
                # Fix function definitions without colons
                elif re.match(r'^\s*def\s+\w+.*[^:]$', line.strip()):
                    lines[i] = line.rstrip() + ':\n'
                    # Add pass if next line is empty or not indented
                    if i + 1 < len(lines) and (not lines[i + 1].strip() or not lines[i + 1].startswith('    ')):
                        lines.insert(i + 1, '    pass\n')
                    modified = True
                
                # Fix if/elif/else without colons
                elif re.match(r'^\s*(if|elif|else)\s+.*[^:]$', line.strip()):
                    lines[i] = line.rstrip() + ':\n'
                    # Add pass if next line is empty or not indented
                    if i + 1 < len(lines) and (not lines[i + 1].strip() or not lines[i + 1].startswith('    ')):
                        lines.insert(i + 1, '    pass\n')
                    modified = True
                
                # Fix try/except/finally without colons  
                elif re.match(r'^\s*(try|except|finally)\s*[^:]$', line.strip()):
                    lines[i] = line.rstrip() + ':\n'
                    # Add pass if next line is empty or not indented
                    if i + 1 < len(lines) and (not lines[i + 1].strip() or not lines[i + 1].startswith('    ')):
                        lines.insert(i + 1, '    pass\n')
                    modified = True
                
                # Fix for/while without colons
                elif re.match(r'^\s*(for|while)\s+.*[^:]$', line.strip()):
                    lines[i] = line.rstrip() + ':\n'
                    # Add pass if next line is empty or not indented
                    if i + 1 < len(lines) and (not lines[i + 1].strip() or not lines[i + 1].startswith('    ')):
                        lines.insert(i + 1, '    pass\n')
                    modified = True
                
                if lines[i] != original_line:
                    modified = True
            
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                return True
            
            return False
            
        except Exception as e:
            print(f"  Error fixing syntax patterns in {file_path}: {e}")
            return False

    def fix_empty_files(self, file_path: str) -> bool:
        """Fix files that are empty or only have whitespace"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # If file is empty or only whitespace
            if not content.strip():
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('"""Module placeholder"""\npass\n')
                return True
            
            # If file has only imports but no actual code
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            code_lines = [line for line in lines if not (line.startswith('import ') or line.startswith('from ') or line.startswith('#') or line.startswith('"""') or line.startswith("'''"))]
            
            if not code_lines:
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write('\n\n# Placeholder implementation\npass\n')
                return True
            
            return False
            
        except Exception as e:
            print(f"  Error fixing empty file {file_path}: {e}")
            return False

    def verify_syntax(self, file_path: str) -> bool:
        """Verify that a file has valid Python syntax"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
            return True
        except Exception:
            return False

    def get_parsing_errors(self) -> List[Dict]:
        """Get current parsing errors"""
        errors = []
        for py_file in self.systems_path.rglob("*.py"):
            if py_file.name.startswith('.'):
                continue
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                errors.append({
                    'file': str(py_file),
                    'error': str(e),
                    'line': e.lineno
                })
            except Exception as e:
                errors.append({
                    'file': str(py_file),
                    'error': f"Parse error: {str(e)}",
                    'line': 0
                })
        return errors

    def run_import_fixes(self):
        """Run import and syntax fixes"""
        print("=== Import Syntax Fixes for Task 59 ===")
        
        # Get files with parsing errors
        errors = self.get_parsing_errors()
        error_files = [error['file'] for error in errors]
        
        print(f"Found {len(error_files)} files with parsing errors")
        
        if not error_files:
            print("No parsing errors found!")
            return True
        
        fixes_applied = 0
        
        for file_path in error_files:
            file_name = Path(file_path).name
            print(f"\nProcessing: {file_name}")
            
            fixed = False
            
            # Try import fixes first
            if self.fix_malformed_imports(file_path):
                print(f"  ✓ Fixed malformed imports")
                fixed = True
            
            # Try syntax pattern fixes
            if self.fix_common_syntax_patterns(file_path):
                print(f"  ✓ Fixed syntax patterns")
                fixed = True
            
            # Try empty file fixes
            if self.fix_empty_files(file_path):
                print(f"  ✓ Fixed empty file")
                fixed = True
            
            # Verify the fix
            if self.verify_syntax(file_path):
                print(f"  ✅ {file_name} now has valid syntax")
                fixes_applied += 1
                self.fixed_files.append(file_path)
            else:
                print(f"  ⚠️ {file_name} still has syntax issues")
                self.failed_files.append(file_path)
                if not fixed:
                    print(f"  ⚠️ No fixes were applied")
        
        print(f"\n=== Import Fixes Results ===")
        print(f"Files successfully fixed: {fixes_applied}")
        print(f"Files still with issues: {len(self.failed_files)}")
        
        # Final verification
        final_errors = self.get_parsing_errors()
        print(f"\nFinal parsing errors remaining: {len(final_errors)}")
        
        if self.failed_files and len(self.failed_files) <= 10:
            print("\nFiles still needing attention:")
            for file_path in self.failed_files:
                print(f"  - {Path(file_path).name}")
        
        return len(final_errors) == 0

if __name__ == "__main__":
    fixer = ImportSyntaxFixer()
    success = fixer.run_import_fixes()
    
    if success:
        print("\n🎉 All parsing errors resolved!")
    else:
        print(f"\n⚠️  Some parsing errors remain.")
    
    sys.exit(0 if success else 1) 