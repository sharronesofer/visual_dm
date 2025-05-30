#!/usr/bin/env python3
"""
Fix Indentation Errors Script

This script fixes common indentation errors found during compilation.
"""

import os
import re
import sys


def fix_file_indentation(filepath):
    """Fix indentation issues in a Python file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        lines = content.split('\n')
        fixed_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Fix common patterns
            
            # Pattern 1: Fix unexpected indents at start of line
            if re.match(r'^    \w', line) and i > 0:
                prev_line = lines[i-1].strip()
                if not prev_line.endswith(':') and not prev_line.startswith('#') and prev_line:
                    # This might be an unexpected indent, dedent it
                    line = line[4:]  # Remove 4 spaces
            
            # Pattern 2: Fix missing indentation after control statements
            if i < len(lines) - 1:
                next_line = lines[i + 1] if i + 1 < len(lines) else ""
                if (line.strip().endswith(':') and 
                    next_line.strip() and 
                    not next_line.startswith(' ') and 
                    not next_line.startswith('\t')):
                    # Next line needs indentation
                    lines[i + 1] = '    ' + next_line
            
            # Pattern 3: Fix indentation level mismatches
            if line.strip() and not line.startswith('#'):
                # Count leading spaces
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces % 4 != 0 and leading_spaces > 0:
                    # Fix to nearest 4-space boundary
                    correct_spaces = (leading_spaces // 4) * 4
                    if leading_spaces % 4 >= 2:
                        correct_spaces += 4
                    line = ' ' * correct_spaces + line.lstrip()
            
            fixed_lines.append(line)
            i += 1
        
        fixed_content = '\n'.join(fixed_lines)
        
        # Only write if content changed
        if fixed_content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False


def main():
    """Main function to fix indentation errors in known problematic files."""
    
    # Files identified with indentation errors
    problem_files = [
        'backend/systems/motif/consolidated_manager.py',
        'backend/systems/motif/repository.py', 
        'backend/systems/tension_war/utils/peace_utils.py',
        'backend/systems/tension_war/utils/tension_utils.py',
        'backend/systems/world_state/world_manager.py',
        'backend/systems/world_generation/world_generator.py',
        'backend/systems/world_generation/api.py',
        'backend/systems/world_generation/components.py',
        'backend/systems/memory/api/memory_routes.py',
        'backend/systems/combat/repositories/combat_serializer.py',
        'backend/systems/combat/combat_class.py',
        'backend/systems/character/models/character_model.py',
        'backend/systems/analytics/middleware/analytics_middleware.py',
        'backend/systems/analytics/rules.py',
        'backend/systems/time/utils/time_utils.py',
        'backend/systems/time/models/calendar_model.py',
        'backend/systems/faction/services/faction_integration.py',
        'backend/systems/faction/utils.py',
        'backend/systems/migration/services/migration_service.py',
        'backend/systems/migration/services/resource_management_service.py',
        'backend/systems/poi/services/poi_service.py',
        'backend/systems/population/services/metropolitan_spread_service.py',
        'backend/systems/population/routers.py',
        'backend/systems/worldgen/system_hooks.py',
        'backend/systems/worldgen/utils.py',
        'backend/systems/worldgen/router.py',
    ]
    
    fixed_count = 0
    total_count = 0
    
    for filepath in problem_files:
        if os.path.exists(filepath):
            total_count += 1
            print(f"Fixing {filepath}...")
            if fix_file_indentation(filepath):
                fixed_count += 1
                print(f"  ✅ Fixed")
            else:
                print(f"  ⏭️  No changes needed")
        else:
            print(f"  ❌ File not found: {filepath}")
    
    print(f"\nSummary: Fixed {fixed_count}/{total_count} files")


if __name__ == "__main__":
    main() 