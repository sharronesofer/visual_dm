#!/usr/bin/env python3
"""
Unity Asset Reorganizer

This script helps with the reorganization of Unity assets according to the consolidation plan.
It provides dry-run capability to preview changes before actually moving files.
"""

import os
import shutil
import argparse
import json
import re
from typing import Dict, List, Tuple, Set
import glob

# Configuration
UNITY_PROJECT_PATH = "../VDM"
ASSETS_PATH = os.path.join(UNITY_PROJECT_PATH, "Assets")
NEW_STRUCTURE = {
    "Scripts/Core": ["Scripts/VisualDM/Core", "VisualDM/Core"],
    "Scripts/Networking/Multiplayer": ["VisualDM/Network/Multiplayer"],
    "Scripts/Networking/API": ["Scripts/VisualDM/Networking", "Scripts/Net"],
    "Scripts/Systems/Events": ["Scripts/VisualDM/Systems/Events", "VisualDM/Systems/Events", "Scripts/Systems/Events"],
    "Scripts/Systems/State": ["Scripts/VisualDM/Systems/State", "VisualDM/Systems/State"],
    "Scripts/Systems/Time": ["Scripts/VisualDM/Systems/Time", "VisualDM/Systems/Time"],
    "Scripts/Systems/Performance": ["Scripts/Systems/Performance"],
    "Scripts/UI": ["Scripts/VisualDM/UI", "VisualDM/UI"],
    "Scripts/Utils": ["Scripts/VisualDM/Utils", "VisualDM/Utils"],
    "Scripts/World": ["Scripts/VisualDM/World", "VisualDM/World", "Scripts/World"],
    "Resources": ["VisualDM/Resources"],
    "Prefabs": ["VisualDM/Prefabs"],
    "Materials": ["VisualDM/Materials"],
    "Textures": ["VisualDM/Textures"]
}


def find_all_assets(asset_path: str) -> List[str]:
    """Find all asset files in the project."""
    return glob.glob(f"{asset_path}/**/*.*", recursive=True)


def map_asset_to_new_location(asset_path: str) -> Tuple[str, bool]:
    """
    Map an asset to its new location based on the defined structure.
    Returns the new path and a boolean indicating if it's a move or not.
    """
    rel_path = os.path.relpath(asset_path, ASSETS_PATH)
    
    # If the file is already in the right location according to our plan, keep it there
    for new_dir, old_dirs in NEW_STRUCTURE.items():
        if rel_path.startswith(new_dir):
            return asset_path, False
    
    # For files in directories that should be moved
    for new_dir, old_dirs in NEW_STRUCTURE.items():
        for old_dir in old_dirs:
            if rel_path.startswith(old_dir):
                # Compute the new path by replacing the old directory prefix with the new one
                new_rel_path = rel_path.replace(old_dir, new_dir, 1)
                new_full_path = os.path.join(ASSETS_PATH, new_rel_path)
                return new_full_path, True
    
    # If not covered by our mapping rules, keep it where it is
    return asset_path, False


def collect_file_operations(assets: List[str]) -> Dict[str, str]:
    """
    Collect file operations to perform.
    Returns a dictionary mapping source paths to destination paths.
    """
    operations = {}
    
    for asset in assets:
        new_path, should_move = map_asset_to_new_location(asset)
        if should_move:
            operations[asset] = new_path
    
    return operations


def create_directories(paths: List[str]):
    """Create all necessary directories for the new structure."""
    for path in paths:
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)


def update_script_references(file_path: str, path_changes: Dict[str, str]) -> int:
    """
    Update references in script files to point to the new locations.
    Returns the number of replacements made.
    """
    if not file_path.endswith('.cs') and not file_path.endswith('.unity'):
        return 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        replacements = 0
        
        # For each file that has been moved, update references to it
        for old_path, new_path in path_changes.items():
            old_rel_path = os.path.relpath(old_path, ASSETS_PATH)
            new_rel_path = os.path.relpath(new_path, ASSETS_PATH)
            
            # Replace full paths and asset paths
            old_asset_path = f"Assets/{old_rel_path}"
            new_asset_path = f"Assets/{new_rel_path}"
            
            # Replace asset paths (Unity asset reference format)
            content = content.replace(old_asset_path, new_asset_path)
            
            # For C# files, also try to update any namespace references
            if file_path.endswith('.cs'):
                # Extract old and new namespaces (assuming they're based on the directory structure)
                old_namespace = old_rel_path.split('/')[0]
                if '/' in old_rel_path:
                    old_namespace += '.' + '.'.join(old_rel_path.split('/')[1:-1])
                
                new_namespace = new_rel_path.split('/')[0]
                if '/' in new_rel_path:
                    new_namespace += '.' + '.'.join(new_rel_path.split('/')[1:-1])
                
                # Update namespace references
                if old_namespace != new_namespace:
                    # Only replace namespace references, not partial matches
                    old_ns_pattern = rf'\b{old_namespace}\b'
                    content = re.sub(old_ns_pattern, new_namespace, content)
        
        # Calculate replacements
        if content != original_content:
            replacements = 1  # Simplified - just indicating a change was made
            
            # Write updated content back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return replacements
    
    except Exception as e:
        print(f"Error updating references in {file_path}: {e}")
        return 0


