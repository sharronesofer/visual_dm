#!/usr/bin/env python3
"""
Comprehensive script to fix non-canonical imports throughout the codebase.

This script converts imports to use canonical paths:
- Business logic: backend.systems.*
- Infrastructure: backend.infrastructure.*

Based on the Development Bible requirements for canonical import structure.
"""

import os
import re
import glob
from pathlib import Path

def get_backend_root():
    """Get the backend root directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent

def read_file(file_path):
    """Read file content with UTF-8 encoding."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def write_file(file_path, content):
    """Write file content with UTF-8 encoding."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing {file_path}: {e}")
        return False

def fix_canonical_imports(content):
    """Fix non-canonical imports to use canonical infrastructure paths."""
    
    # Infrastructure import fixes - convert deep nested paths to canonical
    infrastructure_fixes = [
        # Database imports
        (r'from backend\.infrastructure\.shared\.database\.base import', 
         'from backend.infrastructure.database import'),
        (r'from backend\.infrastructure\.shared\.database\.session import', 
         'from backend.infrastructure.database import'),
        
        # Utils imports  
        (r'from backend\.infrastructure\.shared\.utils\.database import', 
         'from backend.infrastructure.utils import'),
        (r'from backend\.infrastructure\.shared\.utils\.error import', 
         'from backend.infrastructure.utils import'),
        (r'from backend\.infrastructure\.shared\.utils\.error_utils import', 
         'from backend.infrastructure.utils import'),
        (r'from backend\.infrastructure\.shared\.utils\.file import', 
         'from backend.infrastructure.utils import'),
        (r'from backend\.infrastructure\.shared\.utils\.firebase import', 
         'from backend.infrastructure.utils import'),
        (r'from backend\.infrastructure\.shared\.utils\.logging import', 
         'from backend.infrastructure.utils import'),
        (r'from backend\.infrastructure\.shared\.utils\.noise import', 
         'from backend.infrastructure.utils import'),
        (r'from backend\.infrastructure\.shared\.utils\.rules import', 
         'from backend.infrastructure.utils import'),
        (r'from backend\.infrastructure\.shared\.utils\.security import', 
         'from backend.infrastructure.utils import'),
        (r'from backend\.infrastructure\.shared\.utils\.validation import', 
         'from backend.infrastructure.utils import'),
        
        # Models imports
        (r'from backend\.infrastructure\.shared\.models\.base import', 
         'from backend.infrastructure.models import'),
        (r'from backend\.infrastructure\.shared\.models\.save import', 
         'from backend.infrastructure.models import'),
        
        # Repository imports
        (r'from backend\.infrastructure\.shared\.repositories\.base_repository import', 
         'from backend.infrastructure.repositories import'),
        
        # Events imports
        (r'from backend\.infrastructure\.events\.core\.event_base import', 
         'from backend.infrastructure.events import'),
        (r'from backend\.infrastructure\.events\.events\.event_dispatcher import', 
         'from backend.infrastructure.events import'),
        (r'from backend\.infrastructure\.events\.events\.event_types import', 
         'from backend.infrastructure.events import'),
        (r'from backend\.infrastructure\.events\.models\.event_dispatcher import', 
         'from backend.infrastructure.events import'),
        (r'from backend\.infrastructure\.events\.services\.event_dispatcher import', 
         'from backend.infrastructure.events import'),
        (r'from backend\.infrastructure\.shared\.events\.bus import', 
         'from backend.infrastructure.events import'),
        (r'from backend\.infrastructure\.shared\.events\.dispatcher import', 
         'from backend.infrastructure.events import'),
        (r'from backend\.infrastructure\.shared\.events\.event_dispatcher import', 
         'from backend.infrastructure.events import'),
        
        # Data loader imports
        (r'from backend\.infrastructure\.data\.loaders\.game_data_registry import', 
         'from backend.infrastructure.data import'),
        
        # Rules imports
        (r'from backend\.infrastructure\.shared\.rules\.rules_utils import', 
         'from backend.infrastructure.rules import'),
    ]
    
    # Fix incorrect backend.systems imports in infrastructure files
    systems_fixes = [
        # Fix incorrect app.* imports
        (r'from backend\.systems\.app\.db\.session import', 
         'from backend.infrastructure.database import'),
        (r'from backend\.systems\.app\.models\.base import', 
         'from backend.infrastructure.models import'),
        (r'from backend\.systems\.app\.api\.v1\.endpoints import', 
         'from backend.infrastructure.api.v1.endpoints import'),
        (r'from backend\.systems\.app\.api\.v1\.api import', 
         'from backend.infrastructure.api.v1 import'),
        (r'from backend\.systems\.app\.middleware\.(.*) import', 
         r'from backend.infrastructure.middleware.\1 import'),
        (r'from backend\.systems\.app\.db import', 
         'from backend.infrastructure.database import'),
        
        # Fix base imports
        (r'from backend\.systems\.base import Base', 
         'from backend.infrastructure.database import Base'),
        (r'from backend\.systems\.base_service import', 
         'from backend.infrastructure.services import'),
        (r'from backend\.systems\.base_repository import', 
         'from backend.infrastructure.repositories import'),
        
        # Fix model imports
        (r'from backend\.systems\.models\.base import', 
         'from backend.infrastructure.models import'),
        (r'from backend\.systems\.models\.(.*) import', 
         r'from backend.systems.\1.models import'),
        
        # Fix repository imports
        (r'from backend\.systems\.repositories\.base_repository import', 
         'from backend.infrastructure.repositories import'),
        (r'from backend\.systems\.repositories\.repository_factory import', 
         'from backend.infrastructure.repositories import'),
        
        # Fix config imports
        (r'from backend\.systems\.config import', 
         'from backend.infrastructure.config import'),
        
        # Fix security imports
        (r'from backend\.systems\.security import', 
         'from backend.infrastructure.core.security import'),
        (r'from backend\.systems\.dependencies import', 
         'from backend.infrastructure.core.dependencies import'),
        (r'from backend\.systems\.errors import', 
         'from backend.infrastructure.core import'),
        
        # Fix specific system imports that should be canonical
        (r'from backend\.systems\.dispatcher import', 
         'from backend.infrastructure.events import'),
        (r'from backend\.systems\.event_types import', 
         'from backend.infrastructure.events import'),
        (r'from backend\.systems\.gpt_client import', 
         'from backend.infrastructure.llm.services import'),
        (r'from backend\.systems\.types import', 
         'from backend.infrastructure.types import'),
        
        # Fix auth imports
        (r'from backend\.systems\.auth import', 
         'from backend.infrastructure.auth.auth_user.routers import'),
        (r'from backend\.systems\.user import', 
         'from backend.infrastructure.auth.auth_user.models import'),
        (r'from backend\.systems\.role import', 
         'from backend.infrastructure.auth.auth_user.models import'),
        (r'from backend\.systems\.permission import', 
         'from backend.infrastructure.auth.auth_user.models import'),
        
        # Fix utils imports
        (r'from backend\.systems\.utils\.game\.(.*) import', 
         r'from backend.infrastructure.events.utils.game.\1 import'),
        (r'from backend\.systems\.core\.cache import', 
         'from backend.infrastructure.utils import'),
    ]
    
    # Apply infrastructure fixes
    for pattern, replacement in infrastructure_fixes:
        content = re.sub(pattern, replacement, content)
    
    # Apply systems fixes
    for pattern, replacement in systems_fixes:
        content = re.sub(pattern, replacement, content)
    
    return content

def process_file(file_path):
    """Process a single Python file to fix imports."""
    content = read_file(file_path)
    if content is None:
        return False
    
    original_content = content
    fixed_content = fix_canonical_imports(content)
    
    if fixed_content != original_content:
        if write_file(file_path, fixed_content):
            print(f"✅ Fixed imports in: {file_path}")
            return True
        else:
            print(f"❌ Failed to write: {file_path}")
            return False
    
    return False

def find_python_files(backend_root):
    """Find all Python files in the backend directory."""
    python_files = []
    
    # Find all .py files in systems and infrastructure
    for pattern in ['systems/**/*.py', 'infrastructure/**/*.py']:
        full_pattern = os.path.join(backend_root, pattern)
        python_files.extend(glob.glob(full_pattern, recursive=True))
    
    # Filter out __pycache__ directories
    python_files = [f for f in python_files if '__pycache__' not in f]
    
    return python_files

def main():
    """Main function to fix all canonical imports."""
    backend_root = get_backend_root()
    print(f"Backend root: {backend_root}")
    
    # Find all Python files
    python_files = find_python_files(backend_root)
    print(f"Found {len(python_files)} Python files to process")
    
    # Process each file
    fixed_count = 0
    total_files = len(python_files)
    
    for i, file_path in enumerate(python_files, 1):
        rel_path = os.path.relpath(file_path, backend_root)
        print(f"[{i}/{total_files}] Processing: {rel_path}")
        
        if process_file(file_path):
            fixed_count += 1
    
    print(f"\n📊 Summary:")
    print(f"Total files processed: {total_files}")
    print(f"Files with imports fixed: {fixed_count}")
    print(f"Files unchanged: {total_files - fixed_count}")
    
    if fixed_count > 0:
        print(f"\n✅ Successfully fixed canonical imports in {fixed_count} files!")
    else:
        print(f"\n✅ All imports were already canonical!")

if __name__ == "__main__":
    main() 