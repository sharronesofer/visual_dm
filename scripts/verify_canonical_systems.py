#!/usr/bin/env python3
"""
Verify current systems against canonical Development Bible model.
"""

import os
from pathlib import Path

# Canonical systems from Development Bible (backend/systems/)
CANONICAL_BUSINESS_LOGIC_SYSTEMS = [
    "analytics",      # -> MOVED TO INFRASTRUCTURE ✅
    "arc",
    "auth_user",      # -> MOVED TO INFRASTRUCTURE ✅  
    "character",
    "chaos",
    "combat",
    "crafting",
    "data",           # -> MOVED TO INFRASTRUCTURE ✅
    "dialogue", 
    "diplomacy",
    "economy",
    "equipment",
    "event_base",     # -> DEPRECATED/REMOVED ✅
    "events",         # -> MOVED TO INFRASTRUCTURE ✅
    "faction",
    "integration",    # -> MOVED TO INFRASTRUCTURE ✅
    "inventory",
    "llm",
    "loot", 
    "magic",
    "memory",
    "motif",
    "npc",
    "poi",
    "population",
    "quest",
    "region",
    "religion",
    "rumor",
    "shared",         # -> MOVED TO INFRASTRUCTURE ✅
    "storage",        # -> MOVED TO INFRASTRUCTURE ✅
    "tension_war",
    "time",
    "world_generation",
    "world_state"
]

# Additional systems mentioned in Development Bible but not in main list
CANONICAL_ADDITIONAL_SYSTEMS = [
    "world",          # Mentioned as separate from world_state
]

# Expected to be in infrastructure (not business logic)
CANONICAL_INFRASTRUCTURE_SYSTEMS = [
    "analytics",
    "auth_user", 
    "data",
    "events",
    "integration",
    "shared",
    "storage"
]

# Canonical internal structure for each system (individual system directories)
CANONICAL_SYSTEM_STRUCTURE = [
    "models",        # System-specific specialized models
    "services", 
    "repositories",
    "routers",
    "events",
    "utils",
    "__init__.py"
]

# Canonical shared domain components (at systems package level)
CANONICAL_SHARED_COMPONENTS = [
    "models",        # Shared core domain models (Character, Item, Faction, etc.)
    "repositories",  # Shared domain repositories (MarketRepository, etc.)
    "schemas",       # Shared domain schemas (WorldData, Event, etc.)
    "rules"          # Shared game rules and balance constants
]

def get_current_systems():
    """Get current systems in backend/systems/"""
    systems_path = Path("backend/systems")
    if not systems_path.exists():
        return []
    
    current_systems = []
    for item in systems_path.iterdir():
        if item.is_dir() and not item.name.startswith('__'):
            current_systems.append(item.name)
    
    return sorted(current_systems)

def get_current_infrastructure():
    """Get current infrastructure components"""
    infra_path = Path("backend/infrastructure")
    if not infra_path.exists():
        return []
    
    current_infra = []
    for item in infra_path.iterdir():
        if item.is_dir() and not item.name.startswith('__'):
            current_infra.append(item.name)
    
    return sorted(current_infra)

def check_system_structure(system_name):
    """Check if a system has canonical internal structure"""
    system_path = Path(f"backend/systems/{system_name}")
    if not system_path.exists():
        return {}
    
    structure_status = {}
    for component in CANONICAL_SYSTEM_STRUCTURE:
        if component == "__init__.py":
            structure_status[component] = (system_path / component).exists()
        else:
            structure_status[component] = (system_path / component).is_dir()
    
    return structure_status

