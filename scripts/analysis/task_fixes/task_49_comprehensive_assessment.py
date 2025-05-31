#!/usr/bin/env python3
"""
Task 49: Comprehensive Backend System Assessment and Chaos System Implementation
Analysis of backend systems structure, test organization, imports, and preparation for chaos system
"""

import os
import sys
import json
import re
import ast
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class SystemAnalysis:
    """Analysis results for a system"""
    name: str
    has_models: bool = False
    has_services: bool = False
    has_repositories: bool = False
    has_routers: bool = False
    has_schemas: bool = False
    has_utils: bool = False
    has_init: bool = False
    models_count: int = 0
    services_count: int = 0
    repositories_count: int = 0
    routers_count: int = 0
    schemas_count: int = 0
    utils_count: int = 0
    files: List[str] = None
    issues: List[str] = None
    misplaced_tests: List[str] = None
    import_issues: List[str] = None
    missing_components: List[str] = None
    
    def __post_init__(self):
        if self.files is None:
            self.files = []
        if self.issues is None:
            self.issues = []
        if self.misplaced_tests is None:
            self.misplaced_tests = []
        if self.import_issues is None:
            self.import_issues = []
        if self.missing_components is None:
            self.missing_components = []

@dataclass
class ImportAnalysis:
    """Analysis of import patterns"""
    file_path: str
    imports: List[str] = None
    non_canonical_imports: List[str] = None
    missing_dependencies: List[str] = None
    circular_dependencies: List[str] = None
    
    def __post_init__(self):
        if self.imports is None:
            self.imports = []
        if self.non_canonical_imports is None:
            self.non_canonical_imports = []
        if self.missing_dependencies is None:
            self.missing_dependencies = []
        if self.circular_dependencies is None:
            self.circular_dependencies = []

@dataclass
class TestAnalysis:
    """Analysis of test structure"""
    system_name: str
    canonical_test_path: str
    has_canonical_tests: bool = False
    misplaced_test_paths: List[str] = None
    duplicate_tests: List[str] = None
    missing_test_coverage: List[str] = None
    test_files_count: int = 0
    
    def __post_init__(self):
        if self.misplaced_test_paths is None:
            self.misplaced_test_paths = []
        if self.duplicate_tests is None:
            self.duplicate_tests = []
        if self.missing_test_coverage is None:
            self.missing_test_coverage = []

