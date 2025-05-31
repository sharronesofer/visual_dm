#!/usr/bin/env python3
"""
Fix imports after directory restructuring.

This script updates all import statements to reflect the new directory structure:
- Moved from systems to infrastructure: analytics, auth_user, data, events, integration, services, shared, storage
- Moved from infrastructure to systems: models, schemas, rules, repositories
- Removed: event_base (deprecated)
"""

import os
import re
import sys
from pathlib import Path

# Define the import mappings
IMPORT_MAPPINGS = {
    # Moved from systems to infrastructure
    r'from backend\.systems\.analytics': 'from backend.infrastructure.analytics',
    r'import backend\.systems\.analytics': 'import backend.infrastructure.analytics',
    r'from backend\.systems\.auth_user': 'from backend.infrastructure.auth_user',
    r'import backend\.systems\.auth_user': 'import backend.infrastructure.auth_user',
    r'from backend\.systems\.data': 'from backend.infrastructure.data',
    r'import backend\.systems\.data': 'import backend.infrastructure.data',
    r'from backend\.systems\.events': 'from backend.infrastructure.events',
    r'import backend\.systems\.events': 'import backend.infrastructure.events',
    r'from backend\.systems\.integration': 'from backend.infrastructure.integration',
    r'import backend\.systems\.integration': 'import backend.infrastructure.integration',
    r'from backend\.systems\.services': 'from backend.infrastructure.services',
    r'import backend\.systems\.services': 'import backend.infrastructure.services',
    r'from backend\.systems\.shared': 'from backend.infrastructure.shared',
    r'import backend\.systems\.shared': 'import backend.infrastructure.shared',
    r'from backend\.systems\.storage': 'from backend.infrastructure.storage',
    r'import backend\.systems\.storage': 'import backend.infrastructure.storage',
    
    # Moved from infrastructure to systems
    r'from backend\.infrastructure\.models': 'from backend.infrastructure.shared.models',
    r'import backend\.infrastructure\.models': 'import backend.infrastructure.shared.models',
    r'from backend\.infrastructure\.schemas': 'from backend.systems.schemas',
    r'import backend\.infrastructure\.schemas': 'import backend.systems.schemas',
    r'from backend\.infrastructure\.validation\.rules': 'from backend.systems.rules.rules',
    r'from backend\.infrastructure\.repositories\.market_repository': 'from backend.infrastructure.repositories.market_repository',
    
    # Remove deprecated event_base imports
    r'from backend\.systems\.event_base.*': '# REMOVED: deprecated event_base import',
    r'import backend\.systems\.event_base.*': '# REMOVED: deprecated event_base import',
}

def fix_imports_in_file(file_path: Path) -> bool:
    """Fix imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all import mappings
        for pattern, replacement in IMPORT_MAPPINGS.items():
            content = re.sub(pattern, replacement, content)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed imports in: {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def find_python_files(root_dir: Path) -> list:
    """Find all Python files in the directory tree."""
    python_files = []
    
    for root, dirs, files in os.walk(root_dir):
        # Skip backup directories
        if 'backup' in root or '__pycache__' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    return python_files

def main():
    """Main function to fix all imports."""
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print(f"Fixing imports in project: {project_root}")
    
    # Find all Python files
    python_files = find_python_files(project_root)
    print(f"Found {len(python_files)} Python files")
    
    # Fix imports in each file
    fixed_count = 0
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            fixed_count += 1
    
    print(f"Fixed imports in {fixed_count} files")

if __name__ == "__main__":
    main() 