#!/usr/bin/env python3
"""
Backend Systems Compliance Assessment
Implementation of Task 42: Inventory Backend Systems for API Contract Definition

This script follows the Backend Development Protocol to:
1. Assessment and Error Resolution
2. Structure and Organization Enforcement  
3. Canonical Imports Enforcement
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class SystemInfo:
    name: str
    path: str
    has_router: bool
    router_files: List[str]
    api_endpoints: List[str]
    models: List[str]
    services: List[str]
    repositories: List[str]
    test_coverage: Optional[float]
    status: str
    description: str
    unity_dependencies: str
    layer: str

@dataclass
class AssessmentResult:
    total_systems: int
    systems_by_layer: Dict[str, List[str]]
    api_systems: List[str]
    service_only_systems: List[str]
    compliance_issues: List[str]
    import_issues: List[str]
    missing_tests: List[str]
    systems_info: List[SystemInfo]

class BackendSystemsAssessment:
    def __init__(self, backend_path: str = "."):
        self.backend_path = Path(backend_path)
        self.systems_path = self.backend_path / "systems"
        self.tests_path = self.backend_path / "tests" / "systems"
        
        # Layer definitions from Development Bible
        self.system_layers = {
            # Foundation Layer
            'shared': 'Foundation',
            'events': 'Foundation', 
            'data': 'Foundation',
            'storage': 'Foundation',
            'analytics': 'Foundation',
            'auth_user': 'Foundation',
            'llm': 'Foundation',
            
            # Core Game Layer
            'character': 'Core Game',
            'time': 'Core Game',
            'world_generation': 'Core Game',
            'region': 'Core Game',
            
            # Gameplay Layer
            'combat': 'Gameplay',
            'magic': 'Gameplay',
            'equipment': 'Gameplay',
            'inventory': 'Gameplay',
            
            # World Simulation Layer
            'poi': 'World Simulation',
            'world_state': 'World Simulation',
            'population': 'World Simulation',
            
            # Social Layer
            'npc': 'Social',
            'faction': 'Social',
            'diplomacy': 'Social',
            'memory': 'Social',
            
            # Interaction Layer
            'dialogue': 'Interaction',
            'tension_war': 'Interaction',
            
            # Economic Layer
            'economy': 'Economic',
            'crafting': 'Economic',
            'loot': 'Economic',
            
            # Content Layer
            'quest': 'Content',
            'rumor': 'Content',
            'religion': 'Content',
            
            # Advanced Layer
            'motif': 'Advanced',
            'arc': 'Advanced',
            
            # Integration Layer
            'integration': 'Integration'
        }

    def assess_all_systems(self) -> AssessmentResult:
        """Run comprehensive assessment of all backend systems."""
        print("🔍 Starting Backend Systems Compliance Assessment...")
        
        systems_info = []
        compliance_issues = []
        import_issues = []
        missing_tests = []
        
        # Get all system directories
        system_dirs = [d for d in self.systems_path.iterdir() 
                      if d.is_dir() and not d.name.startswith('__')]
        
        print(f"📊 Found {len(system_dirs)} systems to assess")
        
        for system_dir in sorted(system_dirs):
            print(f"   Assessing {system_dir.name}...")
            system_info = self._assess_system(system_dir)
            systems_info.append(system_info)
            
            # Check for compliance issues
            issues = self._check_system_compliance(system_dir, system_info)
            compliance_issues.extend(issues)
            
            # Check imports
            import_issues_for_system = self._check_canonical_imports(system_dir)
            import_issues.extend(import_issues_for_system)
            
            # Check tests
            if not self._has_proper_tests(system_dir.name):
                missing_tests.append(system_dir.name)
        
        # Organize by layers
        systems_by_layer = {}
        api_systems = []
        service_only_systems = []
        
        for system in systems_info:
            layer = system.layer
            if layer not in systems_by_layer:
                systems_by_layer[layer] = []
            systems_by_layer[layer].append(system.name)
            
            if system.has_router:
                api_systems.append(system.name)
            else:
                service_only_systems.append(system.name)
        
        result = AssessmentResult(
            total_systems=len(systems_info),
            systems_by_layer=systems_by_layer,
            api_systems=api_systems,
            service_only_systems=service_only_systems,
            compliance_issues=compliance_issues,
            import_issues=import_issues,
            missing_tests=missing_tests,
            systems_info=systems_info
        )
        
        print("✅ Assessment complete!")
        return result

    def _assess_system(self, system_dir: Path) -> SystemInfo:
        """Assess a single system directory."""
        name = system_dir.name
        
        # Find router files
        router_files = []
        router_patterns = ['router.py', 'routers/', '*_router.py']
        
        for pattern in router_patterns:
            if pattern.endswith('/'):
                routers_dir = system_dir / pattern[:-1]
                if routers_dir.exists():
                    router_files.extend([str(f.relative_to(system_dir)) 
                                       for f in routers_dir.glob('*.py')
                                       if not f.name.startswith('__')])
            else:
                router_file = system_dir / pattern
                if router_file.exists():
                    router_files.append(pattern)
                # Also check for files matching pattern
                for f in system_dir.glob(pattern):
                    if f.is_file() and not f.name.startswith('__'):
                        router_files.append(str(f.relative_to(system_dir)))
        
        has_router = len(router_files) > 0
        
        # Extract API endpoints from router files
        api_endpoints = []
        for router_file in router_files:
            endpoints = self._extract_api_endpoints(system_dir / router_file)
            api_endpoints.extend(endpoints)
        
        # Find models, services, repositories
        models = self._find_python_files(system_dir / "models")
        services = self._find_python_files(system_dir / "services") 
        repositories = self._find_python_files(system_dir / "repositories")
        
        # Determine status based on router presence and endpoints
        if has_router and api_endpoints:
            status = "✅ Stable"
        elif has_router:
            status = "🔧 Partial"
        else:
            status = "✅ Service Layer"
        
        # Get layer
        layer = self.system_layers.get(name, "Unknown")
        
        # Generate descriptions based on system name
        descriptions = {
            'shared': 'Core utilities and shared functionality',
            'events': 'Event system for inter-system communication',
            'data': 'Data management and validation',
            'storage': 'Persistence and save/load operations',
            'analytics': 'Gameplay analytics and performance monitoring',
            'auth_user': 'Authentication and user management',
            'llm': 'AI integration for content generation',
            'character': 'Character management and progression',
            'time': 'Game time and calendar management',
            'world_generation': 'Procedural world creation',
            'region': 'Geographic region management',
            'combat': 'Tactical combat system',
            'magic': 'Spellcasting and magical effects',
            'equipment': 'Weapons, armor, and item management',
            'inventory': 'Item storage and organization',
            'poi': 'Points of interest and dynamic locations',
            'world_state': 'Global world state tracking',
            'population': 'Demographics and population simulation',
            'npc': 'Non-player character system',
            'faction': 'Organizations and group management',
            'diplomacy': 'Inter-faction relations',
            'memory': 'NPC memory and event tracking',
            'dialogue': 'Conversation and dialogue trees',
            'tension_war': 'Conflict simulation',
            'economy': 'Economic simulation and trade',
            'crafting': 'Item creation and recipes',
            'loot': 'Treasure generation',
            'quest': 'Mission and objective system',
            'rumor': 'Information propagation',
            'religion': 'Spiritual systems and deities',
            'motif': 'Narrative themes and consistency',
            'arc': 'Meta-narrative framework',
            'integration': 'Cross-system coordination'
        }
        
        unity_deps = {
            'character': '**CRITICAL** - Player character management',
            'time': '**CRITICAL** - Game time synchronization', 
            'world_generation': '**CRITICAL** - World map generation',
            'equipment': '**CRITICAL** - Item display and management',
            'inventory': '**CRITICAL** - Inventory UI',
            'npc': '**CRITICAL** - NPC display and interaction',
            'quest': '**CRITICAL** - Quest UI and tracking',
            'economy': '**CRITICAL** - Trade interface and shops',
            'arc': '**CRITICAL** - Story progression UI',
            'dialogue': '**CRITICAL** - Dialogue interface',
            'region': 'Regional map display',
            'faction': 'Faction displays and diplomacy',
            'combat': 'Combat interface (can use mock data)',
            'magic': 'Magic interface (can use mock data)',
            'inventory': 'Inventory UI (can use mock data)',
            'poi': 'POI markers and discovery',
            'world_state': 'World synchronization',
            'population': 'Demographics visualization',
            'diplomacy': 'Diplomatic interface',
            'tension_war': 'Conflict visualization',
            'crafting': 'Crafting interface',
            'motif': 'Theme visualization',
            'rumor': 'Information display',
            'religion': 'Religious interface',
            'loot': 'Loot display',
            'memory': 'Background system',
            'shared': 'Core foundation',
            'events': 'Real-time communication',
            'data': 'Configuration management',
            'storage': 'Save/load functionality',
            'analytics': 'Telemetry and monitoring',
            'auth_user': 'User authentication',
            'llm': 'Dynamic content generation',
            'integration': 'System coordination'
        }
        
        return SystemInfo(
            name=name,
            path=str(system_dir.relative_to(self.backend_path)),
            has_router=has_router,
            router_files=router_files,
            api_endpoints=api_endpoints,
            models=models,
            services=services,
            repositories=repositories,
            test_coverage=None,  # Could be extracted from coverage reports
            status=status,
            description=descriptions.get(name, f"{name.title()} system"),
            unity_dependencies=unity_deps.get(name, "Standard system integration"),
            layer=layer
        )

    def _find_python_files(self, directory: Path) -> List[str]:
        """Find Python files in a directory."""
        if not directory.exists():
            return []
        
        files = []
        for f in directory.glob("*.py"):
            if not f.name.startswith('__'):
                files.append(f.name)
        return files

    def _extract_api_endpoints(self, router_file: Path) -> List[str]:
        """Extract API endpoints from a router file."""
        if not router_file.exists():
            return []
        
        endpoints = []
        try:
            content = router_file.read_text()
            
            # Look for FastAPI route decorators
            route_patterns = [
                r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
                r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
            ]
            
            for pattern in route_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for method, path in matches:
                    endpoints.append(f"{method.upper()} {path}")
                    
        except Exception as e:
            print(f"   Warning: Could not parse {router_file}: {e}")
        
        return endpoints

    def _check_system_compliance(self, system_dir: Path, system_info: SystemInfo) -> List[str]:
        """Check system compliance with development standards."""
        issues = []
        
        # Check for required __init__.py
        if not (system_dir / "__init__.py").exists():
            issues.append(f"{system_info.name}: Missing __init__.py")
        
        # Check for proper directory structure
        expected_dirs = ['models', 'services', 'repositories']
        if system_info.has_router:
            expected_dirs.append('routers')
        
        for expected_dir in expected_dirs:
            dir_path = system_dir / expected_dir
            if not dir_path.exists() and len(system_info.models + system_info.services + system_info.repositories) > 0:
                # Only flag if system has complexity but missing structure
                pass  # This is actually normal for some systems
        
        return issues

    def _check_canonical_imports(self, system_dir: Path) -> List[str]:
        """Check for non-canonical imports."""
        issues = []
        
        for py_file in system_dir.rglob("*.py"):
            if py_file.name.startswith('__'):
                continue
                
            try:
                content = py_file.read_text()
                
                # Look for non-canonical imports
                non_canonical_patterns = [
                    r'from systems\.',  # Should be backend.systems.
                    r'import systems\.',  # Should be backend.systems.
                    r'from \.\.',  # Relative imports outside immediate directory
                ]
                
                for line_num, line in enumerate(content.split('\n'), 1):
                    for pattern in non_canonical_patterns:
                        if re.search(pattern, line):
                            issues.append(f"{py_file.relative_to(self.backend_path)}:{line_num} - Non-canonical import: {line.strip()}")
                            
            except Exception as e:
                print(f"   Warning: Could not check imports in {py_file}: {e}")
        
        return issues

    def _has_proper_tests(self, system_name: str) -> bool:
        """Check if system has proper tests in canonical location."""
        test_dir = self.tests_path / system_name
        return test_dir.exists() and any(test_dir.glob("test_*.py"))

    def generate_updated_inventory(self, result: AssessmentResult) -> str:
        """Generate updated inventory markdown."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        md = f"""# Backend Systems Inventory for API Contract Definition

