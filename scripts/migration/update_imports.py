#!/usr/bin/env python3
"""
Script to update imports throughout the backend codebase to match the new structure.
"""

import os
import re
import sys
from pathlib import Path

def update_imports_in_file(file_path):
    """
    Update imports in a single file.
    
    Returns:
        int: Number of replacements made
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define import patterns and their replacements
    import_patterns = [
        # app.core.database -> backend.core.database
        (r'from app\.core\.database', r'from backend.infrastructure.shared.database'),
        
        # app.core.models.X -> backend.systems.X.models.X or backend.core.models.X
        (r'from app\.core\.models\.character', r'from backend.systems.character.models.character'),
        (r'from app\.core\.models\.user', r'from backend.infrastructure.auth_user.models.user_models'),
        (r'from app\.core\.models\.party', r'from backend.systems.party.models.party'),
        (r'from app\.core\.models\.world', r'from backend.systems.world_state.models.world'),
        (r'from app\.core\.models\.region', r'from backend.systems.region.models.region'),
        (r'from app\.core\.models\.quest', r'from backend.systems.quest.models.quest'),
        (r'from app\.core\.models\.spell', r'from backend.systems.magic.models.spell'),
        (r'from app\.core\.models\.inventory', r'from backend.systems.inventory.models.inventory'),
        (r'from app\.core\.models\.combat', r'from backend.systems.combat.models.stats'),
        (r'from app\.core\.models\.save', r'from backend.infrastructure.shared.models.save'),
        
        # app.core.utils -> backend.core.utils
        (r'from app\.core\.utils\.error_utils', r'from backend.infrastructure.shared.utils.error'),
        (r'from app\.core\.utils', r'from backend.infrastructure.shared.utils'),
        
        # app.models -> backend.systems
        (r'from app\.models', r'from backend.systems.character.models'),
        
        # app.rules -> backend.core.rules
        (r'from app\.rules', r'from backend.infrastructure.shared.rules'),
        
        # app.core.services -> backend.systems.X.services
        (r'from app\.core\.services\.character_service', r'from backend.systems.character.services.character_service'),
        
        # backend.systems.core_shared -> backend.core
        (r'from backend\.systems\.core_shared', r'from backend.core'),
    ]
    
    original_content = content
    for pattern, replacement in import_patterns:
        content = re.sub(pattern, replacement, content)
    
    # Check if content was modified
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return sum(len(re.findall(pattern, original_content)) for pattern, _ in import_patterns)
    
    return 0

def update_imports_in_directory(directory, extensions=None):
    """
    Recursively update imports in all files in a directory.
    
    Args:
        directory (str): Directory to process
        extensions (list): File extensions to process, e.g. ['.py']
    
    Returns:
        tuple: (files_processed, total_replacements)
    """
    if extensions is None:
        extensions = ['.py']  # Default to Python files only
    
    files_processed = 0
    total_replacements = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    replacements = update_imports_in_file(file_path)
                    if replacements > 0:
                        files_processed += 1
                        total_replacements += replacements
                        print(f"Updated {file_path} ({replacements} replacements)")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    return files_processed, total_replacements

def main():
    """Main function."""
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'systems')
    
    print(f"Updating imports in {directory}...")
    files_processed, total_replacements = update_imports_in_directory(directory)
    print(f"Done! Updated {files_processed} files with {total_replacements} replacements.")

if __name__ == "__main__":
    main() 