class Task49ComprehensiveAssessment:
    """Comprehensive assessment for Task 49 backend systems analysis"""
    
    def __init__(self, backend_dir: str = "backend"):
        self.backend_dir = Path(backend_dir)
        self.systems_dir = self.backend_dir / "systems"
        self.tests_dir = self.backend_dir / "tests" / "systems"
        self.docs_dir = Path("docs")
        
        # Expected system structure based on Development Bible
        self.expected_systems = {
            'analytics', 'arc', 'auth_user', 'character', 'chaos', 'combat', 
            'crafting', 'data', 'dialogue', 'diplomacy', 'economy', 'equipment',
            'event_base', 'events', 'faction', 'integration', 'inventory', 'llm',
            'loot', 'magic', 'memory', 'motif', 'npc', 'poi', 'population',
            'quest', 'region', 'religion', 'rumor', 'shared', 'storage',
            'tension_war', 'time', 'world_generation', 'world_state'
        }
        
        # Expected components per system
        self.expected_components = ['models', 'services', 'repositories', 'routers', 'schemas']
        
        # Analysis results
        self.system_analyses: Dict[str, SystemAnalysis] = {}
        self.import_analyses: List[ImportAnalysis] = []
        self.test_analyses: Dict[str, TestAnalysis] = {}
        self.global_issues: List[str] = []
        
    def run_assessment(self) -> Dict[str, Any]:
        """Run comprehensive assessment of backend systems"""
        print("🔍 Starting Task 49 Comprehensive Backend Assessment...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'task': 'Task 49: Comprehensive Backend System Assessment',
            'backend_dir': str(self.backend_dir),
            'systems_analyzed': 0,
            'issues_found': 0,
            'systems': {},
            'imports': [],
            'tests': {},
            'global_issues': [],
            'chaos_system_status': {},
            'recommendations': []
        }
        
        try:
            # Step 1: Analyze systems structure
            print("📂 Analyzing systems structure...")
            self._analyze_systems_structure()
            
            # Step 2: Analyze test organization
            print("🧪 Analyzing test organization...")
            self._analyze_test_organization()
            
            # Step 3: Analyze imports
            print("📦 Analyzing import patterns...")
            self._analyze_imports()
            
            # Step 4: Special analysis for chaos system (Task 49 target)
            print("⚡ Analyzing chaos system for Task 49...")
            self._analyze_chaos_system()
            
            # Step 5: Generate recommendations
            print("💡 Generating recommendations...")
            self._generate_recommendations()
            
            # Compile results
            results.update({
                'systems_analyzed': len(self.system_analyses),
                'issues_found': sum(len(analysis.issues) for analysis in self.system_analyses.values()),
                'systems': {name: asdict(analysis) for name, analysis in self.system_analyses.items()},
                'imports': [asdict(analysis) for analysis in self.import_analyses],
                'tests': {name: asdict(analysis) for name, analysis in self.test_analyses.items()},
                'global_issues': self.global_issues,
                'chaos_system_status': self._get_chaos_system_status(),
                'recommendations': self._get_recommendations()
            })
            
            print(f"✅ Assessment complete! Found {results['issues_found']} issues across {results['systems_analyzed']} systems")
            
        except Exception as e:
            print(f"❌ Assessment failed: {e}")
            results['error'] = str(e)
            
        return results
    
    def _analyze_systems_structure(self):
        """Analyze the structure of all backend systems"""
        if not self.systems_dir.exists():
            self.global_issues.append(f"Systems directory does not exist: {self.systems_dir}")
            return
            
        # Check each expected system
        for system_name in self.expected_systems:
            system_path = self.systems_dir / system_name
            analysis = SystemAnalysis(name=system_name)
            
            if not system_path.exists():
                analysis.issues.append(f"System directory missing: {system_path}")
                analysis.missing_components.extend(self.expected_components)
            else:
                self._analyze_system_directory(system_path, analysis)
            
            self.system_analyses[system_name] = analysis
        
        # Check for unexpected systems
        if self.systems_dir.exists():
            for item in self.systems_dir.iterdir():
                if item.is_dir() and item.name not in self.expected_systems and item.name != '__pycache__':
                    self.global_issues.append(f"Unexpected system directory: {item}")
    
    def _analyze_system_directory(self, system_path: Path, analysis: SystemAnalysis):
        """Analyze individual system directory structure"""
        system_name = system_path.name
        
        # Check for __init__.py
        init_file = system_path / "__init__.py"
        analysis.has_init = init_file.exists()
        if not analysis.has_init:
            analysis.issues.append(f"Missing __init__.py in {system_path}")
        
        # Check expected components
        for component in self.expected_components:
            component_path = system_path / component
            
            if component == 'models':
                analysis.has_models = component_path.exists()
                if analysis.has_models:
                    analysis.models_count = len(list(component_path.glob("*.py")))
                else:
                    analysis.missing_components.append('models')
                    
            elif component == 'services':
                analysis.has_services = component_path.exists()
                if analysis.has_services:
                    analysis.services_count = len(list(component_path.glob("*.py")))
                else:
                    analysis.missing_components.append('services')
                    
            elif component == 'repositories':
                analysis.has_repositories = component_path.exists()
                if analysis.has_repositories:
                    analysis.repositories_count = len(list(component_path.glob("*.py")))
                else:
                    analysis.missing_components.append('repositories')
                    
            elif component == 'routers':
                analysis.has_routers = component_path.exists()
                if analysis.has_routers:
                    analysis.routers_count = len(list(component_path.glob("*.py")))
                else:
                    analysis.missing_components.append('routers')
                    
            elif component == 'schemas':
                analysis.has_schemas = component_path.exists()
                if analysis.has_schemas:
                    analysis.schemas_count = len(list(component_path.glob("*.py")))
                else:
                    analysis.missing_components.append('schemas')
        
        # Check for utils
        utils_path = system_path / "utils"
        analysis.has_utils = utils_path.exists()
        if analysis.has_utils:
            analysis.utils_count = len(list(utils_path.glob("*.py")))
        
        # Check for misplaced test directories
        test_dirs = list(system_path.glob("test*"))
        for test_dir in test_dirs:
            if test_dir.is_dir():
                analysis.misplaced_tests.append(str(test_dir))
                analysis.issues.append(f"Misplaced test directory: {test_dir}")
        
        # Collect all Python files
        for py_file in system_path.rglob("*.py"):
            analysis.files.append(str(py_file))
    
    def _analyze_test_organization(self):
        """Analyze test organization and identify misplaced tests"""
        if not self.tests_dir.exists():
            self.global_issues.append(f"Tests directory does not exist: {self.tests_dir}")
            return
        
        # Analyze canonical test structure
        for system_name in self.expected_systems:
            canonical_test_path = self.tests_dir / system_name
            analysis = TestAnalysis(
                system_name=system_name,
                canonical_test_path=str(canonical_test_path)
            )
            
            if canonical_test_path.exists():
                analysis.has_canonical_tests = True
                analysis.test_files_count = len(list(canonical_test_path.rglob("*.py")))
            else:
                analysis.missing_test_coverage.append(f"No canonical tests for {system_name}")
            
            # Check for misplaced tests in system directories
            system_path = self.systems_dir / system_name
            if system_path.exists():
                for test_path in system_path.rglob("test*.py"):
                    analysis.misplaced_test_paths.append(str(test_path))
                
                # Check for test directories in system folder
                for test_dir in system_path.glob("test*"):
                    if test_dir.is_dir():
                        for test_file in test_dir.rglob("*.py"):
                            analysis.misplaced_test_paths.append(str(test_file))
            
            self.test_analyses[system_name] = analysis
    
    def _analyze_imports(self):
        """Analyze import patterns across all Python files"""
        for system_name, analysis in self.system_analyses.items():
            for file_path in analysis.files:
                self._analyze_file_imports(file_path)
    
    def _analyze_file_imports(self, file_path: str):
        """Analyze imports in a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            analysis = ImportAnalysis(file_path=file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis.imports.append(alias.name)
                        self._check_import_canonicality(alias.name, analysis)
                        
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        full_import = f"{module}.{alias.name}" if module else alias.name
                        analysis.imports.append(full_import)
                        self._check_import_canonicality(module, analysis)
            
            if analysis.non_canonical_imports or analysis.missing_dependencies:
                self.import_analyses.append(analysis)
                
        except Exception as e:
            # Skip files that can't be parsed
            pass
    
    def _check_import_canonicality(self, import_name: str, analysis: ImportAnalysis):
        """Check if import follows canonical backend.systems.* format"""
        if not import_name:
            return
            
        # Check for non-canonical imports
        non_canonical_patterns = [
            r'^utils\.',
            r'^shared\.',
            r'^backend\.(?!systems\.)',
            r'^\w+(?<!backend)\.(?!systems)',
        ]
        
        for pattern in non_canonical_patterns:
            if re.match(pattern, import_name):
                analysis.non_canonical_imports.append(import_name)
                break
        
        # Check for missing backend.systems prefix
        if ('.' in import_name and 
            not import_name.startswith('backend.systems.') and 
            not import_name.startswith(('fastapi', 'pydantic', 'sqlalchemy', 'pytest', 'typing', 'datetime', 'asyncio', 'json', 'os', 'sys', 'pathlib', 're', 'uuid', 'enum'))):
            analysis.non_canonical_imports.append(import_name)
    
    def _analyze_chaos_system(self):
        """Special analysis for chaos system (Task 49 target)"""
        chaos_system = self.system_analyses.get('chaos')
        if not chaos_system:
            self.global_issues.append("Chaos system not found - required for Task 49")
            return
        
        # Check chaos system requirements from Task 49
        required_components = [
            'pressure_monitor',
            'chaos_calculator', 
            'event_trigger',
            'mitigation_factor',
            'cross_system_integration'
        ]
        
        chaos_path = self.systems_dir / "chaos"
        if chaos_path.exists():
            existing_files = [f.stem for f in chaos_path.rglob("*.py")]
            missing_components = [comp for comp in required_components if comp not in existing_files]
            
            if missing_components:
                chaos_system.issues.extend([f"Missing chaos component: {comp}" for comp in missing_components])
    
    def _get_chaos_system_status(self) -> Dict[str, Any]:
        """Get status of chaos system for Task 49"""
        chaos_analysis = self.system_analyses.get('chaos')
        if not chaos_analysis:
            return {'status': 'missing', 'issues': ['Chaos system directory not found']}
        
        return {
            'status': 'partial' if chaos_analysis.issues else 'ready',
            'has_models': chaos_analysis.has_models,
            'has_services': chaos_analysis.has_services,
            'has_repositories': chaos_analysis.has_repositories,
            'has_routers': chaos_analysis.has_routers,
            'missing_components': chaos_analysis.missing_components,
            'issues': chaos_analysis.issues,
            'files': chaos_analysis.files
        }
    
    def _generate_recommendations(self):
        """Generate recommendations based on analysis"""
        self.recommendations = []
        
        # System structure recommendations
        missing_systems = [name for name, analysis in self.system_analyses.items() 
                          if analysis.missing_components]
        if missing_systems:
            self.recommendations.append(f"Create missing components for systems: {', '.join(missing_systems)}")
        
        # Test organization recommendations
        misplaced_tests = [analysis for analysis in self.test_analyses.values() 
                          if analysis.misplaced_test_paths]
        if misplaced_tests:
            self.recommendations.append("Relocate misplaced test files to canonical /backend/tests/systems/ structure")
        
        # Import recommendations
        if self.import_analyses:
            self.recommendations.append("Fix non-canonical imports to use backend.systems.* format")
        
        # Chaos system recommendations
        chaos_status = self._get_chaos_system_status()
        if chaos_status['status'] != 'ready':
            self.recommendations.append("Implement missing chaos system components for Task 49")
    
    def _get_recommendations(self) -> List[str]:
        """Get all recommendations"""
        return getattr(self, 'recommendations', [])

def main():
    """Main execution"""
    print("🚀 Task 49: Comprehensive Backend System Assessment")
    print("=" * 60)
    
    assessment = Task49ComprehensiveAssessment()
    results = assessment.run_assessment()
    
    # Save results
    output_file = "task_49_assessment_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: {output_file}")
    
    # Print summary
    print("\n📊 ASSESSMENT SUMMARY")
    print("=" * 40)
    print(f"Systems analyzed: {results['systems_analyzed']}")
    print(f"Issues found: {results['issues_found']}")
    print(f"Global issues: {len(results['global_issues'])}")
    print(f"Import issues: {len(results['imports'])}")
    
    print("\n🎯 CHAOS SYSTEM STATUS (Task 49)")
    print("=" * 40)
    chaos_status = results['chaos_system_status']
    print(f"Status: {chaos_status.get('status', 'unknown')}")
    print(f"Missing components: {len(chaos_status.get('missing_components', []))}")
    print(f"Issues: {len(chaos_status.get('issues', []))}")
    
    print("\n💡 RECOMMENDATIONS")
    print("=" * 40)
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"{i}. {rec}")
    
    if results['issues_found'] > 0:
        print(f"\n⚠️  Found {results['issues_found']} issues requiring attention")
        return 1
    else:
        print("\n✅ No critical issues found - system ready for Task 49 implementation")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 