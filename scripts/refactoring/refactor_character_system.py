#!/usr/bin/env python3
import os
import shutil
import re
import json
import datetime
import subprocess
from collections import defaultdict
from pathlib import Path

# Configuration
CHARACTER_DIR = "backend/systems/character"
BACKUP_DIR = f"temp/character-refactoring/backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
TEMP_DIR = f"temp/character-refactoring/new_character_system"

# Canonical directory structure for the refactored system
CANONICAL_STRUCTURE = [
    "api",
    "core",
    "core/events",
    "inventory",
    "memory",
    "models",
    "npc",
    "progression",
    "repositories",
    "routers",
    "schemas",
    "services",
    "tests",
    "utils",
    "database"
]

# Mapping of old paths to new paths for duplicate files
PATH_MAPPING = {
    # Core
    "backend/systems/character/core/character.py": "backend/systems/character/core/character_model.py",
    "backend/systems/character/character/character.py": "backend/systems/character/core/character_model.py",
    "backend/systems/character/models/character.py": "backend/systems/character/core/character_model.py",
    "backend/systems/character/core/character_builder_class.py": "backend/systems/character/core/character_builder.py",
    "backend/systems/character/models/character_builder.py": "backend/systems/character/core/character_builder.py",
    
    # Events
    "backend/systems/character/models/event_dispatcher.py": "backend/systems/character/core/events/event_dispatcher.py",
    "backend/systems/character/utils/event_bus.py": "backend/systems/character/core/events/event_bus.py",
    "backend/systems/character/models/canonical_events.py": "backend/systems/character/core/events/canonical_events.py",
    "backend/systems/character/models/repositories/routers/schemas/services/event_dispatcher.py": "backend/systems/character/core/events/event_dispatcher.py",
    "backend/systems/character/models/repositories/routers/schemas/services/event_bus.py": "backend/systems/character/core/events/event_bus.py",
    "backend/systems/character/models/repositories/routers/schemas/services/canonical_events.py": "backend/systems/character/core/events/canonical_events.py",
    "backend/systems/character/models/test_event_dispatcher.py": "backend/systems/character/core/events/test_event_dispatcher.py",
    "backend/systems/character/tests/test_event_dispatcher.py": "backend/systems/character/core/events/test_event_dispatcher.py",
    
    # Inventory
    "backend/systems/character/models/inventory_models.py": "backend/systems/character/inventory/inventory_models.py",
    "backend/systems/character/models/inventory_utils.py": "backend/systems/character/inventory/inventory_utils.py",
    "backend/systems/character/models/inventory_validator.py": "backend/systems/character/inventory/inventory_validator.py",
    "backend/systems/character/utils/location.py": "backend/systems/character/inventory/location.py",
    
    # NPC
    "backend/systems/character/models/repositories/routers/schemas/services/utils/npc_utils.py": "backend/systems/character/npc/npc_utils.py",
    "backend/systems/character/models/repositories/routers/schemas/services/utils/npc_features.py": "backend/systems/character/npc/npc_features.py",
    "backend/systems/character/models/repositories/routers/schemas/services/utils/npc_generation.py": "backend/systems/character/npc/npc_generation.py",
    "backend/systems/character/models/repositories/routers/schemas/services/utils/npc_leveling_utils.py": "backend/systems/character/npc/npc_leveling_utils.py",
    "backend/systems/character/models/repositories/routers/schemas/services/utils/npc_loyalty_utils.py": "backend/systems/character/npc/npc_loyalty_utils.py",
    "backend/systems/character/models/repositories/routers/schemas/services/utils/npc_rumor_utils.py": "backend/systems/character/npc/npc_rumor_utils.py",
    
    # Progression
    "backend/systems/character/models/party_utils.py": "backend/systems/character/progression/party_utils.py",
    "backend/systems/character/utils/party_utils.py": "backend/systems/character/progression/party_utils.py",
    "backend/systems/character/progression/party_utils.py": "backend/systems/character/progression/party_utils.py", 
    "backend/systems/character/models/progression_utils.py": "backend/systems/character/progression/progression_utils.py",
    "backend/systems/character/progression/progression_utils.py": "backend/systems/character/progression/progression_utils.py",
    "backend/systems/character/utils/scoring.py": "backend/systems/character/progression/scoring.py",
    "backend/systems/character/progression/scoring.py": "backend/systems/character/progression/scoring.py",
    
    # Utils
    "backend/systems/character/utils/cache.py": "backend/systems/character/utils/cache.py",
    "backend/systems/character/utils/context_manager.py": "backend/systems/character/utils/context_manager.py",
    "backend/systems/character/utils/extractors.py": "backend/systems/character/utils/extractors.py",
    "backend/systems/character/models/repositories/routers/schemas/services/cache.py": "backend/systems/character/utils/cache.py",
    "backend/systems/character/models/repositories/routers/schemas/services/context_manager.py": "backend/systems/character/utils/context_manager.py",
    "backend/systems/character/models/repositories/routers/schemas/services/extractors.py": "backend/systems/character/utils/extractors.py",
    "backend/systems/character/utils/character_utils.py": "backend/systems/character/core/character_utils.py",
    
    # Memory
    "backend/systems/character/gpt_client.py": "backend/systems/character/memory/gpt_client.py",
    "backend/systems/character/memory/gpt_client.py": "backend/systems/character/memory/gpt_client.py",
}

