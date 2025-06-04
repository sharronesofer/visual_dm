#!/usr/bin/env python3
"""
Script to update faction import statements after moving files to infrastructure.
"""

import os
import re
from pathlib import Path

def update_imports_in_file(file_path: Path):
    """Update import statements in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Update specific model imports
        content = re.sub(
            r'from backend\.systems\.faction\.models\.models import',
            'from backend.infrastructure.models.faction.models import',
            content
        )
        
        # Update schema imports - fix the paths after restructure
        content = re.sub(
            r'from backend\.infrastructure\.schemas\.faction\.faction\.faction_types import',
            'from backend.infrastructure.schemas.faction.faction_types import',
            content
        )
        content = re.sub(
            r'from backend\.infrastructure\.schemas\.faction\.faction\.expansion_schemas import',
            'from backend.infrastructure.schemas.faction.expansion_schemas import',
            content
        )
        content = re.sub(
            r'from backend\.infrastructure\.schemas\.faction\.faction\.succession_schemas import',
            'from backend.infrastructure.schemas.faction.succession_schemas import',
            content
        )
        
        # Update repository imports - fix the paths after restructure
        content = re.sub(
            r'from backend\.infrastructure\.repositories\.faction\.faction\.faction_repository import',
            'from backend.infrastructure.repositories.faction.faction_repository import',
            content
        )
        content = re.sub(
            r'from backend\.infrastructure\.repositories\.faction\.faction\.alliance_repository import',
            'from backend.infrastructure.repositories.faction.alliance_repository import',
            content
        )
        content = re.sub(
            r'from backend\.infrastructure\.repositories\.faction\.faction\.succession_repository import',
            'from backend.infrastructure.repositories.faction.succession_repository import',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {file_path}")
            return True
        return False
        
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Main function to update all files."""
    backend_dir = Path(".")
    
    # Find all Python files
    python_files = list(backend_dir.rglob("*.py"))
    
    updated_count = 0
    for file_path in python_files:
        # Skip __pycache__ directories
        if "__pycache__" in str(file_path):
            continue
            
        if update_imports_in_file(file_path):
            updated_count += 1
    
    print(f"Updated {updated_count} files")

if __name__ == "__main__":
    main() 