#!/usr/bin/env python3
"""
Script to fix chaos system imports after architectural refactoring.
Updates imports from backend.systems.chaos.{api,schemas,repositories,routers,utils,models}
to backend.infrastructure.chaos.{api,schemas,repositories,utils,models}
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Define the import mappings
        mappings = [
            # API imports
            (r'from backend\.systems\.chaos\.api\.', 'from backend.infrastructure.systems.chaos.api.'),
            # Schema imports
            (r'from backend\.systems\.chaos\.schemas\.', 'from backend.infrastructure.systems.chaos.schemas.'),
            # Repository imports
            (r'from backend\.systems\.chaos\.repositories\.', 'from backend.infrastructure.systems.chaos.repositories.'),
            # Router imports (moved to api)
            (r'from backend\.systems\.chaos\.routers\.', 'from backend.infrastructure.systems.chaos.api.'),
            # Utils imports
            (r'from backend\.systems\.chaos\.utils\.', 'from backend.infrastructure.systems.chaos.utils.'),
            # Models imports
            (r'from backend\.systems\.chaos\.models\.', 'from backend.infrastructure.systems.chaos.models.'),
        ]
        
        # Apply each mapping
        for pattern, replacement in mappings:
            content = re.sub(pattern, replacement, content)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {file_path}")
            return True
        else:
            print(f"No changes: {file_path}")
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix all imports"""
    # Get all Python files that need updating
    files_to_update = [
        # Core business logic files
        "backend/systems/chaos/core/system_integrator.py",
        "backend/systems/chaos/core/pressure_monitor.py", 
        "backend/systems/chaos/core/event_triggers.py",
        "backend/systems/chaos/core/narrative_moderator.py",
        "backend/systems/chaos/core/chaos_engine.py",
        "backend/systems/chaos/core/cascade_engine.py",
        "backend/systems/chaos/core/warning_system.py",
        "backend/systems/chaos/core/event_trigger.py",
        
        # Service files
        "backend/systems/chaos/services/event_service.py",
        "backend/systems/chaos/services/mitigation_service.py",
        "backend/systems/chaos/services/pressure_service.py",
        "backend/systems/chaos/services/chaos_service.py",
        "backend/systems/chaos/services/event_manager.py",
        
        # Analytics files
        "backend/systems/chaos/analytics/chaos_analytics.py",
        "backend/systems/chaos/analytics/event_tracker.py",
        
        # Infrastructure files that reference each other
        "backend/infrastructure/chaos/utils/event_utils.py",
        "backend/infrastructure/chaos/utils/pressure_calculations.py",
        "backend/infrastructure/chaos/utils/chaos_calculator.py",
        "backend/infrastructure/chaos/utils/event_helpers.py",
        
        # Test files
        "backend/tests/integration/root_tests/test_chaos_system.py",
        "backend/tests/systems/chaos/test_task_49_components.py",
        "backend/tests/systems/chaos/test_chaos_utils.py",
        "backend/tests/systems/chaos/test_chaos_models.py",
        "backend/tests/systems/chaos/test_complete_chaos_system.py",
    ]
    
    updated_count = 0
    for file_path in files_to_update:
        if os.path.exists(file_path):
            if fix_imports_in_file(file_path):
                updated_count += 1
        else:
            print(f"File not found: {file_path}")
    
    print(f"\nCompleted: Updated {updated_count} files")

if __name__ == "__main__":
    main() 