#!/usr/bin/env python3
"""
Monolithic File Analysis for Refactoring
Identifies large files, analyzes responsibilities, dependencies, and coupling
Creates comprehensive refactoring plan for Task 54
"""

import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
import json
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict

@dataclass
class FileAnalysis:
    """Analysis results for a single file"""
    path: str
    lines: int
    classes: List[str]
    functions: List[str]
    imports: List[str]
    dependencies: Set[str]
    responsibilities: List[str]
    complexity_score: int
    refactoring_priority: str
    suggested_modules: List[Dict[str, Any]]

@dataclass
class RefactoringPlan:
    """Complete refactoring plan"""
    target_files: List[FileAnalysis]
    modular_architecture: Dict[str, List[str]]
    dependency_map: Dict[str, Set[str]]
    risk_assessment: Dict[str, str]
    implementation_phases: List[Dict[str, Any]]

class MonolithicFileAnalyzer:
    """Analyzes backend systems for monolithic files requiring refactoring"""
    
    def __init__(self, backend_path: str = "systems"):
        self.backend_path = Path(backend_path)
        self.analysis_results = []
        self.refactoring_plan = None
        
        # Define responsibility patterns
        self.responsibility_patterns = {
            'Database Operations': [
                r'create_\w+', r'get_\w+', r'update_\w+', r'delete_\w+',
                r'find_\w+', r'save_\w+', r'load_\w+', r'query_\w+'
            ],
            'Business Logic': [
                r'calculate_\w+', r'process_\w+', r'validate_\w+', r'generate_\w+',
                r'execute_\w+', r'handle_\w+', r'manage_\w+'
            ],
            'API/Routing': [
                r'@router\.\w+', r'@app\.\w+', r'async def \w+.*request',
                r'FastAPI', r'HTTPException'
            ],
            'Data Models': [
                r'class \w+\(.*BaseModel\)', r'class \w+\(.*Model\)',
                r'Field\(', r'validator'
            ],
            'Utilities': [
                r'def \w+_utils?', r'def \w+_helper', r'def format_\w+',
                r'def parse_\w+', r'def convert_\w+'
            ],
            'Event Handling': [
                r'def on_\w+', r'def handle_\w+_event', r'EventDispatcher',
                r'emit_\w+', r'subscribe_\w+'
            ],
            'File I/O': [
                r'open\(', r'\.read\(\)', r'\.write\(\)', r'json\.load',
                r'json\.dump', r'pickle\.'
            ],
            'Configuration': [
                r'config\w*', r'settings\w*', r'env\w*', r'\.env',
                r'Config', r'Settings'
            ]
        }

    def analyze_file(self, file_path: Path) -> FileAnalysis:
        """Analyze a single Python file for refactoring opportunities"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Count lines
            lines = len(content.splitlines())
            
            # Extract classes and functions
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            
            # Extract imports
            imports = self._extract_imports(tree)
            
            # Analyze dependencies
            dependencies = self._analyze_dependencies(content, imports)
            
            # Identify responsibilities
            responsibilities = self._identify_responsibilities(content)
            
            # Calculate complexity score
            complexity_score = self._calculate_complexity(content, classes, functions)
            
            # Determine refactoring priority
            priority = self._determine_priority(lines, complexity_score, len(responsibilities))
            
            # Suggest modular breakdown
            suggested_modules = self._suggest_modules(content, classes, functions, responsibilities)
            
            return FileAnalysis(
                path=str(file_path),
                lines=lines,
                classes=classes,
                functions=functions,
                imports=imports,
                dependencies=dependencies,
                responsibilities=responsibilities,
                complexity_score=complexity_score,
                refactoring_priority=priority,
                suggested_modules=suggested_modules
            )
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract all import statements"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports.extend([f"{module}.{alias.name}" for alias in node.names])
        return imports

    def _analyze_dependencies(self, content: str, imports: List[str]) -> Set[str]:
        """Analyze external dependencies"""
        dependencies = set()
        
        # Backend system dependencies
        for imp in imports:
            if 'backend.systems' in imp:
                system = imp.split('.')[2] if len(imp.split('.')) > 2 else imp
                dependencies.add(system)
        
        # Third-party dependencies
        third_party = ['fastapi', 'pydantic', 'sqlalchemy', 'firebase', 'pytest']
        for tp in third_party:
            if tp in content.lower():
                dependencies.add(tp)
                
        return dependencies

    def _identify_responsibilities(self, content: str) -> List[str]:
        """Identify different responsibilities in the file"""
        responsibilities = []
        
        for responsibility, patterns in self.responsibility_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    responsibilities.append(responsibility)
                    break
        
        return list(set(responsibilities))

    def _calculate_complexity(self, content: str, classes: List[str], functions: List[str]) -> int:
        """Calculate complexity score based on various metrics"""
        score = 0
        
        # Line count factor
        lines = len(content.splitlines())
        score += min(lines // 100, 50)  # Max 50 points for lines
        
        # Function/class count factor
        score += min(len(functions), 30)  # Max 30 points for functions
        score += min(len(classes) * 5, 20)  # Max 20 points for classes
        
        # Nesting complexity
        nesting_patterns = [r'if.*:', r'for.*:', r'while.*:', r'try:', r'with.*:']
        for pattern in nesting_patterns:
            score += min(len(re.findall(pattern, content)), 10)
        
        # Import complexity
        import_lines = [line for line in content.splitlines() if line.strip().startswith(('import ', 'from '))]
        score += min(len(import_lines), 15)
        
        return min(score, 100)  # Cap at 100

    def _determine_priority(self, lines: int, complexity: int, responsibilities: int) -> str:
        """Determine refactoring priority based on metrics"""
        if lines > 2000 or complexity > 80 or responsibilities > 6:
            return "CRITICAL"
        elif lines > 1500 or complexity > 60 or responsibilities > 4:
            return "HIGH"
        elif lines > 1000 or complexity > 40 or responsibilities > 3:
            return "MEDIUM"
        else:
            return "LOW"

    def _suggest_modules(self, content: str, classes: List[str], functions: List[str], responsibilities: List[str]) -> List[Dict[str, Any]]:
        """Suggest how to break down the file into modules"""
        modules = []
        
        # Group functions by responsibility patterns
        function_groups = defaultdict(list)
        
        for func in functions:
            for responsibility, patterns in self.responsibility_patterns.items():
                for pattern in patterns:
                    if re.search(pattern.replace('def ', '').replace('class ', ''), func):
                        function_groups[responsibility].append(func)
                        break
                else:
                    continue
                break
        
        # Create module suggestions
        for responsibility, funcs in function_groups.items():
            if funcs:
                module_name = responsibility.lower().replace(' ', '_').replace('/', '_')
                modules.append({
                    'module_name': f"{module_name}.py",
                    'responsibility': responsibility,
                    'functions': funcs,
                    'estimated_lines': len(funcs) * 20,  # Rough estimate
                    'priority': 'high' if len(funcs) > 5 else 'medium'
                })
        
        # Add class-based modules
        if classes:
            modules.append({
                'module_name': 'models.py',
                'responsibility': 'Data Models',
                'functions': [],
                'classes': classes,
                'estimated_lines': len(classes) * 30,
                'priority': 'high' if len(classes) > 3 else 'medium'
            })
        
        return modules

    def scan_systems(self, min_lines: int = 500) -> List[FileAnalysis]:
        """Scan all backend systems for files exceeding minimum lines"""
        target_files = []
        
        # Get all Python files
        for py_file in self.backend_path.rglob("*.py"):
            if py_file.name.startswith('__'):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    line_count = len(f.readlines())
                
                if line_count >= min_lines:
                    analysis = self.analyze_file(py_file)
                    if analysis:
                        target_files.append(analysis)
                        print(f"Analyzed: {py_file.relative_to(self.backend_path)} ({line_count} lines)")
                        
            except Exception as e:
                print(f"Error reading {py_file}: {e}")
        
        # Sort by priority and size
        target_files.sort(key=lambda x: (
            ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].index(x.refactoring_priority),
            -x.lines
        ))
        
        return target_files

    def create_refactoring_plan(self, target_files: List[FileAnalysis]) -> RefactoringPlan:
        """Create comprehensive refactoring plan"""
        
        # Create modular architecture map
        modular_architecture = {}
        for analysis in target_files:
            system_name = Path(analysis.path).parts[-2]  # Get system directory name
            modular_architecture[system_name] = []
            
            for module in analysis.suggested_modules:
                modular_architecture[system_name].append(module['module_name'])
        
        # Create dependency map
        dependency_map = {}
        for analysis in target_files:
            file_key = str(Path(analysis.path).relative_to(self.backend_path))
            dependency_map[file_key] = analysis.dependencies
        
        # Risk assessment
        risk_assessment = {}
        for analysis in target_files:
            file_key = str(Path(analysis.path).relative_to(self.backend_path))
            
            # Assess risk based on dependencies and complexity
            risk = "LOW"
            if len(analysis.dependencies) > 10:
                risk = "HIGH"
            elif len(analysis.dependencies) > 5 or analysis.complexity_score > 70:
                risk = "MEDIUM"
            
            risk_assessment[file_key] = risk
        
        # Implementation phases
        phases = []
        
        # Phase 1: Critical priority files
        critical_files = [f for f in target_files if f.refactoring_priority == "CRITICAL"]
        if critical_files:
            phases.append({
                'phase': 1,
                'description': 'Refactor critical monolithic files',
                'files': [f.path for f in critical_files],
                'estimated_effort': 'High',
                'dependencies': [],
                'risks': ['API breaking changes', 'Test coverage gaps']
            })
        
        # Phase 2: High priority files
        high_files = [f for f in target_files if f.refactoring_priority == "HIGH"]
        if high_files:
            phases.append({
                'phase': 2,
                'description': 'Refactor high priority monolithic files',
                'files': [f.path for f in high_files],
                'estimated_effort': 'Medium-High',
                'dependencies': ['Phase 1 completion'],
                'risks': ['Integration complexity', 'Performance impact']
            })
        
        # Phase 3: Medium priority files
        medium_files = [f for f in target_files if f.refactoring_priority == "MEDIUM"]
        if medium_files:
            phases.append({
                'phase': 3,
                'description': 'Refactor medium priority files',
                'files': [f.path for f in medium_files],
                'estimated_effort': 'Medium',
                'dependencies': ['Phase 2 completion'],
                'risks': ['Time constraints', 'Resource allocation']
            })
        
        return RefactoringPlan(
            target_files=target_files,
            modular_architecture=modular_architecture,
            dependency_map=dependency_map,
            risk_assessment=risk_assessment,
            implementation_phases=phases
        )

    def generate_report(self, output_file: str = "backend/task54_refactoring_analysis.json"):
        """Generate comprehensive analysis report"""
        
        print("🔍 Scanning backend systems for monolithic files...")
        target_files = self.scan_systems(min_lines=500)
        
        print(f"\n📊 Found {len(target_files)} files requiring analysis")
        
        print("\n🛠️ Creating refactoring plan...")
        self.refactoring_plan = self.create_refactoring_plan(target_files)
        
        # Prepare report data
        report_data = {
            'analysis_summary': {
                'total_files_analyzed': len(target_files),
                'critical_priority': len([f for f in target_files if f.refactoring_priority == "CRITICAL"]),
                'high_priority': len([f for f in target_files if f.refactoring_priority == "HIGH"]),
                'medium_priority': len([f for f in target_files if f.refactoring_priority == "MEDIUM"]),
                'low_priority': len([f for f in target_files if f.refactoring_priority == "LOW"])
            },
            'target_files': [asdict(f) for f in target_files],
            'refactoring_plan': asdict(self.refactoring_plan)
        }
        
        # Save report
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n✅ Analysis complete! Report saved to: {output_file}")
        
        # Print summary
        self._print_summary(target_files)
        
        return report_data

    def _print_summary(self, target_files: List[FileAnalysis]):
        """Print analysis summary to console"""
        print("\n" + "="*80)
        print("🎯 MONOLITHIC FILES REFACTORING ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"\n📈 PRIORITY BREAKDOWN:")
        priority_counts = Counter(f.refactoring_priority for f in target_files)
        for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = priority_counts.get(priority, 0)
            print(f"  {priority:8}: {count:2} files")
        
        print(f"\n🏗️ TOP REFACTORING TARGETS:")
        for i, analysis in enumerate(target_files[:10], 1):
            path_short = "/".join(Path(analysis.path).parts[-2:])
            print(f"  {i:2}. {path_short:<40} ({analysis.lines:4} lines, {analysis.refactoring_priority:8})")
        
        print(f"\n📋 MOST COMMON RESPONSIBILITIES:")
        all_responsibilities = []
        for f in target_files:
            all_responsibilities.extend(f.responsibilities)
        resp_counts = Counter(all_responsibilities)
        for resp, count in resp_counts.most_common(5):
            print(f"  {resp:<25}: {count} files")
        
        print(f"\n🔗 MOST COUPLED SYSTEMS:")
        all_deps = []
        for f in target_files:
            all_deps.extend(f.dependencies)
        dep_counts = Counter(all_deps)
        for dep, count in dep_counts.most_common(5):
            print(f"  {dep:<25}: {count} dependencies")

if __name__ == "__main__":
    analyzer = MonolithicFileAnalyzer()
    analyzer.generate_report() 