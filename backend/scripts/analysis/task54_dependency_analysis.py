#!/usr/bin/env python3
"""
Dependency Analysis for Monolithic File Refactoring
Maps cross-system dependencies and identifies coupling issues
Supports Task 54 refactoring planning
"""

import ast
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter
import networkx as nx

class DependencyAnalyzer:
    """Analyzes dependencies and coupling between backend systems"""
    
    def __init__(self, backend_path: str = "backend/systems"):
        self.backend_path = Path(backend_path)
        self.dependency_graph = nx.DiGraph()
        self.coupling_matrix = defaultdict(lambda: defaultdict(int))
        self.circular_dependencies = []
        self.high_coupling_pairs = []
        
    def analyze_file_dependencies(self, file_path: Path) -> Dict[str, any]:
        """Analyze dependencies for a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Extract imports
            imports = self._extract_detailed_imports(tree)
            
            # Analyze function calls
            function_calls = self._extract_function_calls(tree)
            
            # Find system dependencies
            system_deps = self._identify_system_dependencies(imports, content)
            
            # Calculate coupling metrics
            coupling_score = self._calculate_coupling_score(imports, function_calls)
            
            return {
                'file': str(file_path.relative_to(self.backend_path)),
                'imports': imports,
                'function_calls': function_calls,
                'system_dependencies': system_deps,
                'coupling_score': coupling_score,
                'lines': len(content.splitlines())
            }
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None

    def _extract_detailed_imports(self, tree: ast.AST) -> List[Dict[str, str]]:
        """Extract detailed import information"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'alias': alias.asname,
                        'from_module': None
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append({
                        'type': 'from_import',
                        'module': alias.name,
                        'alias': alias.asname,
                        'from_module': module
                    })
        
        return imports

    def _extract_function_calls(self, tree: ast.AST) -> List[str]:
        """Extract function calls to identify runtime dependencies"""
        function_calls = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    function_calls.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    # Handle method calls like obj.method()
                    if isinstance(node.func.value, ast.Name):
                        function_calls.append(f"{node.func.value.id}.{node.func.attr}")
        
        return function_calls

    def _identify_system_dependencies(self, imports: List[Dict], content: str) -> Dict[str, List[str]]:
        """Identify which backend systems this file depends on"""
        system_deps = defaultdict(list)
        
        for imp in imports:
            module = imp.get('from_module') or imp.get('module', '')
            
            if 'backend.systems.' in module:
                parts = module.split('.')
                if len(parts) >= 3:
                    system = parts[2]
                    system_deps[system].append(imp['module'])
        
        # Also check for runtime dependencies in strings
        system_patterns = [
            'combat', 'diplomacy', 'motif', 'analytics', 'character',
            'world_generation', 'inventory', 'equipment', 'quest',
            'faction', 'npc', 'population', 'region', 'memory'
        ]
        
        for system in system_patterns:
            if system in content and system not in system_deps:
                # Check if it's likely a runtime dependency
                if re.search(rf'{system}[._]', content):
                    system_deps[system].append('runtime_reference')
        
        return dict(system_deps)

    def _calculate_coupling_score(self, imports: List[Dict], function_calls: List[str]) -> int:
        """Calculate coupling score for the file"""
        score = 0
        
        # Import coupling
        backend_imports = len([imp for imp in imports 
                              if 'backend.systems' in (imp.get('from_module') or imp.get('module', ''))])
        score += backend_imports * 2
        
        # External library coupling
        external_imports = len([imp for imp in imports 
                               if not (imp.get('from_module') or imp.get('module', '')).startswith('backend')])
        score += external_imports
        
        # Function call coupling
        external_calls = len([call for call in function_calls if '.' in call])
        score += external_calls
        
        return score

    def build_dependency_graph(self, critical_files: List[str]) -> nx.DiGraph:
        """Build dependency graph for critical files"""
        
        print("🔍 Building dependency graph for critical files...")
        
        file_dependencies = {}
        
        # Analyze each critical file
        for file_pattern in critical_files:
            file_paths = list(self.backend_path.rglob(file_pattern))
            
            for file_path in file_paths:
                if file_path.is_file() and file_path.suffix == '.py':
                    analysis = self.analyze_file_dependencies(file_path)
                    if analysis:
                        file_dependencies[analysis['file']] = analysis
        
        # Build graph
        for file_name, analysis in file_dependencies.items():
            self.dependency_graph.add_node(file_name, **analysis)
            
            # Add edges for dependencies
            for system, deps in analysis['system_dependencies'].items():
                for other_file in file_dependencies:
                    if system in other_file:
                        self.dependency_graph.add_edge(file_name, other_file, 
                                                     weight=len(deps))
        
        return self.dependency_graph

    def find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies in the graph"""
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            self.circular_dependencies = cycles
            return cycles
        except Exception as e:
            print(f"Error finding cycles: {e}")
            return []

    def calculate_coupling_matrix(self) -> Dict[str, Dict[str, int]]:
        """Calculate coupling matrix between systems"""
        
        systems = set()
        file_to_system = {}
        
        # Map files to systems
        for node in self.dependency_graph.nodes():
            parts = node.split('/')
            if len(parts) >= 2:
                system = parts[0]
                systems.add(system)
                file_to_system[node] = system
        
        # Calculate coupling between systems
        for edge in self.dependency_graph.edges(data=True):
            source_file, target_file = edge[0], edge[1]
            weight = edge[2].get('weight', 1)
            
            source_system = file_to_system.get(source_file)
            target_system = file_to_system.get(target_file)
            
            if source_system and target_system and source_system != target_system:
                self.coupling_matrix[source_system][target_system] += weight
        
        return dict(self.coupling_matrix)

    def identify_high_coupling_pairs(self, threshold: int = 5) -> List[Tuple[str, str, int]]:
        """Identify pairs of systems with high coupling"""
        
        high_coupling = []
        
        for source_system, targets in self.coupling_matrix.items():
            for target_system, coupling_score in targets.items():
                if coupling_score >= threshold:
                    high_coupling.append((source_system, target_system, coupling_score))
        
        # Sort by coupling score descending
        high_coupling.sort(key=lambda x: x[2], reverse=True)
        self.high_coupling_pairs = high_coupling
        
        return high_coupling

    def suggest_refactoring_order(self) -> List[str]:
        """Suggest optimal refactoring order based on dependencies"""
        
        try:
            # Use topological sort to suggest order
            topo_order = list(nx.topological_sort(self.dependency_graph))
            return topo_order
        except nx.NetworkXError:
            # If cycles exist, use approximate ordering
            print("⚠️ Circular dependencies detected, using approximate ordering")
            
            # Calculate in-degree (how many things depend on this file)
            in_degrees = dict(self.dependency_graph.in_degree())
            
            # Sort by in-degree (files with fewer dependencies should be refactored first)
            ordered_files = sorted(in_degrees.items(), key=lambda x: x[1])
            
            return [file for file, _ in ordered_files]

    def generate_refactoring_recommendations(self) -> Dict[str, any]:
        """Generate comprehensive refactoring recommendations"""
        
        # Analyze most coupled systems
        coupling_matrix = self.calculate_coupling_matrix()
        high_coupling = self.identify_high_coupling_pairs()
        
        # Find circular dependencies
        cycles = self.find_circular_dependencies()
        
        # Suggest refactoring order
        refactor_order = self.suggest_refactoring_order()
        
        # Identify shared utilities that should be extracted
        shared_candidates = self._identify_shared_utility_candidates()
        
        recommendations = {
            'coupling_analysis': {
                'coupling_matrix': coupling_matrix,
                'high_coupling_pairs': high_coupling,
                'most_coupled_systems': self._get_most_coupled_systems(coupling_matrix)
            },
            'dependency_issues': {
                'circular_dependencies': cycles,
                'cycle_count': len(cycles),
                'problematic_files': self._identify_problematic_files(cycles)
            },
            'refactoring_strategy': {
                'recommended_order': refactor_order,
                'shared_utilities': shared_candidates,
                'decoupling_priorities': self._prioritize_decoupling_efforts(high_coupling)
            },
            'architectural_suggestions': {
                'interface_abstractions': self._suggest_interface_abstractions(high_coupling),
                'event_driven_opportunities': self._identify_event_opportunities(coupling_matrix),
                'shared_infrastructure': self._suggest_shared_infrastructure()
            }
        }
        
        return recommendations

    def _identify_shared_utility_candidates(self) -> List[Dict[str, any]]:
        """Identify functions that appear in multiple systems and should be shared"""
        
        # This would require deeper analysis of function definitions
        # For now, return common patterns
        candidates = [
            {
                'utility_type': 'Mathematical Operations',
                'functions': ['calculate_distance', 'apply_modifiers', 'random_weighted_choice'],
                'systems_using': ['combat', 'world_generation', 'character'],
                'priority': 'high'
            },
            {
                'utility_type': 'Data Validation',
                'functions': ['validate_coordinates', 'validate_character_data', 'sanitize_input'],
                'systems_using': ['character', 'world_generation', 'inventory'],
                'priority': 'high'
            },
            {
                'utility_type': 'Event Processing',
                'functions': ['emit_event', 'register_handler', 'process_event_queue'],
                'systems_using': ['combat', 'diplomacy', 'faction', 'quest'],
                'priority': 'medium'
            }
        ]
        
        return candidates

    def _get_most_coupled_systems(self, coupling_matrix: Dict) -> List[Tuple[str, int]]:
        """Get systems with highest coupling scores"""
        
        system_totals = defaultdict(int)
        
        for source, targets in coupling_matrix.items():
            for target, score in targets.items():
                system_totals[source] += score
                system_totals[target] += score
        
        sorted_systems = sorted(system_totals.items(), key=lambda x: x[1], reverse=True)
        return sorted_systems[:10]

    def _identify_problematic_files(self, cycles: List[List[str]]) -> List[str]:
        """Identify files that appear in multiple cycles"""
        
        file_cycle_count = Counter()
        
        for cycle in cycles:
            for file in cycle:
                file_cycle_count[file] += 1
        
        # Return files that appear in multiple cycles
        return [file for file, count in file_cycle_count.items() if count > 1]

    def _prioritize_decoupling_efforts(self, high_coupling: List[Tuple]) -> List[Dict[str, any]]:
        """Prioritize which coupling relationships to address first"""
        
        priorities = []
        
        for source, target, score in high_coupling[:5]:  # Top 5
            priority = {
                'source_system': source,
                'target_system': target,
                'coupling_score': score,
                'strategy': self._suggest_decoupling_strategy(source, target),
                'effort_estimate': 'high' if score > 10 else 'medium'
            }
            priorities.append(priority)
        
        return priorities

    def _suggest_decoupling_strategy(self, source: str, target: str) -> str:
        """Suggest strategy for decoupling two systems"""
        
        strategies = {
            ('combat', 'character'): 'Extract character combat interface',
            ('diplomacy', 'faction'): 'Use event-driven communication',
            ('motif', 'quest'): 'Create motif integration service',
            ('world_generation', 'region'): 'Abstract world generation interface'
        }
        
        return strategies.get((source, target), 'Use dependency injection and interfaces')

    def _suggest_interface_abstractions(self, high_coupling: List[Tuple]) -> List[Dict[str, str]]:
        """Suggest interface abstractions to reduce coupling"""
        
        interfaces = []
        
        common_patterns = [
            ('character', 'Provide ICharacterService interface'),
            ('combat', 'Create ICombatEngine interface'),
            ('world_generation', 'Define IWorldGenerator interface'),
            ('faction', 'Implement IFactionRepository interface')
        ]
        
        for system, suggestion in common_patterns:
            interfaces.append({
                'system': system,
                'interface_suggestion': suggestion,
                'benefits': 'Reduces direct dependencies, improves testability'
            })
        
        return interfaces

    def _identify_event_opportunities(self, coupling_matrix: Dict) -> List[Dict[str, any]]:
        """Identify opportunities for event-driven architecture"""
        
        opportunities = []
        
        # Systems with high outbound coupling are good candidates for events
        for source, targets in coupling_matrix.items():
            total_outbound = sum(targets.values())
            
            if total_outbound > 15:  # High coupling threshold
                opportunities.append({
                    'system': source,
                    'outbound_coupling': total_outbound,
                    'suggestion': f'Convert {source} to use event publication instead of direct calls',
                    'affected_systems': list(targets.keys())
                })
        
        return opportunities

    def _suggest_shared_infrastructure(self) -> List[Dict[str, str]]:
        """Suggest shared infrastructure components"""
        
        return [
            {
                'component': 'Event Bus',
                'purpose': 'Central event routing and handling',
                'systems_benefiting': 'combat, diplomacy, faction, quest'
            },
            {
                'component': 'Configuration Manager',
                'purpose': 'Centralized configuration management',
                'systems_benefiting': 'all systems'
            },
            {
                'component': 'Validation Framework',
                'purpose': 'Common validation patterns and utilities',
                'systems_benefiting': 'character, inventory, world_generation'
            },
            {
                'component': 'Cache Manager',
                'purpose': 'Distributed caching for performance',
                'systems_benefiting': 'analytics, world_state, motif'
            }
        ]

    def analyze_critical_files(self, output_file: str = "backend/task54_dependency_analysis.json"):
        """Perform comprehensive dependency analysis on critical files"""
        
        print("🔍 Starting comprehensive dependency analysis...")
        
        # Define critical files based on our previous analysis
        critical_files = [
            "combat/combat_class.py",
            "diplomacy/services.py", 
            "motif/consolidated_manager.py",
            "analytics/services/analytics_service.py",
            "character/services/character_service.py",
            "llm/core/dm_core.py",
            "motif/utils.py",
            "world_generation/world_generation_utils.py",
            "world_generation/biome_utils.py",
            "inventory/utils.py"
        ]
        
        # Build dependency graph
        self.build_dependency_graph(critical_files)
        
        print(f"📊 Analyzed {len(self.dependency_graph.nodes)} files")
        print(f"🔗 Found {len(self.dependency_graph.edges)} dependencies")
        
        # Generate recommendations
        recommendations = self.generate_refactoring_recommendations()
        
        # Save results
        with open(output_file, 'w') as f:
            json.dump(recommendations, f, indent=2, default=str)
        
        print(f"✅ Dependency analysis complete! Report saved to: {output_file}")
        
        # Print summary
        self._print_analysis_summary(recommendations)
        
        return recommendations

    def _print_analysis_summary(self, recommendations: Dict):
        """Print analysis summary to console"""
        
        print("\n" + "="*80)
        print("🔗 DEPENDENCY ANALYSIS SUMMARY")
        print("="*80)
        
        coupling_analysis = recommendations['coupling_analysis']
        dependency_issues = recommendations['dependency_issues']
        
        print(f"\n📈 COUPLING ANALYSIS:")
        print(f"  High coupling pairs: {len(coupling_analysis['high_coupling_pairs'])}")
        
        print(f"\n🔄 DEPENDENCY ISSUES:")
        print(f"  Circular dependencies: {dependency_issues['cycle_count']}")
        print(f"  Problematic files: {len(dependency_issues['problematic_files'])}")
        
        print(f"\n🏗️ TOP COUPLING ISSUES:")
        for source, target, score in coupling_analysis['high_coupling_pairs'][:5]:
            print(f"  {source} → {target}: {score} dependencies")
        
        print(f"\n🎯 REFACTORING PRIORITIES:")
        refactoring_strategy = recommendations['refactoring_strategy']
        for priority in refactoring_strategy['decoupling_priorities']:
            source = priority['source_system']
            target = priority['target_system']
            score = priority['coupling_score']
            print(f"  {source} ↔ {target}: Score {score} - {priority['strategy']}")

if __name__ == "__main__":
    analyzer = DependencyAnalyzer()
    analyzer.analyze_critical_files() 