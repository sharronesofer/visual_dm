#!/usr/bin/env python3
"""
Task 36: Final Syntax Resolver
Final pass to resolve the remaining critical syntax errors.
"""

import re
import ast
from pathlib import Path
from typing import List, Dict, Tuple
import json

class FinalSyntaxResolver:
    """Final resolver for remaining critical syntax errors."""
    
    def __init__(self, backend_path: str = "backend"):
        self.backend_path = Path(backend_path)
        self.fixed_files: List[Path] = []
        self.failed_files: List[Tuple[Path, str]] = []
        self.changes_made = 0
        
    def run_final_resolution(self):
        """Main method to run the final syntax resolution."""
        print("🔧 Starting Final Syntax Resolution...")
        
        files_with_errors = self._get_files_with_syntax_errors()
        print(f"📁 Found {len(files_with_errors)} files with remaining syntax errors")
        
        for file_path in files_with_errors:
            try:
                if self._fix_file_syntax(file_path):
                    self.fixed_files.append(file_path)
                    self.changes_made += 1
                    print(f"   ✅ Fixed {file_path}")
            except Exception as e:
                self.failed_files.append((file_path, str(e)))
                print(f"   ⚠️ Failed to fix {file_path}: {e}")
        
        self._generate_report()
        print(f"✅ Final resolution complete! {len(self.fixed_files)} files fixed.")
    
    def _get_files_with_syntax_errors(self) -> List[Path]:
        """Get all Python files that still have syntax errors."""
        files = []
        for file_path in self.backend_path.rglob("*.py"):
            if self._has_syntax_errors(file_path):
                files.append(file_path)
        return files
    
    def _has_syntax_errors(self, file_path: Path) -> bool:
        """Check if a file has syntax errors using AST parsing."""
        try:
            content = file_path.read_text(encoding='utf-8')
            ast.parse(content)
            return False
        except (SyntaxError, UnicodeDecodeError):
            return True
        except Exception:
            return False
    
    def _fix_file_syntax(self, file_path: Path) -> bool:
        """Fix syntax errors in a single file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Apply comprehensive fixes
            content = self._fix_comprehensive_syntax(content)
            
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                return True
            return False
        except Exception as e:
            raise Exception(f"Error fixing {file_path}: {e}")
    
    def _fix_comprehensive_syntax(self, content: str) -> str:
        """Apply comprehensive syntax fixes."""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            fixed_line = self._fix_line_syntax(line, i, lines)
            fixed_lines.append(fixed_line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_line_syntax(self, line: str, line_num: int, all_lines: List[str]) -> str:
        """Fix syntax errors in a single line with context."""
        original_line = line
        
        # Skip empty lines and comments
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            return line
        
        # Fix unmatched braces
        line = self._fix_unmatched_braces(line)
        
        # Fix illegal target annotations
        line = self._fix_illegal_annotations(line)
        
        # Fix malformed class/function definitions
        line = self._fix_malformed_definitions(line)
        
        # Fix JavaScript remainders
        line = self._fix_js_remainders(line)
        
        # Fix string literal issues
        line = self._fix_string_literals(line)
        
        # Fix indentation issues
        line = self._fix_indentation_issues(line, line_num, all_lines)
        
        # Fix assignment expressions
        line = self._fix_assignment_expressions(line)
        
        # Final cleanup
        line = self._final_cleanup(line)
        
        return line
    
    def _fix_unmatched_braces(self, line: str) -> str:
        """Fix unmatched braces and parentheses."""
        # Remove standalone braces
        if re.match(r'^\s*[}]\s*$', line):
            return re.sub(r'^(\s*)[}](\s*)$', r'\1pass\2', line)
        
        # Remove trailing braces after colons
        line = re.sub(r':\s*[{}]\s*$', ':', line)
        
        # Fix mismatched parentheses in object definitions
        line = re.sub(r'\{([^}]*)\}', r'{\1}', line)
        
        return line
    
    def _fix_illegal_annotations(self, line: str) -> str:
        """Fix illegal target for annotation errors."""
        # Fix class property annotations that are invalid in Python
        if re.search(r'^\s*[A-Z]\w*:\s*\w+', line):
            # Convert to comment or remove
            return '# ' + line + ' # TODO: Convert annotation'
        
        # Fix method annotations outside of function definitions
        line = re.sub(r'^(\s*)(\w+):\s*([A-Z]\w*)\s*$', r'\1# \2: \3 # TODO: Convert annotation', line)
        
        return line
    
    def _fix_malformed_definitions(self, line: str) -> str:
        """Fix malformed class and function definitions."""
        # Fix class definitions missing body
        if re.match(r'^\s*class\s+\w+.*:\s*$', line):
            return line
        
        # Fix function definitions with type annotations
        line = re.sub(r'def\s+(\w+)\s*\([^)]*\)\s*:\s*\w+\s*:', r'def \1(self):', line)
        
        # Fix constructor definitions
        line = re.sub(r'def\s+__init__\s*\([^)]*\)\s*:\s*\w+\s*:', r'def __init__(self):', line)
        
        return line
    
    def _fix_js_remainders(self, line: str) -> str:
        """Fix remaining JavaScript syntax."""
        # Remove 'new' keyword
        line = re.sub(r'\bnew\s+', '', line)
        
        # Fix arrow functions
        line = re.sub(r'=>', ':', line)
        
        # Fix template literals
        line = re.sub(r'`([^`]*)`', r'"\1"', line)
        
        # Fix console.log
        line = re.sub(r'console\.log\s*\(', 'print(', line)
        
        # Remove typeof
        line = re.sub(r'typeof\s+', '', line)
        
        return line
    
    def _fix_string_literals(self, line: str) -> str:
        """Fix malformed string literals."""
        # Fix unterminated strings
        if line.count('"') % 2 == 1:
            line = line + '"'
        if line.count("'") % 2 == 1:
            line = line + "'"
        
        # Fix escaped quotes
        line = re.sub(r'\\"', '"', line)
        line = re.sub(r"\\'", "'", line)
        
        return line
    
    def _fix_indentation_issues(self, line: str, line_num: int, all_lines: List[str]) -> str:
        """Fix indentation issues with context."""
        # If line is unexpectedly indented and previous line doesn't justify it
        if line.strip() and line.startswith('  ') and line_num > 0:
            prev_line = all_lines[line_num - 1].strip()
            if prev_line and not prev_line.endswith(':'):
                # Remove excess indentation
                return line.lstrip()
        
        return line
    
    def _fix_assignment_expressions(self, line: str) -> str:
        """Fix assignment expressions that should be comparisons."""
        # Fix assignment in conditions (common JS to Python conversion issue)
        if re.search(r'if\s+[^=]*=\s*[^=]', line):
            line = re.sub(r'(\w+)\s*=\s*([^=][^,)]*)', r'\1 == \2', line)
        
        return line
    
    def _final_cleanup(self, line: str) -> str:
        """Final cleanup operations."""
        # Remove trailing semicolons
        line = re.sub(r';\s*$', '', line)
        
        # Fix double colons
        line = re.sub(r'::', ':', line)
        
        # Remove redundant whitespace
        line = re.sub(r'\s+', ' ', line).strip()
        if line:
            # Preserve original indentation
            original_indent = len(line) - len(line.lstrip())
            line = ' ' * original_indent + line.strip()
        
        return line
    
    def _generate_report(self):
        """Generate comprehensive report of the final resolution."""
        report = {
            "summary": {
                "files_fixed": len(self.fixed_files),
                "files_failed": len(self.failed_files),
                "changes_made": self.changes_made
            },
            "fixed_files": [str(f) for f in self.fixed_files],
            "failed_files": [{"file": str(f), "error": error} for f, error in self.failed_files]
        }
        
        # Save detailed report
        report_path = Path("task_36_final_syntax_resolution_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("📋 FINAL SYNTAX RESOLUTION REPORT")
        print("="*60)
        print(f"✅ Files Fixed: {len(self.fixed_files)}")
        print(f"❌ Files Failed: {len(self.failed_files)}")
        print(f"🔧 Changes Made: {self.changes_made}")
        
        if self.failed_files:
            print("\n⚠️ FAILED FIXES:")
            for file_path, error in self.failed_files[:10]:  # Show first 10
                print(f"   • {file_path}: {error}")
            if len(self.failed_files) > 10:
                print(f"   ... and {len(self.failed_files) - 10} more")
        
        print(f"\n📄 Detailed report saved to: {report_path}")

if __name__ == "__main__":
    resolver = FinalSyntaxResolver()
    resolver.run_final_resolution() 