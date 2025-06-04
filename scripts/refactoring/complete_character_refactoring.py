#!/usr/bin/env python3
"""
Complete Character System Refactoring Script

This script completes the refactoring of backend/systems/character by:
1. Moving misplaced files to their correct systems
2. Updating imports throughout the codebase  
3. Removing duplicate files
4. Ensuring consistency across the backend

Based on the Visual DM Development Bible and refactoring documentation.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# Base directory for the project
BASE_DIR = Path("/Users/Sharrone/Dreamforge")
BACKEND_DIR = BASE_DIR / "backend"
CHARACTER_DIR = BACKEND_DIR / "systems" / "character"

# File relocations: (source_path, target_system, target_filename)
FILE_RELOCATIONS = [
    # Rumor system files
    ("models/rumor.py", "rumor", "models/rumor.py"),
    ("models/prompt_manager.py", "rumor", None),  # None means delete (duplicate exists)
    
    # World state files  
    ("models/world_state_manager.py", "world_state", "models/world_state_manager.py"),
    ("models/world_state_loader.py", "world_state", "models/world_state_loader.py"),
    
    # Quest system files
    ("models/quest_utils.py", "quest", "utils/quest_utils.py"),
    ("models/quest_validators.py", "quest", "validators/quest_validators.py"),
    ("models/quest_state_manager.py", "quest", "managers/quest_state_manager.py"),
    
    # World generation files
    ("models/worldgen_utils.py", "world_generation", "utils/worldgen_utils.py"),
    
    # Tension/War files
    ("models/tension_utils.py", "tension_war", "utils/tension_utils.py"),
    
    # Region files
    ("models/region_revolt_utils.py", "region", "utils/region_revolt_utils.py"),
    
    # Loot/Analytics files
    ("models/history.py", "loot", "models/history.py"),
    
    # Auth/User files
    ("models/user_models.py", "auth_user", "models/user_models.py"),
    
    # Economy files
    ("models/shop_utils.py", "economy", "utils/shop_utils.py"),
]

# Import replacements: (old_import_pattern, new_import_pattern)
IMPORT_REPLACEMENTS = [
    # Rumor system
    (r"from backend\.systems\.character\.models\.rumor", "from backend.systems.rumor.models.rumor"),
    (r"from backend\.systems\.character\.models\.prompt_manager", "from backend.systems.rumor.prompt_manager"),
    
    # World state
    (r"from backend\.systems\.character\.models\.world_state_manager", "from backend.systems.world_state.models.world_state_manager"),
    (r"from backend\.systems\.character\.models\.world_state_loader", "from backend.systems.world_state.models.world_state_loader"),
    
    # Quest system
    (r"from backend\.systems\.character\.models\.quest_utils", "from backend.systems.quest.utils.quest_utils"),
    (r"from backend\.systems\.character\.models\.quest_validators", "from backend.systems.quest.validators.quest_validators"),
    (r"from backend\.systems\.character\.models\.quest_state_manager", "from backend.systems.quest.managers.quest_state_manager"),
    
    # World generation
    (r"from backend\.systems\.character\.models\.worldgen_utils", "from backend.systems.world_generation.utils.worldgen_utils"),
    
    # Tension/War
    (r"from backend\.systems\.character\.models\.tension_utils", "from backend.systems.tension.utils.tension_utils"),
    
    # Region
    (r"from backend\.systems\.character\.models\.region_revolt_utils", "from backend.systems.region.utils.region_revolt_utils"),
    
    # Loot
    (r"from backend\.systems\.character\.models\.history", "from backend.systems.loot.models.history"),
    
    # Auth/User
    (r"from backend\.systems\.character\.models\.user_models", "from backend.infrastructure.auth_user.models.user_models"),
    
    # Economy
    (r"from backend\.systems\.character\.models\.shop_utils", "from backend.infrastructure.utils.shop_utils"),
]

def ensure_directory_exists(path: Path):
    """Ensure a directory exists, creating it if necessary."""
    path.mkdir(parents=True, exist_ok=True)

def move_file(source_path: Path, target_path: Path):
    """Move a file from source to target, creating directories if needed."""
    ensure_directory_exists(target_path.parent)
    shutil.move(str(source_path), str(target_path))
    print(f"Moved: {source_path} -> {target_path}")

def delete_file(file_path: Path):
    """Delete a file."""
    if file_path.exists():
        file_path.unlink()
        print(f"Deleted duplicate: {file_path}")

def update_imports_in_file(file_path: Path, replacements: List[Tuple[str, str]]):
    """Update import statements in a Python file."""
    if not file_path.exists() or file_path.suffix != '.py':
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for old_pattern, new_pattern in replacements:
            content = re.sub(old_pattern, new_pattern, content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated imports in: {file_path}")
            
    except Exception as e:
        print(f"Error updating {file_path}: {e}")

def find_python_files(directory: Path) -> List[Path]:
    """Find all Python files in a directory recursively."""
    python_files = []
    for path in directory.rglob("*.py"):
        python_files.append(path)
    return python_files

def relocate_files():
    """Move files to their correct systems."""
    print("=== Relocating Files ===")
    
    for source_rel_path, target_system, target_filename in FILE_RELOCATIONS:
        source_path = CHARACTER_DIR / source_rel_path
        
        if not source_path.exists():
            print(f"Warning: Source file not found: {source_path}")
            continue
            
        if target_filename is None:
            # Delete duplicate file
            delete_file(source_path)
            continue
            
        target_system_dir = BACKEND_DIR / "systems" / target_system
        target_path = target_system_dir / target_filename
        
        # Create target directory structure
        ensure_directory_exists(target_path.parent)
        
        # Move the file
        move_file(source_path, target_path)

def update_all_imports():
    """Update imports throughout the backend."""
    print("\n=== Updating Imports ===")
    
    # Find all Python files in backend
    python_files = find_python_files(BACKEND_DIR)
    
    for file_path in python_files:
        update_imports_in_file(file_path, IMPORT_REPLACEMENTS)

def verify_character_system():
    """Verify that the character system structure is correct."""
    print("\n=== Verifying Character System ===")
    
    # Check that only character-related files remain in models/
    models_dir = CHARACTER_DIR / "models"
    if models_dir.exists():
        remaining_files = list(models_dir.glob("*.py"))
        print(f"Remaining files in character/models/: {len(remaining_files)}")
        
        character_related_files = [
            "relationship.py", "mood.py", "goal.py", "visual_model.py", 
            "model.py", "base.py", "serialization.py", "randomization.py",
            "blendshapes.py", "materials.py", "animation.py", "mesh.py", 
            "presets.py", "__init__.py"
        ]
        
        for file_path in remaining_files:
            if file_path.name not in character_related_files:
                print(f"WARNING: Non-character file still in models/: {file_path.name}")

def create_missing_init_files():
    """Create __init__.py files in directories that need them."""
    print("\n=== Creating Missing __init__.py Files ===")
    
    directories_needing_init = [
        "backend/systems/rumor/models",
        "backend/systems/world_state/models", 
        "backend/systems/quest/utils",
        "backend/systems/quest/validators",
        "backend/systems/quest/managers",
        "backend/systems/world_generation/utils",
        "backend/systems/tension_war/utils",
        "backend/systems/region/utils",
        "backend/systems/loot/models",
        "backend/systems/auth_user/models",
        "backend/systems/economy/utils",
    ]
    
    for dir_path in directories_needing_init:
        init_path = BASE_DIR / dir_path / "__init__.py"
        if not init_path.parent.exists():
            ensure_directory_exists(init_path.parent)
        
        if not init_path.exists():
            with open(init_path, 'w') as f:
                f.write('"""Auto-generated __init__.py"""\n')
            print(f"Created: {init_path}")

def main():
    """Main function to execute the refactoring."""
    print("Starting Character System Refactoring Completion...")
    print(f"Base directory: {BASE_DIR}")
    print(f"Character directory: {CHARACTER_DIR}")
    
    # Step 1: Relocate files
    relocate_files()
    
    # Step 2: Create missing __init__.py files
    create_missing_init_files()
    
    # Step 3: Update imports
    update_all_imports()
    
    # Step 4: Verify the result
    verify_character_system()
    
    print("\n=== Refactoring Complete ===")
    print("Next steps:")
    print("1. Run tests to ensure everything still works")
    print("2. Check for any remaining import errors")
    print("3. Remove any empty directories")
    print("4. Update documentation if needed")

if __name__ == "__main__":
    main() 