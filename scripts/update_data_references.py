#!/usr/bin/env python3
"""
Data Reference Migration Script

This script helps developers update code references from old data file locations
to the new centralized data structure.

Usage:
    python update_data_references.py [directory]

If directory is not specified, the script will scan the entire project.
"""

import os
import re
import sys
import glob
from pathlib import Path

# Mapping of old paths to new paths
PATH_MAPPING = {
    # Biomes
    "data/builders/world_parameters/biomes/adjacency.json": "data/biomes/adjacency.json",
    "data/rules_json/land_types.json": "data/biomes/land_types.json",
    
    # World generation
    "data/modding/worlds/example_world_seed.json": "data/world/generation/example_world_seed.json",
    "data/modding/worlds/world_seed.schema.json": "data/world/generation/world_seed.schema.json",
    
    # Religion
    "backend/systems/religion/data/religion_templates.json": "data/systems/religion/religion_templates.json",
    
    # Crafting
    "data/stations/crafting_stations.json": "data/crafting/stations/crafting_stations.json",
    "data/recipes/weapons.json": "data/crafting/recipes/weapons.json",
    "data/recipes/alchemy.json": "data/crafting/recipes/alchemy.json",
    
    # Weather
    "VDM/Assets/StreamingAssets/Data/weather_types.json": "data/builders/world_parameters/biomes/weather_types.json",
    "VDM/Assets/StreamingAssets/Schemas/weather_types.schema.json": "data/modding/schemas/weather_types.schema.json",
}

# File types to scan
FILE_EXTENSIONS = ('.py', '.cs', '.js', '.ts', '.json', '.md', '.txt')

def find_files(directory):
    """Find all relevant files to scan."""
    files = []
    for ext in FILE_EXTENSIONS:
        files.extend(glob.glob(f"{directory}/**/*{ext}", recursive=True))
    
    # Filter out files to ignore
    files = [f for f in files if 
             not f.startswith('venv/') and 
             not f.startswith('node_modules/') and
             not f.startswith('.git/')]
    
    return files

def update_file(file_path):
    """Update references in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        original_content = content
        changes_made = False
        
        for old_path, new_path in PATH_MAPPING.items():
            if old_path in content:
                content = content.replace(old_path, new_path)
                changes_made = True
        
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            return True
        
        return False
    
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Main function."""
    directory = '.'
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    
    print(f"Scanning directory: {directory}")
    files = find_files(directory)
    print(f"Found {len(files)} files to scan")
    
    updated_files = 0
    for file_path in files:
        if update_file(file_path):
            updated_files += 1
            print(f"Updated: {file_path}")
    
    print(f"\nSummary:")
    print(f"- Scanned {len(files)} files")
    print(f"- Updated {updated_files} files")
    
    if updated_files > 0:
        print("\nPlease review the changes carefully before committing!")
        print("This script performs simple text replacement and may not handle all cases.")
        print("You may need to manually fix some references.")

if __name__ == "__main__":
    main() 