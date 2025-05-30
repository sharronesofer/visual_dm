#!/usr/bin/env python3
"""
Script to fix event system imports across the codebase.
Updates all imports to use the canonical backend.systems.events path.
"""

import os
import re
import glob
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix event system imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Define import replacements
        replacements = [
            # Direct submodule imports to main module
            (r'from backend\.systems\.events\.event_dispatcher import EventDispatcher, EventBase', 
             'from backend.systems.events import EventDispatcher, EventBase'),
            (r'from backend\.systems\.events\.event_dispatcher import EventDispatcher', 
             'from backend.systems.events import EventDispatcher'),
            (r'from backend\.systems\.events\.event_base import EventBase', 
             'from backend.systems.events import EventBase'),
            (r'from backend\.systems\.events\.event_types import ([^,\n]+)', 
             r'from backend.systems.events import \1'),
            (r'from backend\.systems\.events\.middleware import ([^,\n]+)', 
             r'from backend.systems.events import \1'),
            
            # Fix EventBus references to EventDispatcher
            (r'from backend\.systems\.events\.event_bus import EventBus', 
             'from backend.systems.events import get_event_dispatcher'),
            (r'from backend\.systems\.events\.event_dispatcher import EventBus', 
             'from backend.systems.events import get_event_dispatcher'),
            
            # Fix models.event_dispatcher references
            (r'from backend\.systems\.events\.models\.event_dispatcher import ([^,\n]+)', 
             r'from backend.systems.events import \1'),
            
            # Fix services.event_dispatcher references  
            (r'from backend\.systems\.events\.services\.event_dispatcher import ([^,\n]+)', 
             r'from backend.systems.events import \1'),
            
            # Fix canonical_events references
            (r'from backend\.systems\.events\.canonical_events import ([^,\n]+)', 
             r'from backend.systems.events import \1'),
        ]
        
        # Apply replacements
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        # Fix EventBus usage to get_event_dispatcher
        content = re.sub(r'\bEventBus\b', 'get_event_dispatcher()', content)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix imports across the codebase."""
    # Find all Python files in backend/systems
    backend_systems_path = Path("backend/systems")
    
    if not backend_systems_path.exists():
        print("backend/systems directory not found. Run from project root.")
        return
    
    # Get all Python files
    python_files = list(backend_systems_path.rglob("*.py"))
    
    # Exclude the events system itself to avoid circular issues
    python_files = [f for f in python_files if not str(f).startswith("backend/systems/events/")]
    
    print(f"Found {len(python_files)} Python files to check...")
    
    updated_count = 0
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            updated_count += 1
    
    print(f"\nCompleted! Updated {updated_count} files.")
    
    # Also check some key documentation files
    doc_files = [
        "docs/Development_Bible.md",
        "docs/guides/event_system_migration.md",
        "backend/systems/events/README.md"
    ]
    
    print("\nChecking documentation files...")
    for doc_file in doc_files:
        if Path(doc_file).exists():
            if fix_imports_in_file(doc_file):
                updated_count += 1
    
    print(f"\nTotal files updated: {updated_count}")

if __name__ == "__main__":
    main() 