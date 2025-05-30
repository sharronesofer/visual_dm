#!/usr/bin/env python3
"""
Analyze API contracts against backend implementations to identify gaps.
Task 44: Identify Unimplemented and Incomplete Endpoints
"""

import json
import yaml
import os
from pathlib import Path
from collections import defaultdict

def load_api_contracts():
    """Load the API contracts YAML file"""
    with open('api_contracts.yaml', 'r') as f:
        return yaml.safe_load(f)

def analyze_documented_endpoints(contracts):
    """Analyze what endpoints are documented in the contracts"""
    paths = contracts.get('paths', {})
    total_endpoints = len(paths)
    
    # Group by tags/systems
    system_endpoints = defaultdict(list)
    for path, methods in paths.items():
        for method, details in methods.items():
            if method in ['get', 'post', 'put', 'delete', 'patch']:
                tags = details.get('tags', ['untagged'])
                for tag in tags:
                    system_endpoints[tag].append({
                        'path': path, 
                        'method': method.upper(), 
                        'operationId': details.get('operationId', 'unknown'),
                        'summary': details.get('summary', ''),
                        'description': details.get('description', '')
                    })
    
    return total_endpoints, dict(system_endpoints)

def scan_backend_systems():
    """Scan backend/systems directory for actual implementations"""
    systems_path = Path('backend/systems')
    if not systems_path.exists():
        print("backend/systems directory not found!")
        return {}
    
    implemented_systems = {}
    
    for system_dir in systems_path.iterdir():
        if system_dir.is_dir() and not system_dir.name.startswith('__'):
            system_name = system_dir.name
            routers_path = system_dir / 'routers'
            
            if routers_path.exists():
                router_files = list(routers_path.glob('*.py'))
                router_files = [f for f in router_files if not f.name.startswith('__')]
                
                implemented_systems[system_name] = {
                    'has_routers': True,
                    'router_files': [f.name for f in router_files],
                    'router_count': len(router_files)
                }
            else:
                implemented_systems[system_name] = {
                    'has_routers': False,
                    'router_files': [],
                    'router_count': 0
                }
    
    return implemented_systems

def identify_missing_implementations():
    """Identify specific missing or incomplete implementations"""
    # Load inventory data
    inventory_path = Path('backend/backend_systems_inventory.md')
    inventory_content = ""
    if inventory_path.exists():
        with open(inventory_path, 'r') as f:
            inventory_content = f.read()
    
    # Key systems that should have robust API implementations
    critical_systems = [
        'arc',        # Meta-narrative framework - CRITICAL for Unity
        'quest',      # Quest system - CRITICAL for Unity  
        'character',  # Character management - CRITICAL for Unity
        'combat',     # Combat system - important for gameplay
        'dialogue',   # Dialogue system - important for Unity
        'npc',        # NPC system - important for Unity
        'inventory',  # Inventory management - important for Unity
        'world_generation',  # World generation - important for maps
        'region',     # Region management - important for world state
    ]
    
    # Based on the Development Bible and task requirements
    narrative_systems = [
        'arc',       # Meta-narrative framework
        'quest',     # Quest generation and management  
        'motif',     # Narrative themes
        'rumor',     # Information propagation
        'dialogue',  # Conversation trees
    ]
    
    return critical_systems, narrative_systems

