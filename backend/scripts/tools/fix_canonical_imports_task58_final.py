#!/usr/bin/env python3
"""
Comprehensive Canonical Import Fixer for Task 58

This script systematically fixes all import issues in the backend systems
to ensure all imports follow the canonical backend.systems.* structure.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Set
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def get_backend_root() -> Path:
    """Get the backend directory path."""
    current_dir = Path(__file__).parent
    if current_dir.name == 'backend':
        return current_dir
    # If running from backend subdirectory, find backend root
    while current_dir.parent and current_dir.name != 'backend':
        current_dir = current_dir.parent
    if current_dir.name == 'backend':
        return current_dir
    
    # Fallback: look for backend directory
    for path in [Path.cwd(), Path.cwd().parent]:
        backend_path = path / 'backend'
        if backend_path.exists() and backend_path.is_dir():
            return backend_path
    
    raise RuntimeError("Could not find backend directory")

# Import pattern fixes - most specific first to avoid conflicts
IMPORT_FIXES = [
    # Fix specific problematic imports first
    (r'from backend.systems.rumor.utils import'),
    (r'from backend.systems.dialogue.extractors import'),
    
    # Fix non-canonical NPC imports
    (r'from backend.systems.npc.services.npc_service import'),
    (r'from backend.systems.npc.routers.npc_router import'),
    (r'from backend.systems.npc.services.npc_location_service import'),
    (r'from backend.systems.npc.models.npc_events import'),
    (r'from backend.systems.rumor.utils import'),
    (r'from backend.systems.npc.utils.npc_leveling_utils import'),
    (r'from backend.systems.npc.services.npc_service import'),
    (r'from backend.systems.npc.services.npc_service import'),
    (r'from backend.systems.quest.npc_quests import'),
    (r'from backend.systems.npc.repositories.npc_repository import'),
    
    # Fix relative imports with system context detection
    # These will be handled by detect_system_context function
    
    # Fix generic patterns (commented out imports are fine to leave)
    (r'^(\s*)# from app\.', r'\1# from backend.systems.'),
    (r'^(\s*)# from backend.systems.dialogue.'),
]

def detect_system_context(file_path: Path) -> str:
    """
    Detect which system a file belongs to based on its path.
    Returns the system name for use in canonical imports.
    """
    parts = file_path.parts
    backend_idx = -1
    
    for i, part in enumerate(parts):
        if part == 'backend':
            backend_idx = i
            break
    
    if backend_idx == -1:
        return 'unknown'
    
    # Look for systems directory
    if backend_idx + 1 < len(parts) and parts[backend_idx + 1] == 'systems':
        if backend_idx + 2 < len(parts):
            return parts[backend_idx + 2]
    
    return 'unknown'

def fix_relative_imports(content: str, file_path: Path) -> str:
    """
    Fix relative imports based on the file's system context.
    """
    system = detect_system_context(file_path)
    if system == 'unknown':
        return content
    
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        original_line = line
        stripped = line.strip()
        
        # Skip comments and empty lines
        if not stripped or stripped.startswith('#'):
            fixed_lines.append(line)
            continue
        
        # Fix relative imports from backend.systems.module import)
        if re.match(r'^\s*from\s+\.\s*import', stripped):
            # from backend.systems.SYSTEM import something
            new_line = re.sub(r'from\s+\.\s+import', f'from backend.systems.{system} import', line)
            if new_line != line:
                logger.info(f"Fixed relative import in {file_path}: {stripped}")
            fixed_lines.append(new_line)
            continue
            
        if re.match(r'^\s*from\s+\.[\w.]+\s+import', stripped):
            # from backend.systems.module import backend.systems.SYSTEM.module import something
            match = re.search(r'from\s+\.([\w.]+)\s+import', stripped)
            if match:
                module_path = match.group(1)
                new_line = re.sub(
                    r'from\s+\.([\w.]+)\s+import',
                    f'from backend.systems.{system}.{module_path} import',
                    line
                )
                if new_line != line:
                    logger.info(f"Fixed relative import in {file_path}: {stripped}")
                fixed_lines.append(new_line)
                continue
        
        # Fix relative imports from backend.systems.module import)
        if re.match(r'^\s*from\s+\.\.[\w.]*\s+import', stripped):
            # from backend.systems.module import backend.systems.module import something
            match = re.search(r'from\s+\.\.([\w.]*)\s+import', stripped)
            if match:
                module_path = match.group(1).strip('.')
                if module_path:
                    new_line = re.sub(
                        r'from\s+\.\.([\w.]*)\s+import',
                        f'from backend.systems.{module_path} import',
                        line
                    )
                else:
                    # from backend.systems import -> from backend.systems import
                    new_line = re.sub(
                        r'from\s+\.\.\s+import',
                        'from backend.systems import',
                        line
                    )
                if new_line != line:
                    logger.info(f"Fixed relative import in {file_path}: {stripped}")
                fixed_lines.append(new_line)
                continue
        
        # No changes needed
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_imports_in_file(file_path: Path) -> bool:
    """
    Fix imports in a single file.
    Returns True if changes were made.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply pattern-based fixes
        for pattern, replacement in IMPORT_FIXES:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        # Apply relative import fixes
        content = fix_relative_imports(content, file_path)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Fixed imports in: {file_path}")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return False

