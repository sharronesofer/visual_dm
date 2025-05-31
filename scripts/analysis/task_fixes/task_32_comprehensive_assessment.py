#!/usr/bin/env python3
"""
Task 32: Comprehensive Backend Assessment and Reorganization
Analyzes the Visual DM backend structure and identifies issues for reorganization.
"""

import os
import json
import ast
import re
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Any
import subprocess

class BackendAssessment:
    def __init__(self, backend_path: str):
        self.backend_path = Path(backend_path)
        self.issues = defaultdict(list)
        self.recommendations = defaultdict(list)
        self.stats = defaultdict(int)
        self.systems_analysis = {}
        
    def run_comprehensive_assessment(self) -> Dict[str, Any]:
        """Run complete backend assessment"""
        print("🔍 Starting Comprehensive Backend Assessment...")
        
        # Core assessments
        self.analyze_directory_structure()
        self.analyze_systems_organization()
        self.analyze_import_patterns()
        self.analyze_test_structure()
        self.analyze_code_quality()
        self.analyze_duplication()
        self.check_development_bible_compliance()
        self.analyze_api_structure()
        
        # Generate comprehensive report
        report = self.generate_assessment_report()
        self.save_report(report)
        
        return report
    
    def analyze_directory_structure(self):
        """Analyze overall directory structure for issues"""
        print("📁 Analyzing directory structure...")
        
        # Check for canonical systems structure
        systems_path = self.backend_path / "systems"
        if not systems_path.exists():
            self.issues["structure"].append("Missing canonical systems directory")
            return
            
        # Count systems
        systems = [d for d in systems_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
        self.stats["total_systems"] = len(systems)
        
        # Check for duplicate systems directories
        duplicate_systems = []
        for root, dirs, files in os.walk(self.backend_path):
            if 'systems' in dirs and root != str(self.backend_path):
                duplicate_systems.append(root)
        
        if duplicate_systems:
            self.issues["structure"].extend([f"Duplicate systems directory: {path}" for path in duplicate_systems])
            self.recommendations["structure"].append("Consolidate all systems into single canonical /backend/systems directory")
        
        # Check for proper __init__.py files
        missing_init_files = []
        for system_dir in systems:
            if not (system_dir / "__init__.py").exists():
                missing_init_files.append(str(system_dir))
        
        if missing_init_files:
            self.issues["structure"].extend([f"Missing __init__.py: {path}" for path in missing_init_files])
    
    def analyze_systems_organization(self):
        """Analyze individual systems for proper organization"""
        print("🏗️ Analyzing systems organization...")
        
        systems_path = self.backend_path / "systems"
        if not systems_path.exists():
            return
            
        for system_dir in systems_path.iterdir():
            if not system_dir.is_dir() or system_dir.name.startswith('.'):
                continue
                
            system_name = system_dir.name
            system_analysis = {
                "files": [],
                "has_init": False,
                "has_main_module": False,
                "has_tests": False,
                "file_count": 0,
                "issues": []
            }
            
            # Analyze system files
            for file_path in system_dir.rglob("*.py"):
                system_analysis["files"].append(str(file_path.relative_to(system_dir)))
                system_analysis["file_count"] += 1
                
                if file_path.name == "__init__.py":
                    system_analysis["has_init"] = True
                elif file_path.name == f"{system_name}.py" or file_path.name == f"{system_name}_system.py":
                    system_analysis["has_main_module"] = True
            
            # Check for test files
            test_files = list(system_dir.rglob("test_*.py"))
            system_analysis["has_tests"] = len(test_files) > 0
            system_analysis["test_count"] = len(test_files)
            
            # Identify issues
            if not system_analysis["has_init"]:
                system_analysis["issues"].append("Missing __init__.py")
            if not system_analysis["has_main_module"]:
                system_analysis["issues"].append(f"Missing main module ({system_name}.py)")
            if not system_analysis["has_tests"]:
                system_analysis["issues"].append("No test files found")
            
            self.systems_analysis[system_name] = system_analysis
    
    def analyze_import_patterns(self):
        """Analyze import patterns for issues"""
        print("📦 Analyzing import patterns...")
        
        import_issues = []
        relative_imports = []
        circular_imports = []
        
        for py_file in self.backend_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for relative imports
                relative_pattern = r'from\s+\.+\w*\s+import|import\s+\.+\w*'
                if re.search(relative_pattern, content):
                    relative_imports.append(str(py_file.relative_to(self.backend_path)))
                
                # Check for non-canonical imports
                non_canonical_pattern = r'from\s+(?!backend\.systems\.).*systems\.'
                if re.search(non_canonical_pattern, content):
                    import_issues.append(str(py_file.relative_to(self.backend_path)))
                    
            except Exception as e:
                self.issues["imports"].append(f"Error reading {py_file}: {e}")
        
        if relative_imports:
            self.issues["imports"].extend([f"Relative import in: {path}" for path in relative_imports])
            self.recommendations["imports"].append("Replace relative imports with absolute imports using backend.systems.*")
        
        if import_issues:
            self.issues["imports"].extend([f"Non-canonical import in: {path}" for path in import_issues])
    
    def analyze_test_structure(self):
        """Analyze test structure and organization"""
        print("🧪 Analyzing test structure...")
        
        # Check main tests directory
        tests_path = self.backend_path / "tests"
        if not tests_path.exists():
            self.issues["tests"].append("Missing main tests directory")
            return
        
        # Check for test/systems structure
        test_systems_path = tests_path / "systems"
        if not test_systems_path.exists():
            self.issues["tests"].append("Missing tests/systems directory")
            return
        
        # Analyze test coverage for each system
        systems_path = self.backend_path / "systems"
        if systems_path.exists():
            for system_dir in systems_path.iterdir():
                if not system_dir.is_dir() or system_dir.name.startswith('.'):
                    continue
                
                system_name = system_dir.name
                test_system_path = test_systems_path / system_name
                
                if not test_system_path.exists():
                    self.issues["tests"].append(f"No tests directory for system: {system_name}")
                else:
                    # Count test files
                    test_files = list(test_system_path.rglob("test_*.py"))
                    self.stats[f"test_files_{system_name}"] = len(test_files)
                    
                    # Check for placeholder tests
                    placeholder_tests = []
                    for test_file in test_files:
                        try:
                            with open(test_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if 'assert True' in content and content.count('assert True') > content.count('assert '):
                                    placeholder_tests.append(str(test_file.relative_to(self.backend_path)))
                        except Exception:
                            pass
                    
                    if placeholder_tests:
                        self.issues["tests"].extend([f"Placeholder test: {path}" for path in placeholder_tests])
    
    def analyze_code_quality(self):
        """Analyze code quality issues"""
        print("🔍 Analyzing code quality...")
        
        syntax_errors = []
        empty_files = []
        large_files = []
        
        for py_file in self.backend_path.rglob("*.py"):
            try:
                # Check file size
                file_size = py_file.stat().st_size
                if file_size == 0:
                    empty_files.append(str(py_file.relative_to(self.backend_path)))
                elif file_size > 50000:  # 50KB threshold
                    large_files.append(str(py_file.relative_to(self.backend_path)))
                
                # Check syntax
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    syntax_errors.append(f"{py_file.relative_to(self.backend_path)}: {e}")
                    
            except Exception as e:
                self.issues["quality"].append(f"Error analyzing {py_file}: {e}")
        
        if syntax_errors:
            self.issues["quality"].extend([f"Syntax error: {error}" for error in syntax_errors])
        if empty_files:
            self.issues["quality"].extend([f"Empty file: {path}" for path in empty_files])
        if large_files:
            self.issues["quality"].extend([f"Large file (>50KB): {path}" for path in large_files])
    
    def analyze_duplication(self):
        """Analyze code duplication issues"""
        print("🔄 Analyzing duplication...")
        
        # Check for duplicate test files
        test_files = defaultdict(list)
        for test_file in self.backend_path.rglob("test_*.py"):
            filename = test_file.name
            test_files[filename].append(str(test_file.relative_to(self.backend_path)))
        
        duplicate_tests = {name: paths for name, paths in test_files.items() if len(paths) > 1}
        if duplicate_tests:
            for name, paths in duplicate_tests.items():
                self.issues["duplication"].append(f"Duplicate test file {name}: {', '.join(paths)}")
        
        # Check for duplicate system implementations
        system_files = defaultdict(list)
        for py_file in self.backend_path.rglob("*.py"):
            if py_file.parent.name == "systems" or "systems" in str(py_file):
                filename = py_file.name
                if not filename.startswith("test_") and filename != "__init__.py":
                    system_files[filename].append(str(py_file.relative_to(self.backend_path)))
        
        duplicate_systems = {name: paths for name, paths in system_files.items() if len(paths) > 1}
        if duplicate_systems:
            for name, paths in duplicate_systems.items():
                self.issues["duplication"].append(f"Duplicate system file {name}: {', '.join(paths)}")
    
    def check_development_bible_compliance(self):
        """Check compliance with development bible standards"""
        print("📖 Checking Development Bible compliance...")
        
        # Check for required system components
        required_components = [
            "analytics", "auth_user", "character", "combat", "dialogue",
            "economy", "events", "faction", "inventory", "quest", "world_state"
        ]
        
        systems_path = self.backend_path / "systems"
        if systems_path.exists():
            existing_systems = [d.name for d in systems_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
            missing_systems = [sys for sys in required_components if sys not in existing_systems]
            
            if missing_systems:
                self.issues["compliance"].extend([f"Missing required system: {sys}" for sys in missing_systems])
        
        # Check for proper API structure
        api_path = self.backend_path / "app" / "api"
        if not api_path.exists():
            self.issues["compliance"].append("Missing API directory structure")
    
    def analyze_api_structure(self):
        """Analyze API structure and organization"""
        print("🌐 Analyzing API structure...")
        
        # Look for API files
        api_files = []
        for py_file in self.backend_path.rglob("*.py"):
            if "api" in str(py_file) or "router" in py_file.name or "endpoint" in py_file.name:
                api_files.append(str(py_file.relative_to(self.backend_path)))
        
        self.stats["api_files"] = len(api_files)
        
        if len(api_files) == 0:
            self.issues["api"].append("No API files found")
            self.recommendations["api"].append("Create proper FastAPI structure with routers for each system")
    
    def generate_assessment_report(self) -> Dict[str, Any]:
        """Generate comprehensive assessment report"""
        print("📊 Generating assessment report...")
        
        # Calculate severity scores
        critical_issues = len(self.issues["structure"]) + len(self.issues["compliance"])
        major_issues = len(self.issues["imports"]) + len(self.issues["api"])
        minor_issues = len(self.issues["quality"]) + len(self.issues["duplication"])
        
        # Generate recommendations based on issues
        if self.issues["structure"]:
            self.recommendations["structure"].append("Consolidate all systems into canonical /backend/systems structure")
        if self.issues["imports"]:
            self.recommendations["imports"].append("Standardize all imports to use backend.systems.* format")
        if self.issues["tests"]:
            self.recommendations["tests"].append("Replace placeholder tests with real implementation")
        if self.issues["duplication"]:
            self.recommendations["duplication"].append("Remove duplicate files and consolidate functionality")
        
        report = {
            "assessment_summary": {
                "total_systems": self.stats["total_systems"],
                "critical_issues": critical_issues,
                "major_issues": major_issues,
                "minor_issues": minor_issues,
                "total_issues": sum(len(issues) for issues in self.issues.values()),
                "compliance_score": max(0, 100 - (critical_issues * 10 + major_issues * 5 + minor_issues * 2))
            },
            "systems_analysis": self.systems_analysis,
            "issues_by_category": dict(self.issues),
            "recommendations_by_category": dict(self.recommendations),
            "statistics": dict(self.stats),
            "priority_actions": self.generate_priority_actions()
        }
        
        return report
    
    def generate_priority_actions(self) -> List[Dict[str, Any]]:
        """Generate prioritized action items"""
        actions = []
        
        # Critical actions
        if self.issues["structure"]:
            actions.append({
                "priority": "CRITICAL",
                "action": "Fix Directory Structure",
                "description": "Consolidate systems into canonical structure",
                "estimated_effort": "2-4 hours",
                "impact": "Enables proper imports and organization"
            })
        
        if self.issues["compliance"]:
            actions.append({
                "priority": "CRITICAL", 
                "action": "Development Bible Compliance",
                "description": "Implement missing required systems",
                "estimated_effort": "1-2 days",
                "impact": "Ensures complete system coverage"
            })
        
        # Major actions
        if self.issues["imports"]:
            actions.append({
                "priority": "MAJOR",
                "action": "Standardize Imports",
                "description": "Fix all non-canonical import patterns",
                "estimated_effort": "4-6 hours",
                "impact": "Improves maintainability and prevents circular imports"
            })
        
        if self.issues["tests"]:
            actions.append({
                "priority": "MAJOR",
                "action": "Implement Real Tests",
                "description": "Replace placeholder tests with actual validation",
                "estimated_effort": "2-3 days",
                "impact": "Enables proper testing and validation"
            })
        
        # Minor actions
        if self.issues["duplication"]:
            actions.append({
                "priority": "MINOR",
                "action": "Remove Duplicates",
                "description": "Clean up duplicate files and consolidate",
                "estimated_effort": "2-3 hours",
                "impact": "Reduces confusion and maintenance overhead"
            })
        
        return actions
    
    def save_report(self, report: Dict[str, Any]):
        """Save assessment report to file"""
        report_path = self.backend_path.parent / "task_32_assessment_results.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Assessment report saved to: {report_path}")
        
        # Also create a summary markdown file
        self.create_summary_markdown(report)
    
    def create_summary_markdown(self, report: Dict[str, Any]):
        """Create a human-readable summary in markdown"""
        summary_path = self.backend_path.parent / "TASK_32_ASSESSMENT_SUMMARY.md"
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("# Task 32: Backend Assessment Summary\n\n")
            
            # Overview
            summary = report["assessment_summary"]
            f.write(f"## Overview\n\n")
            f.write(f"- **Total Systems**: {summary['total_systems']}\n")
            f.write(f"- **Compliance Score**: {summary['compliance_score']}/100\n")
            f.write(f"- **Total Issues**: {summary['total_issues']}\n")
            f.write(f"  - Critical: {summary['critical_issues']}\n")
            f.write(f"  - Major: {summary['major_issues']}\n")
            f.write(f"  - Minor: {summary['minor_issues']}\n\n")
            
            # Priority Actions
            f.write("## Priority Actions\n\n")
            for action in report["priority_actions"]:
                f.write(f"### {action['priority']}: {action['action']}\n")
                f.write(f"- **Description**: {action['description']}\n")
                f.write(f"- **Estimated Effort**: {action['estimated_effort']}\n")
                f.write(f"- **Impact**: {action['impact']}\n\n")
            
            # Issues by Category
            f.write("## Issues by Category\n\n")
            for category, issues in report["issues_by_category"].items():
                if issues:
                    f.write(f"### {category.title()}\n")
                    for issue in issues[:10]:  # Limit to first 10 issues
                        f.write(f"- {issue}\n")
                    if len(issues) > 10:
                        f.write(f"- ... and {len(issues) - 10} more\n")
                    f.write("\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            for category, recommendations in report["recommendations_by_category"].items():
                if recommendations:
                    f.write(f"### {category.title()}\n")
                    for rec in recommendations:
                        f.write(f"- {rec}\n")
                    f.write("\n")
        
        print(f"📄 Summary saved to: {summary_path}")

def main():
    """Main execution function"""
    backend_path = "/Users/Sharrone/Visual_DM/backend"
    
    if not os.path.exists(backend_path):
        print(f"❌ Backend path not found: {backend_path}")
        return
    
    print("🚀 Starting Task 32: Comprehensive Backend Assessment")
    print("=" * 60)
    
    assessor = BackendAssessment(backend_path)
    report = assessor.run_comprehensive_assessment()
    
    print("\n" + "=" * 60)
    print("✅ Assessment Complete!")
    print(f"📊 Found {report['assessment_summary']['total_issues']} total issues")
    print(f"🎯 Compliance Score: {report['assessment_summary']['compliance_score']}/100")
    print("\nNext steps:")
    print("1. Review the detailed assessment report")
    print("2. Address critical issues first")
    print("3. Implement recommended fixes")
    print("4. Re-run assessment to verify improvements")

if __name__ == "__main__":
    main() 