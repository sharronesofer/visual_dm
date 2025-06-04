#!/usr/bin/env python3
"""
Task 59: Expand Unit Tests for New Modular Structure
Backend Development Protocol Implementation

This script performs systematic assessment and remediation according to:
- Assessment and Error Resolution
- Structure and Organization Enforcement  
- Canonical Imports Enforcement
- Achievement of ≥90% test coverage
"""

import os
import sys
import json
import subprocess
import ast
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import re

class Task59AssessmentRemediation:
    def __init__(self, backend_root: str = "/Users/Sharrone/Dreamforge/backend"):
        self.backend_root = Path(backend_root)
        self.systems_root = self.backend_root / "systems"
        self.tests_root = self.backend_root / "tests"
        self.issues_found = defaultdict(list)
        self.remediation_actions = []
        self.coverage_data = {}
        
    def run_comprehensive_assessment(self):
        """Run complete assessment according to Backend Development Protocol"""
        print("=== Task 59: Backend Development Protocol Assessment ===")
        
        # Phase 1: Assessment and Error Resolution
        print("\n1. Running Assessment and Error Resolution...")
        self.assess_parsing_errors()
        self.assess_import_structure()
        self.assess_missing_implementations()
        
        # Phase 2: Structure and Organization Enforcement
        print("\n2. Running Structure and Organization Enforcement...")
        self.enforce_test_organization()
        self.identify_duplicate_tests()
        self.validate_canonical_organization()
        
        # Phase 3: Canonical Imports Enforcement  
        print("\n3. Running Canonical Imports Enforcement...")
        self.enforce_canonical_imports()
        self.eliminate_orphan_dependencies()
        
        # Phase 4: Coverage Analysis
        print("\n4. Running Coverage Analysis...")
        self.analyze_current_coverage()
        self.identify_missing_tests()
        
        # Generate comprehensive report
        self.generate_assessment_report()
        
        return self.issues_found, self.remediation_actions
    
    def assess_parsing_errors(self):
        """Identify and categorize Python parsing errors"""
        print("  Assessing parsing errors...")
        
        parsing_errors = []
        for python_file in self.systems_root.rglob("*.py"):
            try:
                with open(python_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    ast.parse(content)
            except SyntaxError as e:
                parsing_errors.append({
                    'file': str(python_file),
                    'error': str(e),
                    'line': e.lineno if hasattr(e, 'lineno') else None
                })
            except Exception as e:
                parsing_errors.append({
                    'file': str(python_file),
                    'error': f"Parse error: {str(e)}",
                    'line': None
                })
        
        if parsing_errors:
            self.issues_found['parsing_errors'] = parsing_errors
            self.remediation_actions.append("Fix syntax errors in Python files")
            
        print(f"    Found {len(parsing_errors)} parsing errors")
        return parsing_errors
    
    def assess_import_structure(self):
        """Assess import structure and identify non-canonical imports"""
        print("  Assessing import structure...")
        
        non_canonical_imports = []
        relative_imports = []
        
        for python_file in self.systems_root.rglob("*.py"):
            try:
                with open(python_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for relative imports
                relative_pattern = r'from\s+\.+\w*\s+import|import\s+\.+\w*'
                if re.search(relative_pattern, content):
                    relative_imports.append(str(python_file))
                
                # Check for non-canonical backend imports
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if ('import' in line and 
                        'backend' in line and 
                        not line.strip().startswith('#') and
                        'backend.systems.' not in line):
                        non_canonical_imports.append({
                            'file': str(python_file),
                            'line': i,
                            'content': line.strip()
                        })
                        
            except Exception as e:
                self.issues_found['import_analysis_errors'].append({
                    'file': str(python_file),
                    'error': str(e)
                })
        
        if relative_imports:
            self.issues_found['relative_imports'] = relative_imports
            self.remediation_actions.append("Convert relative imports to absolute imports")
            
        if non_canonical_imports:
            self.issues_found['non_canonical_imports'] = non_canonical_imports
            self.remediation_actions.append("Convert imports to canonical backend.systems.* format")
            
        print(f"    Found {len(relative_imports)} files with relative imports")
        print(f"    Found {len(non_canonical_imports)} non-canonical import statements")
        
        return relative_imports, non_canonical_imports
    
    def assess_missing_implementations(self):
        """Identify missing implementations that should exist per Development_Bible.md"""
        print("  Assessing missing implementations...")
        
        # Check for placeholder implementations, TODOs, and NotImplementedError
        missing_implementations = []
        
        for python_file in self.systems_root.rglob("*.py"):
            try:
                with open(python_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for i, line in enumerate(lines, 1):
                    line_lower = line.lower().strip()
                    if (('todo' in line_lower or 
                         'fixme' in line_lower or
                         'notimplementederror' in line_lower or
                         'raise NotImplementedError' in line or
                         'pass  # TODO' in line) and
                        not line.strip().startswith('#')):
                        missing_implementations.append({
                            'file': str(python_file),
                            'line': i,
                            'content': line.strip(),
                            'type': 'missing_implementation'
                        })
                        
            except Exception as e:
                continue
                
        if missing_implementations:
            self.issues_found['missing_implementations'] = missing_implementations
            self.remediation_actions.append("Implement missing functionality per Development_Bible.md")
            
        print(f"    Found {len(missing_implementations)} missing implementations")
        return missing_implementations
    
    def enforce_test_organization(self):
        """Enforce proper test organization under /backend/tests/"""
        print("  Enforcing test organization...")
        
        misplaced_tests = []
        
        # Find test files in /backend/systems/
        for test_file in self.systems_root.rglob("test*.py"):
            misplaced_tests.append(str(test_file))
            
        # Find test directories in /backend/systems/
        for test_dir in self.systems_root.rglob("test*"):
            if test_dir.is_dir():
                misplaced_tests.append(str(test_dir))
                
        if misplaced_tests:
            self.issues_found['misplaced_tests'] = misplaced_tests
            self.remediation_actions.append("Move test files from /backend/systems/ to /backend/tests/")
            
        print(f"    Found {len(misplaced_tests)} misplaced test files/directories")
        return misplaced_tests
    
    def identify_duplicate_tests(self):
        """Identify duplicate test files and functions"""
        print("  Identifying duplicate tests...")
        
        test_functions = defaultdict(list)
        test_files = defaultdict(list)
        
        # Collect all test functions
        for test_file in self.tests_root.rglob("test*.py"):
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                        test_functions[node.name].append(str(test_file))
                        
                # Track file names
                file_name = test_file.name
                test_files[file_name].append(str(test_file))
                        
            except Exception as e:
                continue
        
        # Find duplicates
        duplicate_functions = {name: files for name, files in test_functions.items() if len(files) > 1}
        duplicate_files = {name: files for name, files in test_files.items() if len(files) > 1}
        
        if duplicate_functions:
            self.issues_found['duplicate_test_functions'] = duplicate_functions
            
        if duplicate_files:
            self.issues_found['duplicate_test_files'] = duplicate_files
            self.remediation_actions.append("Remove duplicate test files")
            
        print(f"    Found {len(duplicate_functions)} duplicate test functions")
        print(f"    Found {len(duplicate_files)} duplicate test files")
        
        return duplicate_functions, duplicate_files
    
    def validate_canonical_organization(self):
        """Validate that code follows canonical /backend/systems/ organization"""
        print("  Validating canonical organization...")
        
        organization_issues = []
        
        # Check for proper system directory structure
        expected_structure = {
            'models', 'services', 'repositories', 'routers', 'schemas', 'utils'
        }
        
        for system_dir in self.systems_root.iterdir():
            if system_dir.is_dir() and not system_dir.name.startswith('_'):
                system_structure = {item.name for item in system_dir.iterdir() if item.is_dir()}
                
                # Check if system has at least one expected component
                if not system_structure.intersection(expected_structure):
                    organization_issues.append({
                        'system': system_dir.name,
                        'issue': 'Missing standard directory structure',
                        'expected': list(expected_structure),
                        'found': list(system_structure)
                    })
        
        if organization_issues:
            self.issues_found['organization_issues'] = organization_issues
            self.remediation_actions.append("Reorganize systems to follow canonical structure")
            
        print(f"    Found {len(organization_issues)} organization issues")
        return organization_issues
    
    def enforce_canonical_imports(self):
        """Enforce canonical backend.systems.* import format"""
        print("  Enforcing canonical imports...")
        
        # This will be detailed in the remediation phase
        canonical_import_violations = []
        
        # Scan all Python files for import violations
        for python_file in self.systems_root.rglob("*.py"):
            try:
                with open(python_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for i, line in enumerate(lines, 1):
                    if 'import' in line and not line.strip().startswith('#'):
                        # Check for non-canonical patterns
                        if ('from systems.' in line or 
                            'import systems.' in line or
                            ('from .' in line and 'import' in line)):
                            canonical_import_violations.append({
                                'file': str(python_file),
                                'line': i,
                                'content': line.strip()
                            })
                            
            except Exception:
                continue
        
        if canonical_import_violations:
            self.issues_found['canonical_import_violations'] = canonical_import_violations
            self.remediation_actions.append("Fix non-canonical import statements")
            
        print(f"    Found {len(canonical_import_violations)} canonical import violations")
        return canonical_import_violations
    
    def eliminate_orphan_dependencies(self):
        """Identify and eliminate orphan dependencies"""
        print("  Identifying orphan dependencies...")
        
        orphan_dependencies = []
        
        # Look for imports pointing outside /backend/systems/
        for python_file in self.systems_root.rglob("*.py"):
            try:
                with open(python_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for i, line in enumerate(lines, 1):
                    if 'import' in line and not line.strip().startswith('#'):
                        # Check for external references that should be internal
                        if any(pattern in line for pattern in [
                            'from utils import',
                            'import utils.',
                            'from shared import',
                            'import shared.'
                        ]) and 'backend.systems' not in line:
                            orphan_dependencies.append({
                                'file': str(python_file),
                                'line': i,
                                'content': line.strip()
                            })
                            
            except Exception:
                continue
        
        if orphan_dependencies:
            self.issues_found['orphan_dependencies'] = orphan_dependencies
            self.remediation_actions.append("Eliminate orphan dependencies")
            
        print(f"    Found {len(orphan_dependencies)} orphan dependencies")
        return orphan_dependencies
    
    def analyze_current_coverage(self):
        """Analyze current test coverage"""
        print("  Analyzing current coverage...")
        
        try:
            # Run coverage analysis on a subset first to avoid errors
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                '--co', '-q'
            ], cwd=self.backend_root, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Count tests
                lines = result.stdout.strip().split('\n')
                test_count = len([line for line in lines if '::' in line])
                self.coverage_data['total_tests'] = test_count
            else:
                self.coverage_data['collection_errors'] = result.stderr
                
        except Exception as e:
            self.coverage_data['analysis_error'] = str(e)
            
        print(f"    Coverage analysis completed")
        return self.coverage_data
    
    def identify_missing_tests(self):
        """Identify modules missing comprehensive tests"""
        print("  Identifying missing tests...")
        
        missing_tests = []
        
        # Get all Python modules in systems
        all_modules = list(self.systems_root.rglob("*.py"))
        
        # Get all test files
        test_files = set()
        for test_file in self.tests_root.rglob("test*.py"):
            test_files.add(test_file.name)
            
        # Check for missing test files
        for module in all_modules:
            if module.name != '__init__.py':
                expected_test_name = f"test_{module.name}"
                if expected_test_name not in test_files:
                    missing_tests.append({
                        'module': str(module),
                        'expected_test': expected_test_name
                    })
        
        if missing_tests:
            self.issues_found['missing_tests'] = missing_tests[:50]  # Limit output
            self.remediation_actions.append("Create missing test files")
            
        print(f"    Found {len(missing_tests)} modules without corresponding tests")
        return missing_tests
    
    def generate_assessment_report(self):
        """Generate comprehensive assessment report"""
        report_path = self.backend_root / "task59_assessment_report.json"
        
        report = {
            'task': 'Task 59: Expand Unit Tests for New Modular Structure',
            'timestamp': subprocess.run(['date'], capture_output=True, text=True).stdout.strip(),
            'assessment_summary': {
                'total_issues_categories': len(self.issues_found),
                'total_remediation_actions': len(self.remediation_actions),
                'critical_issues': self.identify_critical_issues()
            },
            'issues_found': dict(self.issues_found),
            'remediation_actions': self.remediation_actions,
            'coverage_data': self.coverage_data,
            'next_steps': self.generate_next_steps()
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n=== Assessment Report Generated: {report_path} ===")
        print(f"Issues Categories: {len(self.issues_found)}")
        print(f"Remediation Actions: {len(self.remediation_actions)}")
        
        return report
    
    def identify_critical_issues(self):
        """Identify the most critical issues that must be fixed first"""
        critical = []
        
        if 'parsing_errors' in self.issues_found:
            critical.append("Parsing errors must be fixed before any testing")
            
        if 'canonical_import_violations' in self.issues_found:
            critical.append("Import structure violations prevent proper testing")
            
        if 'misplaced_tests' in self.issues_found:
            critical.append("Test organization violations")
            
        return critical
    
    def generate_next_steps(self):
        """Generate prioritized next steps"""
        return [
            "1. Fix all parsing errors to enable test execution",
            "2. Reorganize test files to /backend/tests/ structure", 
            "3. Convert all imports to canonical backend.systems.* format",
            "4. Implement missing functionality per Development_Bible.md",
            "5. Create comprehensive unit tests for modular components",
            "6. Achieve ≥90% test coverage across all systems",
            "7. Validate cross-system integration and API contracts"
        ]

def main():
    """Main execution function"""
    assessor = Task59AssessmentRemediation()
    issues, actions = assessor.run_comprehensive_assessment()
    
    print(f"\n=== Task 59 Assessment Complete ===")
    print(f"Found {len(issues)} issue categories")
    print(f"Generated {len(actions)} remediation actions")
    print("\nRefer to task59_assessment_report.json for detailed findings")
    
    return issues, actions

if __name__ == "__main__":
    main() 