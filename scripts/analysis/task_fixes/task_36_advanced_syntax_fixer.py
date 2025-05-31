#!/usr/bin/env python3
"""
Task 36: Advanced Syntax Error Fixer
Handles complex syntax errors that require more sophisticated pattern matching.
"""

import os
import ast
import re
from pathlib import Path
from typing import List, Dict, Tuple

class AdvancedSyntaxFixer:
    def __init__(self, backend_path: str = "backend"):
        self.backend_path = Path(backend_path)
        self.fixes_applied = []
        self.errors_remaining = []

    def run_advanced_fixes(self):
        """Run advanced syntax fixes"""
        print("🔧 Starting Advanced Syntax Error Resolution...")
        print("=" * 60)
        
        # Get all Python files with syntax errors
        error_files = self._get_files_with_syntax_errors()
        
        print(f"Found {len(error_files)} files with syntax errors")
        
        for file_path in error_files:
            self._fix_file_syntax_errors(file_path)
        
        self._generate_report()

    def _get_files_with_syntax_errors(self) -> List[Path]:
        """Get all Python files that have syntax errors"""
        error_files = []
        
        for py_file in self.backend_path.rglob("*.py"):
            if '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                try:
                    ast.parse(content)
                except SyntaxError:
                    error_files.append(py_file)
                except Exception:
                    # Other parsing errors
                    error_files.append(py_file)
                    
            except Exception:
                # File read errors
                continue
        
        return error_files

    def _fix_file_syntax_errors(self, file_path: Path):
        """Fix syntax errors in a specific file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply various syntax fixes
            content = self._fix_javascript_syntax(content)
            content = self._fix_malformed_strings(content)
            content = self._fix_indentation_errors(content)
            content = self._fix_bracket_mismatches(content)
            content = self._fix_line_continuation_errors(content)
            content = self._fix_incomplete_statements(content)
            
            # Check if we made changes and they're valid
            if content != original_content:
                try:
                    ast.parse(content)
                    # Write the fixed content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.fixes_applied.append(f"Fixed syntax errors in {file_path}")
                    print(f"   ✅ Fixed {file_path}")
                except SyntaxError as e:
                    # Our fix didn't work, revert
                    self.errors_remaining.append(f"Could not fix {file_path}: {e}")
                    print(f"   ⚠️ Could not fix {file_path}: {e}")
            else:
                self.errors_remaining.append(f"No applicable fixes for {file_path}")
                
        except Exception as e:
            self.errors_remaining.append(f"Error processing {file_path}: {e}")
            print(f"   ❌ Error processing {file_path}: {e}")

    def _fix_javascript_syntax(self, content: str) -> str:
        """Fix JavaScript-like syntax that appears in Python files"""
        
        # Fix JavaScript object literals that look like Python dicts
        # Convert { key: value } to { "key": value }
        content = re.sub(r'\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'{ "\1":', content)
        
        # Fix unmatched braces - remove standalone closing braces
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            stripped = line.strip()
            # Remove lines that are just closing braces
            if stripped in ['}', '})', '}]', '];', '};']:
                continue
            # Fix lines with unmatched closing braces
            if stripped.startswith('}') and not any(c in stripped for c in ['{', '(', '[']):
                continue
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

    def _fix_malformed_strings(self, content: str) -> str:
        """Fix malformed string literals"""
        
        # Fix unterminated string literals by adding closing quotes
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Check for unterminated strings
            if line.count('"') % 2 == 1 and not line.strip().endswith('\\'):
                # Add closing quote
                line = line + '"'
            elif line.count("'") % 2 == 1 and not line.strip().endswith('\\'):
                # Add closing quote
                line = line + "'"
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

    def _fix_indentation_errors(self, content: str) -> str:
        """Fix indentation errors"""
        
        lines = content.split('\n')
        fixed_lines = []
        expected_indent = 0
        
        for line in lines:
            if not line.strip():
                fixed_lines.append(line)
                continue
            
            # Calculate expected indentation based on previous lines
            stripped = line.strip()
            
            # Skip lines that are clearly malformed
            if stripped.startswith('def ') or stripped.startswith('class '):
                expected_indent = 0
            elif stripped.endswith(':'):
                # This line should increase indentation for next line
                pass
            
            # Fix obvious indentation errors
            if line.startswith('    ') and expected_indent == 0:
                # Remove unexpected indentation
                line = line.lstrip()
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

    def _fix_bracket_mismatches(self, content: str) -> str:
        """Fix bracket, parenthesis, and brace mismatches"""
        
        # Count and balance brackets
        open_brackets = {'(': 0, '[': 0, '{': 0}
        close_brackets = {')': '(', ']': '[', '}': '{'}
        
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Count brackets in this line
            for char in line:
                if char in open_brackets:
                    open_brackets[char] += 1
                elif char in close_brackets:
                    matching_open = close_brackets[char]
                    if open_brackets[matching_open] > 0:
                        open_brackets[matching_open] -= 1
                    else:
                        # Unmatched closing bracket - remove it
                        line = line.replace(char, '', 1)
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

    def _fix_line_continuation_errors(self, content: str) -> str:
        """Fix line continuation character errors"""
        
        # Fix backslash followed by non-whitespace
        content = re.sub(r'\\\s*([^\s\n])', r' \1', content)
        
        # Remove unnecessary line continuations
        content = re.sub(r'\\\s*\n\s*$', '\n', content, flags=re.MULTILINE)
        
        return content

    def _fix_incomplete_statements(self, content: str) -> str:
        """Fix incomplete statements and expressions"""
        
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Fix incomplete function definitions
            if stripped.startswith('def ') and not stripped.endswith(':'):
                if '(' in stripped and ')' not in stripped:
                    line = line + '):'
                elif not stripped.endswith(':'):
                    line = line + ':'
            
            # Fix incomplete class definitions
            elif stripped.startswith('class ') and not stripped.endswith(':'):
                if '(' in stripped and ')' not in stripped:
                    line = line + '):'
                elif not stripped.endswith(':'):
                    line = line + ':'
            
            # Fix incomplete if/for/while statements
            elif any(stripped.startswith(kw + ' ') for kw in ['if', 'elif', 'for', 'while', 'with', 'try', 'except', 'finally']) and not stripped.endswith(':'):
                line = line + ':'
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

    def _generate_report(self):
        """Generate report of fixes applied"""
        print("\n" + "=" * 60)
        print("📋 ADVANCED SYNTAX FIXER REPORT")
        print("=" * 60)
        
        print(f"\n✅ FIXES APPLIED ({len(self.fixes_applied)}):")
        for fix in self.fixes_applied[:10]:  # Show first 10
            print(f"   • {fix}")
        if len(self.fixes_applied) > 10:
            print(f"   ... and {len(self.fixes_applied) - 10} more")
        
        if self.errors_remaining:
            print(f"\n⚠️ ERRORS REMAINING ({len(self.errors_remaining)}):")
            for error in self.errors_remaining[:10]:  # Show first 10
                print(f"   • {error}")
            if len(self.errors_remaining) > 10:
                print(f"   ... and {len(self.errors_remaining) - 10} more")
        
        print(f"\n📊 SUMMARY:")
        print(f"   • Advanced Fixes Applied: {len(self.fixes_applied)}")
        print(f"   • Files Still With Errors: {len(self.errors_remaining)}")

if __name__ == "__main__":
    fixer = AdvancedSyntaxFixer()
    fixer.run_advanced_fixes() 