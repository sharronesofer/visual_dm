#!/usr/bin/env python3
"""
Fix circular imports of EventBase throughout the codebase.
Changes 'from backend.infrastructure.events.core.event_base import EventBase' to 
'from backend.infrastructure.events.core.event_base import EventBase'
"""

import os
import re

def fix_event_imports():
    """Fix EventBase import paths to avoid circular imports"""
    
    # Define the problematic pattern and its fix
    old_pattern = r'from backend\.infrastructure\.events import EventBase'
    new_import = 'from backend.infrastructure.events.core.event_base import EventBase'
    
    # Also handle EventDispatcher imports that might be problematic
    dispatcher_pattern = r'from backend\.infrastructure\.events import EventBase, EventDispatcher'
    dispatcher_replacement = '''from backend.infrastructure.events.core.event_base import EventBase
from backend.infrastructure.events.services.event_dispatcher import EventDispatcher'''
    
    # Find all Python files in backend
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip __pycache__ and .git directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    fixed_files = 0
    total_fixes = 0
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix EventBase + EventDispatcher imports first
            if re.search(dispatcher_pattern, content):
                content = re.sub(dispatcher_pattern, dispatcher_replacement, content)
                total_fixes += 1
            
            # Fix standalone EventBase imports
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_import, content)
                total_fixes += 1
            
            # Write back if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"Fixed: {file_path}")
                fixed_files += 1
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    print(f"\nSummary:")
    print(f"Fixed {fixed_files} files")
    print(f"Applied {total_fixes} import fixes")

if __name__ == "__main__":
    print("Fixing EventBase circular imports...")
    fix_event_imports()
    print("Done!") 