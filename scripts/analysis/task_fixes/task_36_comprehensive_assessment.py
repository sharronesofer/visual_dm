#!/usr/bin/env python3
"""
Task 36: Comprehensive Backend Assessment and Error Resolution
Analyzes backend systems for syntax errors, import issues, missing logic, and compliance violations.
"""

import os
import ast
import re
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Any

class BackendAssessment:
    def __init__(self, backend_path: str = "backend"):
        self.backend_path = Path(backend_path)
        self.systems_path = self.backend_path / "systems"
        self.tests_path = self.backend_path / "tests"
        
        # Issue tracking
        self.syntax_errors = []
        self.import_issues = []
        self.missing_logic = []
        self.test_location_violations = []
        self.non_canonical_imports = []
        self.duplicate_definitions = []
        self.coverage_gaps = []
        self.bible_violations = []
        
        # Statistics
        self.stats = {
            'total_files': 0,
            'python_files': 0,
            'systems_analyzed': 0,
            'tests_analyzed': 0
        }

    def run_assessment(self):
        """Run comprehensive backend assessment"""
        print("🔍 Starting Comprehensive Backend Assessment...")
        print("=" * 60)
        
        # Check if paths exist
        if not self.systems_path.exists():
            print(f"❌ Systems path not found: {self.systems_path}")
            return
            
        if not self.tests_path.exists():
            print(f"❌ Tests path not found: {self.tests_path}")
            return
        
        # Run all assessments
        self._analyze_syntax_errors()
        self._analyze_import_issues()
        self._analyze_missing_logic()
        self._analyze_test_organization()
        self._analyze_canonical_imports()
        self._analyze_duplicates()
        self._analyze_coverage()
        self._analyze_bible_compliance()
        
        # Generate report
        self._generate_report()

    def _analyze_syntax_errors(self):
        """Check for Python syntax errors that prevent compilation"""
        print("\n🔧 Analyzing Syntax Errors...")
        
        for py_file in self._get_python_files():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Try to parse the AST
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    self.syntax_errors.append({
                        'file': str(py_file),
                        'line': e.lineno,
                        'error': str(e),
                        'severity': 'CRITICAL'
                    })
                except Exception as e:
                    self.syntax_errors.append({
                        'file': str(py_file),
                        'line': 0,
                        'error': f"Parse error: {str(e)}",
                        'severity': 'HIGH'
                    })
                    
            except Exception as e:
                self.syntax_errors.append({
                    'file': str(py_file),
                    'line': 0,
                    'error': f"File read error: {str(e)}",
                    'severity': 'HIGH'
                })

    def _analyze_import_issues(self):
        """Analyze import dependency issues"""
        print("📦 Analyzing Import Dependencies...")
        
        for py_file in self._get_python_files():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find import statements
                import_lines = []
                for i, line in enumerate(content.split('\n'), 1):
                    line = line.strip()
                    if line.startswith(('import ', 'from ')) and not line.startswith('#'):
                        import_lines.append((i, line))
                
                # Check for problematic imports
                for line_num, import_line in import_lines:
                    if self._is_problematic_import(import_line):
                        self.import_issues.append({
                            'file': str(py_file),
                            'line': line_num,
                            'import': import_line,
                            'issue': 'Potentially problematic import'
                        })
                        
            except Exception as e:
                self.import_issues.append({
                    'file': str(py_file),
                    'line': 0,
                    'import': '',
                    'issue': f"Analysis error: {str(e)}"
                })

    def _analyze_missing_logic(self):
        """Find TODO comments and placeholder implementations"""
        print("🚧 Analyzing Missing Logic...")
        
        todo_patterns = [
            r'TODO',
            r'FIXME',
            r'XXX',
            r'HACK',
            r'pass\s*#.*implement',
            r'raise NotImplementedError',
            r'def.*:\s*pass\s*$',
            r'class.*:\s*pass\s*$'
        ]
        
        for py_file in self._get_python_files():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    for pattern in todo_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            self.missing_logic.append({
                                'file': str(py_file),
                                'line': i,
                                'content': line.strip(),
                                'type': 'incomplete_implementation'
                            })
                            
            except Exception as e:
                self.missing_logic.append({
                    'file': str(py_file),
                    'line': 0,
                    'content': '',
                    'type': f'analysis_error: {str(e)}'
                })

    def _analyze_test_organization(self):
        """Check if test files are in correct locations"""
        print("📁 Analyzing Test Organization...")
        
        # Find test files outside of /backend/tests/
        for root, dirs, files in os.walk(self.backend_path):
            for file in files:
                if file.startswith('test_') or file.endswith('_test.py'):
                    file_path = Path(root) / file
                    
                    # Check if it's outside the tests directory
                    try:
                        file_path.relative_to(self.tests_path)
                    except ValueError:
                        # File is not under tests directory
                        self.test_location_violations.append({
                            'file': str(file_path),
                            'expected_location': str(self.tests_path),
                            'violation': 'test_file_outside_tests_directory'
                        })

    def _analyze_canonical_imports(self):
        """Check for non-canonical import patterns"""
        print("🎯 Analyzing Canonical Imports...")
        
        for py_file in self._get_python_files():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for i, line in enumerate(content.split('\n'), 1):
                    line = line.strip()
                    if line.startswith(('import ', 'from ')) and not line.startswith('#'):
                        if self._is_non_canonical_import(line):
                            self.non_canonical_imports.append({
                                'file': str(py_file),
                                'line': i,
                                'import': line,
                                'issue': 'non_canonical_import_pattern'
                            })
                            
            except Exception as e:
                self.non_canonical_imports.append({
                    'file': str(py_file),
                    'line': 0,
                    'import': '',
                    'issue': f'analysis_error: {str(e)}'
                })

    def _analyze_duplicates(self):
        """Find duplicate function/class definitions"""
        print("🔍 Analyzing Code Duplicates...")
        
        definitions = defaultdict(list)
        
        for py_file in self._get_python_files():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                            definitions[node.name].append({
                                'file': str(py_file),
                                'line': node.lineno,
                                'type': type(node).__name__
                            })
                except:
                    pass  # Skip files with syntax errors
                    
            except Exception:
                pass
        
        # Find duplicates
        for name, locations in definitions.items():
            if len(locations) > 1:
                self.duplicate_definitions.append({
                    'name': name,
                    'locations': locations,
                    'count': len(locations)
                })

    def _analyze_coverage(self):
        """Check test coverage gaps"""
        print("📊 Analyzing Test Coverage...")
        
        # Get all system modules
        system_modules = set()
        for py_file in self.systems_path.rglob("*.py"):
            if py_file.name != "__init__.py":
                rel_path = py_file.relative_to(self.systems_path)
                module_path = str(rel_path.with_suffix(''))
                system_modules.add(module_path.replace('/', '.'))
        
        # Get all test modules
        test_modules = set()
        for py_file in self.tests_path.rglob("test_*.py"):
            rel_path = py_file.relative_to(self.tests_path)
            module_path = str(rel_path.with_suffix(''))
            test_modules.add(module_path.replace('/', '.'))
        
        # Find coverage gaps
        for module in system_modules:
            test_module = f"test_{module.replace('.', '_')}"
            if test_module not in test_modules:
                self.coverage_gaps.append({
                    'module': module,
                    'missing_test': test_module,
                    'issue': 'no_corresponding_test_file'
                })

    def _analyze_bible_compliance(self):
        """Check Development Bible compliance"""
        print("📖 Analyzing Development Bible Compliance...")
        
        # Check for required directory structure
        required_dirs = [
            'systems',
            'tests',
            'systems/core',
            'systems/character',
            'systems/combat',
            'systems/inventory',
            'systems/loot'
        ]
        
        for req_dir in required_dirs:
            dir_path = self.backend_path / req_dir
            if not dir_path.exists():
                self.bible_violations.append({
                    'type': 'missing_directory',
                    'path': str(dir_path),
                    'requirement': f'Development Bible requires {req_dir} directory'
                })

    def _get_python_files(self) -> List[Path]:
        """Get all Python files in backend"""
        python_files = []
        for py_file in self.backend_path.rglob("*.py"):
            python_files.append(py_file)
            self.stats['total_files'] += 1
            if py_file.suffix == '.py':
                self.stats['python_files'] += 1
        return python_files

    def _is_problematic_import(self, import_line: str) -> bool:
        """Check if import might be problematic"""
        problematic_patterns = [
            r'from\s+\.\.',  # Relative imports going up
            r'import\s+sys',  # Direct sys imports
            r'from\s+sys',
        ]
        
        for pattern in problematic_patterns:
            if re.search(pattern, import_line):
                return True
        return False

    def _is_non_canonical_import(self, import_line: str) -> bool:
        """Check if import doesn't follow backend.systems.* pattern"""
        # Skip standard library and third-party imports
        if any(lib in import_line for lib in ['typing', 'dataclasses', 'enum', 'abc', 'pathlib', 'json', 'os', 'sys', 'logging']):
            return False
        
        # Check for relative imports or non-canonical patterns
        if '..' in import_line or import_line.startswith('from .'):
            return True
            
        # Check for backend imports that don't use canonical format
        if 'backend' in import_line and 'backend.systems' not in import_line:
            return True
            
        return False

    def _generate_report(self):
        """Generate comprehensive assessment report"""
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE BACKEND ASSESSMENT REPORT")
        print("=" * 60)
        
        total_issues = (len(self.syntax_errors) + len(self.import_issues) + 
                       len(self.missing_logic) + len(self.test_location_violations) +
                       len(self.non_canonical_imports) + len(self.duplicate_definitions) +
                       len(self.coverage_gaps) + len(self.bible_violations))
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Issues Found: {total_issues}")
        print(f"   Files Analyzed: {self.stats['python_files']}")
        
        # Critical Issues (Syntax Errors)
        if self.syntax_errors:
            print(f"\n🚨 CRITICAL SYNTAX ERRORS ({len(self.syntax_errors)}):")
            for error in self.syntax_errors[:10]:  # Show first 10
                print(f"   ❌ {error['file']}:{error['line']} - {error['error']}")
            if len(self.syntax_errors) > 10:
                print(f"   ... and {len(self.syntax_errors) - 10} more")
        
        # Missing Logic
        if self.missing_logic:
            print(f"\n🚧 INCOMPLETE IMPLEMENTATIONS ({len(self.missing_logic)}):")
            for issue in self.missing_logic[:5]:  # Show first 5
                print(f"   ⚠️  {issue['file']}:{issue['line']} - {issue['content'][:50]}...")
            if len(self.missing_logic) > 5:
                print(f"   ... and {len(self.missing_logic) - 5} more")
        
        # Non-canonical Imports
        if self.non_canonical_imports:
            print(f"\n📦 NON-CANONICAL IMPORTS ({len(self.non_canonical_imports)}):")
            for issue in self.non_canonical_imports[:5]:
                print(f"   🔄 {issue['file']}:{issue['line']} - {issue['import']}")
            if len(self.non_canonical_imports) > 5:
                print(f"   ... and {len(self.non_canonical_imports) - 5} more")
        
        # Duplicates
        if self.duplicate_definitions:
            print(f"\n🔍 POTENTIAL DUPLICATES ({len(self.duplicate_definitions)}):")
            for dup in self.duplicate_definitions[:5]:
                print(f"   🔄 '{dup['name']}' defined in {dup['count']} locations")
            if len(self.duplicate_definitions) > 5:
                print(f"   ... and {len(self.duplicate_definitions) - 5} more")
        
        # Test Organization
        if self.test_location_violations:
            print(f"\n📁 TEST LOCATION VIOLATIONS ({len(self.test_location_violations)}):")
            for violation in self.test_location_violations:
                print(f"   📂 {violation['file']} should be in {violation['expected_location']}")
        
        # Coverage Gaps
        if self.coverage_gaps:
            print(f"\n📊 COVERAGE GAPS ({len(self.coverage_gaps)}):")
            for gap in self.coverage_gaps[:5]:
                print(f"   📋 {gap['module']} missing test: {gap['missing_test']}")
            if len(self.coverage_gaps) > 5:
                print(f"   ... and {len(self.coverage_gaps) - 5} more")
        
        # Bible Violations
        if self.bible_violations:
            print(f"\n📖 DEVELOPMENT BIBLE VIOLATIONS ({len(self.bible_violations)}):")
            for violation in self.bible_violations:
                print(f"   📜 {violation['type']}: {violation['path']}")
        
        print(f"\n✅ Assessment Complete!")
        print(f"   Next: Begin systematic error resolution starting with critical syntax errors")
        
        # Save detailed report
        self._save_detailed_report()

    def _save_detailed_report(self):
        """Save detailed JSON report"""
        report = {
            'summary': {
                'total_issues': (len(self.syntax_errors) + len(self.import_issues) + 
                               len(self.missing_logic) + len(self.test_location_violations) +
                               len(self.non_canonical_imports) + len(self.duplicate_definitions) +
                               len(self.coverage_gaps) + len(self.bible_violations)),
                'files_analyzed': self.stats['python_files']
            },
            'syntax_errors': self.syntax_errors,
            'import_issues': self.import_issues,
            'missing_logic': self.missing_logic,
            'test_location_violations': self.test_location_violations,
            'non_canonical_imports': self.non_canonical_imports,
            'duplicate_definitions': self.duplicate_definitions,
            'coverage_gaps': self.coverage_gaps,
            'bible_violations': self.bible_violations
        }
        
        with open('task_36_assessment_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: task_36_assessment_report.json")

if __name__ == "__main__":
    assessment = BackendAssessment()
    assessment.run_assessment() 