def execute_reorganization(operations: Dict[str, str], dry_run: bool = True) -> Tuple[int, int]:
    """
    Execute the reorganization operations.
    If dry_run is True, only print what would be done without making changes.
    Returns a tuple of (files_moved, scripts_updated).
    """
    files_moved = 0
    scripts_updated = 0
    
    if dry_run:
        print("== DRY RUN - No changes will be made ==")
    else:
        # Create all necessary directories first
        create_directories(operations.values())
    
    # Process each file operation
    for src, dst in operations.items():
        if src != dst:
            rel_src = os.path.relpath(src, ASSETS_PATH)
            rel_dst = os.path.relpath(dst, ASSETS_PATH)
            
            if dry_run:
                print(f"Would move: {rel_src} -> {rel_dst}")
            else:
                # Create the parent directory if it doesn't exist
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                
                # Move the file
                try:
                    shutil.move(src, dst)
                    print(f"Moved: {rel_src} -> {rel_dst}")
                    files_moved += 1
                except Exception as e:
                    print(f"Error moving {rel_src}: {e}")
    
    # Update script references if this is not a dry run
    if not dry_run:
        # Get all script files
        all_scripts = glob.glob(f"{ASSETS_PATH}/**/*.cs", recursive=True)
        all_scenes = glob.glob(f"{ASSETS_PATH}/**/*.unity", recursive=True)
        all_files_to_update = all_scripts + all_scenes
        
        print(f"Updating references in {len(all_files_to_update)} files...")
        for file_path in all_files_to_update:
            updates = update_script_references(file_path, operations)
            if updates > 0:
                scripts_updated += 1
                print(f"Updated references in: {os.path.relpath(file_path, ASSETS_PATH)}")
    
    return files_moved, scripts_updated


def create_backup(backup_dir: str):
    """Create a backup of the assets directory."""
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    backup_path = os.path.join(backup_dir, "Assets_Backup")
    print(f"Creating backup of Assets directory to {backup_path}...")
    
    try:
        shutil.copytree(ASSETS_PATH, backup_path)
        print("Backup created successfully.")
        return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Reorganize Unity assets')
    parser.add_argument('--project', default=UNITY_PROJECT_PATH,
                        help='Path to Unity project')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview changes without making them')
    parser.add_argument('--backup', action='store_true',
                        help='Create a backup before reorganizing')
    parser.add_argument('--backup-dir', default='backups',
                        help='Directory to store backup')
    
    args = parser.parse_args()
    
    global UNITY_PROJECT_PATH, ASSETS_PATH
    UNITY_PROJECT_PATH = args.project
    ASSETS_PATH = os.path.join(UNITY_PROJECT_PATH, "Assets")
    
    if not os.path.exists(ASSETS_PATH):
        print(f"Error: Assets directory not found at {ASSETS_PATH}")
        return
    
    # Create backup if requested
    if args.backup and not args.dry_run:
        if not create_backup(args.backup_dir):
            print("Aborting due to backup failure.")
            return
    
    print(f"Analyzing Unity project assets at: {ASSETS_PATH}")
    
    # Find all assets
    all_assets = find_all_assets(ASSETS_PATH)
    print(f"Found {len(all_assets)} asset files")
    
    # Determine operations
    operations = collect_file_operations(all_assets)
    print(f"Identified {len(operations)} files that need to be moved")
    
    # Execute reorganization
    files_moved, scripts_updated = execute_reorganization(operations, args.dry_run)
    
    if args.dry_run:
        print(f"DRY RUN - Would move {len(operations)} files and update references")
    else:
        print(f"Successfully moved {files_moved} files and updated {scripts_updated} scripts")
    
    print("Done!")


if __name__ == "__main__":
    main() 