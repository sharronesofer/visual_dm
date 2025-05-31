#!/usr/bin/env python3
"""
Fix problematic import paths that have .models.models instead of just .models.
This is a conservative fix that only changes import paths, not model names.
"""

import os
import re

def fix_models_imports():
    """Fix import paths from .models.models to .models"""
    
    # Define the problematic patterns and their fixes
    import_fixes = [
        (r'from backend\.systems\.npc\.models\.models import', 'from backend.systems.npc.models import'),
        (r'from backend\.systems\.poi\.models\.models import', 'from backend.systems.poi.models import'),
        (r'from backend\.systems\.religion\.models\.models import', 'from backend.systems.religion.models import'),
        (r'from backend\.systems\.character\.models\.models import', 'from backend.systems.character.models import'),
        (r'from backend\.systems\.faction\.models\.models import', 'from backend.systems.faction.models import'),
    ]
    
    # Find all Python files in backend
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip __pycache__ and .git directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    fixed_files = 0
    total_fixes = 0
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply import path fixes
            for pattern, replacement in import_fixes:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    total_fixes += 1
            
            # Write back if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"Fixed: {file_path}")
                fixed_files += 1
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    print(f"\nSummary:")
    print(f"Fixed {fixed_files} files")
    print(f"Applied {total_fixes} import path fixes")

if __name__ == "__main__":
    print("Fixing problematic .models.models import paths...")
    fix_models_imports()
    print("Done!") 