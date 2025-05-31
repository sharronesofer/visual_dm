#!/usr/bin/env python3
"""
This script updates imports from backend.systems.event to backend.systems.events.
"""

import os
import re
import sys
from pathlib import Path

# Define patterns for imports
patterns = [
    (r"from backend\.systems\.event import (.*)", r"from backend.infrastructure.events import \1"),
    (r"from backend\.systems\.event\.(.*) import (.*)", r"from backend.infrastructure.events.\1 import \2"),
    (r"import backend\.systems\.event\.(.*)", r"import backend.infrastructure.events.\1"),
    (r"import backend\.systems\.event", r"import backend.infrastructure.events"),
]

def update_imports(file_path):
    """Update imports in a single file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changed = False
    
    # Apply all patterns
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Check if content was changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        changed = True
        print(f"Updated imports in {file_path}")
    
    return changed

def find_python_files(start_path):
    """Find all Python files recursively."""
    for root, dirs, files in os.walk(start_path):
        for file in files:
            if file.endswith('.py'):
                yield os.path.join(root, file)

def main():
    """Main function."""
    # Set the starting directory (project root)
    start_dir = '.'
    if len(sys.argv) > 1:
        start_dir = sys.argv[1]
    
    updated_files = []
    
    # Find and update Python files
    for file_path in find_python_files(start_dir):
        if update_imports(file_path):
            updated_files.append(file_path)
    
    # Print summary
    print(f"\nUpdated {len(updated_files)} files:")
    for file in updated_files:
        print(f"  - {file}")

if __name__ == "__main__":
    main() 