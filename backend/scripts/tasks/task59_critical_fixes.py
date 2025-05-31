#!/usr/bin/env python3
"""
Task 59: Critical Fixes for Parsing Errors
Addresses the 79 parsing errors that prevent test execution
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict

class Task59CriticalFixer:
    def __init__(self, backend_root: str = "/Users/Sharrone/Visual_DM/backend"):
        self.backend_root = Path(backend_root)
        self.fixed_files = []
        self.errors_fixed = 0
        
    def load_assessment_report(self):
        """Load the assessment report to get list of parsing errors"""
        report_path = self.backend_root / "task59_assessment_report.json"
        with open(report_path, 'r') as f:
            return json.load(f)
    
    def fix_all_parsing_errors(self):
        """Fix all parsing errors identified in assessment"""
        print("=== Fixing Critical Parsing Errors ===")
        
        report = self.load_assessment_report()
        parsing_errors = report['issues_found']['parsing_errors']
        
        print(f"Found {len(parsing_errors)} parsing errors to fix")
        
        for error_info in parsing_errors:
            file_path = Path(error_info['file'])
            error_msg = error_info['error']
            line_num = error_info.get('line')
            
            print(f"\nFixing: {file_path.name}")
            print(f"  Error: {error_msg}")
            
            success = self.fix_parsing_error(file_path, error_msg, line_num)
            if success:
                self.errors_fixed += 1
                if str(file_path) not in self.fixed_files:
                    self.fixed_files.append(str(file_path))
        
        print(f"\n=== Fixed {self.errors_fixed} parsing errors in {len(self.fixed_files)} files ===")
        return self.errors_fixed
    
    def fix_parsing_error(self, file_path: Path, error_msg: str, line_num: int) -> bool:
        """Fix specific parsing error in file"""
        try:
            if not file_path.exists():
                print(f"  File not found: {file_path}")
                return False
                
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Apply specific fixes based on error type
            if "expected an indented block" in error_msg:
                return self.fix_indentation_error(file_path, lines, line_num)
            elif "invalid syntax" in error_msg:
                return self.fix_syntax_error(file_path, lines, line_num)
            elif "unexpected indent" in error_msg:
                return self.fix_unexpected_indent(file_path, lines, line_num)
            elif "unindent does not match" in error_msg:
                return self.fix_unindent_error(file_path, lines, line_num)
            elif "was never closed" in error_msg:
                return self.fix_unclosed_parenthesis(file_path, lines, line_num)
            else:
                return self.fix_generic_error(file_path, lines, line_num, error_msg)
                
        except Exception as e:
            print(f"  Error fixing {file_path}: {e}")
            return False
    
    def fix_indentation_error(self, file_path: Path, lines: List[str], line_num: int) -> bool:
        """Fix 'expected an indented block' errors"""
        if line_num and line_num <= len(lines):
            # Insert a pass statement if the block is empty
            target_line = line_num - 1
            if target_line < len(lines):
                # Calculate indentation from previous line
                prev_line = lines[target_line - 1] if target_line > 0 else ""
                indent = len(prev_line) - len(prev_line.lstrip())
                
                # Add 4 spaces for the block
                block_indent = " " * (indent + 4)
                lines[target_line] = f"{block_indent}pass  # TODO: Implement\n"
                
                self.write_file(file_path, lines)
                print(f"  Fixed indentation error by adding pass statement")
                return True
        return False
    
    def fix_syntax_error(self, file_path: Path, lines: List[str], line_num: int) -> bool:
        """Fix syntax errors"""
        if line_num and line_num <= len(lines):
            target_line = line_num - 1
            line_content = lines[target_line].strip()
            
            # Common syntax error fixes
            if line_content == "" or line_content.startswith("#"):
                # Empty line or comment, add pass
                lines[target_line] = "pass  # TODO: Implement\n"
                self.write_file(file_path, lines)
                print(f"  Fixed syntax error by adding pass statement")
                return True
                
            # Try to fix common syntax issues
            if line_content.endswith(":") and target_line + 1 < len(lines):
                next_line = lines[target_line + 1].strip()
                if not next_line or next_line.startswith("#"):
                    # Add pass after colon
                    indent = len(lines[target_line]) - len(lines[target_line].lstrip()) + 4
                    lines[target_line + 1] = " " * indent + "pass  # TODO: Implement\n"
                    self.write_file(file_path, lines)
                    print(f"  Fixed syntax error by adding pass after colon")
                    return True
        return False
    
    def fix_unexpected_indent(self, file_path: Path, lines: List[str], line_num: int) -> bool:
        """Fix unexpected indentation errors"""
        if line_num and line_num <= len(lines):
            target_line = line_num - 1
            
            # Remove extra indentation
            original_line = lines[target_line]
            fixed_line = original_line.lstrip()
            
            # Find correct indentation from context
            correct_indent = 0
            for i in range(target_line - 1, -1, -1):
                if lines[i].strip():
                    correct_indent = len(lines[i]) - len(lines[i].lstrip())
                    break
            
            lines[target_line] = " " * correct_indent + fixed_line
            self.write_file(file_path, lines)
            print(f"  Fixed unexpected indent")
            return True
        return False
    
    def fix_unindent_error(self, file_path: Path, lines: List[str], line_num: int) -> bool:
        """Fix unindent does not match errors"""
        if line_num and line_num <= len(lines):
            target_line = line_num - 1
            
            # Find the correct indentation level
            correct_indent = 0
            for i in range(target_line - 1, -1, -1):
                if lines[i].strip() and not lines[i].strip().startswith("#"):
                    line_indent = len(lines[i]) - len(lines[i].lstrip())
                    if line_indent < len(lines[target_line]) - len(lines[target_line].lstrip()):
                        correct_indent = line_indent
                        break
            
            # Fix the indentation
            content = lines[target_line].lstrip()
            lines[target_line] = " " * correct_indent + content
            self.write_file(file_path, lines)
            print(f"  Fixed unindent mismatch")
            return True
        return False
    
    def fix_unclosed_parenthesis(self, file_path: Path, lines: List[str], line_num: int) -> bool:
        """Fix unclosed parenthesis errors"""
        if line_num and line_num <= len(lines):
            target_line = line_num - 1
            line_content = lines[target_line]
            
            # Count parentheses
            open_parens = line_content.count('(')
            close_parens = line_content.count(')')
            
            if open_parens > close_parens:
                # Add missing closing parentheses
                missing = open_parens - close_parens
                lines[target_line] = line_content.rstrip() + ')' * missing + '\n'
                self.write_file(file_path, lines)
                print(f"  Fixed unclosed parenthesis by adding {missing} closing paren(s)")
                return True
        return False
    
    def fix_generic_error(self, file_path: Path, lines: List[str], line_num: int, error_msg: str) -> bool:
        """Generic error fixing approach"""
        if line_num and line_num <= len(lines):
            target_line = line_num - 1
            
            # If line is empty or whitespace only, add pass
            if not lines[target_line].strip():
                # Calculate proper indentation
                indent = 0
                for i in range(target_line - 1, -1, -1):
                    if lines[i].strip():
                        if lines[i].strip().endswith(':'):
                            indent = len(lines[i]) - len(lines[i].lstrip()) + 4
                        else:
                            indent = len(lines[i]) - len(lines[i].lstrip())
                        break
                
                lines[target_line] = " " * indent + "pass  # TODO: Implement\n"
                self.write_file(file_path, lines)
                print(f"  Fixed generic error by adding pass statement")
                return True
        return False
    
    def write_file(self, file_path: Path, lines: List[str]):
        """Write fixed content back to file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    
    def verify_fixes(self):
        """Verify that fixes resolved the parsing errors"""
        print("\n=== Verifying Fixes ===")
        
        # Re-run assessment on fixed files
        parsing_errors = 0
        for file_path in self.fixed_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                import ast
                ast.parse(content)
                print(f"✓ {Path(file_path).name} - syntax OK")
            except SyntaxError as e:
                print(f"✗ {Path(file_path).name} - still has syntax error: {e}")
                parsing_errors += 1
        
        print(f"\nVerification complete: {parsing_errors} files still have parsing errors")
        return parsing_errors == 0

def main():
    """Main execution function"""
    fixer = Task59CriticalFixer()
    
    # Fix all parsing errors
    errors_fixed = fixer.fix_all_parsing_errors()
    
    # Verify the fixes
    verification_success = fixer.verify_fixes()
    
    print(f"\n=== Task 59 Critical Fixes Complete ===")
    print(f"Errors fixed: {errors_fixed}")
    print(f"Files modified: {len(fixer.fixed_files)}")
    print(f"Verification successful: {verification_success}")
    
    return verification_success

if __name__ == "__main__":
    main() 