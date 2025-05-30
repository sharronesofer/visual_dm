#!/usr/bin/env python3
"""
Fix remaining relative imports to canonical backend.systems.* format
Following Backend Development Protocol requirements
"""

import re
from pathlib import Path

def fix_remaining_imports():
    """Fix all remaining relative imports using specific patterns"""
    
    files_to_fix = [
        "systems/economy/repositories/economy_repository.py",
        "systems/economy/services/economy_service.py", 
        "systems/motif/consolidated_manager.py",
        "systems/tension_war/routers/tension_router.py",
        "systems/tension_war/services/proxy_war_manager.py",
        "systems/tension_war/services/diplomatic_manager.py",
        "systems/tension_war/services/tension_manager.py",
        "systems/tension_war/services/war_manager.py",
        "systems/tension_war/services/alliance_manager.py",
        "systems/tension_war/services/peace_manager.py",
        "systems/memory/utils/memory_utils.py",
        "systems/memory/services/memory_manager.py",
        "systems/arc/routers/arc_router.py",
        "systems/arc/services/quest_integration.py",
        "systems/arc/services/arc_manager.py",
        "systems/arc/services/progression_tracker.py",
        "systems/analytics/utils/__init__.py"
    ]
    
    fixed_count = 0
    
    for file_path in files_to_fix:
        try:
            path = Path(file_path)
            if not path.exists():
                continue
                
            # Extract system name
            system_name = path.parts[1]
            
            content = path.read_text()
            original = content
            
            # Fix all relative import patterns
            # Pattern 1: from ..models import
            content = re.sub(
                r'from \.\.([a-zA-Z_]+) import',
                f'from backend.systems.{system_name}.\\1 import',
                content
            )
            
            # Pattern 2: from .models import  
            content = re.sub(
                r'from \.([a-zA-Z_]+) import',
                f'from backend.systems.{system_name}.\\1 import',
                content
            )
            
            # Pattern 3: from ...shared import
            content = re.sub(
                r'from \.\.\.([a-zA-Z_]+) import',
                r'from backend.systems.\1 import',
                content
            )
            
            # Pattern 4: Multiline imports
            content = re.sub(
                r'from \.\.([a-zA-Z_]+) import \(',
                f'from backend.systems.{system_name}.\\1 import (',
                content
            )
            
            content = re.sub(
                r'from \.([a-zA-Z_]+) import \(',
                f'from backend.systems.{system_name}.\\1 import (',
                content
            )
            
            if content != original:
                path.write_text(content)
                fixed_count += 1
                print(f'Fixed: {file_path}')
                
        except Exception as e:
            print(f'Error processing {file_path}: {e}')
    
    print(f'Fixed {fixed_count} files')

if __name__ == "__main__":
    fix_remaining_imports() 