#!/usr/bin/env python
"""
Migration Script for Tension/War to Diplomacy System Consolidation

This script updates imports and references from the tension_war module to use the
diplomacy module instead, as we've consolidated the functionality.

Usage:
    python migrate_tension_diplomacy.py

This will:
1. Scan all Python files for imports from tension_war
2. Replace them with equivalent imports from diplomacy
3. Update function/class references as needed
"""

import os
import re
import sys
from pathlib import Path

# Mapping of old imports to new imports
IMPORT_MAPPING = {
    'from backend.systems.tension': 'from backend.systems.diplomacy',
    'from backend.systems.tension.models': 'from backend.systems.diplomacy.models',
    'from backend.systems.tension.services': 'from backend.systems.diplomacy.services',
    'from backend.systems.tension.utils': 'from backend.systems.diplomacy.services',
    'from backend.systems.tension.schemas': 'from backend.infrastructure.schemas.diplomacy_schemas',
    'from backend.systems.tension.router': 'from backend.infrastructure.api.diplomacy_router',
    'import backend.systems.tension': 'import backend.systems.diplomacy',
}

# Mapping of old classes/functions to new classes/functions
CLASS_MAPPING = {
    'UnifiedTensionManager': 'TensionService',
    'WarManager': 'DiplomacyService',
    'TensionLevel': 'DiplomaticStatus',
    'WarState': 'DiplomaticEvent',  # Approximate mapping
    'WarOutcome': 'DiplomaticEvent',  # Approximate mapping
}

# Files to skip
SKIP_FILES = {
    'backend/systems/tension_war',  # Skip the old module itself
    'backend/migrate_tension_diplomacy.py',  # Skip this script
}


def update_file(file_path):
    """Update imports and references in a single file."""
    with open(file_path, 'r') as f:
        content = f.read()

    original_content = content
    
    # Replace imports
    for old_import, new_import in IMPORT_MAPPING.items():
        content = content.replace(old_import, new_import)
    
    # Replace class and function references
    for old_class, new_class in CLASS_MAPPING.items():
        # Match whole word only using regex
        content = re.sub(r'\b{}\b'.format(old_class), new_class, content)
    
    # Only write if something changed
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    
    return False


def should_skip(file_path):
    """Check if a file should be skipped."""
    for skip_pattern in SKIP_FILES:
        if skip_pattern in str(file_path):
            return True
    return False


def scan_directory(directory):
    """Scan a directory for Python files and update them."""
    updated_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if not file.endswith('.py'):
                continue
            
            file_path = Path(root) / file
            
            if should_skip(file_path):
                continue
            
            if update_file(file_path):
                updated_files.append(str(file_path))
    
    return updated_files


def main():
    """Main function."""
    # Use the backend directory as the root for scanning
    directory = Path('backend')
    
    if not directory.exists():
        print(f"Error: Directory '{directory}' not found.")
        sys.exit(1)
    
    print(f"Scanning directory: {directory}")
    updated_files = scan_directory(directory)
    
    if updated_files:
        print(f"Updated {len(updated_files)} files:")
        for file in updated_files:
            print(f"  - {file}")
    else:
        print("No files needed updating.")


if __name__ == '__main__':
    main() 