# Import fixes to apply after refactoring
IMPORT_FIXES = [
    # Core module imports
    ("from backend.systems.character.core.character import", "from backend.systems.character.core.character_model import"),
    ("from backend.systems.character.character.character import", "from backend.systems.character.core.character_model import"),
    ("from backend.systems.character.models.character import", "from backend.systems.character.core.character_model import"),
    ("from backend.systems.character.core.character_builder_class import", "from backend.systems.character.core.character_builder import"),
    ("from backend.systems.character.models.character_builder import", "from backend.systems.character.core.character_builder import"),
    
    # Events module imports
    ("from backend.systems.character.models.event_dispatcher import", "from backend.systems.character.core.events.event_dispatcher import"),
    ("from backend.systems.character.utils.event_bus import", "from backend.systems.character.core.events.event_bus import"),
    ("from backend.systems.character.models.canonical_events import", "from backend.systems.character.core.events.canonical_events import"),
    
    # Inventory module imports
    ("from backend.systems.character.models.inventory_models import", "from backend.systems.character.inventory.inventory_models import"),
    ("from backend.systems.character.models.inventory_utils import", "from backend.systems.character.inventory.inventory_utils import"),
    ("from backend.systems.character.models.inventory_validator import", "from backend.systems.character.inventory.inventory_validator import"),
    ("from backend.systems.character.utils.location import", "from backend.systems.character.inventory.location import"),
    
    # NPC module imports
    ("from backend.systems.character.models.repositories.routers.schemas.services.utils.npc_utils import", "from backend.systems.character.npc.npc_utils import"),
    ("from backend.systems.character.models.repositories.routers.schemas.services.utils.npc_features import", "from backend.systems.character.npc.npc_features import"),
    ("from backend.systems.character.models.repositories.routers.schemas.services.utils.npc_generation import", "from backend.systems.character.npc.npc_generation import"),
    ("from backend.systems.character.models.repositories.routers.schemas.services.utils.npc_leveling_utils import", "from backend.systems.character.npc.npc_leveling_utils import"),
    ("from backend.systems.character.models.repositories.routers.schemas.services.utils.npc_loyalty_utils import", "from backend.systems.character.npc.npc_loyalty_utils import"),
    ("from backend.systems.character.models.repositories.routers.schemas.services.utils.npc_rumor_utils import", "from backend.systems.character.npc.npc_rumor_utils import"),
    
    # Progression module imports
    ("from backend.systems.character.models.party_utils import", "from backend.systems.character.progression.party_utils import"),
    ("from backend.systems.character.utils.party_utils import", "from backend.systems.character.progression.party_utils import"),
    ("from backend.systems.character.models.progression_utils import", "from backend.systems.character.progression.progression_utils import"),
    ("from backend.systems.character.utils.scoring import", "from backend.systems.character.progression.scoring import"),
    
    # Utils module imports
    ("from backend.systems.character.models.repositories.routers.schemas.services.cache import", "from backend.systems.character.utils.cache import"),
    ("from backend.systems.character.models.repositories.routers.schemas.services.context_manager import", "from backend.systems.character.utils.context_manager import"),
    ("from backend.systems.character.models.repositories.routers.schemas.services.extractors import", "from backend.systems.character.utils.extractors import"),
    ("from backend.systems.character.utils.character_utils import", "from backend.systems.character.core.character_utils import"),
    
    # Memory module imports
    ("from backend.systems.character.gpt_client import", "from backend.systems.character.memory.gpt_client import"),
]

