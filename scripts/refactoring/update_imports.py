#!/usr/bin/env python3
"""
Script to update import paths after reorganizing backend structure.
"""

import os
import re
import glob

def update_imports_in_file(filepath):
    """Update import statements in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Update event system imports
        content = re.sub(
            r'from backend\.app\.core\.events',
            'from backend.systems.events',
            content
        )
        content = re.sub(
            r'from backend\.core\.events',
            'from backend.systems.events',
            content
        )
        
        # Update character imports
        content = re.sub(
            r'from backend\.app\.characters',
            'from backend.systems.character',
            content
        )
        
        # Update core model imports
        content = re.sub(
            r'from backend\.core\.models',
            'from backend.systems.shared.models',
            content
        )
        
        # Update core AI imports
        content = re.sub(
            r'from backend\.core\.ai',
            'from backend.systems.llm.services',
            content
        )
        
        # Update database imports
        content = re.sub(
            r'from backend\.core\.database',
            'from backend.systems.shared.database',
            content
        )
        content = re.sub(
            r'from backend\.app\.core\.database',
            'from backend.systems.shared.database',
            content
        )
        
        # Update config imports
        content = re.sub(
            r'from backend\.app\.core\.config',
            'from backend.systems.shared.config',
            content
        )
        content = re.sub(
            r'from backend\.app\.config',
            'from backend.systems.shared.config',
            content
        )
        content = re.sub(
            r'from backend\.core\.config',
            'from backend.systems.shared.config',
            content
        )
        
        # Update world state imports
        content = re.sub(
            r'from backend\.app\.core\.world_state',
            'from backend.systems.world_state',
            content
        )
        
        # Update memory system imports
        content = re.sub(
            r'from backend\.app\.core\.memory',
            'from backend.systems.memory',
            content
        )
        
        # Update rumor system imports
        content = re.sub(
            r'from backend\.app\.core\.rumors',
            'from backend.systems.rumor',
            content
        )
        
        # Update time system imports
        content = re.sub(
            r'from backend\.app\.core\.time_system',
            'from backend.systems.time',
            content
        )
        
        # Update schema imports
        content = re.sub(
            r'from backend\.app\.schemas',
            'from backend.systems.shared.schemas',
            content
        )
        
        # Update utils imports
        content = re.sub(
            r'from backend\.core\.utils',
            'from backend.systems.shared.utils',
            content
        )
        
        # Update auth imports
        content = re.sub(
            r'from backend\.core\.auth',
            'from backend.systems.auth_user.services',
            content
        )
        
        # Update permissions imports
        content = re.sub(
            r'from backend\.core\.permissions',
            'from backend.systems.shared.utils.security',
            content
        )
        
        # Update logging imports
        content = re.sub(
            r'from backend\.core\.logging',
            'from backend.systems.shared.utils.logging',
            content
        )
        
        # Update exceptions imports
        content = re.sub(
            r'from backend\.core\.exceptions',
            'from backend.systems.shared.utils.exceptions',
            content
        )
        
        # Update rules imports
        content = re.sub(
            r'from backend\.core\.rules',
            'from backend.systems.shared.rules',
            content
        )
        
        # Update event_bus imports (deprecated, should use event_dispatcher)
        content = re.sub(
            r'from backend\.core\.event_bus',
            'from backend.systems.events.event_dispatcher',
            content
        )
        
        # Update db imports
        content = re.sub(
            r'from backend\.core\.db',
            'from backend.systems.shared.database',
            content
        )
        
        # Update any remaining backend.app imports to backend.systems
        content = re.sub(
            r'from backend\.app\.',
            'from backend.systems.',
            content
        )
        
        # Update import statements (not from statements)
        content = re.sub(
            r'import backend\.app\.core\.events',
            'import backend.systems.events',
            content
        )
        content = re.sub(
            r'import backend\.app\.characters',
            'import backend.systems.character',
            content
        )
        content = re.sub(
            r'import backend\.core\.models',
            'import backend.systems.shared.models',
            content
        )
        content = re.sub(
            r'import backend\.core\.ai',
            'import backend.systems.llm.services',
            content
        )
        content = re.sub(
            r'import backend\.core\.events',
            'import backend.systems.events',
            content
        )
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Main function to update all Python files."""
    # Find all Python files in the backend directory
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip backup directories
        if 'temp' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Updating imports in {len(python_files)} Python files...")
    
    updated_count = 0
    for filepath in python_files:
        if update_imports_in_file(filepath):
            updated_count += 1
            print(f"Updated: {filepath}")
    
    print(f"Updated {updated_count} out of {len(python_files)} files.")

if __name__ == "__main__":
    main() 