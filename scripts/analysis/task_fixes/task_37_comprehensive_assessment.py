#!/usr/bin/env python3
"""
Task 37 Comprehensive Backend Systems Assessment
Performs comprehensive analysis on target systems under /backend/systems/ and /backend/tests/
"""

import os
import sys
import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict
import subprocess

class Task37Assessment:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.backend_root = self.project_root / "backend"
        self.systems_root = self.backend_root / "systems"
        self.tests_root = self.backend_root / "tests"
        
        self.results = {
            "assessment_summary": {},
            "structural_issues": {},
            "import_violations": {},
            "missing_implementations": {},
            "duplicate_tests": {},
            "orphan_dependencies": {},
            "errors_found": [],
            "recommendations": []
        }
    
    def run_comprehensive_analysis(self):
        """Run all assessment components"""
        print("=== Task 37 Comprehensive Backend Systems Assessment ===\n")
        
        # 1. Assessment and Error Resolution
        print("1. Running system analysis and error detection...")
        self.analyze_systems_for_errors()
        
        # 2. Structure and Organization Enforcement
        print("2. Checking structure and organization...")
        self.check_test_organization()
        self.find_duplicate_tests()
        
        # 3. Canonical Imports Enforcement
        print("3. Analyzing import compliance...")
        self.analyze_import_compliance()
        
        # 4. Module and Function Development
        print("4. Checking for duplication prevention...")
        self.check_module_duplication()
        
        # 5. Generate final report
        print("5. Generating assessment report...")
        self.generate_final_report()
    
    def analyze_systems_for_errors(self):
        """Analyze target systems for errors and compliance issues"""
        systems_analyzed = 0
        errors_found = 0
        
        for system_dir in self.systems_root.iterdir():
            if system_dir.is_dir() and not system_dir.name.startswith('__'):
                systems_analyzed += 1
                system_errors = self.analyze_single_system(system_dir)
                if system_errors:
                    errors_found += len(system_errors)
                    self.results["errors_found"].extend(system_errors)
        
        self.results["assessment_summary"]["systems_analyzed"] = systems_analyzed
        self.results["assessment_summary"]["errors_found"] = errors_found
    
    def analyze_single_system(self, system_dir: Path) -> List[Dict]:
        """Analyze a single system for errors and compliance"""
        errors = []
        system_name = system_dir.name
        
        # Check for required components
        required_components = ["models", "services", "repositories", "routers"]
        missing_components = []
        
        for component in required_components:
            component_file = system_dir / f"{component}.py"
            component_dir = system_dir / component
            
            if not (component_file.exists() or component_dir.exists()):
                missing_components.append(component)
        
        if missing_components:
            errors.append({
                "type": "missing_components",
                "system": system_name,
                "missing": missing_components,
                "severity": "high"
            })
        
        # Check Python syntax in all .py files
        for py_file in system_dir.rglob("*.py"):
            syntax_errors = self.check_python_syntax(py_file)
            if syntax_errors:
                errors.extend(syntax_errors)
        
        # Check for import issues
        import_errors = self.check_system_imports(system_dir)
        if import_errors:
            errors.extend(import_errors)
        
        return errors
    
    def check_python_syntax(self, file_path: Path) -> List[Dict]:
        """Check Python file for syntax errors"""
        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            ast.parse(content)
            
        except SyntaxError as e:
            errors.append({
                "type": "syntax_error",
                "file": str(file_path.relative_to(self.project_root)),
                "line": e.lineno,
                "message": str(e),
                "severity": "critical"
            })
        except Exception as e:
            errors.append({
                "type": "file_error", 
                "file": str(file_path.relative_to(self.project_root)),
                "message": str(e),
                "severity": "medium"
            })
        
        return errors
    
    def check_system_imports(self, system_dir: Path) -> List[Dict]:
        """Check system for import compliance issues"""
        errors = []
        system_name = system_dir.name
        
        for py_file in system_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find import statements
                import_lines = []
                for line_num, line in enumerate(content.split('\n'), 1):
                    line = line.strip()
                    if line.startswith(('import ', 'from ')) and not line.startswith('#'):
                        import_lines.append((line_num, line))
                
                # Check for non-canonical imports
                for line_num, import_line in import_lines:
                    if self.is_non_canonical_import(import_line, system_name):
                        errors.append({
                            "type": "non_canonical_import",
                            "file": str(py_file.relative_to(self.project_root)),
                            "line": line_num,
                            "import": import_line,
                            "system": system_name,
                            "severity": "medium"
                        })
            
            except Exception as e:
                errors.append({
                    "type": "import_analysis_error",
                    "file": str(py_file.relative_to(self.project_root)),
                    "message": str(e),
                    "severity": "low"
                })
        
        return errors
    
    def is_non_canonical_import(self, import_line: str, system_name: str) -> bool:
        """Check if import violates canonical backend.systems.* format"""
        # Skip standard library and external package imports
        if any(import_line.startswith(f'from {pkg}') or import_line.startswith(f'import {pkg}') 
               for pkg in ['os', 'sys', 'json', 'typing', 'datetime', 'pathlib', 'fastapi', 'pydantic', 'sqlalchemy']):
            return False
        
        # Check for imports from outside backend.systems
        if 'from backend.' in import_line and 'from backend.systems.' not in import_line:
            return True
        
        # Check for relative imports that don't follow canonical structure
        if import_line.startswith('from .') or import_line.startswith('from ..'):
            return True
        
        return False
    
    def check_test_organization(self):
        """Check test file organization and identify misplaced tests"""
        misplaced_tests = []
        test_structure_issues = []
        
        # Check for test files in system directories
        for system_dir in self.systems_root.iterdir():
            if system_dir.is_dir() and not system_dir.name.startswith('__'):
                test_dirs = list(system_dir.glob("test*"))
                for test_dir in test_dirs:
                    if test_dir.is_dir():
                        misplaced_tests.append({
                            "type": "misplaced_test_directory",
                            "location": str(test_dir.relative_to(self.project_root)),
                            "should_be": f"backend/tests/systems/{system_dir.name}/",
                            "severity": "high"
                        })
                
                # Check for individual test files
                test_files = list(system_dir.glob("test_*.py"))
                for test_file in test_files:
                    misplaced_tests.append({
                        "type": "misplaced_test_file",
                        "location": str(test_file.relative_to(self.project_root)),
                        "should_be": f"backend/tests/systems/{system_dir.name}/",
                        "severity": "high"
                    })
        
        # Verify canonical test structure exists
        canonical_test_dir = self.tests_root / "systems"
        if not canonical_test_dir.exists():
            test_structure_issues.append({
                "type": "missing_canonical_test_structure",
                "missing": str(canonical_test_dir.relative_to(self.project_root)),
                "severity": "critical"
            })
        
        self.results["structural_issues"]["misplaced_tests"] = misplaced_tests
        self.results["structural_issues"]["test_structure_issues"] = test_structure_issues
    
    def find_duplicate_tests(self):
        """Find duplicate test functions across the test suite"""
        test_functions = defaultdict(list)
        
        # Scan all test files
        for test_file in self.tests_root.rglob("test_*.py"):
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse and find test functions
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                        test_functions[node.name].append(str(test_file.relative_to(self.project_root)))
            
            except Exception as e:
                continue
        
        # Find duplicates
        duplicates = {name: files for name, files in test_functions.items() if len(files) > 1}
        self.results["duplicate_tests"] = duplicates
    
    def analyze_import_compliance(self):
        """Analyze import compliance across all systems"""
        non_canonical_imports = []
        orphan_dependencies = []
        
        for system_dir in self.systems_root.iterdir():
            if system_dir.is_dir() and not system_dir.name.startswith('__'):
                system_imports = self.get_system_imports(system_dir)
                
                for import_info in system_imports:
                    if self.is_orphan_dependency(import_info):
                        orphan_dependencies.append(import_info)
                    
                    if not self.is_canonical_import(import_info):
                        non_canonical_imports.append(import_info)
        
        self.results["import_violations"]["non_canonical"] = non_canonical_imports
        self.results["orphan_dependencies"] = orphan_dependencies
    
    def get_system_imports(self, system_dir: Path) -> List[Dict]:
        """Get all imports from a system directory"""
        imports = []
        
        for py_file in system_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for line_num, line in enumerate(content.split('\n'), 1):
                    line = line.strip()
                    if line.startswith(('import ', 'from ')) and not line.startswith('#'):
                        imports.append({
                            "file": str(py_file.relative_to(self.project_root)),
                            "line": line_num,
                            "import_statement": line,
                            "system": system_dir.name
                        })
            except Exception:
                continue
        
        return imports
    
    def is_orphan_dependency(self, import_info: Dict) -> bool:
        """Check if import references a non-existent module or utility outside canonical structure"""
        import_statement = import_info["import_statement"]
        
        # Check for imports from non-existent backend modules
        if "from backend." in import_statement and "from backend.systems." not in import_statement:
            module_parts = import_statement.split("from ")[1].split(" import")[0].strip()
            module_path = self.backend_root / module_parts.replace("backend.", "").replace(".", "/")
            
            if not module_path.exists() and not (module_path.parent / f"{module_path.name}.py").exists():
                return True
        
        return False
    
    def is_canonical_import(self, import_info: Dict) -> bool:
        """Check if import follows canonical backend.systems.* format"""
        import_statement = import_info["import_statement"]
        
        # Allow standard library and external imports
        standard_libs = ['os', 'sys', 'json', 'typing', 'datetime', 'pathlib', 'fastapi', 'pydantic', 'sqlalchemy']
        if any(f'import {lib}' in import_statement or f'from {lib}' in import_statement for lib in standard_libs):
            return True
        
        # Check backend imports
        if 'backend' in import_statement:
            return 'backend.systems.' in import_statement or 'backend.tests.' in import_statement
        
        # Relative imports are not canonical
        if import_statement.startswith('from .') or import_statement.startswith('from ..'):
            return False
        
        return True
    
    def check_module_duplication(self):
        """Check for duplicate function implementations across modules"""
        function_signatures = defaultdict(list)
        
        for system_dir in self.systems_root.iterdir():
            if system_dir.is_dir() and not system_dir.name.startswith('__'):
                for py_file in system_dir.rglob("*.py"):
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                signature = f"{node.name}({len(node.args.args)})"
                                function_signatures[signature].append({
                                    "file": str(py_file.relative_to(self.project_root)),
                                    "function": node.name,
                                    "line": node.lineno
                                })
                    except Exception:
                        continue
        
        # Find potential duplicates
        potential_duplicates = {sig: locs for sig, locs in function_signatures.items() if len(locs) > 1}
        self.results["missing_implementations"]["potential_duplicates"] = potential_duplicates
    
    def generate_final_report(self):
        """Generate final assessment report"""
        report = {
            "task_37_assessment": "COMPLETE",
            "timestamp": "2025-05-29",
            "summary": {
                "systems_analyzed": self.results["assessment_summary"].get("systems_analyzed", 0),
                "total_errors": len(self.results["errors_found"]),
                "structural_issues": len(self.results["structural_issues"].get("misplaced_tests", [])),
                "import_violations": len(self.results["import_violations"].get("non_canonical", [])),
                "duplicate_tests": len(self.results["duplicate_tests"]),
                "orphan_dependencies": len(self.results["orphan_dependencies"])
            },
            "detailed_results": self.results
        }
        
        # Generate recommendations
        recommendations = []
        
        if self.results["errors_found"]:
            recommendations.append("Fix syntax errors and missing components in systems")
        
        if self.results["structural_issues"].get("misplaced_tests"):
            recommendations.append("Relocate misplaced test files to /backend/tests/*")
        
        if self.results["import_violations"].get("non_canonical"):
            recommendations.append("Convert imports to canonical backend.systems.* format")
        
        if self.results["duplicate_tests"]:
            recommendations.append("Remove duplicate test functions")
        
        if self.results["orphan_dependencies"]:
            recommendations.append("Fix or remove orphan module dependencies")
        
        report["recommendations"] = recommendations
        
        # Save assessment results
        output_file = self.project_root / "task_37_assessment_results.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n=== Task 37 Assessment Results ===")
        print(f"Systems Analyzed: {report['summary']['systems_analyzed']}")
        print(f"Total Errors Found: {report['summary']['total_errors']}")
        print(f"Structural Issues: {report['summary']['structural_issues']}")
        print(f"Import Violations: {report['summary']['import_violations']}")
        print(f"Duplicate Tests: {report['summary']['duplicate_tests']}")
        print(f"Orphan Dependencies: {report['summary']['orphan_dependencies']}")
        
        if recommendations:
            print(f"\nRecommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        
        print(f"\nDetailed results saved to: {output_file}")
        
        return report

def main():
    """Main execution function"""
    assessment = Task37Assessment()
    results = assessment.run_comprehensive_analysis()
    return results

if __name__ == "__main__":
    main() 