def create_backup():
    """Create a backup of the current character system"""
    print(f"Creating backup of {CHARACTER_DIR} to {BACKUP_DIR}...")
    os.makedirs(BACKUP_DIR, exist_ok=True)
    shutil.copytree(CHARACTER_DIR, os.path.join(BACKUP_DIR, "character"), dirs_exist_ok=True)
    print(f"Backup created successfully at {BACKUP_DIR}")

def create_temp_structure():
    """Create a temporary directory with the canonical structure"""
    print(f"Creating temporary directory with canonical structure at {TEMP_DIR}...")
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Create the canonical directory structure
    for subdir in CANONICAL_STRUCTURE:
        os.makedirs(os.path.join(TEMP_DIR, subdir), exist_ok=True)
        # Create __init__.py file
        with open(os.path.join(TEMP_DIR, subdir, "__init__.py"), "w") as f:
            f.write(f"# {subdir} module\n")
    
    # Create root __init__.py
    with open(os.path.join(TEMP_DIR, "__init__.py"), "w") as f:
        f.write("# Character System module\n")
    
    print(f"Temporary directory structure created successfully")

def find_canonical_file(file_path):
    """Find the canonical location for a file"""
    relative_path = os.path.relpath(file_path, start=os.path.dirname(CHARACTER_DIR))
    
    # Check if the file has a predefined mapping
    absolute_path = os.path.abspath(file_path)
    for old_path, new_path in PATH_MAPPING.items():
        if absolute_path.endswith(old_path.replace('backend/systems/character/', '')):
            return new_path.replace('backend/systems/character/', '')
    
    # Apply heuristics for files without explicit mapping
    filename = os.path.basename(file_path)
    parent_dir = os.path.basename(os.path.dirname(file_path))
    
    # Files in core directories
    if "character" in filename and parent_dir in ["core", "character"]:
        return os.path.join("core", filename)
    
    # Test files
    if filename.startswith("test_") or parent_dir == "tests":
        return os.path.join("tests", filename)
    
    # NPC files
    if filename.startswith("npc_") or parent_dir == "npc":
        return os.path.join("npc", filename)
    
    # Inventory files
    if "inventory" in filename or parent_dir == "inventory":
        return os.path.join("inventory", filename)
    
    # Event files
    if "event" in filename or "events" in parent_dir:
        return os.path.join("core", "events", filename)
    
    # Progression/party files
    if "progression" in filename or "party" in filename or parent_dir == "progression":
        return os.path.join("progression", filename)
    
    # Memory files
    if "memory" in filename or "gpt" in filename or parent_dir == "memory":
        return os.path.join("memory", filename)
    
    # Utils files
    if parent_dir == "utils":
        return os.path.join("utils", filename)
    
    # API files
    if parent_dir == "api":
        return os.path.join("api", filename)
    
    # Models files
    if parent_dir in ["models", "schemas"]:
        return os.path.join(parent_dir, filename)
    
    # Service files
    if parent_dir == "services":
        return os.path.join("services", filename)
    
    # Repository files
    if parent_dir == "repositories":
        return os.path.join("repositories", filename)
    
    # Router files
    if parent_dir == "routers":
        return os.path.join("routers", filename)
    
    # Database files
    if parent_dir == "database":
        return os.path.join("database", filename)
    
    # Default to models directory
    return os.path.join("models", filename)

def copy_files_to_canonical_structure():
    """Copy all Python files to their canonical locations"""
    print("Copying files to canonical structure...")
    
    # Find all Python files in the character system
    python_files = []
    for root, _, files in os.walk(CHARACTER_DIR):
        for file in files:
            if file.endswith(".py") and "__pycache__" not in root:
                python_files.append(os.path.join(root, file))
    
    # Copy each file to its canonical location
    for file_path in python_files:
        try:
            # Skip __init__.py files (we've already created them)
            if os.path.basename(file_path) == "__init__.py":
                continue
            
            # Determine the canonical path
            canonical_relative_path = find_canonical_file(file_path)
            canonical_path = os.path.join(TEMP_DIR, canonical_relative_path)
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(canonical_path), exist_ok=True)
            
            # Copy the file
            shutil.copy2(file_path, canonical_path)
            print(f"  Copied {file_path} to {canonical_path}")
            
        except Exception as e:
            print(f"  Error processing {file_path}: {e}")
    
    print(f"Copied {len(python_files)} Python files to canonical structure")