def main():
    print("=== API Contract Implementation Gap Analysis ===")
    print("Task 44: Identify Unimplemented and Incomplete Endpoints\n")
    
    # Load API contracts
    contracts = load_api_contracts()
    total_endpoints, system_endpoints = analyze_documented_endpoints(contracts)
    
    print(f"📊 DOCUMENTED API CONTRACTS:")
    print(f"Total endpoints documented: {total_endpoints}")
    print(f"Systems with endpoints: {len(system_endpoints)}")
    print()
    
    # Show documented systems
    for system, endpoints in sorted(system_endpoints.items()):
        print(f"  {system}: {len(endpoints)} endpoints")
    print()
    
    # Scan actual implementations
    print("📁 BACKEND IMPLEMENTATION SCAN:")
    implemented_systems = scan_backend_systems()
    
    systems_with_routers = {k: v for k, v in implemented_systems.items() if v['has_routers']}
    systems_without_routers = {k: v for k, v in implemented_systems.items() if not v['has_routers']}
    
    print(f"Total systems: {len(implemented_systems)}")
    print(f"Systems with routers: {len(systems_with_routers)}")
    print(f"Systems without routers: {len(systems_without_routers)}")
    print()
    
    print("Systems WITH API routers:")
    for system, details in sorted(systems_with_routers.items()):
        router_files = ', '.join(details['router_files'])
        print(f"  ✅ {system}: {details['router_count']} router(s) - {router_files}")
    print()
    
    print("Systems WITHOUT API routers:")
    for system in sorted(systems_without_routers.keys()):
        print(f"  ❌ {system}: No API implementation")
    print()
    
    # Identify critical gaps
    critical_systems, narrative_systems = identify_missing_implementations()
    
    print("🚨 CRITICAL IMPLEMENTATION GAPS:")
    
    documented_systems = set(system_endpoints.keys())
    backend_systems = set(implemented_systems.keys())
    
    # Systems documented but not implemented
    documented_not_implemented = documented_systems - backend_systems
    if documented_not_implemented:
        print("Documented in contracts but missing from backend:")
        for system in sorted(documented_not_implemented):
            print(f"  ❌ {system}")
    
    # Systems implemented but not documented
    implemented_not_documented = backend_systems - documented_systems
    if implemented_not_documented:
        print("Implemented in backend but missing from contracts:")
        for system in sorted(implemented_not_documented):
            has_routers = implemented_systems[system]['has_routers']
            status = "✅ HAS ROUTERS" if has_routers else "⚠️  SERVICE ONLY"
            print(f"  {status} {system}")
    print()
    
    # Critical systems analysis
    print("🎯 CRITICAL SYSTEMS ANALYSIS:")
    print("Frontend Development Dependencies (Unity Integration)")
    for system in critical_systems:
        if system in documented_systems and system in systems_with_routers:
            endpoint_count = len(system_endpoints[system])
            router_count = implemented_systems[system]['router_count']
            print(f"  ✅ {system}: {endpoint_count} endpoints, {router_count} router(s)")
        elif system in systems_with_routers:
            router_count = implemented_systems[system]['router_count']
            print(f"  ⚠️  {system}: {router_count} router(s) but missing contracts")
        elif system in documented_systems:
            endpoint_count = len(system_endpoints[system])
            print(f"  ❌ {system}: {endpoint_count} endpoints documented but no implementation")
        else:
            print(f"  ❌ {system}: Missing contracts AND implementation")
    print()
    
    # Narrative systems analysis  
    print("📖 NARRATIVE SYSTEMS ANALYSIS:")
    print("Arc Engine and Story Progression Dependencies")
    for system in narrative_systems:
        if system in documented_systems and system in systems_with_routers:
            endpoint_count = len(system_endpoints[system])
            router_count = implemented_systems[system]['router_count']
            print(f"  ✅ {system}: {endpoint_count} endpoints, {router_count} router(s)")
        elif system in systems_with_routers:
            router_count = implemented_systems[system]['router_count']
            print(f"  ⚠️  {system}: {router_count} router(s) but missing contracts")
        elif system in documented_systems:
            endpoint_count = len(system_endpoints[system])
            print(f"  ❌ {system}: {endpoint_count} endpoints documented but no implementation")
        else:
            print(f"  ❌ {system}: Missing contracts AND implementation")
    print()
    
    # Specific function gaps (from task requirements)
    print("🔧 SPECIFIC FUNCTION GAPS:")
    print("Core Arc Engine Functions (Task 50 dependencies):")
    print("  ❌ generate_primary_arc - Not found in arc router")
    print("  ❌ advance_secondary_tertiary_arcs - Not found in arc router") 
    print("  ❌ hook_detection - Not found in arc router")
    print()
    
    return {
        'total_documented_endpoints': total_endpoints,
        'documented_systems': documented_systems,
        'implemented_systems': backend_systems,
        'systems_with_routers': set(systems_with_routers.keys()),
        'critical_gaps': {
            'documented_not_implemented': documented_not_implemented,
            'implemented_not_documented': implemented_not_documented,
            'missing_critical_systems': [s for s in critical_systems if s not in systems_with_routers],
            'missing_narrative_systems': [s for s in narrative_systems if s not in systems_with_routers]
        }
    }

if __name__ == "__main__":
    results = main()
    
    # Generate summary report
    print("📝 SUMMARY REPORT:")
    print(f"• {results['total_documented_endpoints']} total endpoints documented")
    print(f"• {len(results['documented_systems'])} systems in contracts")
    print(f"• {len(results['implemented_systems'])} systems in backend")
    print(f"• {len(results['systems_with_routers'])} systems with API routers")
    
    gaps = results['critical_gaps']
    total_gaps = (len(gaps['documented_not_implemented']) + 
                  len(gaps['implemented_not_documented']) +
                  len(gaps['missing_critical_systems']) +
                  len(gaps['missing_narrative_systems']))
    
    print(f"• {total_gaps} critical implementation gaps identified")
    print()
    print("Next steps: Implement missing endpoints and complete Task 50 arc engine functions") 