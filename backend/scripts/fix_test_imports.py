#!/usr/bin/env python3
"""
Script to fix broken imports in test files after backend refactoring.
This script identifies and fixes common import patterns that were broken during the refactoring.
"""

import os
import re
import glob
from pathlib import Path

def fix_import_line(line, filename):
    """
    Fix a single import line based on common patterns.
    
    Args:
        line: The line of code to potentially fix
        filename: The filename for context
    
    Returns:
        The fixed line or the original line if no fix needed
    """
    # Pattern 1: Fix wildcard imports from systems
    # from backend.systems.{system} import * -> more specific imports
    wildcard_pattern = r'from backend\.systems\.(\w+) import \*'
    match = re.match(wildcard_pattern, line.strip())
    
    if match:
        system_name = match.group(1)
        
        # Determine what to import based on the test file name
        test_type = None
        if 'test_models' in filename:
            test_type = 'models'
        elif 'test_repositories' in filename:
            test_type = 'repositories'
        elif 'test_routers' in filename:
            test_type = 'routers'
        elif 'test_services' in filename:
            test_type = 'services'
        elif 'test_schemas' in filename:
            test_type = 'schemas'
        elif 'test_events' in filename:
            test_type = 'events'
        elif 'test_utils' in filename:
            test_type = 'utils'
        
        if test_type:
            # Import the specific module instead of wildcard
            return f"from backend.systems.{system_name} import {test_type}\n"
        else:
            # For general test files, import common modules
            return f"from backend.systems.{system_name} import models, repositories, services, schemas\n"
    
    # Pattern 2: Fix infrastructure wildcard imports
    # from backend.infrastructure.{system} import * -> more specific imports
    infra_wildcard_pattern = r'from backend\.infrastructure\.(\w+) import \*'
    match = re.match(infra_wildcard_pattern, line.strip())
    
    if match:
        system_name = match.group(1)
        
        # Determine what to import based on the test file name
        test_type = None
        if 'test_models' in filename:
            test_type = 'models'
        elif 'test_repositories' in filename:
            test_type = 'repositories'
        elif 'test_routers' in filename:
            test_type = 'routers'
        elif 'test_services' in filename:
            test_type = 'services'
        elif 'test_schemas' in filename:
            test_type = 'schemas'
        elif 'test_events' in filename:
            test_type = 'events'
        elif 'test_utils' in filename:
            test_type = 'utils'
        
        if test_type:
            # Import the specific module instead of wildcard
            return f"from backend.infrastructure.{system_name} import {test_type}\n"
        else:
            # For general test files, import common modules that might exist
            return f"from backend.infrastructure.{system_name} import models, services\n"
    
    # Pattern 3: Fix direct module imports that may have moved structure
    # from backend.systems.{system} import {module} -> from backend.systems.{system}.{subdir} import {module}
    direct_module_pattern = r'from backend\.systems\.(\w+) import (\w+)'
    match = re.match(direct_module_pattern, line.strip())
    
    if match:
        system_name = match.group(1)
        module_name = match.group(2)
        
        # Skip if this is already a known good pattern (like models, repositories, etc.)
        if module_name in ['models', 'repositories', 'services', 'schemas', 'routers', 'events', 'utils']:
            return line
        
        # Map known module patterns to their new locations
        module_location_map = {
            # Common patterns
            'export': 'utils.export',
            'factory': 'utils.factory', 
            'migrations': 'utils.migrations',
            'validator': 'utils.validator',
            'notification': 'utils.notification',
            'operations': 'utils.operations',
            'transformer': 'utils.transformer',
            'truth_tracker': 'utils.truth_tracker',
            'manager': 'services.manager',
            'websocket_events': 'services.websocket_events',
            'arc': 'core.arc',
            
            # NPC specific
            'npc_builder_class': 'services.npc_builder_class',
            'npc_location_service': 'services.npc_location_service', 
            'npc_routes': 'routers.npc_routes',
            'npc_character_routes': 'routers.npc_character_routes',
            'npc_travel_utils': 'utils.npc_travel_utils',
            'npc_loyalty_class': 'utils.npc_loyalty_class',
            
            # Equipment specific
            'durability_utils': 'utils.durability_utils',
            'set_bonus_utils': 'utils.set_bonus_utils',
            'inventory_utils': 'utils.inventory_utils',
            'identify_item_utils': 'utils.identify_item_utils',
            
            # World state specific
            'world_routes': 'routers.world_routes',
        }
        
        if module_name in module_location_map:
            new_location = module_location_map[module_name]
            return f"from backend.systems.{system_name}.{new_location} import {module_name}\n"
    
    # Pattern 4: Fix infrastructure direct module imports
    infra_direct_pattern = r'from backend\.infrastructure\.(\w+) import (\w+)'
    match = re.match(infra_direct_pattern, line.strip())
    
    if match:
        system_name = match.group(1)
        module_name = match.group(2)
        
        # Skip if this is already a known good pattern
        if module_name in ['models', 'repositories', 'services', 'schemas', 'routers', 'events', 'utils']:
            return line
            
        # Map known infrastructure modules
        infra_module_map = {
            'event_dispatcher': 'services.event_dispatcher',
            'canonical_events': 'events.canonical_events',
            'event_types': 'events.event_types',
        }
        
        if module_name in infra_module_map:
            new_location = infra_module_map[module_name]
            return f"from backend.infrastructure.{system_name}.{new_location} import {module_name}\n"
    
    # Pattern 5: Fix specific module imports that may have moved
    # This handles cases like from backend.systems.{system}.{old_module} import something
    specific_pattern = r'from backend\.systems\.(\w+)\.(\w+) import (.+)'
    match = re.match(specific_pattern, line.strip())
    
    if match:
        system_name = match.group(1)
        module_name = match.group(2)
        imports = match.group(3)
        
        # Map old module names to new structure
        module_mapping = {
            'gpt_client': 'services.gpt_client',
            'manager': 'services.manager',
            'core_models': 'models',
            'database': 'repositories',
            'repository': 'repositories',
            'websocket_manager': 'services.websocket_manager',
            'event_publisher': 'events.event_publisher',
            'exceptions': 'models.exceptions',
        }
        
        if module_name in module_mapping:
            new_module = module_mapping[module_name]
            return f"from backend.systems.{system_name}.{new_module} import {imports}\n"
    
    return line

