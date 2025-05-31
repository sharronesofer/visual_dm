#!/usr/bin/env python3
"""
Script to fix import issues identified in Task 27 analysis
Converts non-canonical imports to canonical backend.systems.* format
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Set

def fix_import_issues():
    """Main function to fix import issues"""
    backend_path = Path('.')  # Current directory is already backend/
    systems_path = backend_path / 'systems'
    
    if not systems_path.exists():
        print(f"❌ Systems path not found: {systems_path}")
        return
    
    # Common import mappings
    import_mappings = {
        # Standard library imports that were incorrectly flagged
        'dataclasses': None,  # Keep as is
        'time': None,  # Keep as is
        
        # Local imports that need to be canonical
        'economy_manager': 'backend.systems.economy.economy_manager',
        'memory': 'backend.systems.memory.memory',
        'memory_manager': 'backend.systems.memory.memory_manager',
        'memory_utils': 'backend.systems.memory.memory_utils',
        'memory_categories': 'backend.systems.memory.memory_categories',
        'combat_class': 'backend.systems.combat.combat_class',
        'combat_state_class': 'backend.systems.combat.combat_state_class',
        'combat_area': 'backend.systems.combat.combat_area',
        'combat_animation_system': 'backend.systems.combat.combat_animation_system',
        'combat_debug_interface': 'backend.systems.combat.combat_debug_interface',
        'combat_ram': 'backend.systems.combat.combat_ram',
        'combat_state_firebase_utils': 'backend.systems.combat.combat_state_firebase_utils',
        'canonical_events': 'backend.systems.events.canonical_events',
        'dialogue.scoring': 'backend.systems.dialogue.scoring',
        'dialogue.extractors': 'backend.systems.dialogue.extractors',
        'rumor_transformer': 'backend.systems.rumor.rumor_transformer',
        'faction_service': 'backend.systems.faction.services.faction_service',
        'arc_manager': 'backend.systems.arc.services.arc_manager',
        'npc_quests': 'backend.systems.npc.npc_quests',
        'integration': 'backend.systems.integration',
        'database': 'backend.infrastructure.shared.database',
        'inventory_utils': 'backend.systems.inventory.inventory_utils',
    }
    
    # Standard library modules that should not be converted
    stdlib_modules = {
        'os', 'sys', 'json', 'ast', 're', 'pathlib', 'typing', 'collections',
        'datetime', 'uuid', 'hashlib', 'logging', 'sqlite3', 'asyncio',
        'dataclasses', 'time', 'math', 'random', 'copy', 'functools',
        'itertools', 'operator', 'pickle', 'tempfile', 'shutil', 'glob'
    }
    
    # Third-party modules that should not be converted
    thirdparty_modules = {
        'fastapi', 'pydantic', 'sqlalchemy', 'pytest', 'uvicorn', 'httpx',
        'pandas', 'numpy', 'requests', 'click', 'jinja2', 'websockets',
        'openai', 'firebase_admin', 'dateutil'
    }
    
    # Import mappings for local imports
    local_import_mappings = {
        '.models': 'backend.systems.{system}.models',
        '.services': 'backend.systems.{system}.services', 
        '.repositories': 'backend.systems.{system}.repositories',
        '.routers': 'backend.systems.{system}.routers',
        '.schemas': 'backend.systems.{system}.schemas',
        '.utils': 'backend.systems.{system}.utils',
        '.core': 'backend.systems.{system}.core',
        '.database': 'backend.systems.{system}.database'
    }
    
    files_processed = 0
    files_fixed = 0
    
    # Process all Python files in systems
    for py_file in systems_path.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
            
        files_processed += 1
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
                
            # Fix relative imports
            content = fix_relative_imports(original_content, py_file, backend_path)
            
            # Fix local imports  
            system_name = get_system_name(py_file, systems_path)
            if system_name:
                mappings = {k: v.format(system=system_name) for k, v in local_import_mappings.items()}
                content = fix_local_imports(content, mappings, stdlib_modules, thirdparty_modules)
            
            # Write back if changed
            if content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_fixed += 1
                print(f"✅ Fixed imports in: {py_file.relative_to(backend_path)}")
                
        except Exception as e:
            print(f"❌ Error processing {py_file}: {e}")
    
    print(f"\nProcessed {files_processed} files, fixed imports in {files_fixed} files")

def get_system_name(file_path: Path, systems_path: Path) -> str:
    """Get the system name from a file path"""
    try:
        relative_path = file_path.relative_to(systems_path)
        return relative_path.parts[0] if relative_path.parts else ""
    except ValueError:
        return ""

def fix_relative_imports(content: str, file_path: Path, backend_path: Path) -> str:
    """Convert relative imports to absolute canonical imports"""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Match relative imports like "from backend.systems.module import something"
        relative_match = re.match(r'^(\s*)from\s+\.([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import\s+(.+)$', line)
        if relative_match:
            indent, module_path, imports = relative_match.groups()
            
            # Determine the canonical path
            relative_to_systems = file_path.relative_to(backend_path)
            system_name = relative_to_systems.parts[0]
            
            # Convert to canonical import
            canonical_module = f"backend.systems.{system_name}.{module_path}"
            fixed_line = f"{indent}from {canonical_module} import {imports}"
            fixed_lines.append(fixed_line)
            continue
        
        # Match relative imports like "from backend.systems import module"
        relative_match2 = re.match(r'^(\s*)from\s+\.\s+import\s+(.+)$', line)
        if relative_match2:
            indent, imports = relative_match2.groups()
            
            # Determine the canonical path
            relative_to_systems = file_path.relative_to(backend_path)
            system_name = relative_to_systems.parts[0]
            
            # Convert to canonical import
            canonical_module = f"backend.systems.{system_name}"
            fixed_line = f"{indent}from {canonical_module} import {imports}"
            fixed_lines.append(fixed_line)
            continue
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_local_imports(content: str, mappings: Dict[str, str], stdlib: Set[str], thirdparty: Set[str]) -> str:
    """Fix local imports using the mapping table"""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Match "from module import something"
        import_match = re.match(r'^(\s*)from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import\s+(.+)$', line)
        if import_match:
            indent, module, imports = import_match.groups()
            
            # Skip if it's already canonical
            if module.startswith('backend.systems.'):
                fixed_lines.append(line)
                continue
            
            # Skip standard library and third-party modules
            root_module = module.split('.')[0]
            if root_module in stdlib or root_module in thirdparty:
                fixed_lines.append(line)
                continue
            
            # Check if we have a mapping for this module
            if module in mappings and mappings[module] is not None:
                canonical_module = mappings[module]
                fixed_line = f"{indent}from {canonical_module} import {imports}"
                fixed_lines.append(fixed_line)
                continue
        
        # Match "import module"
        import_match2 = re.match(r'^(\s*)import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)$', line)
        if import_match2:
            indent, module = import_match2.groups()
            
            # Skip if it's already canonical
            if module.startswith('backend.systems.'):
                fixed_lines.append(line)
                continue
            
            # Skip standard library and third-party modules
            root_module = module.split('.')[0]
            if root_module in stdlib or root_module in thirdparty:
                fixed_lines.append(line)
                continue
            
            # Check if we have a mapping for this module
            if module in mappings and mappings[module] is not None:
                canonical_module = mappings[module]
                fixed_line = f"{indent}import {canonical_module}"
                fixed_lines.append(fixed_line)
                continue
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def create_missing_init_files():
    """Create missing __init__.py files"""
    print("📁 Creating missing __init__.py files...")
    
    backend_path = Path('.')  # Current directory is already backend/
    systems_path = backend_path / 'systems'
    
    if not systems_path.exists():
        print(f"❌ Systems path not found: {systems_path}")
        return
    
    # Get all directories that need __init__.py files
    directories_needing_init = set()
    
    # Check systems directory
    for py_file in systems_path.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        # Add all parent directories up to systems/
        current_dir = py_file.parent
        while current_dir != systems_path.parent:
            if current_dir != systems_path:  # Don't add systems/ itself
                directories_needing_init.add(current_dir)
            current_dir = current_dir.parent
    
    # Create missing __init__.py files
    created_count = 0
    for directory in directories_needing_init:
        init_file = directory / "__init__.py"
        if not init_file.exists():
            try:
                init_file.write_text("")
                created_count += 1
                print(f"✅ Created: {init_file.relative_to(backend_path)}")
            except Exception as e:
                print(f"❌ Failed to create {init_file}: {e}")
    
    print(f"Created {created_count} __init__.py files")

if __name__ == "__main__":
    print("🔧 Fixing import issues...")
    fix_import_issues()
    
    print("\n📁 Creating missing __init__.py files...")
    create_missing_init_files()
    
    print("\n✅ Import fixes complete!") 