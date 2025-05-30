#!/usr/bin/env python3
"""
Backend Development Protocol: Test Organization
Relocate misplaced test files to proper /backend/tests/systems/ structure
"""

import os
import shutil
from pathlib import Path
import re

def organize_test_files():
    """Organize misplaced test files according to protocol"""
    backend_root = Path("/Users/Sharrone/Visual_DM/backend")
    tests_dir = backend_root / "tests"
    systems_tests_dir = tests_dir / "systems"
    
    # Mapping of test files to appropriate system directories
    test_mappings = {
        # World generation related tests
        'test_river_generator.py': 'world_generation',
        'test_biome_utils.py': 'world_generation', 
        'test_coastline_utils.py': 'world_generation',
        'test_elevation_utils.py': 'world_generation',
        'test_world_generation_utils.py': 'world_generation',
        'test_world_manager.py': 'world_generation',
        'test_world_generator.py': 'world_generation',
        'test_world_utils.py': 'world_generation',
        'test_optimized_worldgen.py': 'world_generation',
        'test_worldgen_routes.py': 'world_generation',
        'test_worldgen_routes_endpoints.py': 'world_generation',
        'test_regional_features.py': 'world_generation',
        'test_resource_utils.py': 'world_generation',
        'test_continent_repository.py': 'world_generation',
        'test_continent_service.py': 'world_generation',
        'test_settlement_service.py': 'world_generation',
        'test_seed_loader.py': 'world_generation',
        'test_config.py': 'world_generation',
        'test_modding_system.py': 'world_generation',
        'test_initialize_modding.py': 'world_generation',
        
        # Service utilities
        'test_service_utils.py': 'shared',
        
        # POI related
        'test_poi_generator.py': 'poi',
        
        # Generic components and routes
        'test_components.py': 'shared',
        'test_router.py': 'shared',
        'test_api.py': 'shared',
        
        # Events
        'test_events.py': 'events'
    }
    
    moved_files = []
    
    print("🗂️ Organizing misplaced test files...")
    
    # Move files from /backend/tests/ to appropriate system directories
    for test_file in tests_dir.glob('test_*.py'):
        if test_file.name in test_mappings:
            target_system = test_mappings[test_file.name]
            target_dir = systems_tests_dir / target_system
            
            # Create target directory if it doesn't exist
            target_dir.mkdir(parents=True, exist_ok=True)
            
            target_path = target_dir / test_file.name
            
            # Check if target already exists
            if target_path.exists():
                print(f"  ⚠️ Target exists: {target_path}")
                # Backup existing file
                backup_path = target_path.with_suffix('.py.backup')
                shutil.move(str(target_path), str(backup_path))
                print(f"    📦 Backed up existing file to: {backup_path}")
            
            # Move the file
            shutil.move(str(test_file), str(target_path))
            moved_files.append((test_file.name, target_system))
            print(f"  ✅ Moved {test_file.name} → systems/{target_system}/")
    
    print(f"\n📊 Summary: Moved {len(moved_files)} test files")
    for filename, system in moved_files:
        print(f"  - {filename} → {system}")
    
    return moved_files

def remove_duplicate_tests():
    """Remove duplicate test files identified in the inventory"""
    backend_root = Path("/Users/Sharrone/Visual_DM/backend")
    systems_tests_dir = backend_root / "tests" / "systems"
    
    # Known duplicates from inventory (keep the more appropriate location)
    duplicates_to_remove = [
        # Keep in region, remove from poi
        systems_tests_dir / "poi" / "test_utils_comprehensive.py",
        
        # Keep in quest, remove from dialogue  
        systems_tests_dir / "dialogue" / "test_quest_integration.py",
        
        # Keep in inventory, remove from dialogue
        systems_tests_dir / "dialogue" / "test_utils.py",
        
        # Keep in inventory, remove from poi (if it exists)
        systems_tests_dir / "poi" / "test_utils_comprehensive.py",
        
        # Keep in arc, remove from poi  
        systems_tests_dir / "poi" / "test_services.py",
        
        # Keep in arc, remove from auth_user
        systems_tests_dir / "auth_user" / "unit" / "test_repositories.py",
        
        # Keep in arc, remove from dialogue
        systems_tests_dir / "dialogue" / "test_quest_integration.py",
        
        # Keep in arc, remove from region
        systems_tests_dir / "region" / "test_routers.py",
        
        # Keep in arc, remove from crafting
        systems_tests_dir / "crafting" / "test_integration.py",
        
        # Keep in analytics, remove from dialogue  
        systems_tests_dir / "dialogue" / "test_utils.py",
        
        # Keep in analytics, remove from arc
        systems_tests_dir / "arc" / "test_models.py",
        
        # Keep in analytics, remove from crafting
        systems_tests_dir / "crafting" / "test_schemas.py",
        
        # Keep in analytics, remove from world_state
        systems_tests_dir / "world_state" / "test_event_integration.py"
    ]
    
    removed_files = []
    
    print("\n🗑️ Removing duplicate test files...")
    
    for duplicate_path in duplicates_to_remove:
        if duplicate_path.exists():
            # Create backup before removing
            backup_path = duplicate_path.with_suffix('.py.duplicate_backup')
            shutil.copy2(str(duplicate_path), str(backup_path))
            
            # Remove the duplicate
            duplicate_path.unlink()
            removed_files.append(str(duplicate_path))
            print(f"  ❌ Removed duplicate: {duplicate_path.relative_to(systems_tests_dir)}")
            print(f"    📦 Backup created: {backup_path.relative_to(systems_tests_dir)}")
        else:
            print(f"  ℹ️ Already removed: {duplicate_path.relative_to(systems_tests_dir)}")
    
    print(f"\n📊 Summary: Removed {len(removed_files)} duplicate files")
    
    return removed_files

def main():
    """Main execution for test organization"""
    print("🚀 Backend Development Protocol: Test Organization")
    print("=" * 60)
    
    try:
        moved_files = organize_test_files()
        removed_files = remove_duplicate_tests()
        
        print("\n✅ Test organization completed successfully!")
        print(f"📁 Moved: {len(moved_files)} files")
        print(f"🗑️ Removed: {len(removed_files)} duplicates")
        
    except Exception as e:
        print(f"\n❌ Error during test organization: {e}")
        raise

if __name__ == "__main__":
    main() 