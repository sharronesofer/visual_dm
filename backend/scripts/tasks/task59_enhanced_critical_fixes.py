#!/usr/bin/env python3
"""
Enhanced Critical Fixes for Task 59: Backend Development Protocol
Handles more sophisticated parsing errors that the basic fixes couldn't resolve.
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class EnhancedCriticalFixer:
    def __init__(self, systems_path: str = "systems"):
        self.systems_path = Path(systems_path)
        self.fixed_files = []
        self.failed_files = []
        
    def assess_parsing_errors(self) -> List[Dict]:
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
                    'line': e.lineno,
                    'text': e.text.strip() if e.text else '',
                    'offset': e.offset
                })
            except Exception as e:
                errors.append({
                    'file': str(py_file),
                    'error': f"Parse error: {str(e)}",
                    'line': 0,
                    'text': '',
                    'offset': 0
                })
        return errors

    def fix_unmatched_parenthesis(self, file_path: str, line_num: int) -> bool:
        """Fix unmatched parenthesis errors"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if line_num > len(lines):
                return False
                
            line = lines[line_num - 1]
            
            # Count parentheses
            open_parens = line.count('(')
            close_parens = line.count(')')
            
            if open_parens > close_parens:
                # Add missing closing parentheses
                lines[line_num - 1] = line.rstrip() + ')' * (open_parens - close_parens) + '\n'
            elif close_parens > open_parens:
                # Remove extra closing parentheses
                diff = close_parens - open_parens
                new_line = line
                for _ in range(diff):
                    new_line = new_line.replace(')', '', 1)
                lines[line_num - 1] = new_line
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
        except Exception as e:
            print(f"  Error fixing unmatched parenthesis in {file_path}: {e}")
            return False

    def fix_invalid_syntax_comprehensive(self, file_path: str, line_num: int, error_text: str) -> bool:
        """Comprehensive fix for invalid syntax errors"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if line_num > len(lines):
                return False
                
            line = lines[line_num - 1].strip()
            
            # Pattern matching for common invalid syntax patterns
            fixes_applied = False
            
            # Fix incomplete class definitions
            if line.startswith('class ') and not line.endswith(':'):
                lines[line_num - 1] = line + ':\n'
                if line_num < len(lines) and not lines[line_num].strip():
                    lines[line_num] = '    pass\n'
                fixes_applied = True
            
            # Fix incomplete function definitions
            elif line.startswith('def ') and not line.endswith(':'):
                lines[line_num - 1] = line + ':\n'
                if line_num < len(lines) and not lines[line_num].strip():
                    lines[line_num] = '    pass\n'
                fixes_applied = True
                    
            # Fix incomplete if/elif/else statements
            elif re.match(r'^\s*(if|elif|else)\s+.*[^:]$', line):
                lines[line_num - 1] = line + ':\n'
                if line_num < len(lines) and not lines[line_num].strip():
                    lines[line_num] = '    pass\n'
                fixes_applied = True
                    
            # Fix incomplete try/except/finally statements
            elif re.match(r'^\s*(try|except|finally)\s*[^:]$', line):
                lines[line_num - 1] = line + ':\n'
                if line_num < len(lines) and not lines[line_num].strip():
                    lines[line_num] = '    pass\n'
                fixes_applied = True
                    
            # Fix incomplete for/while loops
            elif re.match(r'^\s*(for|while)\s+.*[^:]$', line):
                lines[line_num - 1] = line + ':\n'
                if line_num < len(lines) and not lines[line_num].strip():
                    lines[line_num] = '    pass\n'
                fixes_applied = True
                    
            # Fix missing quotes
            elif line.count('"') % 2 == 1:  # Odd number of quotes
                lines[line_num - 1] = line + '"\n'
                fixes_applied = True
            elif line.count("'") % 2 == 1:  # Odd number of quotes
                lines[line_num - 1] = line + "'\n"
                fixes_applied = True
                
            # Fix incomplete import statements
            elif line.startswith('from ') and 'import' not in line:
                lines[line_num - 1] = line + ' import *\n'
                fixes_applied = True
                
            if fixes_applied:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                return True
                
            return False
        except Exception as e:
            print(f"  Error fixing invalid syntax in {file_path}: {e}")
            return False

    def fix_unexpected_indent_advanced(self, file_path: str, line_num: int) -> bool:
        """Advanced fix for unexpected indent errors"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if line_num > len(lines):
                return False
                
            # Get the problematic line and surrounding context
            target_line = lines[line_num - 1]
            
            # Look at previous lines to determine correct indentation
            prev_indent = 0
            for i in range(line_num - 2, -1, -1):
                prev_line = lines[i].rstrip()
                if prev_line.strip():  # Non-empty line
                    prev_indent = len(prev_line) - len(prev_line.lstrip())
                    
                    # If previous line ends with colon, increase indent
                    if prev_line.endswith(':'):
                        prev_indent += 4
                    break
            
            # Fix the indentation
            content = target_line.strip()
            if content:  # Don't process empty lines
                lines[line_num - 1] = ' ' * prev_indent + content + '\n'
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
        except Exception as e:
            print(f"  Error fixing unexpected indent in {file_path}: {e}")
            return False

    def fix_unindent_mismatch_advanced(self, file_path: str, line_num: int) -> bool:
        """Advanced fix for unindent mismatch errors"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if line_num > len(lines):
                return False
                
            # Find valid indentation levels above the problematic line
            valid_indents = set()
            for i in range(line_num - 1):
                line = lines[i].rstrip()
                if line.strip():  # Non-empty line
                    indent = len(line) - len(line.lstrip())
                    valid_indents.add(indent)
            
            # Get current line content
            current_line = lines[line_num - 1]
            content = current_line.strip()
            
            if content:  # Don't process empty lines
                current_indent = len(current_line) - len(current_line.lstrip())
                
                # Find the closest valid indentation level
                if valid_indents:
                    closest_indent = min(valid_indents, key=lambda x: abs(x - current_indent))
                    lines[line_num - 1] = ' ' * closest_indent + content + '\n'
                else:
                    # Default to no indentation
                    lines[line_num - 1] = content + '\n'
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
        except Exception as e:
            print(f"  Error fixing unindent mismatch in {file_path}: {e}")
            return False

    def fix_file_structure_issues(self, file_path: str) -> bool:
        """Fix structural issues in files that cause parsing errors"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # If file is empty or whitespace-only, add minimal structure
            if not content.strip():
                content = '"""Module placeholder"""\npass\n'
            
            # Ensure file ends with newline
            if not content.endswith('\n'):
                content += '\n'
            
            # Fix obvious structural issues
            lines = content.split('\n')
            fixed_lines = []
            
            for i, line in enumerate(lines):
                # Remove trailing whitespace
                line = line.rstrip()
                
                # Skip processing empty lines
                if not line:
                    fixed_lines.append('')
                    continue
                
                # Ensure proper spacing after colons
                if ':' in line and not line.endswith(':'):
                    # This might be a complex case, leave as is
                    fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(fixed_lines))
            
            return True
        except Exception as e:
            print(f"  Error fixing file structure in {file_path}: {e}")
            return False

    def fix_parsing_error(self, error_info: Dict) -> bool:
        """Fix a specific parsing error using appropriate method"""
        file_path = error_info['file']
        error = error_info['error']
        line_num = error_info['line']
        
        print(f"\nFixing: {Path(file_path).name}")
        print(f"  Error: {error}")
        
        try:
            # Determine fix strategy based on error type
            if "unmatched ')'" in error:
                return self.fix_unmatched_parenthesis(file_path, line_num)
            elif "invalid syntax" in error:
                return self.fix_invalid_syntax_comprehensive(file_path, line_num, error_info.get('text', ''))
            elif "unexpected indent" in error:
                return self.fix_unexpected_indent_advanced(file_path, line_num)
            elif "unindent does not match" in error:
                return self.fix_unindent_mismatch_advanced(file_path, line_num)
            else:
                # Try general file structure fixes
                return self.fix_file_structure_issues(file_path)
                
        except Exception as e:
            print(f"  Failed to fix {file_path}: {e}")
            return False

    def verify_fix(self, file_path: str) -> bool:
        """Verify that a file can now be parsed without errors"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
            return True
        except Exception:
            return False

    def run_enhanced_fixes(self):
        """Run enhanced critical fixes"""
        print("=== Enhanced Critical Fixes for Task 59 ===")
        
        # Get current parsing errors
        errors = self.assess_parsing_errors()
        print(f"Found {len(errors)} parsing errors to fix")
        
        if not errors:
            print("No parsing errors found!")
            return
        
        # Fix each error
        fixes_successful = 0
        for error_info in errors:
            if self.fix_parsing_error(error_info):
                if self.verify_fix(error_info['file']):
                    print(f"  ✓ Successfully fixed {Path(error_info['file']).name}")
                    fixes_successful += 1
                    self.fixed_files.append(error_info['file'])
                else:
                    print(f"  ⚠ Fixed but still has issues: {Path(error_info['file']).name}")
                    self.failed_files.append(error_info['file'])
            else:
                print(f"  ✗ Failed to fix: {Path(error_info['file']).name}")
                self.failed_files.append(error_info['file'])
        
        print(f"\n=== Enhanced Fixes Results ===")
        print(f"Successfully fixed: {fixes_successful}")
        print(f"Failed to fix: {len(self.failed_files)}")
        
        if self.failed_files:
            print("\nFiles still needing manual intervention:")
            for file_path in self.failed_files[:10]:  # Show first 10
                print(f"  - {Path(file_path).name}")
            if len(self.failed_files) > 10:
                print(f"  ... and {len(self.failed_files) - 10} more")

        # Final verification
        print(f"\n=== Final Verification ===")
        remaining_errors = self.assess_parsing_errors()
        print(f"Remaining parsing errors: {len(remaining_errors)}")
        
        return len(remaining_errors) == 0

if __name__ == "__main__":
    fixer = EnhancedCriticalFixer()
    success = fixer.run_enhanced_fixes()
    
    if success:
        print("\n🎉 All parsing errors resolved! Ready to proceed with testing protocol.")
    else:
        print("\n⚠️  Some parsing errors remain. Manual intervention may be required.")
    
    sys.exit(0 if success else 1) 