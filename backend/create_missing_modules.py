#!/usr/bin/env python3
"""
Script to identify and create missing modules that are being imported.
"""

import os
import re
from pathlib import Path

def find_missing_imports():
    """Find import statements for modules that don't exist."""
    missing_imports = set()
    
    # Scan all Python files for import statements
    for py_file in Path('systems').rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find imports of the form: from backend.systems.MODULE_NAME import ...
            import_matches = re.findall(r'from backend\.systems\.([^.\s]+)', content)
            
            for module_name in import_matches:
                module_path = Path(f'systems/{module_name}')
                if not module_path.exists():
                    missing_imports.add(module_name)
                    
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    return missing_imports

def create_stub_module(module_name):
    """Create a basic stub module with __init__.py."""
    module_path = Path(f'systems/{module_name}')
    
    # Create directory
    module_path.mkdir(exist_ok=True)
    
    # Create __init__.py
    init_file = module_path / '__init__.py'
    if not init_file.exists():
        init_content = f'''"""
{module_name.replace('_', ' ').title()} module for Visual DM backend.
Auto-generated stub module.
"""

# This is a stub module created to resolve import errors.
# Implement the actual functionality as needed.

__all__ = []
'''
        
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write(init_content)
        
        print(f"Created stub module: {module_path}")
        return True
    
    return False

def find_specific_missing_imports():
    """Find specific imports that are missing from modules."""
    missing_classes = {}
    
    for py_file in Path('systems').rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find specific imports: from backend.systems.MODULE import CLASS
            specific_imports = re.findall(r'from backend\.systems\.([^.\s]+)\s+import\s+([^#\n]+)', content)
            
            for module_name, imports in specific_imports:
                module_path = Path(f'systems/{module_name}')
                if module_path.exists():
                    # Check if the imported classes exist
                    init_file = module_path / '__init__.py'
                    if init_file.exists():
                        with open(init_file, 'r', encoding='utf-8') as f:
                            init_content = f.read()
                        
                        # Parse imported items
                        imported_items = [item.strip() for item in imports.split(',')]
                        for item in imported_items:
                            item = item.strip()
                            if item and item not in init_content:
                                if module_name not in missing_classes:
                                    missing_classes[module_name] = set()
                                missing_classes[module_name].add(item)
                
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    return missing_classes

def main():
    """Main function to find and create missing modules."""
    print("🔍 Scanning for missing modules...")
    
    missing_modules = find_missing_imports()
    
    if missing_modules:
        print(f"Found {len(missing_modules)} missing modules:")
        for module in sorted(missing_modules):
            print(f"  - {module}")
        
        print("\n🔨 Creating stub modules...")
        created = 0
        for module in missing_modules:
            if create_stub_module(module):
                created += 1
        
        print(f"Created {created} stub modules.")
    else:
        print("✅ No missing modules found.")
    
    print("\n🔍 Scanning for missing classes/imports...")
    missing_classes = find_specific_missing_imports()
    
    if missing_classes:
        print("Missing classes/functions in existing modules:")
        for module, classes in missing_classes.items():
            print(f"  {module}: {', '.join(sorted(classes))}")
    else:
        print("✅ No missing classes found in existing modules.")

if __name__ == '__main__':
    main() 