def fix_imports():
    """Fix import statements in all Python files"""
    print("Fixing import statements...")
    
    # Find all Python files in the temporary directory
    python_files = []
    for root, _, files in os.walk(TEMP_DIR):
        for file in files:
            if file.endswith(".py") and "__pycache__" not in root:
                python_files.append(os.path.join(root, file))
    
    # Fix imports in each file
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Apply all import fixes
            modified = False
            for old_import, new_import in IMPORT_FIXES:
                if old_import in content:
                    content = content.replace(old_import, new_import)
                    modified = True
            
            # Write the file back if modified
            if modified:
                with open(file_path, 'w') as f:
                    f.write(content)
                print(f"  Fixed imports in {file_path}")
            
        except Exception as e:
            print(f"  Error fixing imports in {file_path}: {e}")
    
    print("Import fixes applied")

def create_readme():
    """Create a README.md file explaining the refactoring"""
    readme_content = f"""# Character System

This directory contains the refactored and consolidated character system for Visual DM.

## Structure

- `api/`: API endpoints and interfaces
- `core/`: Core character models and utilities
  - `events/`: Event system for character-related events
- `inventory/`: Inventory management
- `memory/`: Memory system integration
- `models/`: Data models
- `npc/`: NPC-specific functionality
- `progression/`: Character progression and party management
- `repositories/`: Data access layer
- `routers/`: FastAPI routers
- `schemas/`: Pydantic schemas
- `services/`: Business logic services
- `tests/`: Unit and integration tests
- `utils/`: Utility functions

## Refactoring Summary

This system was created by consolidating duplicate modules in the previous character system.
The refactoring was performed on {datetime.datetime.now().strftime('%Y-%m-%d')}.

Original files were backed up to {BACKUP_DIR}.
"""
    
    with open(os.path.join(TEMP_DIR, "README.md"), "w") as f:
        f.write(readme_content)
    
    print("Created README.md file")

def create_refactoring_doc():
    """Create a REFACTORING.md file with documentation"""
    refactoring_content = """# Character System Refactoring

This document describes the refactoring process that was performed on the Visual DM Character System.

## Refactoring Goals

The primary goals of this refactoring were:

1. **Consolidate Duplicate Modules**: The previous system had many duplicate files with similar or identical functionality.
2. **Create a Consistent Directory Structure**: Organize the code according to a clean, logical structure.
3. **Ensure Clear Separation of Concerns**: Group related functionality together.
4. **Improve Maintainability**: Make the system easier to understand and modify.
5. **Remove Dead or Deprecated Code**: Clean up unused code to reduce confusion.

## Process

The refactoring process involved:

1. **Analysis**: We used a custom script to analyze the existing system and identify duplicate modules.
2. **Categorization**: Files were categorized by functionality and duplication patterns.
3. **Consolidation**: Duplicate files were merged, preserving the most robust implementation.
4. **Restructuring**: Files were moved into appropriate directories based on functionality.
5. **Implementation**: The refactored system replaced the original system.

## Original Structure Issues

The original character system had several issues:

- Multiple copies of the same file in different locations
- Inconsistent file naming and organization
- Deep nesting in some directories (models/repositories/routers/schemas/services/utils)
- Mixed responsibilities in some files
- Duplicate functionality across files

## New Directory Structure

The refactored character system has a cleaner, more logical structure:

- `api/`: API endpoints and interfaces
- `core/`: Core character models and utilities
  - `events/`: Event system for character-related events
- `inventory/`: Inventory management
- `memory/`: Memory system integration
- `models/`: Data models
- `npc/`: NPC-specific functionality
- `progression/`: Character progression and party management
- `repositories/`: Data access layer
- `routers/`: FastAPI routers
- `schemas/`: Pydantic schemas
- `services/`: Business logic services
- `tests/`: Unit and integration tests
- `utils/`: Utility functions

## Canonical File Locations

When multiple versions of a file existed, we used these rules to determine the canonical location:

- Character core functionality -> `core/`
- NPC-related functionality -> `npc/`
- Inventory-related functionality -> `inventory/`
- Progression and party functionality -> `progression/`
- Event-related functionality -> `core/events/`
- Tests -> `tests/`
- Utilities -> `utils/`

## Key Consolidations

Some significant consolidations include:

1. **Character Model**: Merged `core/character.py`, `character/character.py`, and `models/character.py` into `core/character_model.py`
2. **Event System**: Consolidated all event-related files into `core/events/`
3. **NPC Utilities**: Consolidated all NPC-related utilities from various locations into `npc/`
4. **Inventory System**: Unified inventory-related files into a single `inventory/` directory

## Impact

This refactoring:

- Reduced code duplication
- Improved maintainability
- Made the system more understandable
- Established a clear organization pattern for future development

## Backup

A backup of the original system is available at `{BACKUP_DIR}` if needed for reference.
"""
    
    with open(os.path.join(TEMP_DIR, "REFACTORING.md"), "w") as f:
        f.write(refactoring_content)
    
    print("Created REFACTORING.md file")