def find_python_files(root_path: Path) -> List[Path]:
    """Find all Python files in the backend systems and tests directories."""
    python_files = []
    
    # Search in systems directory
    systems_path = root_path / 'systems'
    if systems_path.exists():
        python_files.extend(systems_path.rglob('*.py'))
    
    # Search in tests directory
    tests_path = root_path / 'tests'
    if tests_path.exists():
        python_files.extend(tests_path.rglob('*.py'))
    
    return python_files

def validate_imports(root_path: Path) -> List[Tuple[Path, str]]:
    """
    Validate that all imports are now canonical.
    Returns list of (file_path, problematic_line) tuples.
    """
    issues = []
    python_files = find_python_files(root_path)
    
    # Patterns that indicate non-canonical imports
    problematic_patterns = [
        r'from\s+app\.',
        r'import\s+app\.',
        r'from\s+dialogue\.(?!.*backend\.systems\.dialogue)',
        r'import\s+dialogue\.(?!.*backend\.systems\.dialogue)',
        r'from\s+systems\.(?!.*backend\.systems)',
        r'import\s+systems\.(?!.*backend\.systems)',
        r'from\s+\.\s+import',  # from backend.systems import
        r'from\s+\.\.+',        # from backend.systems import or from backend.systems import
    ]
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                stripped_line = line.strip()
                # Skip comments
                if stripped_line.startswith('#'):
                    continue
                
                for pattern in problematic_patterns:
                    if re.search(pattern, stripped_line):
                        issues.append((file_path, f"Line {line_num}: {stripped_line}"))
        
        except Exception as e:
            logger.error(f"Error validating {file_path}: {e}")
    
    return issues

def main():
    """Main function to fix all canonical imports."""
    try:
        backend_root = get_backend_root()
        logger.info(f"Backend root: {backend_root}")
        
        # Find all Python files
        python_files = find_python_files(backend_root)
        logger.info(f"Found {len(python_files)} Python files to process")
        
        # Fix imports
        fixed_count = 0
        for file_path in python_files:
            if fix_imports_in_file(file_path):
                fixed_count += 1
        
        logger.info(f"Fixed imports in {fixed_count} files")
        
        # Validate results
        logger.info("Validating canonical import compliance...")
        issues = validate_imports(backend_root)
        
        if issues:
            logger.warning(f"Found {len(issues)} remaining import issues:")
            for file_path, issue in issues[:20]:  # Show first 20 issues
                logger.warning(f"  {file_path.relative_to(backend_root)}: {issue}")
            if len(issues) > 20:
                logger.warning(f"  ... and {len(issues) - 20} more issues")
        else:
            logger.info("✅ All imports are now canonical!")
        
        return len(issues) == 0
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 