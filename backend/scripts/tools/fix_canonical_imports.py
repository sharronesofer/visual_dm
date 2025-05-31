#!/usr/bin/env python3
"""
Fix all relative imports to canonical backend.systems.* format
Following Backend Development Protocol requirements
"""

import re
import os
from pathlib import Path

def fix_relative_imports():
    """Fix all relative imports in backend/systems to canonical format"""
    systems_path = Path('systems')
    fixed_count = 0
    
    if not systems_path.exists():
        print("Error: systems directory not found")
        return
    
    for py_file in systems_path.rglob('*.py'):
        if py_file.is_file():
            try:
                content = py_file.read_text()
                original = content
                
                # Get the system name from the file path
                parts = py_file.parts
                if len(parts) >= 2:
                    system_name = parts[1]  # e.g., 'arc', 'motif', etc.
                    
                    # Fix relative imports like 'from backend.infrastructure.shared.models import'
                    content = re.sub(
                        r'from \.\.([a-zA-Z_]+) import',
                        f'from backend.systems.{system_name}.\\1 import',
                        content
                    )
                    
                    # Fix relative imports like 'from backend.infrastructure.shared.models import'  
                    content = re.sub(
                        r'from \.([a-zA-Z_]+) import',
                        f'from backend.systems.{system_name}.\\1 import',
                        content
                    )
                    
                    # Fix deeper relative imports like 'from backend.infrastructure.shared import'
                    content = re.sub(
                        r'from \.\.\.([a-zA-Z_]+) import',
                        r'from backend.systems.\1 import',
                        content
                    )
                    
                    # Fix multiline imports starting with 'from ..'
                    content = re.sub(
                        r'from \.\.([a-zA-Z_]+) import \(',
                        f'from backend.systems.{system_name}.\\1 import (',
                        content
                    )
                    
                    # Fix multiline imports starting with 'from .'
                    content = re.sub(
                        r'from \.([a-zA-Z_]+) import \(',
                        f'from backend.systems.{system_name}.\\1 import (',
                        content
                    )
                
                if content != original:
                    py_file.write_text(content)
                    fixed_count += 1
                    print(f'Fixed: {py_file}')
                    
            except Exception as e:
                print(f'Error processing {py_file}: {e}')
    
    print(f'Fixed {fixed_count} files with canonical imports')

if __name__ == "__main__":
    fix_relative_imports() 