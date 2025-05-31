#!/usr/bin/env python3
"""
Task 57: Remove Legacy Code and Technical Debt

This script implements comprehensive cleanup according to the Backend Development Protocol:
1. TODO comment analysis and implementation/removal
2. Deprecated function elimination
3. Unused import cleanup
4. Duplicate implementation detection
5. Documentation updates
"""

import os
import re
import ast
import sys
import json
from typing import List, Dict, Set, Tuple
from pathlib import Path
import subprocess

class LegacyCodeCleaner:
    def __init__(self, backend_path: str = "backend/systems"):
        self.backend_path = Path(backend_path)
        self.issues = {
            "todo_comments": [],
            "deprecated_functions": [],
            "unused_imports": [],
            "duplicate_implementations": [],
            "documentation_updates": []
        }
        
    def analyze_todo_comments(self) -> List[Dict]:
        """Find and categorize TODO comments for implementation or removal."""
        todo_pattern = re.compile(r'#\s*TODO:?\s*(.+)', re.IGNORECASE)
        todos = []
        
        for file_path in self.backend_path.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    match = todo_pattern.search(line)
                    if match:
                        todos.append({
                            "file": str(file_path),
                            "line": i,
                            "comment": match.group(1).strip(),
                            "full_line": line.strip(),
                            "context": self._get_context(lines, i-1, 3)
                        })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        self.issues["todo_comments"] = todos
        return todos
    
    def analyze_deprecated_functions(self) -> List[Dict]:
        """Find deprecated function calls and implementations."""
        deprecated_items = []
        
        # Patterns for deprecated code
        patterns = [
            (r'@deprecated', "Deprecated decorator usage"),
            (r'\.deprecated\(', "Deprecated method call"),
            (r'warnings\.warn.*deprecated', "Deprecation warning"),
            (r'#.*deprecated', "Deprecated comment"),
            (r'DEPRECATED.*=', "Deprecated constant"),
        ]
        
        for file_path in self.backend_path.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                for pattern, description in patterns:
                    for i, line in enumerate(lines, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            deprecated_items.append({
                                "file": str(file_path),
                                "line": i,
                                "pattern": pattern,
                                "description": description,
                                "full_line": line.strip(),
                                "context": self._get_context(lines, i-1, 2)
                            })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        self.issues["deprecated_functions"] = deprecated_items
        return deprecated_items
    
    def analyze_unused_imports(self) -> List[Dict]:
        """Find unused imports in Python files."""
        unused_imports = []
        
        for file_path in self.backend_path.rglob("*.py"):
            try:
                unused = self._find_unused_imports_in_file(file_path)
                if unused:
                    unused_imports.append({
                        "file": str(file_path),
                        "unused_imports": unused
                    })
            except Exception as e:
                print(f"Error analyzing imports in {file_path}: {e}")
        
        self.issues["unused_imports"] = unused_imports
        return unused_imports
    
    def _find_unused_imports_in_file(self, file_path: Path) -> List[str]:
        """Find unused imports in a specific file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Extract all imports
            imports = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        name = alias.asname if alias.asname else alias.name.split('.')[0]
                        imports[name] = alias.name
                elif isinstance(node, ast.ImportFrom):
                    if node.module:  # Skip relative imports without module
                        for alias in node.names:
                            name = alias.asname if alias.asname else alias.name
                            imports[name] = f'{node.module}.{alias.name}'
            
            # Check usage (simplified heuristic)
            unused = []
            for name, full_name in imports.items():
                if name != '*' and name not in ['__all__', '__version__']:
                    # Remove import statements from content for checking
                    content_without_imports = re.sub(
                        rf'^\s*(from\s+.*\s+)?import\s+.*{re.escape(name)}.*$',
                        '', content, flags=re.MULTILINE
                    )
                    
                    # Check if name is used
                    if not re.search(r'\b' + re.escape(name) + r'\b', content_without_imports):
                        unused.append(full_name)
            
            return unused
        except Exception:
            return []
    
    def analyze_duplicate_implementations(self) -> List[Dict]:
        """Find duplicate function implementations across files."""
        duplicates = []
        function_signatures = {}
        
        for file_path in self.backend_path.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Create signature hash
                        signature = f"{node.name}({len(node.args.args)})"
                        
                        if signature in function_signatures:
                            duplicates.append({
                                "signature": signature,
                                "files": [function_signatures[signature], str(file_path)],
                                "function_name": node.name
                            })
                        else:
                            function_signatures[signature] = str(file_path)
                            
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
        
        self.issues["duplicate_implementations"] = duplicates
        return duplicates
    
    def _get_context(self, lines: List[str], line_index: int, context_size: int = 2) -> List[str]:
        """Get context lines around a specific line."""
        start = max(0, line_index - context_size)
        end = min(len(lines), line_index + context_size + 1)
        return [line.rstrip() for line in lines[start:end]]
    
    def implement_todo_fixes(self) -> Dict:
        """Automatically implement or remove TODO comments where possible."""
        fixes_applied = []
        
        for todo in self.issues["todo_comments"]:
            file_path = Path(todo["file"])
            comment = todo["comment"].lower()
            
            # Categorize TODO types
            if any(keyword in comment for keyword in ["implement", "add", "create"]):
                # Implementation required - mark for manual review
                fixes_applied.append({
                    "file": str(file_path),
                    "line": todo["line"],
                    "action": "MANUAL_IMPLEMENTATION_REQUIRED",
                    "comment": todo["comment"]
                })
            elif any(keyword in comment for keyword in ["remove", "delete", "cleanup"]):
                # Removal required - can be automated
                self._remove_todo_line(file_path, todo["line"])
                fixes_applied.append({
                    "file": str(file_path),
                    "line": todo["line"],
                    "action": "REMOVED",
                    "comment": todo["comment"]
                })
            elif any(keyword in comment for keyword in ["fix", "update", "correct"]):
                # Fix required - mark for manual review
                fixes_applied.append({
                    "file": str(file_path),
                    "line": todo["line"],
                    "action": "MANUAL_FIX_REQUIRED",
                    "comment": todo["comment"]
                })
        
        return {"fixes_applied": fixes_applied}
    
    def _remove_todo_line(self, file_path: Path, line_number: int):
        """Remove a TODO comment line from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if 0 <= line_number - 1 < len(lines):
                line = lines[line_number - 1]
                # Only remove if it's just a TODO comment
                if re.match(r'^\s*#\s*TODO', line.strip(), re.IGNORECASE):
                    lines.pop(line_number - 1)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
        except Exception as e:
            print(f"Error removing TODO line from {file_path}: {e}")
    
    def remove_unused_imports(self) -> Dict:
        """Remove unused imports from files."""
        removals = []
        
        for item in self.issues["unused_imports"]:
            file_path = Path(item["file"])
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                modified = False
                for unused_import in item["unused_imports"]:
                    # Remove the import line
                    patterns = [
                        rf'^import\s+{re.escape(unused_import)}\s*$',
                        rf'^from\s+.*\s+import\s+.*{re.escape(unused_import.split(".")[-1])}.*$'
                    ]
                    
                    for pattern in patterns:
                        new_content = re.sub(pattern, '', content, flags=re.MULTILINE)
                        if new_content != content:
                            content = new_content
                            modified = True
                            removals.append({
                                "file": str(file_path),
                                "removed_import": unused_import
                            })
                
                if modified:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
            except Exception as e:
                print(f"Error removing imports from {file_path}: {e}")
        
        return {"removals": removals}
    
    def clean_deprecated_code(self) -> Dict:
        """Clean up deprecated code elements."""
        cleaned = []
        
        for item in self.issues["deprecated_functions"]:
            file_path = Path(item["file"])
            
            # Handle specific deprecated patterns
            if "legacy_adapter.py" in str(file_path):
                # Mark entire legacy adapter for removal
                cleaned.append({
                    "file": str(file_path),
                    "action": "ENTIRE_FILE_DEPRECATED",
                    "recommendation": "Remove legacy adapter after verifying no dependencies"
                })
            elif "@deprecated" in item["full_line"]:
                cleaned.append({
                    "file": str(file_path),
                    "line": item["line"],
                    "action": "DEPRECATED_FUNCTION_FOUND",
                    "recommendation": "Remove or replace deprecated function"
                })
        
        return {"cleaned": cleaned}
    
    def generate_report(self) -> Dict:
        """Generate comprehensive cleanup report."""
        return {
            "summary": {
                "todo_comments": len(self.issues["todo_comments"]),
                "deprecated_functions": len(self.issues["deprecated_functions"]),
                "unused_imports": sum(len(item["unused_imports"]) for item in self.issues["unused_imports"]),
                "duplicate_implementations": len(self.issues["duplicate_implementations"]),
                "files_analyzed": len(list(self.backend_path.rglob("*.py")))
            },
            "detailed_issues": self.issues,
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate cleanup recommendations."""
        recommendations = []
        
        if self.issues["todo_comments"]:
            recommendations.append("Review and implement TODO comments or remove if obsolete")
        
        if self.issues["deprecated_functions"]:
            recommendations.append("Remove deprecated functions and update callers")
        
        if self.issues["unused_imports"]:
            recommendations.append("Remove unused imports to clean up code")
        
        if self.issues["duplicate_implementations"]:
            recommendations.append("Consolidate duplicate function implementations")
        
        recommendations.extend([
            "Update imports to use canonical backend.systems.* format",
            "Ensure all tests are in /backend/tests/ directory",
            "Verify all modules follow Development_Bible.md standards"
        ])
        
        return recommendations

def main():
    """Main execution function."""
    print("Task 57: Legacy Code and Technical Debt Cleanup")
    print("=" * 50)
    
    cleaner = LegacyCodeCleaner()
    
    # Run analysis
    print("1. Analyzing TODO comments...")
    todos = cleaner.analyze_todo_comments()
    print(f"   Found {len(todos)} TODO comments")
    
    print("2. Analyzing deprecated functions...")
    deprecated = cleaner.analyze_deprecated_functions()
    print(f"   Found {len(deprecated)} deprecated items")
    
    print("3. Analyzing unused imports...")
    unused = cleaner.analyze_unused_imports()
    total_unused = sum(len(item["unused_imports"]) for item in unused)
    print(f"   Found {total_unused} unused imports in {len(unused)} files")
    
    print("4. Analyzing duplicate implementations...")
    duplicates = cleaner.analyze_duplicate_implementations()
    print(f"   Found {len(duplicates)} potential duplicates")
    
    # Apply automatic fixes
    print("\n5. Applying automatic fixes...")
    
    # Remove unused imports
    import_removals = cleaner.remove_unused_imports()
    print(f"   Removed {len(import_removals['removals'])} unused imports")
    
    # Handle TODOs
    todo_fixes = cleaner.implement_todo_fixes()
    print(f"   Processed {len(todo_fixes['fixes_applied'])} TODO items")
    
    # Clean deprecated code
    deprecated_cleanup = cleaner.clean_deprecated_code()
    print(f"   Identified {len(deprecated_cleanup['cleaned'])} deprecated items for cleanup")
    
    # Generate final report
    report = cleaner.generate_report()
    
    # Save report
    with open("backend/task57_cleanup_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n6. Cleanup Summary:")
    print(f"   - TODO comments: {report['summary']['todo_comments']}")
    print(f"   - Deprecated functions: {report['summary']['deprecated_functions']}")
    print(f"   - Unused imports: {report['summary']['unused_imports']}")
    print(f"   - Duplicate implementations: {report['summary']['duplicate_implementations']}")
    print(f"   - Files analyzed: {report['summary']['files_analyzed']}")
    
    print("\nReport saved to: backend/task57_cleanup_report.json")
    
    return report

if __name__ == "__main__":
    main() 