def main():
    print("🔍 VERIFYING CANONICAL SYSTEMS COMPLIANCE")
    print("=" * 60)
    
    current_systems = get_current_systems()
    current_infra = get_current_infrastructure()
    
    print(f"\n📊 CURRENT STATE:")
    print(f"   Systems in /backend/systems/: {len(current_systems)}")
    print(f"   Components in /backend/infrastructure/: {len(current_infra)}")
    
    # Expected business logic systems (after infrastructure moves)
    expected_business_systems = [s for s in CANONICAL_BUSINESS_LOGIC_SYSTEMS 
                               if s not in CANONICAL_INFRASTRUCTURE_SYSTEMS and s != "event_base"]
    expected_business_systems.extend(CANONICAL_ADDITIONAL_SYSTEMS)
    
    print(f"\n✅ CANONICAL SHARED DOMAIN COMPONENTS:")
    shared_status = []
    for component in CANONICAL_SHARED_COMPONENTS:
        if component in current_systems:
            shared_status.append(component)
            print(f"   ✅ {component}/ - Shared domain component")
        else:
            print(f"   ❌ {component}/ - Missing shared component")
    
    print(f"\n✅ BUSINESS LOGIC SYSTEMS:")
    correctly_placed = []
    for system in current_systems:
        if system in expected_business_systems:
            correctly_placed.append(system)
            print(f"   ✅ {system}")
    
    print(f"\n❌ MISSING BUSINESS LOGIC SYSTEMS:")
    missing_systems = []
    for system in expected_business_systems:
        if system not in current_systems:
            missing_systems.append(system)
            print(f"   ❌ {system}")
    
    print(f"\n✅ INFRASTRUCTURE CORRECTLY MOVED:")
    correctly_moved = []
    for component in current_infra:
        if component in CANONICAL_INFRASTRUCTURE_SYSTEMS:
            correctly_moved.append(component)
            print(f"   ✅ {component}")
    
    print(f"\n🔧 SYSTEM STRUCTURE ANALYSIS:")
    structure_issues = []
    
    # Check individual systems (excluding shared components)
    individual_systems = [s for s in current_systems if s not in CANONICAL_SHARED_COMPONENTS]
    
    for system in individual_systems:
        structure = check_system_structure(system)
        missing_components = [comp for comp, exists in structure.items() if not exists]
        if missing_components:
            structure_issues.append((system, missing_components))
            print(f"   ⚠️  {system}: Missing {', '.join(missing_components)}")
        else:
            print(f"   ✅ {system}: Complete canonical structure")
    
    print(f"\n📈 COMPLIANCE SUMMARY:")
    total_expected = len(expected_business_systems)
    total_correct = len(correctly_placed)
    total_shared = len(shared_status)
    total_shared_expected = len(CANONICAL_SHARED_COMPONENTS)
    
    systems_compliance = (total_correct / total_expected) * 100 if total_expected > 0 else 0
    shared_compliance = (total_shared / total_shared_expected) * 100 if total_shared_expected > 0 else 0
    
    print(f"   Business Systems Compliance: {systems_compliance:.1f}% ({total_correct}/{total_expected})")
    print(f"   Shared Components Compliance: {shared_compliance:.1f}% ({total_shared}/{total_shared_expected})")
    print(f"   Missing Systems: {len(missing_systems)}")
    print(f"   Structure Issues: {len(structure_issues)}")
    
    print(f"\n🚀 RECOMMENDED ACTIONS:")
    if missing_systems:
        print(f"   1. Create missing systems: {', '.join(missing_systems)}")
    if len(shared_status) < len(CANONICAL_SHARED_COMPONENTS):
        missing_shared = [c for c in CANONICAL_SHARED_COMPONENTS if c not in shared_status]
        print(f"   2. Complete shared components: {', '.join(missing_shared)}")
    if structure_issues:
        print(f"   3. Complete structure for: {', '.join([s[0] for s in structure_issues])}")
    
    if systems_compliance == 100.0 and shared_compliance == 100.0 and len(structure_issues) == 0:
        print(f"\n🎉 PERFECT COMPLIANCE! Your structure matches the canonical Development Bible model.")
    
    return {
        'missing_systems': missing_systems,
        'structure_issues': structure_issues,
        'systems_compliance': systems_compliance,
        'shared_compliance': shared_compliance
    }

if __name__ == "__main__":
    results = main() 