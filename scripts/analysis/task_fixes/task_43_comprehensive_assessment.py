#!/usr/bin/env python3
"""
Task 43 Comprehensive Assessment Script
Analyzes backend systems and tests to identify all issues requiring resolution.
"""

import os
import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class BackendSystemsAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backend_systems = self.project_root / "backend" / "systems"
        self.backend_tests = self.project_root / "backend" / "tests" / "systems"
        
        self.issues = {
            "import_errors": [],
            "missing_modules": [],
            "test_failures": [],
            "structural_issues": [],
            "duplicate_functions": [],
            "coverage_gaps": []
        }
        
    def analyze_all(self):
        """Run comprehensive analysis of backend systems."""
        print("🔍 Starting comprehensive backend systems analysis...")
        
        self.analyze_import_structure()
        self.analyze_test_structure()
        self.analyze_missing_modules()
        self.analyze_code_duplication()
        self.analyze_test_coverage()
        self.analyze_canonical_imports()
        
        self.generate_report()
        
    def analyze_import_structure(self):
        """Analyze import structure for canonical compliance."""
        print("📦 Analyzing import structure...")
        
        for py_file in self.backend_systems.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for non-canonical imports
                non_canonical_imports = re.findall(
                    r'from\s+(?!backend\.systems\.)([^.\s]+(?:\.[^.\s]+)*)\s+import',
                    content
                )
                
                for imp in non_canonical_imports:
                    if not imp.startswith(('typing', 'datetime', 'uuid', 'enum', 'dataclasses', 'abc', 'asyncio', 'json', 'logging', 'os', 'sys', 'pathlib', 'collections', 're', 'functools', 'itertools')):
                        self.issues["import_errors"].append({
                            "file": str(py_file.relative_to(self.project_root)),
                            "import": imp,
                            "type": "non_canonical"
                        })
                        
            except Exception as e:
                self.issues["import_errors"].append({
                    "file": str(py_file.relative_to(self.project_root)),
                    "error": str(e),
                    "type": "parse_error"
                })
                
    def analyze_test_structure(self):
        """Analyze test structure and identify issues."""
        print("🧪 Analyzing test structure...")
        
        for test_file in self.backend_tests.rglob("test_*.py"):
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for placeholder tests
                if "assert True" in content:
                    self.issues["test_failures"].append({
                        "file": str(test_file.relative_to(self.project_root)),
                        "issue": "placeholder_test",
                        "details": "Contains 'assert True' placeholder"
                    })
                    
                # Check for import failures
                import_lines = re.findall(r'from\s+([^\s]+)\s+import', content)
                for imp in import_lines:
                    if imp.startswith('backend.systems'):
                        # Check if the module exists
                        module_path = imp.replace('.', '/')
                        expected_file = self.project_root / f"{module_path}.py"
                        expected_init = self.project_root / f"{module_path}/__init__.py"
                        
                        if not expected_file.exists() and not expected_init.exists():
                            self.issues["missing_modules"].append({
                                "test_file": str(test_file.relative_to(self.project_root)),
                                "missing_module": imp,
                                "expected_path": str(expected_file.relative_to(self.project_root))
                            })
                            
            except Exception as e:
                self.issues["test_failures"].append({
                    "file": str(test_file.relative_to(self.project_root)),
                    "issue": "parse_error",
                    "details": str(e)
                })
                
    def analyze_missing_modules(self):
        """Identify missing modules that tests expect."""
        print("📂 Analyzing missing modules...")
        
        # Check for missing shared modules
        shared_path = self.backend_systems / "shared"
        expected_shared_modules = [
            "database/__init__.py",
            "database/session.py",
            "events/__init__.py", 
            "events/dispatcher.py"
        ]
        
        for module in expected_shared_modules:
            module_path = shared_path / module
            if not module_path.exists():
                self.issues["missing_modules"].append({
                    "module": f"backend.systems.shared.{module.replace('/', '.').replace('.py', '')}",
                    "path": str(module_path.relative_to(self.project_root)),
                    "reason": "Expected by test infrastructure"
                })
                
    def analyze_code_duplication(self):
        """Analyze code duplication across systems."""
        print("🔄 Analyzing code duplication...")
        
        function_signatures = defaultdict(list)
        
        for py_file in self.backend_systems.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        signature = f"{node.name}({len(node.args.args)} args)"
                        function_signatures[signature].append(str(py_file.relative_to(self.project_root)))
                        
            except Exception:
                continue
                
        # Find duplicates
        for signature, files in function_signatures.items():
            if len(files) > 1:
                self.issues["duplicate_functions"].append({
                    "signature": signature,
                    "files": files,
                    "count": len(files)
                })
                
    def analyze_test_coverage(self):
        """Analyze test coverage gaps."""
        print("📊 Analyzing test coverage...")
        
        # Find all Python modules in systems
        system_modules = []
        for py_file in self.backend_systems.rglob("*.py"):
            if "__pycache__" in str(py_file) or py_file.name == "__init__.py":
                continue
            system_modules.append(str(py_file.relative_to(self.project_root)))
            
        # Find all test files
        test_files = []
        for test_file in self.backend_tests.rglob("test_*.py"):
            test_files.append(str(test_file.relative_to(self.project_root)))
            
        # Simple heuristic: check if module has corresponding test
        for module in system_modules:
            module_name = Path(module).stem
            system_name = module.split('/')[2]  # backend/systems/SYSTEM_NAME/...
            
            # Look for test file
            expected_test_patterns = [
                f"backend/tests/systems/{system_name}/test_{module_name}.py",
                f"backend/tests/systems/{system_name}/test_{module_name}_*.py"
            ]
            
            has_test = False
            for pattern in expected_test_patterns:
                if any(pattern.replace('*', '') in test_file for test_file in test_files):
                    has_test = True
                    break
                    
            if not has_test:
                self.issues["coverage_gaps"].append({
                    "module": module,
                    "system": system_name,
                    "expected_test": expected_test_patterns[0]
                })
                
    def analyze_canonical_imports(self):
        """Analyze canonical import compliance."""
        print("🎯 Analyzing canonical import compliance...")
        
        for py_file in self.backend_systems.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find all imports
                imports = re.findall(r'from\s+([^\s]+)\s+import|import\s+([^\s,]+)', content)
                
                for imp_tuple in imports:
                    imp = imp_tuple[0] or imp_tuple[1]
                    
                    # Check if it's a backend import that's not canonical
                    if 'backend' in imp and not imp.startswith('backend.systems.'):
                        self.issues["import_errors"].append({
                            "file": str(py_file.relative_to(self.project_root)),
                            "import": imp,
                            "type": "non_canonical_backend"
                        })
                        
            except Exception:
                continue
                
    def generate_report(self):
        """Generate comprehensive analysis report."""
        print("\n" + "="*80)
        print("📋 TASK 43 COMPREHENSIVE ASSESSMENT REPORT")
        print("="*80)
        
        total_issues = sum(len(issues) for issues in self.issues.values())
        print(f"🚨 TOTAL ISSUES FOUND: {total_issues}")
        
        for category, issues in self.issues.items():
            if issues:
                print(f"\n🔸 {category.upper().replace('_', ' ')} ({len(issues)} issues):")
                
                for i, issue in enumerate(issues[:5], 1):  # Show first 5 of each type
                    if category == "import_errors":
                        print(f"  {i}. {issue['file']}: {issue.get('import', issue.get('error', 'Unknown'))}")
                    elif category == "missing_modules":
                        print(f"  {i}. Missing: {issue.get('module', issue.get('missing_module', 'Unknown'))}")
                    elif category == "test_failures":
                        print(f"  {i}. {issue['file']}: {issue['issue']}")
                    elif category == "duplicate_functions":
                        print(f"  {i}. {issue['signature']} in {issue['count']} files")
                    elif category == "coverage_gaps":
                        print(f"  {i}. {issue['module']} (no test found)")
                    else:
                        print(f"  {i}. {issue}")
                        
                if len(issues) > 5:
                    print(f"  ... and {len(issues) - 5} more")
                    
        print(f"\n🎯 PRIORITY ACTIONS NEEDED:")
        print(f"1. Fix {len(self.issues['import_errors'])} import structure issues")
        print(f"2. Create {len(self.issues['missing_modules'])} missing modules")
        print(f"3. Resolve {len(self.issues['test_failures'])} test infrastructure issues")
        print(f"4. Address {len(self.issues['duplicate_functions'])} code duplication instances")
        print(f"5. Add tests for {len(self.issues['coverage_gaps'])} uncovered modules")
        
        print(f"\n✅ NEXT STEPS:")
        print(f"1. Run comprehensive fix script to resolve critical issues")
        print(f"2. Implement missing infrastructure modules")
        print(f"3. Fix canonical import violations")
        print(f"4. Replace placeholder test logic")
        print(f"5. Validate all systems integration")

if __name__ == "__main__":
    project_root = "/Users/Sharrone/Dreamforge"
    analyzer = BackendSystemsAnalyzer(project_root)
    analyzer.analyze_all() 