def fix_test_file(filepath):
    """
    Fix imports in a single test file.
    
    Args:
        filepath: Path to the test file
    """
    print(f"Processing: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        fixed_lines = []
        changes_made = False
        
        for line in lines:
            fixed_line = fix_import_line(line, os.path.basename(filepath))
            if fixed_line != line:
                changes_made = True
                print(f"  Fixed: {line.strip()} -> {fixed_line.strip()}")
            fixed_lines.append(fixed_line)
        
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
            print(f"  ✅ Updated {filepath}")
        else:
            print(f"  ⏭️  No changes needed for {filepath}")
            
    except Exception as e:
        print(f"  ❌ Error processing {filepath}: {e}")

def main():
    """Main function to fix all test imports."""
    print("🔧 Starting test import fixes...")
    
    # Get the script directory and navigate to backend root
    script_dir = Path(__file__).parent
    backend_root = script_dir.parent
    
    # Find all Python test files
    test_patterns = [
        'tests/systems/**/*.py',
        'tests/integration/**/*.py',
    ]
    
    all_test_files = []
    for pattern in test_patterns:
        test_files = glob.glob(str(backend_root / pattern), recursive=True)
        all_test_files.extend(test_files)
    
    # Filter out __init__.py and __pycache__ files
    test_files = [f for f in all_test_files 
                 if not f.endswith('__init__.py') 
                 and '__pycache__' not in f
                 and '.pyc' not in f]
    
    print(f"Found {len(test_files)} test files to process")
    
    # Process each file
    for test_file in sorted(test_files):
        fix_test_file(test_file)
    
    print("\n✅ Import fixes completed!")
    print("\n🧪 You may want to run the tests to verify the fixes:")
    print("   python -m pytest backend/tests/ -v")

if __name__ == "__main__":
    main() 