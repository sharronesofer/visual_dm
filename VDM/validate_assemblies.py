#!/usr/bin/env python3
"""
Unity Assembly Dependency Validator
Validates VDM assembly dependencies to prevent circular references
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

class AssemblyValidator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.assemblies: Dict[str, List[str]] = {}
        self.valid_hierarchy = {
            1: ['VDM.Common', 'VDM.DTOs'],
            2: ['VDM.Services', 'VDM.Core'],
            3: ['VDM.Systems'],
            4: ['VDM.Character', 'VDM.Combat', 'VDM.Modules'],
            5: ['VDM.UI', 'VDM.Runtime'],
            6: ['VDM.Tests']
        }
    
    def load_assemblies(self) -> bool:
        """Load all VDM assembly definitions"""
        try:
            scripts_path = self.project_root / "Assets" / "Scripts"
            
            for asmdef_file in scripts_path.rglob("VDM.*.asmdef"):
                with open(asmdef_file, 'r') as f:
                    data = json.load(f)
                    name = data['name']
                    references = [ref for ref in data.get('references', []) if ref.startswith('VDM.')]
                    self.assemblies[name] = references
                    print(f"✓ Loaded {name}: {references}")
            
            return len(self.assemblies) > 0
        except Exception as e:
            print(f"❌ Error loading assemblies: {e}")
            return False
    
    def find_cycles(self) -> List[List[str]]:
        """Find all circular dependency cycles"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> bool:
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return True
            
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.assemblies.get(node, []):
                if dfs(neighbor, path + [neighbor]):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for assembly in self.assemblies:
            if assembly not in visited:
                dfs(assembly, [assembly])
        
        return cycles
    
    def validate_hierarchy(self) -> List[str]:
        """Validate that dependencies follow the hierarchy"""
        violations = []
        level_map = {}
        
        # Build level map
        for level, assemblies in self.valid_hierarchy.items():
            for assembly in assemblies:
                level_map[assembly] = level
        
        # Check each assembly's dependencies
        for assembly, dependencies in self.assemblies.items():
            if assembly not in level_map:
                violations.append(f"❌ Unknown assembly: {assembly}")
                continue
                
            assembly_level = level_map[assembly]
            
            for dep in dependencies:
                if dep not in level_map:
                    violations.append(f"❌ {assembly} references unknown assembly: {dep}")
                    continue
                
                dep_level = level_map[dep]
                # Assemblies can only reference lower-level assemblies (not same level or higher)
                if dep_level >= assembly_level:
                    violations.append(f"❌ {assembly} (Level {assembly_level}) should not reference {dep} (Level {dep_level})")
        
        return violations
    
    def check_forbidden_patterns(self) -> List[str]:
        """Check for specific forbidden dependency patterns"""
        violations = []
        
        # Core should never reference Runtime
        if 'VDM.Runtime' in self.assemblies.get('VDM.Core', []):
            violations.append("❌ FORBIDDEN: VDM.Core references VDM.Runtime")
        
        # Services should never reference Core
        if 'VDM.Core' in self.assemblies.get('VDM.Services', []):
            violations.append("❌ FORBIDDEN: VDM.Services references VDM.Core")
        
        # UI and Runtime should not reference each other (same level)
        if 'VDM.Runtime' in self.assemblies.get('VDM.UI', []):
            violations.append("❌ FORBIDDEN: VDM.UI references VDM.Runtime (same level)")
        if 'VDM.UI' in self.assemblies.get('VDM.Runtime', []):
            violations.append("❌ FORBIDDEN: VDM.Runtime references VDM.UI (same level)")
        
        # Check for cross-domain dependencies
        domain_modules = ['VDM.Character', 'VDM.Combat', 'VDM.Modules']
        for module in domain_modules:
            deps = self.assemblies.get(module, [])
            cross_deps = [dep for dep in deps if dep in domain_modules and dep != module]
            if cross_deps:
                violations.append(f"❌ FORBIDDEN: {module} cross-references domain modules: {cross_deps}")
        
        return violations
    
    def generate_dependency_graph(self) -> str:
        """Generate a visual dependency graph"""
        graph = "Assembly Dependency Graph:\n"
        graph += "=" * 40 + "\n\n"
        
        for level, assemblies in self.valid_hierarchy.items():
            graph += f"Level {level}:\n"
            for assembly in assemblies:
                if assembly in self.assemblies:
                    deps = self.assemblies[assembly]
                    graph += f"  {assembly}\n"
                    if deps:
                        graph += f"    └─ Dependencies: {', '.join(deps)}\n"
                    else:
                        graph += f"    └─ No dependencies\n"
                else:
                    graph += f"  {assembly} (NOT FOUND)\n"
            graph += "\n"
        
        return graph
    
    def validate(self) -> bool:
        """Run complete validation"""
        print("🔍 Unity Assembly Dependency Validator")
        print("=" * 50)
        
        # Load assemblies
        if not self.load_assemblies():
            print("❌ Failed to load assembly definitions")
            return False
        
        print(f"\n✓ Loaded {len(self.assemblies)} VDM assemblies")
        
        # Check for cycles
        print("\n🔄 Checking for circular dependencies...")
        cycles = self.find_cycles()
        
        if cycles:
            print(f"❌ Found {len(cycles)} circular dependencies:")
            for i, cycle in enumerate(cycles, 1):
                print(f"  {i}. {' → '.join(cycle)}")
        else:
            print("✅ No circular dependencies found")
        
        # Validate hierarchy
        print("\n📊 Validating dependency hierarchy...")
        hierarchy_violations = self.validate_hierarchy()
        
        if hierarchy_violations:
            print(f"❌ Found {len(hierarchy_violations)} hierarchy violations:")
            for violation in hierarchy_violations:
                print(f"  {violation}")
        else:
            print("✅ Dependency hierarchy is valid")
        
        # Check forbidden patterns
        print("\n🚫 Checking forbidden dependency patterns...")
        forbidden_violations = self.check_forbidden_patterns()
        
        if forbidden_violations:
            print(f"❌ Found {len(forbidden_violations)} forbidden patterns:")
            for violation in forbidden_violations:
                print(f"  {violation}")
        else:
            print("✅ No forbidden patterns found")
        
        # Generate dependency graph
        print("\n" + self.generate_dependency_graph())
        
        # Final result
        total_issues = len(cycles) + len(hierarchy_violations) + len(forbidden_violations)
        
        if total_issues == 0:
            print("🎉 ALL VALIDATION CHECKS PASSED!")
            print("✅ Assembly dependency architecture is robust and circular-dependency-free")
            return True
        else:
            print(f"❌ VALIDATION FAILED: {total_issues} issues found")
            print("📖 See ASSEMBLY_DEPENDENCY_ARCHITECTURE.md for guidance")
            return False

def main():
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = "."
    
    validator = AssemblyValidator(project_root)
    success = validator.validate()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 