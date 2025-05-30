#!/usr/bin/env python3
"""
Script to fix import issues in Python files by identifying and correcting
imports that are incorrectly placed inside TYPE_CHECKING blocks.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict

# Common runtime imports that should not be in TYPE_CHECKING blocks
RUNTIME_IMPORTS = {
    'logging', 'json', 'os', 'sys', 'asyncio', 'uuid', 'datetime', 'time',
    'typing', 'pydantic', 'fastapi', 'sqlalchemy', 'pytest', 'unittest',
    'dataclasses', 'enum', 'collections', 'abc', 'functools', 'itertools',
    'pathlib', 'tempfile', 'shutil', 'pickle', 'copy', 'math', 'random',
    'hashlib', 'base64', 'urllib', 'http', 'socket', 'threading', 
    'multiprocessing', 'subprocess', 'contextlib', 'warnings'
}

class ImportFixer:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.fixes_made = []
        
    def fix_file(self, file_path: Path) -> bool:
        """Fix imports in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            fixed_content, changes = self.fix_imports_in_content(content)
            
            if changes:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                self.fixes_made.append((file_path, changes))
                print(f"Fixed {len(changes)} import issues in {file_path}")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def fix_imports_in_content(self, content: str) -> Tuple[str, List[str]]:
        """Fix imports in content and return modified content and list of changes."""
        lines = content.split('\n')
        changes = []
        
        # Find TYPE_CHECKING block
        type_checking_start = None
        type_checking_end = None
        imports_to_move = []
        
        for i, line in enumerate(lines):
            if 'TYPE_CHECKING:' in line:
                type_checking_start = i
            elif type_checking_start is not None and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                # End of TYPE_CHECKING block (non-indented line)
                if not line.strip().startswith('#'):
                    type_checking_end = i
                    break
        
        if type_checking_start is None:
            return content, []
        
        # If we didn't find the end, assume it goes to end of file or next function/class
        if type_checking_end is None:
            type_checking_end = len(lines)
        
        # Scan TYPE_CHECKING block for runtime imports
        for i in range(type_checking_start + 1, type_checking_end):
            line = lines[i].strip()
            if not line or line.startswith('#'):
                continue
                
            # Check for import statements
            if line.startswith('import ') or line.startswith('from '):
                # Extract module name
                if line.startswith('import '):
                    module_name = line.split()[1].split('.')[0]
                elif line.startswith('from '):
                    module_name = line.split()[1].split('.')[0]
                else:
                    continue
                
                # Check if this is a runtime import
                if module_name in RUNTIME_IMPORTS:
                    imports_to_move.append((i, line))
                    changes.append(f"Moved runtime import: {line}")
        
        if not imports_to_move:
            return content, []
        
        # Create new content
        new_lines = []
        
        # Find where to insert the moved imports (after existing imports)
        insert_position = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                insert_position = i + 1
            elif line.strip() and not line.strip().startswith('#') and not line.strip().startswith('"""') and not line.strip().startswith("'''"):
                break
        
        # Build new content
        lines_to_skip = set(i for i, _ in imports_to_move)
        
        for i, line in enumerate(lines):
            if i == insert_position:
                # Insert moved imports here
                for _, import_line in imports_to_move:
                    new_lines.append(import_line)
                
            if i not in lines_to_skip:
                new_lines.append(line)
        
        return '\n'.join(new_lines), changes
    
    def scan_and_fix_directory(self, directory: str = "systems") -> int:
        """Scan directory and fix all Python files."""
        target_dir = self.base_path / directory
        
        if not target_dir.exists():
            print(f"Directory {target_dir} does not exist")
            return 0
        
        python_files = list(target_dir.rglob("*.py"))
        fixed_count = 0
        
        for file_path in python_files:
            if self.fix_file(file_path):
                fixed_count += 1
        
        return fixed_count
    
    def report_fixes(self):
        """Report all fixes made."""
        if not self.fixes_made:
            print("No import fixes were needed.")
            return
        
        print(f"\n=== Import Fix Report ===")
        print(f"Fixed {len(self.fixes_made)} files")
        
        for file_path, changes in self.fixes_made:
            print(f"\n{file_path}:")
            for change in changes:
                print(f"  - {change}")

def main():
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = "."
    
    fixer = ImportFixer(base_path)
    
    print("Starting import fixes...")
    fixed_count = fixer.scan_and_fix_directory("systems")
    
    print(f"\nProcessed and fixed {fixed_count} files")
    fixer.report_fixes()

if __name__ == "__main__":
    main() 