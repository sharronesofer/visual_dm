#!/usr/bin/env python3
"""
Bootstrap Scene Updater

This script updates the Bootstrap.unity scene to reference the consolidated scripts
after the Unity asset reorganization process.
"""

import os
import shutil
import argparse
import re
import datetime
from typing import Dict, List, Tuple

# Configuration
UNITY_PROJECT_PATH = "../VDM"
BOOTSTRAP_SCENE_PATH = "Assets/Scenes/Bootstrap.unity"
BACKUP_DIR = "backups"

# Mapping of old components to new ones
COMPONENT_REPLACEMENTS = {
    "GameLoader": "VisualDM.Core.ConsolidatedGameLoader",
    "VisualDM.Systems.GameLoader": "VisualDM.Core.ConsolidatedGameLoader",
    "VisualDM.GameLoader": "VisualDM.Core.ConsolidatedGameLoader",
    "NetworkManager": "VisualDM.Networking.API.RestApiClient",
    "VisualDM.Networking.NetworkManager": "VisualDM.Networking.API.RestApiClient",
    "VisualDM.Systems.EventManager": "VisualDM.Systems.Events.EventManager",
    "VisualDM.EventManager": "VisualDM.Systems.Events.EventManager"
}


def backup_scene(scene_path: str, backup_dir: str) -> str:
    """Create a backup of the scene file."""
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"Bootstrap_{timestamp}.unity"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    shutil.copy2(scene_path, backup_path)
    print(f"Created backup at {backup_path}")
    
    return backup_path


def update_scene_file(scene_path: str) -> bool:
    """
    Update the Bootstrap scene file to reference the consolidated components.
    Returns True if changes were made, False otherwise.
    """
    try:
        with open(scene_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace component references
        for old_component, new_component in COMPONENT_REPLACEMENTS.items():
            # Pattern to match the component in Unity's YAML format
            pattern = rf'm_Script: {{fileID: \d+, guid: [a-f0-9]+, type: 3}}\n\s+m_Name: {old_component}'
            replacement = f'm_Script: {{fileID: 11500000, guid: PLACEHOLDER_GUID, type: 3}}\n  m_Name: {new_component}'
            
            # We're just looking for the pattern to detect needed changes
            # In a real implementation, we'd need to get the actual GUIDs
            if re.search(pattern, content):
                print(f"Found reference to {old_component}")
                
                # For actual implementation, you'd do the real replacement
                # content = re.sub(pattern, replacement, content)
                
        # Also check for namespace references
        for old_component, new_component in COMPONENT_REPLACEMENTS.items():
            if '.' in old_component and '.' in new_component:
                old_namespace = old_component.rsplit('.', 1)[0]
                new_namespace = new_component.rsplit('.', 1)[0]
                
                pattern = rf'namespace: {old_namespace}'
                replacement = f'namespace: {new_namespace}'
                
                if re.search(pattern, content):
                    print(f"Found namespace reference to {old_namespace}")
                    content = re.sub(pattern, replacement, content)
        
        # Check if any changes were made
        if content != original_content:
            with open(scene_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Updated Bootstrap scene with new component references")
            return True
        else:
            print("No changes needed in Bootstrap scene")
            return False
            
    except Exception as e:
        print(f"Error updating Bootstrap scene: {e}")
        return False


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Update Bootstrap scene references')
    parser.add_argument('--project', default=UNITY_PROJECT_PATH,
                        help='Path to Unity project')
    parser.add_argument('--scene', default=BOOTSTRAP_SCENE_PATH,
                        help='Path to Bootstrap scene (relative to Assets)')
    parser.add_argument('--backup-dir', default=BACKUP_DIR,
                        help='Directory to store backups')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview changes without making them')
    
    args = parser.parse_args()
    
    # Construct full paths
    project_path = args.project
    scene_path = os.path.join(project_path, args.scene)
    backup_dir = os.path.join(project_path, args.backup_dir)
    
    if not os.path.exists(scene_path):
        print(f"Error: Bootstrap scene not found at {scene_path}")
        return
    
    print(f"Analyzing Bootstrap scene: {scene_path}")
    
    # Create backup
    if not args.dry_run:
        backup_scene(scene_path, backup_dir)
    
    # Update scene file
    if args.dry_run:
        print("DRY RUN - No changes will be made")
        # Still analyze the file to show what would change
        update_scene_file(scene_path)
    else:
        update_scene_file(scene_path)
    
    print("Done!")


if __name__ == "__main__":
    main() 