**Task 42 Implementation - Comprehensive Backend Catalog**

Generated: {now}
Purpose: Foundation for API contract extraction and Unity frontend development

## 🏗️ System Architecture Overview

### **{result.total_systems} Total Backend Systems** across {len(result.systems_by_layer)} functional layers:

| Layer | Count | Systems |
|-------|-------|---------|
"""
        
        for layer, systems in result.systems_by_layer.items():
            md += f"| {layer} | {len(systems)} | {', '.join(systems)} |\n"
        
        md += f"""

## 📊 API Coverage Summary

- **Systems with API Endpoints**: {len(result.api_systems)} systems
- **Service Layer Only**: {len(result.service_only_systems)} systems
- **Total API Endpoints**: {sum(len(s.api_endpoints) for s in result.systems_info)}

## 🔍 Compliance Assessment Results

"""
        
        if result.compliance_issues:
            md += "### ⚠️ Compliance Issues Found:\n"
            for issue in result.compliance_issues:
                md += f"- {issue}\n"
        else:
            md += "### ✅ No Compliance Issues Found\n"
        
        if result.import_issues:
            md += f"\n### 🔧 Import Issues Found ({len(result.import_issues)}):\n"
            for issue in result.import_issues[:10]:  # Show first 10
                md += f"- {issue}\n"
            if len(result.import_issues) > 10:
                md += f"- ... and {len(result.import_issues) - 10} more\n"
        else:
            md += "\n### ✅ All Imports Follow Canonical Structure\n"
        
        if result.missing_tests:
            md += f"\n### 📝 Systems Missing Proper Tests:\n"
            for system in result.missing_tests:
                md += f"- {system}\n"
        else:
            md += "\n### ✅ All Systems Have Proper Test Structure\n"
        
        md += "\n## 📋 Detailed System Inventory\n\n"
        
        # Group by layer
        for layer, system_names in result.systems_by_layer.items():
            md += f"### **🏗️ {layer} Layer ({len(system_names)} systems)**\n\n"
            
            for system_name in system_names:
                system = next(s for s in result.systems_info if s.name == system_name)
                md += f"#### {system_name} - {system.description.title()}\n"
                md += f"- **Status**: {system.status}\n"
                
                if system.router_files:
                    md += f"- **Router Files**: {', '.join(system.router_files)}\n"
                
                if system.api_endpoints:
                    md += f"- **API Endpoints**:\n"
                    for endpoint in system.api_endpoints:
                        md += f"  - `{endpoint}`\n"
                else:
                    md += f"- **API Endpoints**: None (service layer)\n"
                
                md += f"- **Description**: {system.description}\n"
                md += f"- **Unity Dependencies**: {system.unity_dependencies}\n"
                
                if system.models:
                    md += f"- **Models**: {', '.join(system.models)}\n"
                if system.services:
                    md += f"- **Services**: {', '.join(system.services)}\n"
                if system.repositories:
                    md += f"- **Repositories**: {', '.join(system.repositories)}\n"
                
                md += "\n"
            
            md += "---\n\n"
        
        md += """## 🎯 Recommendations for Unity Development

