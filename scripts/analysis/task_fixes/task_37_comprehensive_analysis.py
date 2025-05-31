#!/usr/bin/env python3
"""
Task 37: Comprehensive Backend System Assessment and Error Resolution

This script performs:
1. Comprehensive analysis on target systems under /backend/systems/ and /backend/tests/
2. Assessment of compliance with Development_Bible.md
3. Structure and organization enforcement
4. Canonical imports enforcement
5. Module and function development validation
6. Quality and integration standards verification
"""

import os
import sys
import json
import ast
import re
import importlib.util
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SystemAssessment:
    """Assessment results for a single system"""
    name: str
    models_present: bool = False
    services_present: bool = False
    repositories_present: bool = False
    routers_present: bool = False
    schemas_present: bool = False
    tests_present: bool = False
    issues: List[str] = None
    import_violations: List[str] = None
    missing_components: List[str] = None
    duplicate_tests: List[str] = None
    non_canonical_imports: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.import_violations is None:
            self.import_violations = []
        if self.missing_components is None:
            self.missing_components = []
        if self.duplicate_tests is None:
            self.duplicate_tests = []
        if self.non_canonical_imports is None:
            self.non_canonical_imports = []

class BackendSystemAnalyzer:
    """Comprehensive backend system analyzer for Task 37"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.backend_path = self.root_path / "backend"
        self.systems_path = self.backend_path / "systems"
        self.tests_path = self.backend_path / "tests" / "systems"
        self.docs_path = self.root_path / "docs"
        
        # Expected system directories from Development_Bible.md
        self.expected_systems = {
            'analytics', 'arc', 'auth_user', 'character', 'combat', 'crafting',
            'data', 'dialogue', 'diplomacy', 'economy', 'equipment', 'event_base',
            'events', 'faction', 'integration', 'inventory', 'llm', 'loot',
            'magic', 'memory', 'motif', 'npc', 'poi', 'population', 'quest',
            'region', 'religion', 'rumor', 'shared', 'storage', 'tension_war',
            'time', 'world_generation', 'world_state'
        }
        
        self.assessments: Dict[str, SystemAssessment] = {}
        self.global_issues: List[str] = []
        
    def analyze_all_systems(self) -> Dict[str, SystemAssessment]:
        """Run comprehensive analysis on all backend systems"""
        print("🔍 Starting comprehensive backend system analysis...")
        
        # 1. Verify directory structure compliance
        self._verify_directory_structure()
        
        # 2. Analyze each system
        for system_name in self.expected_systems:
            self.assessments[system_name] = self._analyze_system(system_name)
        
        # 3. Check for orphaned systems
        self._check_orphaned_systems()
        
        # 4. Validate canonical imports across all systems
        self._validate_canonical_imports()
        
        # 5. Check for duplicate tests
        self._check_duplicate_tests()
        
        # 6. Verify test organization
        self._verify_test_organization()
        
        # 7. Check Development_Bible.md compliance
        self._check_development_bible_compliance()
        
        print(f"✅ Analysis complete for {len(self.assessments)} systems")
        return self.assessments
    
    def _verify_directory_structure(self):
        """Verify that directory structure matches canonical organization"""
        print("📁 Verifying directory structure...")
        
        # Check if systems directory exists
        if not self.systems_path.exists():
            self.global_issues.append("Missing /backend/systems/ directory")
            return
            
        # Check if tests directory exists
        if not self.tests_path.exists():
            self.global_issues.append("Missing /backend/tests/systems/ directory")
            return
            
        # Check for systems in /backend/systems/ but not in expected list
        actual_systems = {d.name for d in self.systems_path.iterdir() if d.is_dir() and not d.name.startswith('_')}
        unexpected_systems = actual_systems - self.expected_systems
        
        if unexpected_systems:
            self.global_issues.append(f"Unexpected systems found: {unexpected_systems}")
            
        # Check for missing expected systems
        missing_systems = self.expected_systems - actual_systems
        if missing_systems:
            self.global_issues.append(f"Missing expected systems: {missing_systems}")
    
    def _analyze_system(self, system_name: str) -> SystemAssessment:
        """Analyze a single system for compliance and completeness"""
        assessment = SystemAssessment(name=system_name)
        
        system_path = self.systems_path / system_name
        test_path = self.tests_path / system_name
        
        if not system_path.exists():
            assessment.issues.append(f"System directory missing: {system_path}")
            return assessment
            
        # Check for core components
        assessment.models_present = self._has_models(system_path)
        assessment.services_present = self._has_services(system_path)
        assessment.repositories_present = self._has_repositories(system_path)
        assessment.routers_present = self._has_routers(system_path)
        assessment.schemas_present = self._has_schemas(system_path)
        assessment.tests_present = test_path.exists() and any(test_path.glob("*.py"))
        
        # Identify missing components
        if not assessment.models_present:
            assessment.missing_components.append("models")
        if not assessment.services_present:
            assessment.missing_components.append("services")
        if not assessment.repositories_present:
            assessment.missing_components.append("repositories")
        if not assessment.routers_present:
            assessment.missing_components.append("routers")
        if not assessment.schemas_present:
            assessment.missing_components.append("schemas")
        if not assessment.tests_present:
            assessment.missing_components.append("tests")
            
        # Check for import violations in this system
        self._check_system_imports(system_path, assessment)
        
        # Check for proper FastAPI structure in routers
        self._check_fastapi_compliance(system_path, assessment)
        
        return assessment
    
    def _has_models(self, system_path: Path) -> bool:
        """Check if system has models"""
        models_dir = system_path / "models"
        return models_dir.exists() and any(models_dir.glob("*.py"))
    
    def _has_services(self, system_path: Path) -> bool:
        """Check if system has services"""
        services_dir = system_path / "services"
        return services_dir.exists() and any(services_dir.glob("*.py"))
    
    def _has_repositories(self, system_path: Path) -> bool:
        """Check if system has repositories"""
        repo_dir = system_path / "repositories"
        return repo_dir.exists() and any(repo_dir.glob("*.py"))
    
    def _has_routers(self, system_path: Path) -> bool:
        """Check if system has routers"""
        # Check for router.py or routers directory
        router_file = system_path / "router.py"
        routers_dir = system_path / "routers"
        return router_file.exists() or (routers_dir.exists() and any(routers_dir.glob("*.py")))
    
    def _has_schemas(self, system_path: Path) -> bool:
        """Check if system has schemas"""
        schemas_dir = system_path / "schemas"
        schema_file = system_path / "schema.py"
        return schema_file.exists() or (schemas_dir.exists() and any(schemas_dir.glob("*.py")))
    
    def _check_system_imports(self, system_path: Path, assessment: SystemAssessment):
        """Check for non-canonical imports in a system"""
        for py_file in system_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for non-canonical imports
                import_lines = [line.strip() for line in content.split('\n') 
                               if line.strip().startswith(('import ', 'from '))]
                
                for line in import_lines:
                    if self._is_non_canonical_import(line, system_path):
                        assessment.non_canonical_imports.append(f"{py_file}: {line}")
                        
            except Exception as e:
                assessment.issues.append(f"Error reading {py_file}: {e}")
    
    def _is_non_canonical_import(self, import_line: str, system_path: Path) -> bool:
        """Check if an import line violates canonical import rules"""
        # Extract the import path
        if import_line.startswith('from '):
            # from module import something
            match = re.match(r'from\s+([^\s]+)\s+import', import_line)
            if match:
                module_path = match.group(1)
            else:
                return False
        elif import_line.startswith('import '):
            # import module
            match = re.match(r'import\s+([^\s,]+)', import_line)
            if match:
                module_path = match.group(1)
            else:
                return False
        else:
            return False
        
        # Check if it's importing from outside backend.systems
        if module_path.startswith('backend.systems.'):
            return False  # This is canonical
            
        # Check for relative imports that go outside the system
        if module_path.startswith('..') and module_path.count('..') > 1:
            return True  # Going too far up the hierarchy
            
        # Check for imports from non-canonical locations
        problematic_patterns = [
            r'^utils\.', r'^core\.', r'^app\.', r'^src\.',
            r'^backend\.(?!systems\.)', r'^\.\.\.+',
        ]
        
        for pattern in problematic_patterns:
            if re.match(pattern, module_path):
                return True
                
        return False
    
    def _check_fastapi_compliance(self, system_path: Path, assessment: SystemAssessment):
        """Check FastAPI compliance in router files"""
        router_files = []
        
        # Check for router.py
        router_file = system_path / "router.py"
        if router_file.exists():
            router_files.append(router_file)
            
        # Check routers directory
        routers_dir = system_path / "routers"
        if routers_dir.exists():
            router_files.extend(routers_dir.glob("*.py"))
            
        for router_file in router_files:
            try:
                with open(router_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for FastAPI imports
                if 'from fastapi import' not in content and 'import fastapi' not in content:
                    assessment.issues.append(f"Router {router_file} missing FastAPI imports")
                    
                # Check for route decorators
                if not re.search(r'@\w+\.(get|post|put|delete|patch)', content):
                    assessment.issues.append(f"Router {router_file} missing route decorators")
                    
            except Exception as e:
                assessment.issues.append(f"Error checking FastAPI compliance in {router_file}: {e}")
    
    def _check_orphaned_systems(self):
        """Check for systems that exist but shouldn't"""
        if not self.systems_path.exists():
            return
            
        actual_dirs = {d.name for d in self.systems_path.iterdir() 
                      if d.is_dir() and not d.name.startswith('_')}
        orphaned = actual_dirs - self.expected_systems
        
        if orphaned:
            self.global_issues.append(f"Orphaned system directories found: {orphaned}")
    
    def _validate_canonical_imports(self):
        """Validate that all imports follow canonical backend.systems.* format"""
        print("🔍 Validating canonical imports...")
        
        violation_count = 0
        for system_name, assessment in self.assessments.items():
            violation_count += len(assessment.non_canonical_imports)
            
        if violation_count > 0:
            self.global_issues.append(f"Found {violation_count} canonical import violations")
    
    def _check_duplicate_tests(self):
        """Check for duplicate test files across systems"""
        print("🔍 Checking for duplicate tests...")
        
        test_files = {}
        
        # Scan backend/tests/systems/
        if self.tests_path.exists():
            for test_file in self.tests_path.rglob("*.py"):
                relative_path = test_file.relative_to(self.tests_path)
                test_name = test_file.name
                
                if test_name not in test_files:
                    test_files[test_name] = []
                test_files[test_name].append(str(relative_path))
        
        # Find duplicates
        duplicates = {name: paths for name, paths in test_files.items() if len(paths) > 1}
        
        if duplicates:
            for system_name, assessment in self.assessments.items():
                for test_name, paths in duplicates.items():
                    # Check if any of the duplicate paths involve this system
                    system_paths = [p for p in paths if p.startswith(f"{system_name}/")]
                    if system_paths:
                        assessment.duplicate_tests.extend(system_paths)
            
            self.global_issues.append(f"Found duplicate test files: {duplicates}")
    
    def _verify_test_organization(self):
        """Verify that all tests are properly organized under /backend/tests/"""
        print("🔍 Verifying test organization...")
        
        # Check for test files in wrong locations
        misplaced_tests = []
        
        if self.systems_path.exists():
            for test_file in self.systems_path.rglob("*test*.py"):
                misplaced_tests.append(str(test_file.relative_to(self.systems_path)))
        
        if misplaced_tests:
            self.global_issues.append(f"Test files found in wrong locations: {misplaced_tests}")
    
    def _check_development_bible_compliance(self):
        """Check compliance with Development_Bible.md requirements"""
        print("🔍 Checking Development_Bible.md compliance...")
        
        bible_path = self.docs_path / "development_bible.md"
        if not bible_path.exists():
            self.global_issues.append("Development_Bible.md not found")
            return
        
        # Count systems missing critical components
        incomplete_systems = []
        for system_name, assessment in self.assessments.items():
            if len(assessment.missing_components) >= 3:  # Missing 3+ core components
                incomplete_systems.append(system_name)
        
        if incomplete_systems:
            self.global_issues.append(
                f"Systems with significant missing components: {incomplete_systems}"
            )
    
    def generate_report(self) -> Dict:
        """Generate comprehensive assessment report"""
        total_systems = len(self.assessments)
        systems_with_issues = sum(1 for a in self.assessments.values() if a.issues)
        
        # Calculate compliance metrics
        models_coverage = sum(1 for a in self.assessments.values() if a.models_present) / total_systems * 100
        services_coverage = sum(1 for a in self.assessments.values() if a.services_present) / total_systems * 100
        tests_coverage = sum(1 for a in self.assessments.values() if a.tests_present) / total_systems * 100
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "task": "Task 37 - Comprehensive Backend System Assessment",
            "summary": {
                "total_systems": total_systems,
                "systems_analyzed": len(self.assessments),
                "systems_with_issues": systems_with_issues,
                "global_issues_count": len(self.global_issues),
                "compliance_metrics": {
                    "models_coverage": f"{models_coverage:.1f}%",
                    "services_coverage": f"{services_coverage:.1f}%",
                    "tests_coverage": f"{tests_coverage:.1f}%"
                }
            },
            "global_issues": self.global_issues,
            "system_assessments": {
                name: {
                    "models_present": assessment.models_present,
                    "services_present": assessment.services_present,
                    "repositories_present": assessment.repositories_present,
                    "routers_present": assessment.routers_present,
                    "schemas_present": assessment.schemas_present,
                    "tests_present": assessment.tests_present,
                    "missing_components": assessment.missing_components,
                    "issues": assessment.issues,
                    "import_violations": assessment.non_canonical_imports[:10],  # Limit for readability
                    "duplicate_tests": assessment.duplicate_tests
                }
                for name, assessment in self.assessments.items()
            },
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on assessment"""
        recommendations = []
        
        # Global recommendations
        if self.global_issues:
            recommendations.append("Address global structural issues first")
        
        # System-specific recommendations
        incomplete_systems = [name for name, assessment in self.assessments.items() 
                            if len(assessment.missing_components) > 0]
        
        if incomplete_systems:
            recommendations.append(
                f"Implement missing components in {len(incomplete_systems)} systems"
            )
        
        # Import recommendations
        systems_with_import_issues = [name for name, assessment in self.assessments.items() 
                                    if assessment.non_canonical_imports]
        
        if systems_with_import_issues:
            recommendations.append(
                f"Fix canonical import violations in {len(systems_with_import_issues)} systems"
            )
        
        # Test recommendations
        systems_without_tests = [name for name, assessment in self.assessments.items() 
                               if not assessment.tests_present]
        
        if systems_without_tests:
            recommendations.append(
                f"Create tests for {len(systems_without_tests)} systems without test coverage"
            )
        
        return recommendations

def main():
    """Main execution function"""
    print("🚀 Task 37: Comprehensive Backend System Assessment")
    print("=" * 60)
    
    analyzer = BackendSystemAnalyzer()
    
    try:
        # Run comprehensive analysis
        assessments = analyzer.analyze_all_systems()
        
        # Generate report
        report = analyzer.generate_report()
        
        # Save report
        output_file = "task_37_assessment_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Assessment Results:")
        print(f"  Total systems: {report['summary']['total_systems']}")
        print(f"  Systems with issues: {report['summary']['systems_with_issues']}")
        print(f"  Global issues: {report['summary']['global_issues_count']}")
        print(f"  Models coverage: {report['summary']['compliance_metrics']['models_coverage']}")
        print(f"  Services coverage: {report['summary']['compliance_metrics']['services_coverage']}")
        print(f"  Tests coverage: {report['summary']['compliance_metrics']['tests_coverage']}")
        
        print(f"\n📁 Report saved to: {output_file}")
        
        if report['global_issues']:
            print(f"\n⚠️  Global Issues Found:")
            for issue in report['global_issues']:
                print(f"  • {issue}")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
        
        print(f"\n✅ Task 37 assessment completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during assessment: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 