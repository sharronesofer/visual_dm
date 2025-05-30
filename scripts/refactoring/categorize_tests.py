#!/usr/bin/env python3

import os
import re
import shutil
from pathlib import Path
import filecmp

# Base directories
SOURCE_DIR = Path("backend/tests")
TARGET_BASE_DIR = Path("backend/tests/systems")
SYSTEMS_DIR = Path("backend/systems")

# Get all system directories
def get_system_dirs():
    """Get all system directories from backend/systems."""
    return [d for d in SYSTEMS_DIR.iterdir() if d.is_dir() and not d.name.startswith("__")]

def get_system_name_mapping():
    """Create a mapping of keywords to system directories."""
    system_dirs = get_system_dirs()
    mapping = {}
    
    # Add system names directly
    for system_dir in system_dirs:
        name = system_dir.name
        mapping[name] = name
        
        # Add common variations
        if name == "world_generation":
            mapping["worldgen"] = name
        elif name == "tension_war":
            mapping["tension"] = name
        elif name == "auth_user":
            mapping["auth"] = name
        elif name == "world_state":
            mapping["world"] = name
            
    return mapping

def get_test_files():
    """Get all test files in the source directory that are not in systems/ subdirectory."""
    test_files = []
    for item in SOURCE_DIR.iterdir():
        if item.name.startswith("test_") and item.suffix == ".py" and item.is_file():
            test_files.append(item)
    return test_files

def determine_system(test_file, system_mapping):
    """Determine which system a test file belongs to based on its name."""
    file_name = test_file.name.lower()
    
    # Try to extract system name from file name
    for keyword, system in system_mapping.items():
        # Check if keyword is in the filename (excluding 'test_' prefix)
        if keyword in file_name.replace("test_", ""):
            return system
    
    # If no match found, examine file content to look for imports
    with open(test_file, 'r') as f:
        content = f.read()
        
    # Look for imports from backend.systems.X
    imports = re.findall(r'from backend\.systems\.(\w+)', content)
    if imports:
        # Return the most frequently imported system
        system_counts = {}
        for imp in imports:
            if imp in system_mapping.values():
                system_counts[imp] = system_counts.get(imp, 0) + 1
        
        if system_counts:
            return max(system_counts.items(), key=lambda x: x[1])[0]
    
    # Look for specific keywords in the content
    for keyword, system in system_mapping.items():
        # Count occurrences of the keyword
        count = content.lower().count(keyword.lower())
        if count > 2:  # More than 2 occurrences suggests a strong connection
            return system
    
    # Default handling for common patterns
    if "npc" in file_name:
        return "npc"
    elif "crafting" in file_name or "recipe" in file_name or "station" in file_name:
        return "crafting"
    elif "data" in file_name:
        return "data"
    elif "event" in file_name and "event_handler" not in file_name:
        return "events"
    elif "world" in file_name or "worldgen" in file_name:
        return "world_generation"
    elif "state" in file_name:
        return "world_state"
    elif "region" in file_name:
        return "region"
    elif "faction" in file_name:
        return "faction"
    elif "quest" in file_name:
        return "quest"
    elif "analytics" in file_name:
        return "analytics"
    elif "dialogue" in file_name:
        return "dialogue"
    elif "memory" in file_name:
        return "memory"
    elif "integration" in file_name:
        return "shared"  # Integration tests often belong in shared
    
    # If still no match, return None
    return None

def create_target_directory(system_name):
    """Create the target directory for a system if it doesn't exist."""
    target_dir = TARGET_BASE_DIR / system_name
    os.makedirs(target_dir, exist_ok=True)
    
    # Ensure __init__.py exists
    init_file = target_dir / "__init__.py"
    if not init_file.exists():
        with open(init_file, 'w') as f:
            f.write("# Automatically created during test categorization\n")
    
    return target_dir

def move_file(source_file, target_dir):
    """Move a file to the target directory, creating backups if needed."""
    target_file = target_dir / source_file.name
    
    # If target doesn't exist, simply copy
    if not target_file.exists():
        shutil.copy2(source_file, target_file)
        print(f"Moved: {source_file} -> {target_file}")
        return True
    
    # If target exists, compare and copy only if different
    try:
        if not filecmp.cmp(source_file, target_file, shallow=False):
            # Files are different, create a backup
            backup_file = target_file.with_suffix(f"{target_file.suffix}.bak")
            shutil.copy2(target_file, backup_file)
            print(f"Created backup: {backup_file}")
            
            # Copy the source file
            shutil.copy2(source_file, target_file)
            print(f"Updated: {source_file} -> {target_file}")
            return True
        else:
            print(f"Skipped (identical): {source_file}")
            return True
    except Exception as e:
        print(f"Error comparing {source_file} and {target_file}: {e}")
        return False

def main():
    # Get system mapping
    system_mapping = get_system_name_mapping()
    print(f"Found {len(system_mapping)} system keywords")
    
    # Get test files
    test_files = get_test_files()
    print(f"Found {len(test_files)} loose test files to categorize")
    
    # Track statistics
    categorized = 0
    uncategorized = 0
    moved = 0
    
    # Process each file
    for test_file in test_files:
        system = determine_system(test_file, system_mapping)
        
        if system:
            categorized += 1
            print(f"Categorized: {test_file.name} -> {system}")
            
            # Create target directory
            target_dir = create_target_directory(system)
            
            # Move the file
            if move_file(test_file, target_dir):
                moved += 1
                # Remove the original file after successful move
                os.remove(test_file)
                print(f"Deleted original: {test_file}")
        else:
            uncategorized += 1
            print(f"Could not categorize: {test_file.name}")
    
    print(f"\nCategorization summary:")
    print(f"- Total files: {len(test_files)}")
    print(f"- Categorized: {categorized}")
    print(f"- Uncategorized: {uncategorized}")
    print(f"- Successfully moved: {moved}")

if __name__ == "__main__":
    main() 