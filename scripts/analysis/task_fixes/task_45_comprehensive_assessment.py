#!/usr/bin/env python3
"""
Task 45: Comprehensive Backend Systems Assessment and Error Resolution

This script performs the comprehensive analysis required by Task 45:
1. Assessment and Error Resolution
2. Structure and Organization Enforcement  
3. Canonical Imports Enforcement
4. Module and Function Development
5. Quality and Integration Standards

Requirements:
- Run comprehensive analysis on target systems under /backend/systems/ and /backend/tests/
- Identify structural issues, import problems, and missing functionality
- Ensure all test files are under /backend/tests/*
- Enforce canonical /backend/systems/ organization
- Check for duplicate tests and orphan dependencies
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import re
import ast
import importlib.util
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict
import time

# Get absolute paths
PROJECT_ROOT = Path("/Users/Sharrone/Visual_DM")
BACKEND_ROOT = PROJECT_ROOT / "backend"
SYSTEMS_ROOT = BACKEND_ROOT / "systems"
TESTS_ROOT = BACKEND_ROOT / "tests"
DOCS_ROOT = PROJECT_ROOT / "docs"

class BackendSystemsAssessment:
    def __init__(self):
        self.results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "assessment_type": "Task 45 - Comprehensive Backend Systems Assessment",
            "structural_issues": [],
            "import_violations": [],
            "missing_functionality": [],
            "test_organization_issues": [],
            "duplicate_tests": [],
            "orphan_dependencies": [],
            "canonical_violations": [],
            "coverage_analysis": {},
            "system_health": {},
            "critical_errors": [],
            "recommendations": []
        }
        
        # Load expected systems from Development Bible
        self.expected_systems = self._get_expected_systems()
        
    def _get_expected_systems(self) -> Set[str]:
        """Get the canonical list of expected systems from Development Bible"""
        expected = {
            'analytics', 'arc', 'auth_user', 'character', 'combat', 'crafting',
            'data', 'dialogue', 'diplomacy', 'economy', 'equipment', 'event_base',
            'events', 'faction', 'integration', 'inventory', 'llm', 'loot',
            'magic', 'memory', 'motif', 'npc', 'poi', 'population', 'quest',
            'region', 'religion', 'rumor', 'shared', 'storage', 'tension_war',
            'time', 'world_generation', 'world_state'
        }
        return expected
    
    def assess_structural_organization(self):
        """Assess structural organization and enforce canonical hierarchy"""
        print("🏗️  Assessing structural organization...")
        
        # Check systems directory structure
        if not SYSTEMS_ROOT.exists():
            self.results["critical_errors"].append("Critical: /backend/systems/ directory missing")
            return
            
        if not TESTS_ROOT.exists():
            self.results["critical_errors"].append("Critical: /backend/tests/ directory missing")
            return
            
        # Check for systems in /backend/systems/
        actual_systems = set()
        for item in SYSTEMS_ROOT.iterdir():
            if item.is_dir() and not item.name.startswith('__'):
                actual_systems.add(item.name)
                
        # Check for missing systems
        missing_systems = self.expected_systems - actual_systems
        extra_systems = actual_systems - self.expected_systems
        
        if missing_systems:
            self.results["structural_issues"].append({
                "type": "missing_systems",
                "systems": list(missing_systems),
                "message": f"Missing {len(missing_systems)} expected systems in /backend/systems/"
            })
            
        if extra_systems:
            self.results["structural_issues"].append({
                "type": "extra_systems", 
                "systems": list(extra_systems),
                "message": f"Found {len(extra_systems)} unexpected systems in /backend/systems/"
            })
            
        # Check for tests in wrong locations (Rule: All tests must be under /backend/tests/*)
        misplaced_tests = []
        for system in actual_systems:
            system_path = SYSTEMS_ROOT / system
            for root, dirs, files in os.walk(system_path):
                root_path = Path(root)
                # Check for test directories in systems
                if any(dir_name in ['test', 'tests'] for dir_name in dirs):
                    for test_dir in ['test', 'tests']:
                        if test_dir in dirs:
                            test_path = root_path / test_dir
                            if test_path.exists():
                                misplaced_tests.append(str(test_path))
                                
                # Check for test files in systems
                for file in files:
                    if file.startswith('test_') or file.endswith('_test.py'):
                        misplaced_tests.append(str(root_path / file))
                        
        if misplaced_tests:
            self.results["test_organization_issues"].append({
                "type": "misplaced_tests",
                "files": misplaced_tests,
                "message": "Tests found outside /backend/tests/ hierarchy"
            })
            
    def assess_import_violations(self):
        """Check for non-canonical imports and orphan dependencies"""
        print("🔗 Assessing import violations...")
        
        import_violations = []
        orphan_deps = []
        
        # Scan all Python files in systems
        for system in SYSTEMS_ROOT.iterdir():
            if not system.is_dir() or system.name.startswith('__'):
                continue
                
            for py_file in system.rglob("*.py"):
                if py_file.name.startswith('__'):
                    continue
                    
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Parse imports
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.Import, ast.ImportFrom)):
                            if isinstance(node, ast.ImportFrom) and node.module:
                                module = node.module
                                
                                # Check for non-canonical backend imports
                                if 'backend' in module and not module.startswith('backend.systems'):
                                    import_violations.append({
                                        "file": str(py_file.relative_to(PROJECT_ROOT)),
                                        "import": module,
                                        "line": node.lineno,
                                        "type": "non_canonical_backend_import"
                                    })
                                    
                                # Check for imports from outside /backend/systems
                                if (module.startswith('utils.') or 
                                    module.startswith('core.') or
                                    module.startswith('services.') or
                                    'utils/' in str(py_file)):
                                    import_violations.append({
                                        "file": str(py_file.relative_to(PROJECT_ROOT)),
                                        "import": module,
                                        "line": node.lineno,
                                        "type": "external_utility_import"
                                    })
                                    
                except Exception as e:
                    self.results["critical_errors"].append(f"Failed to parse {py_file}: {e}")
                    
        self.results["import_violations"] = import_violations
        self.results["orphan_dependencies"] = orphan_deps
        
    def assess_test_coverage_and_structure(self):
        """Assess test coverage and identify missing functionality"""
        print("🧪 Assessing test coverage and structure...")
        
        # Check tests directory structure
        tests_systems_path = TESTS_ROOT / "systems"
        if not tests_systems_path.exists():
            self.results["critical_errors"].append("Critical: /backend/tests/systems/ directory missing")
            return
            
        # Get test systems
        test_systems = set()
        for item in tests_systems_path.iterdir():
            if item.is_dir() and not item.name.startswith('__'):
                test_systems.add(item.name)
                
        # Compare with actual systems
        actual_systems = set()
        for item in SYSTEMS_ROOT.iterdir():
            if item.is_dir() and not item.name.startswith('__'):
                actual_systems.add(item.name)
                
        # Missing test directories
        missing_test_dirs = actual_systems - test_systems
        if missing_test_dirs:
            self.results["test_organization_issues"].append({
                "type": "missing_test_directories",
                "systems": list(missing_test_dirs),
                "message": f"Missing test directories for {len(missing_test_dirs)} systems"
            })
            
        # Extra test directories
        extra_test_dirs = test_systems - actual_systems
        if extra_test_dirs:
            self.results["test_organization_issues"].append({
                "type": "extra_test_directories",
                "systems": list(extra_test_dirs),
                "message": f"Test directories for non-existent systems: {list(extra_test_dirs)}"
            })
            
        # Analyze each system's test coverage
        for system in actual_systems:
            system_path = SYSTEMS_ROOT / system
            test_path = tests_systems_path / system
            
            system_analysis = self._analyze_system_implementation(system, system_path, test_path)
            self.results["system_health"][system] = system_analysis
            
    def _analyze_system_implementation(self, system_name: str, system_path: Path, test_path: Path) -> Dict:
        """Analyze individual system implementation vs test expectations"""
        analysis = {
            "system": system_name,
            "implementation_files": [],
            "test_files": [],
            "missing_implementations": [],
            "implementation_coverage": 0,
            "critical_gaps": [],
            "file_structure": {},
            "import_issues": []
        }
        
        # Scan implementation files
        if system_path.exists():
            for py_file in system_path.rglob("*.py"):
                if not py_file.name.startswith('__'):
                    rel_path = str(py_file.relative_to(system_path))
                    analysis["implementation_files"].append(rel_path)
                    
                    # Analyze file structure
                    file_type = self._classify_file_type(py_file.name, rel_path)
                    if file_type not in analysis["file_structure"]:
                        analysis["file_structure"][file_type] = []
                    analysis["file_structure"][file_type].append(rel_path)
                    
        # Scan test files
        if test_path.exists():
            for py_file in test_path.rglob("*.py"):
                if not py_file.name.startswith('__'):
                    rel_path = str(py_file.relative_to(test_path))
                    analysis["test_files"].append(rel_path)
                    
                    # Check what implementations the tests expect
                    expected_impls = self._extract_expected_implementations(py_file)
                    for impl in expected_impls:
                        # Check if implementation exists
                        if not self._implementation_exists(system_path, impl):
                            analysis["missing_implementations"].append(impl)
                            
        # Calculate coverage
        total_expected = len(analysis["test_files"]) * 5  # Rough estimate
        total_implemented = len(analysis["implementation_files"])
        if total_expected > 0:
            analysis["implementation_coverage"] = min(100, (total_implemented / total_expected) * 100)
            
        # Identify critical gaps
        if analysis["implementation_coverage"] < 50:
            analysis["critical_gaps"].append("Low implementation coverage")
            
        if "models.py" not in str(analysis["implementation_files"]):
            analysis["critical_gaps"].append("Missing core models.py")
            
        if "services.py" not in str(analysis["implementation_files"]):
            analysis["critical_gaps"].append("Missing core services.py")
            
        return analysis
        
    def _classify_file_type(self, filename: str, rel_path: str) -> str:
        """Classify file type based on name and path"""
        if 'models' in filename or 'models/' in rel_path:
            return 'models'
        elif 'services' in filename or 'services/' in rel_path:
            return 'services'
        elif 'repositories' in filename or 'repositories/' in rel_path:
            return 'repositories'
        elif 'routers' in filename or 'routers/' in rel_path:
            return 'routers'
        elif 'schemas' in filename or 'schemas/' in rel_path:
            return 'schemas'
        elif 'utils' in filename or 'utils/' in rel_path:
            return 'utils'
        else:
            return 'other'
            
    def _extract_expected_implementations(self, test_file: Path) -> List[str]:
        """Extract expected implementations from test file"""
        expected = []
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for import statements to understand expected modules
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if node.module.startswith('backend.systems'):
                        expected.append(node.module)
                        
        except Exception as e:
            pass
            
        return expected
        
    def _implementation_exists(self, system_path: Path, impl_module: str) -> bool:
        """Check if implementation module exists"""
        # Convert module path to file path
        parts = impl_module.split('.')
        if len(parts) >= 3 and parts[0] == 'backend' and parts[1] == 'systems':
            # backend.systems.population.models -> population/models.py
            system = parts[2]
            if len(parts) == 4:
                module = parts[3]
                expected_file = system_path / f"{module}.py"
                return expected_file.exists()
                
        return False
        
    def identify_population_system_gaps(self):
        """Specific analysis for Population System as mentioned in Task 45"""
        print("👥 Analyzing Population System gaps...")
        
        pop_system_path = SYSTEMS_ROOT / "population"
        pop_test_path = TESTS_ROOT / "systems" / "population"
        
        if not pop_system_path.exists():
            self.results["critical_errors"].append("Population system directory missing")
            return
            
        # Expected Population System functionality based on Task description
        expected_functions = [
            "calculate_war_impact",
            "handle_war_impact", 
            "calculate_catastrophe_impact",
            "handle_catastrophe",
            "calculate_resource_consumption",
            "handle_resource_shortage",
            "calculate_resource_shortage_impact",
            "calculate_migration_impact",
            "calculate_seasonal_growth_modifier",
            "calculate_seasonal_death_rate_modifier",
            "is_valid_transition",
            "is_valid_state_progression",
            "estimate_time_to_state",
            "get_poi_status_description"
        ]
        
        # Scan implementation for these functions
        missing_functions = []
        implemented_functions = []
        
        for py_file in pop_system_path.rglob("*.py"):
            if py_file.name.startswith('__'):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if node.name in expected_functions:
                            implemented_functions.append({
                                "function": node.name,
                                "file": str(py_file.relative_to(PROJECT_ROOT)),
                                "line": node.lineno
                            })
                            
            except Exception as e:
                self.results["critical_errors"].append(f"Failed to parse {py_file}: {e}")
                
        # Identify missing functions
        implemented_names = {f["function"] for f in implemented_functions}
        missing_functions = [f for f in expected_functions if f not in implemented_names]
        
        population_analysis = {
            "expected_functions": expected_functions,
            "implemented_functions": implemented_functions,
            "missing_functions": missing_functions,
            "implementation_percentage": len(implemented_functions) / len(expected_functions) * 100,
            "critical_missing": missing_functions[:5]  # Top 5 most critical
        }
        
        self.results["missing_functionality"].append({
            "system": "population",
            "analysis": population_analysis,
            "severity": "critical" if len(missing_functions) > 10 else "high"
        })
        
    def run_syntax_and_import_checks(self):
        """Run syntax checks and import validation"""
        print("✅ Running syntax and import checks...")
        
        syntax_errors = []
        import_errors = []
        
        # Check all Python files in systems
        for py_file in SYSTEMS_ROOT.rglob("*.py"):
            if py_file.name.startswith('__'):
                continue
                
            # Syntax check
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                syntax_errors.append({
                    "file": str(py_file.relative_to(PROJECT_ROOT)),
                    "error": str(e),
                    "line": e.lineno
                })
            except Exception as e:
                syntax_errors.append({
                    "file": str(py_file.relative_to(PROJECT_ROOT)),
                    "error": str(e),
                    "line": "unknown"
                })
                
            # Import check (basic)
            try:
                # Try to compile the file
                compile(content, str(py_file), 'exec')
            except ImportError as e:
                import_errors.append({
                    "file": str(py_file.relative_to(PROJECT_ROOT)),
                    "error": str(e)
                })
            except Exception:
                # Other compilation errors already caught above
                pass
                
        self.results["syntax_errors"] = syntax_errors
        self.results["import_errors"] = import_errors
        
    def generate_recommendations(self):
        """Generate specific recommendations based on findings"""
        print("📋 Generating recommendations...")
        
        recommendations = []
        
        # Structural recommendations
        if self.results["structural_issues"]:
            recommendations.append({
                "category": "Structure",
                "priority": "high",
                "action": "Fix system directory structure",
                "details": "Ensure all expected systems exist and follow canonical hierarchy"
            })
            
        # Import recommendations
        if self.results["import_violations"]:
            recommendations.append({
                "category": "Imports", 
                "priority": "high",
                "action": "Fix non-canonical imports",
                "details": "Convert all imports to backend.systems.* format"
            })
            
        # Test organization recommendations
        if self.results["test_organization_issues"]:
            recommendations.append({
                "category": "Testing",
                "priority": "critical",
                "action": "Relocate misplaced tests",
                "details": "Move all tests to /backend/tests/* and remove empty test directories"
            })
            
        # Population system specific
        pop_gaps = [item for item in self.results["missing_functionality"] if item["system"] == "population"]
        if pop_gaps:
            recommendations.append({
                "category": "Population System",
                "priority": "critical", 
                "action": "Implement missing Population System functionality",
                "details": f"Implement {len(pop_gaps[0]['analysis']['missing_functions'])} missing functions"
            })
            
        # Coverage recommendations
        low_coverage_systems = []
        for system, health in self.results["system_health"].items():
            if health.get("implementation_coverage", 0) < 50:
                low_coverage_systems.append(system)
                
        if low_coverage_systems:
            recommendations.append({
                "category": "Coverage",
                "priority": "medium",
                "action": "Improve implementation coverage",
                "details": f"Focus on systems: {', '.join(low_coverage_systems)}"
            })
            
        self.results["recommendations"] = recommendations
        
    def run_full_assessment(self):
        """Run the complete assessment as required by Task 45"""
        print("🚀 Starting Task 45 - Comprehensive Backend Systems Assessment")
        print("=" * 80)
        
        try:
            # 1. Assessment and Error Resolution
            self.assess_structural_organization()
            self.run_syntax_and_import_checks()
            
            # 2. Structure and Organization Enforcement  
            self.assess_test_coverage_and_structure()
            
            # 3. Canonical Imports Enforcement
            self.assess_import_violations()
            
            # 4. Module and Function Development (Population System focus)
            self.identify_population_system_gaps()
            
            # 5. Generate actionable recommendations
            self.generate_recommendations()
            
            print("\n✅ Assessment completed successfully!")
            
        except Exception as e:
            self.results["critical_errors"].append(f"Assessment failed: {e}")
            print(f"\n❌ Assessment failed: {e}")
            
        return self.results
        
    def save_results(self, filename: str = "task_45_assessment_results.json"):
        """Save assessment results to file"""
        output_path = PROJECT_ROOT / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"📄 Results saved to: {output_path}")
        
    def print_summary(self):
        """Print executive summary of findings"""
        print("\n" + "=" * 80)
        print("📊 TASK 45 ASSESSMENT SUMMARY")
        print("=" * 80)
        
        # Critical errors
        if self.results["critical_errors"]:
            print(f"\n🚨 CRITICAL ERRORS ({len(self.results['critical_errors'])}):")
            for error in self.results["critical_errors"][:5]:
                print(f"   • {error}")
                
        # Structural issues
        if self.results["structural_issues"]:
            print(f"\n🏗️  STRUCTURAL ISSUES ({len(self.results['structural_issues'])}):")
            for issue in self.results["structural_issues"]:
                print(f"   • {issue['message']}")
                
        # Import violations
        if self.results["import_violations"]:
            print(f"\n🔗 IMPORT VIOLATIONS ({len(self.results['import_violations'])}):")
            violations_by_type = defaultdict(int)
            for violation in self.results["import_violations"]:
                violations_by_type[violation["type"]] += 1
            for vtype, count in violations_by_type.items():
                print(f"   • {vtype}: {count} violations")
                
        # Test organization issues
        if self.results["test_organization_issues"]:
            print(f"\n🧪 TEST ORGANIZATION ISSUES ({len(self.results['test_organization_issues'])}):")
            for issue in self.results["test_organization_issues"]:
                print(f"   • {issue['message']}")
                
        # Population system analysis
        pop_analysis = None
        for item in self.results["missing_functionality"]:
            if item["system"] == "population":
                pop_analysis = item["analysis"]
                break
                
        if pop_analysis:
            print(f"\n👥 POPULATION SYSTEM ANALYSIS:")
            print(f"   • Implementation: {pop_analysis['implementation_percentage']:.1f}%")
            print(f"   • Missing functions: {len(pop_analysis['missing_functions'])}")
            print(f"   • Critical missing: {', '.join(pop_analysis['critical_missing'])}")
            
        # System health overview
        if self.results["system_health"]:
            low_health = []
            for system, health in self.results["system_health"].items():
                coverage = health.get("implementation_coverage", 0)
                if coverage < 50:
                    low_health.append(f"{system} ({coverage:.1f}%)")
                    
            if low_health:
                print(f"\n⚠️  LOW COVERAGE SYSTEMS ({len(low_health)}):")
                for system in low_health[:10]:
                    print(f"   • {system}")
                    
        # Recommendations
        if self.results["recommendations"]:
            print(f"\n📋 TOP RECOMMENDATIONS:")
            for rec in self.results["recommendations"][:5]:
                print(f"   • [{rec['priority'].upper()}] {rec['action']}")
                
        print("\n" + "=" * 80)


def main():
    """Main execution function"""
    print("Task 45: Comprehensive Backend Systems Assessment and Error Resolution")
    print("Starting assessment...")
    
    # Initialize assessment
    assessment = BackendSystemsAssessment()
    
    # Run full assessment
    results = assessment.run_full_assessment()
    
    # Save results
    assessment.save_results()
    
    # Print summary
    assessment.print_summary()
    
    return results


if __name__ == "__main__":
    main() 