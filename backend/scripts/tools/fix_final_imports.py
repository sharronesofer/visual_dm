#!/usr/bin/env python3
"""
Fix all remaining relative imports to canonical backend.systems.* format
Final comprehensive import fixes for Backend Development Protocol
"""

import re
from pathlib import Path

def fix_final_imports():
    """Fix all remaining relative imports with comprehensive patterns"""
    
    # Get all files with remaining relative imports
    remaining_files = [
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
    
    for file_path in remaining_files:
        try:
            path = Path(file_path)
            if not path.exists():
                print(f"File not found: {file_path}")
                continue
                
            # Extract system name from path
            system_name = path.parts[1]
            
            content = path.read_text()
            original = content
            
            # Comprehensive pattern fixes
            
            # Pattern 1: from ..models import -> from backend.systems.SYSTEM.models import
            content = re.sub(
                r'from \.\.([a-zA-Z_]+) import',
                f'from backend.systems.{system_name}.\\1 import',
                content
            )
            
            # Pattern 2: from .models import -> from backend.systems.SYSTEM.models import  
            content = re.sub(
                r'from \.([a-zA-Z_]+) import',
                f'from backend.systems.{system_name}.\\1 import',
                content
            )
            
            # Pattern 3: from ...shared import -> from backend.systems.shared import
            content = re.sub(
                r'from \.\.\.([a-zA-Z_]+) import',
                r'from backend.systems.\1 import',
                content
            )
            
            # Pattern 4: from ....shared import -> from backend.systems.shared import (4 dots)
            content = re.sub(
                r'from \.\.\.\.([a-zA-Z_]+) import',
                r'from backend.systems.\1 import',
                content
            )
            
            # Pattern 5: Multiline imports with parentheses
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
            
            # Pattern 6: Multi-level relative imports
            content = re.sub(
                r'from \.\.\.([a-zA-Z_]+)\.([a-zA-Z_]+) import',
                r'from backend.systems.\1.\2 import',
                content
            )
            
            # Pattern 7: Cross-system imports (e.g., from ..events import)
            # These should map to backend.systems.events
            content = re.sub(
                r'from \.\.events import',
                'from backend.systems.events import',
                content
            )
            
            content = re.sub(
                r'from \.\.shared import',
                'from backend.systems.shared import',
                content
            )
            
            if content != original:
                path.write_text(content)
                fixed_count += 1
                print(f'Fixed: {file_path}')
            else:
                print(f'No changes needed: {file_path}')
                
        except Exception as e:
            print(f'Error processing {file_path}: {e}')
    
    print(f'Fixed {fixed_count} files with remaining imports')

if __name__ == "__main__":
    fix_final_imports() 