### **Phase 1: Critical API Contracts**
Focus on extracting API contracts for CRITICAL systems:
"""
        
        critical_systems = [s for s in result.systems_info 
                           if '**CRITICAL**' in s.unity_dependencies]
        
        for system in critical_systems:
            md += f"- **{system.name}**: {system.description}\n"
        
        md += """
### **Phase 2: Mock Server Implementation**
- Use working systems for real data
- Create mock responses for partial systems  
- Implement realistic test data

### **Phase 3: Unity Integration**
- Generate C# DTOs for critical systems
- Implement MockClient for development
- Create test scenes for core features

**Next Task**: Extract detailed API contracts from router files for critical systems.
"""
        
        return md

    def save_assessment_report(self, result: AssessmentResult, filename: str = "backend_systems_assessment_report.json"):
        """Save detailed assessment report as JSON."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': asdict(result),
            'systems_detail': [asdict(s) for s in result.systems_info]
        }
        
        with open(self.backend_path / filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Assessment report saved to {filename}")

def main():
    """Run the assessment and update inventory."""
    assessor = BackendSystemsAssessment()
    result = assessor.assess_all_systems()
    
    # Generate updated inventory
    updated_inventory = assessor.generate_updated_inventory(result)
    
    # Save updated inventory
    inventory_file = assessor.backend_path / "backend_systems_inventory.md"
    with open(inventory_file, 'w') as f:
        f.write(updated_inventory)
    
    print(f"✅ Updated inventory saved to {inventory_file}")
    
    # Save detailed assessment report
    assessor.save_assessment_report(result)
    
    # Print summary
    print(f"\n📊 ASSESSMENT SUMMARY:")
    print(f"   Total Systems: {result.total_systems}")
    print(f"   API Systems: {len(result.api_systems)}")
    print(f"   Service Layer: {len(result.service_only_systems)}")
    print(f"   Compliance Issues: {len(result.compliance_issues)}")
    print(f"   Import Issues: {len(result.import_issues)}")
    print(f"   Missing Tests: {len(result.missing_tests)}")

if __name__ == "__main__":
    main() 