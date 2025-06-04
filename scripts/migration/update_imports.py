#!/usr/bin/env python3
"""
Import Migration Script

Updates all import statements from crafting system to repair/equipment system.
Run this script to automatically update imports across the codebase.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Import mappings from old crafting to new repair/equipment system
IMPORT_MAPPINGS = {
    # Model imports
    "from backend.systems.crafting.models": "from backend.systems.equipment.models",
    "from backend.infrastructure.crafting.services": "from backend.systems.repair.services",
    "from backend.infrastructure.crafting.repositories": "from backend.systems.repair.repositories",
    "from backend.infrastructure.crafting.schemas": "from backend.systems.repair.schemas",
    "from backend.infrastructure.crafting.routers": "from backend.api.repair.routers",
    
    # Specific service imports
    "from backend.infrastructure.crafting.services.crafting_service": "from backend.systems.repair.services.repair_service",
    "from backend.infrastructure.crafting.services.station_service": "from backend.systems.repair.services.station_service",
    
    # Model-specific imports
    "from backend.systems.crafting.models.recipe import CraftingRecipe": "from backend.systems.repair.models.repair_recipe import RepairRecipe",
    "from backend.systems.crafting.models.station import CraftingStation": "from backend.systems.repair.models.repair_station import RepairStation",
    "from backend.systems.crafting.models.ingredient import CraftingIngredient": "from backend.systems.repair.models.repair_material import RepairMaterial",
    "from backend.systems.crafting.models.result import CraftingResult": "from backend.systems.repair.models.repair_result import RepairResult",
}

# Class name mappings
CLASS_MAPPINGS = {
    "CraftingService": "RepairService",
    "CraftingRecipe": "RepairRecipe", 
    "CraftingStation": "RepairStation",
    "CraftingIngredient": "RepairMaterial",
    "CraftingResult": "RepairResult",
    "StationService": "RepairStationService",
    "RecipeRepository": "RepairRecipeRepository",
    "CraftingRepository": "RepairRepository",
}

# Method name mappings
METHOD_MAPPINGS = {
    "craft_item": "perform_repair",
    "get_craftable_items": "get_repairable_equipment",
    "can_craft": "can_repair",
    "get_crafting_stations": "get_repair_stations",
    "get_available_recipes": "get_repair_options",
}

def find_python_files(root_dir: str) -> List[Path]:
    """Find all Python files in the directory tree."""
    python_files = []
    for root, dirs, files in os.walk(root_dir):
        # Skip certain directories
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    return python_files

def update_file_content(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Update a single file's content with new imports and class names.
    
    Returns:
        (changed, changes_made): Boolean if file was changed, list of changes made
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False, []
    
    original_content = content
    changes_made = []
    
    # Update import statements
    for old_import, new_import in IMPORT_MAPPINGS.items():
        if old_import in content:
            content = content.replace(old_import, new_import)
            changes_made.append(f"Import: {old_import} -> {new_import}")
    
    # Update class names
    for old_class, new_class in CLASS_MAPPINGS.items():
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(old_class) + r'\b'
        if re.search(pattern, content):
            content = re.sub(pattern, new_class, content)
            changes_made.append(f"Class: {old_class} -> {new_class}")
    
    # Update method names
    for old_method, new_method in METHOD_MAPPINGS.items():
        # Match method calls and definitions
        patterns = [
            r'\b' + re.escape(old_method) + r'\(',  # method calls
            r'def ' + re.escape(old_method) + r'\(',  # method definitions
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, pattern.replace(old_method, new_method), content)
                changes_made.append(f"Method: {old_method} -> {new_method}")
    
    # Write back if changed
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes_made
        except Exception as e:
            print(f"Error writing {file_path}: {e}")
            return False, []
    
    return False, []

def migrate_imports(root_dir: str = "backend") -> None:
    """
    Migrate all imports in the specified directory.
    
    Args:
        root_dir: Root directory to search for Python files
    """
    print(f"🔍 Searching for Python files in {root_dir}...")
    python_files = find_python_files(root_dir)
    print(f"Found {len(python_files)} Python files")
    
    total_changed = 0
    total_changes = 0
    
    for file_path in python_files:
        # Skip files in the crafting system itself (we're deprecating it)
        if "crafting" in str(file_path) and not "test" in str(file_path):
            continue
            
        changed, changes_made = update_file_content(file_path)
        
        if changed:
            total_changed += 1
            total_changes += len(changes_made)
            print(f"✅ Updated {file_path}")
            for change in changes_made:
                print(f"   - {change}")
        else:
            # Only show files with crafting references that weren't changed
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if any(old_import in content for old_import in IMPORT_MAPPINGS.keys()):
                        print(f"⚠️  File contains crafting references but wasn't changed: {file_path}")
            except:
                pass
    
    print(f"\n🎉 Migration complete!")
    print(f"   Files changed: {total_changed}")
    print(f"   Total changes: {total_changes}")

def create_compatibility_imports(target_dir: str = "backend/api") -> None:
    """
    Create compatibility import files for any API endpoints that still reference crafting.
    """
    compatibility_content = '''"""
Temporary compatibility imports for crafting-to-repair migration.

This file provides imports that maintain API compatibility during the transition.
Remove this file after migration is complete.
"""

import warnings

# Import the compatibility service
from backend.systems.repair.compat.crafting_bridge import (
    CraftingCompatibilityService,
    create_crafting_compatibility_service
)

# Create aliases for common crafting classes (for backwards compatibility)
CraftingService = CraftingCompatibilityService

warnings.warn(
    "Using compatibility crafting imports. Please migrate to repair system.",
    DeprecationWarning,
    stacklevel=2
)
'''
    
    compatibility_file = Path(target_dir) / "crafting_compat.py"
    try:
        compatibility_file.parent.mkdir(parents=True, exist_ok=True)
        with open(compatibility_file, 'w') as f:
            f.write(compatibility_content)
        print(f"✅ Created compatibility imports at {compatibility_file}")
    except Exception as e:
        print(f"❌ Error creating compatibility imports: {e}")

if __name__ == "__main__":
    print("🚀 Starting crafting-to-repair import migration...")
    
    # Get the project root (assuming script is in scripts/migration/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    backend_dir = project_root / "backend"
    
    if not backend_dir.exists():
        print(f"❌ Backend directory not found at {backend_dir}")
        print("Please run this script from the project root or adjust the path.")
        exit(1)
    
    # Run the migration
    migrate_imports(str(backend_dir))
    
    # Create compatibility imports
    create_compatibility_imports(str(backend_dir / "api"))
    
    print("\n📋 Next steps:")
    print("1. Review the changes made by this script")
    print("2. Run tests to ensure nothing is broken")
    print("3. Update any remaining crafting references manually")
    print("4. Update API documentation")
    print("5. Remove crafting system when ready") 