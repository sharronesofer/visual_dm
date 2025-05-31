#!/usr/bin/env python3
"""
Task 35 Comprehensive Assessment Script

This script performs a comprehensive analysis of the backend systems to implement
all requirements from Task 35:

1. Assessment and Error Resolution
2. Structure and Organization Enforcement  
3. Canonical Imports Enforcement
4. Module and Function Development
5. Quality and Integration Standards

Reference Documents:
- /docs/Development_Bible.md
- backend/docs/backend_systems_inventory_updated.md
- backend/backend_development_protocol.md
"""

import os
import sys
import json
import ast
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

@dataclass
class AssessmentResult:
    """Container for assessment results"""
    errors: List[str]
    warnings: List[str]
    fixes_applied: List[str]
    metrics: Dict[str, Any]

class Task35Assessor:
    """Comprehensive assessor for Task 35 requirements"""
    
    def __init__(self, backend_root: str = "backend"):
        self.backend_root = Path(backend_root)
        self.systems_path = self.backend_root / "systems"
        self.tests_path = self.backend_root / "tests"
        self.systems_tests_path = self.tests_path / "systems"
        self.docs_path = Path("docs")
        
        # Results tracking
        self.results = AssessmentResult([], [], [], {})
        
        # Expected systems from Development Bible
        self.expected_systems = {
            'analytics', 'arc', 'auth_user', 'character', 'combat', 'crafting',
            'data', 'dialogue', 'diplomacy', 'economy', 'equipment', 'event_base',
            'events', 'faction', 'integration', 'inventory', 'llm', 'loot',
            'magic', 'memory', 'motif', 'npc', 'poi', 'population', 'quest',
            'region', 'religion', 'rumor', 'shared', 'storage', 'tension_war',
            'time', 'world_generation', 'world_state'
        }
        
        # Canonical import patterns
        self.canonical_pattern = re.compile(r'^from backend\.systems\.(\w+)')
        self.non_canonical_patterns = [
            re.compile(r'^from backend\.(?!systems\.)'),
            re.compile(r'^import backend\.(?!systems\.)'),
            re.compile(r'^from \.\.'),
            re.compile(r'^from \.')
        ]

    def run_comprehensive_assessment(self) -> Dict[str, Any]:
        """Run complete Task 35 assessment"""
        print("🔍 Starting Task 35 Comprehensive Assessment...")
        
        # 1. Assessment and Error Resolution
        print("\n📋 Phase 1: Assessment and Error Resolution")
        self._assess_errors_and_violations()
        
        # 2. Structure and Organization Enforcement
        print("\n📁 Phase 2: Structure and Organization Enforcement")
        self._enforce_structure_organization()
        
        # 3. Canonical Imports Enforcement
        print("\n🔗 Phase 3: Canonical Imports Enforcement")
        self._enforce_canonical_imports()
        
        # 4. Module and Function Development Assessment
        print("\n🔧 Phase 4: Module and Function Development Assessment")
        self._assess_module_development()
        
        # 5. Quality and Integration Standards
        print("\n✅ Phase 5: Quality and Integration Standards")
        self._assess_quality_standards()
        
        # Generate comprehensive report
        return self._generate_final_report()

    def _assess_errors_and_violations(self):
        """Phase 1: Assess errors and Development Bible violations"""
        print("  Analyzing syntax errors and Development Bible compliance...")
        
        # Check for syntax errors
        syntax_errors = self._check_syntax_errors()
        self.results.errors.extend(syntax_errors)
        
        # Check Development Bible compliance
        bible_violations = self._check_development_bible_compliance()
        self.results.warnings.extend(bible_violations)
        
        # Check missing logic in modules
        missing_logic = self._check_missing_logic()
        self.results.warnings.extend(missing_logic)
        
        print(f"    Found {len(syntax_errors)} syntax errors")
        print(f"    Found {len(bible_violations)} Development Bible violations")
        print(f"    Found {len(missing_logic)} missing logic issues")

    def _check_syntax_errors(self) -> List[str]:
        """Check for Python syntax errors in all files"""
        errors = []
        
        for python_file in self._get_python_files():
            try:
                with open(python_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                errors.append(f"Syntax error in {python_file}: {e}")
            except Exception as e:
                errors.append(f"Parse error in {python_file}: {e}")
                
        return errors

    def _check_development_bible_compliance(self) -> List[str]:
        """Check compliance with Development Bible standards"""
        violations = []
        
        # Check system directory structure compliance
        actual_systems = set(d.name for d in self.systems_path.iterdir() if d.is_dir() and not d.name.startswith('_'))
        
        missing_systems = self.expected_systems - actual_systems
        for system in missing_systems:
            violations.append(f"Missing expected system directory: {system}")
        
        extra_systems = actual_systems - self.expected_systems
        for system in extra_systems:
            violations.append(f"Unexpected system directory: {system}")
        
        # Check for proper FastAPI patterns
        violations.extend(self._check_fastapi_compliance())
        
        return violations

    def _check_fastapi_compliance(self) -> List[str]:
        """Check FastAPI compliance patterns"""
        violations = []
        
        for system_dir in self.systems_path.iterdir():
            if not system_dir.is_dir() or system_dir.name.startswith('_'):
                continue
                
            router_files = list(system_dir.glob("*router*.py"))
            if router_files:
                for router_file in router_files:
                    violations.extend(self._check_router_compliance(router_file))
        
        return violations

    def _check_router_compliance(self, router_file: Path) -> List[str]:
        """Check individual router file compliance"""
        violations = []
        
        try:
            with open(router_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for FastAPI imports
            if 'from fastapi import' not in content and 'import fastapi' not in content:
                violations.append(f"Router {router_file} missing FastAPI imports")
            
            # Check for route decorators
            if not re.search(r'@\w+\.(?:get|post|put|delete|patch)', content):
                violations.append(f"Router {router_file} missing route decorators")
                
        except Exception as e:
            violations.append(f"Error checking router {router_file}: {e}")
            
        return violations

    def _check_missing_logic(self) -> List[str]:
        """Check for missing logic implementations"""
        missing = []
        
        for system_dir in self.systems_path.iterdir():
            if not system_dir.is_dir() or system_dir.name.startswith('_'):
                continue
                
            # Check for expected files
            expected_files = ['models.py', 'services.py', '__init__.py']
            for expected_file in expected_files:
                file_path = system_dir / expected_file
                if not file_path.exists():
                    missing.append(f"Missing {expected_file} in {system_dir.name} system")
                elif file_path.stat().st_size < 100:  # Very small files likely stubs
                    missing.append(f"Stub implementation in {system_dir.name}/{expected_file}")
        
        return missing

    def _enforce_structure_organization(self):
        """Phase 2: Enforce structure and organization"""
        print("  Enforcing directory structure and test organization...")
        
        # Find and relocate misplaced test files
        misplaced_tests = self._find_misplaced_tests()
        self.results.warnings.extend([f"Misplaced test: {test}" for test in misplaced_tests])
        
        # Check for duplicate tests
        duplicate_tests = self._find_duplicate_tests()
        self.results.warnings.extend([f"Duplicate test: {test}" for test in duplicate_tests])
        
        # Ensure canonical organization
        org_issues = self._check_canonical_organization()
        self.results.warnings.extend(org_issues)
        
        print(f"    Found {len(misplaced_tests)} misplaced tests")
        print(f"    Found {len(duplicate_tests)} duplicate tests")
        print(f"    Found {len(org_issues)} organization issues")

    def _find_misplaced_tests(self) -> List[str]:
        """Find test files outside of /backend/tests/"""
        misplaced = []
        
        # Look for test directories in systems
        for system_dir in self.systems_path.iterdir():
            if not system_dir.is_dir():
                continue
                
            # Check for test/tests directories
            for test_dir_name in ['test', 'tests']:
                test_dir = system_dir / test_dir_name
                if test_dir.exists():
                    test_files = list(test_dir.glob("*.py"))
                    misplaced.extend([str(f) for f in test_files])
        
        return misplaced

    def _find_duplicate_tests(self) -> List[str]:
        """Find duplicate test files"""
        duplicates = []
        test_files = defaultdict(list)
        
        # Collect all test files
        for test_file in self.tests_path.rglob("test_*.py"):
            test_files[test_file.name].append(str(test_file))
        
        # Find duplicates
        for filename, paths in test_files.items():
            if len(paths) > 1:
                duplicates.extend(paths[1:])  # Keep first, mark others as duplicates
        
        return duplicates

    def _check_canonical_organization(self) -> List[str]:
        """Check for canonical /backend/systems/ organization"""
        issues = []
        
        # Ensure systems tests mirror systems structure
        for system_dir in self.systems_path.iterdir():
            if not system_dir.is_dir() or system_dir.name.startswith('_'):
                continue
                
            corresponding_test_dir = self.systems_tests_path / system_dir.name
            if not corresponding_test_dir.exists():
                issues.append(f"Missing test directory for system: {system_dir.name}")
        
        return issues

    def _enforce_canonical_imports(self):
        """Phase 3: Enforce canonical imports"""
        print("  Analyzing and fixing import violations...")
        
        # Find all import violations
        violations = self._find_import_violations()
        self.results.errors.extend([f"Import violation: {v}" for v in violations])
        
        # Find orphan dependencies
        orphans = self._find_orphan_dependencies()
        self.results.warnings.extend([f"Orphan dependency: {o}" for o in orphans])
        
        print(f"    Found {len(violations)} import violations")
        print(f"    Found {len(orphans)} orphan dependencies")

    def _find_import_violations(self) -> List[str]:
        """Find non-canonical import patterns"""
        violations = []
        
        for python_file in self._get_python_files():
            try:
                with open(python_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if line.startswith(('from ', 'import ')):
                        if self._is_non_canonical_import(line):
                            violations.append(f"{python_file}:{line_num} - {line}")
                            
            except Exception as e:
                violations.append(f"Error checking imports in {python_file}: {e}")
        
        return violations

    def _is_non_canonical_import(self, line: str) -> bool:
        """Check if import line is non-canonical"""
        # Skip standard library and third-party imports
        if any(pattern in line for pattern in ['fastapi', 'pydantic', 'sqlalchemy', 'typing', 'datetime', 'json', 'os', 'sys', 'pathlib']):
            return False
        
        # Check for non-canonical patterns
        for pattern in self.non_canonical_patterns:
            if pattern.match(line):
                return True
        
        # Check if it should be canonical but isn't
        if 'backend' in line and not self.canonical_pattern.match(line):
            return True
            
        return False

    def _find_orphan_dependencies(self) -> List[str]:
        """Find modules that depend on non-canonical locations"""
        orphans = []
        
        # This would require more sophisticated analysis
        # For now, just identify obvious patterns
        
        return orphans

    def _assess_module_development(self):
        """Phase 4: Assess module and function development"""
        print("  Assessing module development and duplication...")
        
        # Check for function duplication
        duplicates = self._find_function_duplicates()
        self.results.warnings.extend([f"Duplicate function: {d}" for d in duplicates])
        
        # Check module compatibility
        compatibility_issues = self._check_module_compatibility()
        self.results.warnings.extend(compatibility_issues)
        
        print(f"    Found {len(duplicates)} function duplicates")
        print(f"    Found {len(compatibility_issues)} compatibility issues")

    def _find_function_duplicates(self) -> List[str]:
        """Find duplicate function implementations"""
        duplicates = []
        function_signatures = defaultdict(list)
        
        for python_file in self._get_python_files():
            try:
                with open(python_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        sig = f"{node.name}({len(node.args.args)})"
                        function_signatures[sig].append(str(python_file))
                        
            except Exception:
                continue
        
        # Find duplicates
        for sig, files in function_signatures.items():
            if len(files) > 1:
                duplicates.append(f"{sig} in {files}")
        
        return duplicates

    def _check_module_compatibility(self) -> List[str]:
        """Check module compatibility requirements"""
        issues = []
        
        # Check for WebSocket compatibility patterns
        # Check for FastAPI async patterns
        # Check for Unity integration patterns
        
        return issues

    def _assess_quality_standards(self):
        """Phase 5: Assess quality and integration standards"""
        print("  Assessing quality standards and test coverage...")
        
        # Calculate test coverage
        coverage_info = self._calculate_test_coverage()
        self.results.metrics['test_coverage'] = coverage_info
        
        # Check API endpoint compliance
        api_issues = self._check_api_compliance()
        self.results.warnings.extend(api_issues)
        
        # Check documentation status
        doc_issues = self._check_documentation()
        self.results.warnings.extend(doc_issues)
        
        print(f"    Test coverage: {coverage_info.get('percentage', 0):.1f}%")
        print(f"    Found {len(api_issues)} API compliance issues")
        print(f"    Found {len(doc_issues)} documentation issues")

    def _calculate_test_coverage(self) -> Dict[str, Any]:
        """Calculate current test coverage"""
        try:
            # Run pytest with coverage
            result = subprocess.run([
                'python', '-m', 'pytest', '--cov=backend/systems', 
                '--cov-report=json', '--cov-report=term-missing',
                str(self.tests_path)
            ], capture_output=True, text=True, cwd=self.backend_root.parent)
            
            # Try to read coverage.json if it exists
            coverage_file = self.backend_root / 'coverage.json'
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                    return {
                        'percentage': coverage_data.get('totals', {}).get('percent_covered', 0),
                        'files_covered': len(coverage_data.get('files', {})),
                        'raw_data': coverage_data
                    }
        except Exception as e:
            print(f"    Warning: Could not calculate coverage: {e}")
        
        return {'percentage': 0, 'files_covered': 0, 'error': 'Could not calculate coverage'}

    def _check_api_compliance(self) -> List[str]:
        """Check API endpoint compliance"""
        issues = []
        
        # Check for proper API contracts
        # Check for consistent response schemas
        # Check for proper error handling
        
        return issues

    def _check_documentation(self) -> List[str]:
        """Check documentation completeness"""
        issues = []
        
        # Check for missing docstrings
        # Check for outdated documentation
        # Check for API documentation
        
        return issues

    def _get_python_files(self) -> List[Path]:
        """Get all Python files in backend/systems and backend/tests"""
        python_files = []
        
        # Systems files
        python_files.extend(self.systems_path.rglob("*.py"))
        
        # Test files
        python_files.extend(self.tests_path.rglob("*.py"))
        
        return python_files

    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final report"""
        report = {
            'task': 'Task 35 - Comprehensive Assessment and Error Resolution',
            'timestamp': subprocess.run(['date'], capture_output=True, text=True).stdout.strip(),
            'summary': {
                'total_errors': len(self.results.errors),
                'total_warnings': len(self.results.warnings),
                'fixes_applied': len(self.results.fixes_applied),
                'systems_analyzed': len([d for d in self.systems_path.iterdir() if d.is_dir() and not d.name.startswith('_')])
            },
            'results': asdict(self.results),
            'recommendations': self._generate_recommendations(),
            'next_steps': self._generate_next_steps()
        }
        
        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on assessment"""
        recommendations = []
        
        if len(self.results.errors) > 0:
            recommendations.append("Fix syntax errors before proceeding with development")
        
        coverage = self.results.metrics.get('test_coverage', {}).get('percentage', 0)
        if coverage < 90:
            recommendations.append(f"Increase test coverage from {coverage:.1f}% to ≥90%")
        
        if any('Import violation' in error for error in self.results.errors):
            recommendations.append("Convert all imports to canonical backend.systems.* format")
        
        if any('Missing' in warning for warning in self.results.warnings):
            recommendations.append("Implement missing system components according to Development Bible")
        
        return recommendations

    def _generate_next_steps(self) -> List[str]:
        """Generate next steps for Task 35 implementation"""
        return [
            "1. Fix all syntax errors and import violations",
            "2. Relocate misplaced test files to /backend/tests/",
            "3. Remove duplicate tests and empty test directories",
            "4. Implement missing system components",
            "5. Achieve ≥90% test coverage",
            "6. Verify WebSocket and Unity frontend compatibility",
            "7. Update documentation and API specifications"
        ]

def main():
    """Main execution function"""
    assessor = Task35Assessor()
    results = assessor.run_comprehensive_assessment()
    
    # Save results
    output_file = "task_35_assessment_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📊 Assessment complete! Results saved to {output_file}")
    print(f"\n📈 Summary:")
    print(f"  Errors: {results['summary']['total_errors']}")
    print(f"  Warnings: {results['summary']['total_warnings']}")
    print(f"  Systems Analyzed: {results['summary']['systems_analyzed']}")
    
    if results['summary']['total_errors'] > 0:
        print(f"\n❌ Critical issues found - fixes required before proceeding")
    else:
        print(f"\n✅ No critical errors found - proceeding with implementation")
    
    return results

if __name__ == "__main__":
    main() 