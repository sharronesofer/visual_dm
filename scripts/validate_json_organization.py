#!/usr/bin/env python3
"""
JSON Organization Validator

This script checks if all JSON files in the project are organized according 
to the canonical structure described in data/README_JSON_ORGANIZATION.md.
"""

import os
import json
import sys
import re
from pathlib import Path

# Define the canonical structure
CANONICAL_STRUCTURE = {
    "biomes": ["land_types.json", "adjacency.json"],
    "entities/races": ["races.json"],
    "entities/monsters": ["level_1_monsters.json", "level_20_monsters.json"],
    "items": ["item_types.json", "equipment.json", "item_effects.json"],
    "crafting/recipes": [],
    "crafting/stations": ["crafting_stations.json"],
    "world/generation": ["world_seed.schema.json"],
    "world/poi": ["building_profiles_corrected.json"],
    "world/world_state": ["global_state.json", "regional_state.json", "poi_state.json"],
    "systems/memory": [],
    "systems/motif": ["motif_types.json"],
    "systems/rumor": [],
    "systems/faction": ["faction_types.json"],
    "systems/religion": ["religion_templates.json"],
    "systems/combat": ["combat_rules.json"],
    "systems/spells": ["level_0_spells.json", "level_1_spells.json"],
    "systems/economy": [],
    "systems/time": [],
    "systems/weather": ["weather_types.json"],
    "systems/events": ["event_types.json"],
    "gameplay/spells": [],
    "gameplay/abilities": [],
    "gameplay/skills": [],
    "narrative/dialogue": [],
    "narrative/quests": [],
    "modding/schemas": ["example.schema.json"],
    "modding/worlds": ["example_world_seed.json"],
}

# Exceptions - files that are allowed to be outside the canonical structure
EXCEPTIONS = [
    # Unity-specific files
    r"VDM/Assets/StreamingAssets/Data/.*\.json",
    r"VDM/Assets/StreamingAssets/Schemas/.*\.json",
    # Package files
    r".*/package\.json",
    r".*/manifest\.json",
    r".*/packages-lock\.json",
    # Editor files
    r"\.vscode/.*\.json",
    r".cursor/.*\.json",
    # Archive and temporary files
    r"archives/.*\.json",
    r".*backup.*\.json",
    # Library and cache files
    r"VDM/Library/.*\.json",
]

def find_json_files(root_dir):
    """Find all JSON files in the project."""
    json_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))
    return json_files

def is_exception(file_path):
    """Check if the file is an exception."""
    for pattern in EXCEPTIONS:
        if re.match(pattern, file_path):
            return True
    return False

def should_be_in_canonical_structure(file_path):
    """Check if the file should be in the canonical structure."""
    if is_exception(file_path):
        return False
    
    # Add other rules here if needed
    return True

def get_canonical_path(file_name):
    """Find the canonical path for a given file name."""
    for dir_path, files in CANONICAL_STRUCTURE.items():
        if file_name in files:
            return os.path.join("data", dir_path, file_name)
    
    # Try to infer from file name patterns
    if file_name.startswith("level_") and file_name.endswith("_spells.json"):
        return os.path.join("data", "systems/spells", file_name)
    if file_name.startswith("level_") and file_name.endswith("_monsters.json"):
        return os.path.join("data", "entities/monsters", file_name)
    
    return None

def check_organization(json_files):
    """Check if JSON files are properly organized."""
    misplaced_files = []
    for file_path in json_files:
        rel_path = os.path.relpath(file_path)
        file_name = os.path.basename(file_path)
        
        if should_be_in_canonical_structure(rel_path):
            canonical_path = get_canonical_path(file_name)
            if canonical_path and canonical_path != rel_path:
                misplaced_files.append((rel_path, canonical_path))
    
    return misplaced_files

def main():
    """Main function."""
    print("Validating JSON organization...")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    json_files = find_json_files(".")
    print(f"Found {len(json_files)} JSON files")
    
    misplaced_files = check_organization(json_files)
    
    if misplaced_files:
        print("\nThe following JSON files are not in their canonical locations:")
        for current, canonical in misplaced_files:
            print(f"  • {current} → {canonical}")
        print(f"\nTotal: {len(misplaced_files)} misplaced files")
        print("\nSuggested actions:")
        print("  1. Move each file to its canonical location")
        print("  2. Update references in code if needed")
        print("  3. If a file should be an exception, add it to EXCEPTIONS in this script")
        return 1
    else:
        print("\nAll JSON files are correctly organized according to the canonical structure!")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 