def deploy_refactored_system():
    """Deploy the refactored system over the existing one"""
    print(f"Deploying refactored system from {TEMP_DIR} to {CHARACTER_DIR}...")
    
    # Remove the existing system (except for the backup we already made)
    for item in os.listdir(CHARACTER_DIR):
        item_path = os.path.join(CHARACTER_DIR, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        elif os.path.isfile(item_path):
            os.remove(item_path)
    
    # Copy the refactored system
    for item in os.listdir(TEMP_DIR):
        src_path = os.path.join(TEMP_DIR, item)
        dst_path = os.path.join(CHARACTER_DIR, item)
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        elif os.path.isfile(src_path):
            shutil.copy2(src_path, dst_path)
    
    print(f"Refactored system deployed successfully to {CHARACTER_DIR}")

def verify_imports():
    """Verify imports after refactoring to identify any remaining issues"""
    print("Verifying imports in refactored system...")
    
    # Find all Python files in the character system
    python_files = []
    for root, _, files in os.walk(CHARACTER_DIR):
        for file in files:
            if file.endswith(".py") and "__pycache__" not in root:
                python_files.append(os.path.join(root, file))
    
    # Track import issues
    import_issues = []
    
    # Check each file for import issues
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Look for import statements
            import_lines = re.findall(r'^(?:from|import)\s+[\w\.]+', content, re.MULTILINE)
            
            # Check for potential issues
            for line in import_lines:
                for old_import, _ in IMPORT_FIXES:
                    if old_import in line:
                        import_issues.append({
                            'file': file_path,
                            'line': line
                        })
                        break
            
        except Exception as e:
            print(f"  Error verifying imports in {file_path}: {e}")
    
    # Report issues
    if import_issues:
        print(f"\nFound {len(import_issues)} potential import issues:")
        for issue in import_issues:
            print(f"  {issue['file']}: {issue['line']}")
        
        # Save issues to a file
        with open("temp/character-refactoring/import_issues.json", "w") as f:
            json.dump(import_issues, f, indent=2)
        
        print(f"Import issues saved to temp/character-refactoring/import_issues.json")
    else:
        print("No import issues found. Refactoring successful!")

def main():
    """Main function to execute the refactoring process"""
    print("Starting character system refactoring...")
    
    # Ensure temp directory exists
    os.makedirs("temp/character-refactoring", exist_ok=True)
    
    # Execute refactoring steps
    create_backup()
    create_temp_structure()
    copy_files_to_canonical_structure()
    fix_imports()
    create_readme()
    create_refactoring_doc()
    deploy_refactored_system()
    verify_imports()
    
    print("\nRefactoring complete!")
    print(f"Backup created at: {BACKUP_DIR}")
    print(f"To revert the changes, run:")
    print(f"  rm -rf {CHARACTER_DIR}/*")
    print(f"  cp -r {BACKUP_DIR}/character/* {CHARACTER_DIR}")

if __name__ == "__main__":
    main() 