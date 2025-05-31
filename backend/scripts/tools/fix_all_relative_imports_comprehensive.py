#!/usr/bin/env python3
"""
Comprehensive Import Fixer for Backend Development Protocol

This script systematically fixes import issues across the backend systems
by converting absolute imports to relative imports within system boundaries
and fixing known import path issues.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Tuple

class ComprehensiveImportFixer:
    def __init__(self, backend_root: str = "systems"):
        self.backend_root = Path(backend_root)
        self.fixes_applied = 0
        self.files_processed = 0
        
        # Known import fixes
        self.known_fixes = {
            "backend.infrastructure.shared.base": "backend.infrastructure.shared.models.base",
            "backend.systems.poi.poi_service": "backend.systems.poi.services.poi_service",
            "backend.systems.loot.base": "backend.systems.loot.models.base",
        }
        
        # System boundaries for relative import conversion
        self.system_dirs = self._find_system_directories()
        
    def _find_system_directories(self) -> List[Path]:
        """Find all system directories that should use relative imports internally"""
        systems = []
        if self.backend_root.exists():
            for item in self.backend_root.iterdir():
                if item.is_dir() and not item.name.startswith('.') and item.name != '__pycache__':
                    systems.append(item)
        return systems
    
    def _find_init_files(self) -> List[Path]:
        """Find all __init__.py files in the backend"""
        init_files = []
        for system_dir in self.system_dirs:
            for init_file in system_dir.rglob("__init__.py"):
                init_files.append(init_file)
        return init_files
    
    def _should_convert_to_relative(self, import_line: str, current_file: Path) -> bool:
        """Determine if an import should be converted to relative"""
        # Only convert imports within the same system
        if not import_line.strip().startswith("from backend.systems."):
            return False
            
        # Find which system this file belongs to
        current_system = None
        for system_dir in self.system_dirs:
            try:
                current_file.relative_to(system_dir)
                current_system = system_dir.name
                break
            except ValueError:
                continue
        
        if not current_system:
            return False
        
        # Check if import is from the same system
        import_pattern = rf"from backend\.systems\.{re.escape(current_system)}\."
        return bool(re.search(import_pattern, import_line))
    
    def _convert_to_relative_import(self, import_line: str, current_file: Path) -> str:
        """Convert absolute import to relative import"""
        # Extract the import parts
        match = re.match(r'from (backend\.systems\.[\w\.]+) import (.+)', import_line.strip())
        if not match:
            return import_line
        
        module_path, imports = match.groups()
        
        # Find current system
        current_system = None
        for system_dir in self.system_dirs:
            try:
                current_file.relative_to(system_dir)
                current_system = system_dir.name
                break
            except ValueError:
                continue
        
        if not current_system:
            return import_line
        
        # Calculate relative path
        system_prefix = f"backend.systems.{current_system}."
        if not module_path.startswith(system_prefix):
            return import_line
        
        relative_path = module_path[len(system_prefix):]
        
        # Calculate dots for relative import
        current_depth = len(current_file.relative_to(self.backend_root / current_system).parts) - 1
        
        if relative_path == "":
            # Importing from system root
            dots = "." * (current_depth + 1)
            return f"from {dots} import {imports}"
        else:
            # Importing from subdirectory
            dots = "." * (current_depth + 1)
            return f"from {dots}{relative_path} import {imports}"
    
    def _apply_known_fixes(self, content: str) -> Tuple[str, int]:
        """Apply known import fixes"""
        fixes_count = 0
        for old_import, new_import in self.known_fixes.items():
            old_pattern = re.escape(old_import)
            new_content = re.sub(old_pattern, new_import, content)
            if new_content != content:
                fixes_count += 1
                content = new_content
        return content, fixes_count
    
    def _fix_specific_issues(self, content: str, file_path: Path) -> Tuple[str, int]:
        """Fix specific known issues"""
        fixes_count = 0
        
        # Fix POI service imports
        if "poi" in str(file_path) and "services" in str(file_path):
            old_content = content
            content = re.sub(
                r'from backend\.systems\.poi\.poi_service import',
                'from backend.systems.poi_service import',
                content
            )
            if content != old_content:
                fixes_count += 1
        
        # Fix loot system imports
        if "loot" in str(file_path) and "models" in str(file_path):
            old_content = content
            content = re.sub(
                r'from backend\.systems\.loot\.base import',
                'from backend.systems.base import',
                content
            )
            if content != old_content:
                fixes_count += 1
        
        return content, fixes_count
    
    def fix_file(self, file_path: Path) -> int:
        """Fix imports in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            fixes_in_file = 0
            
            # Apply known fixes first
            content, known_fixes_count = self._apply_known_fixes(content)
            fixes_in_file += known_fixes_count
            
            # Apply specific fixes
            content, specific_fixes_count = self._fix_specific_issues(content, file_path)
            fixes_in_file += specific_fixes_count
            
            # Convert to relative imports line by line
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('from backend.systems.') and self._should_convert_to_relative(line, file_path):
                    new_line = self._convert_to_relative_import(line, file_path)
                    if new_line != line:
                        lines[i] = new_line
                        fixes_in_file += 1
            
            content = '\n'.join(lines)
            
            # Write back if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Fixed {fixes_in_file} imports in {file_path}")
            
            return fixes_in_file
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return 0
    
    def run(self) -> Dict[str, int]:
        """Run the comprehensive import fixer"""
        print("Starting comprehensive import fixing...")
        
        # Find all Python files to process
        python_files = []
        for system_dir in self.system_dirs:
            for py_file in system_dir.rglob("*.py"):
                if not py_file.name.startswith('.') and py_file.name != '__pycache__':
                    python_files.append(py_file)
        
        print(f"Found {len(python_files)} Python files to process")
        
        # Process each file
        for file_path in python_files:
            fixes = self.fix_file(file_path)
            self.fixes_applied += fixes
            self.files_processed += 1
        
        return {
            "files_processed": self.files_processed,
            "fixes_applied": self.fixes_applied
        }

def main():
    """Main execution function"""
    fixer = ComprehensiveImportFixer()
    results = fixer.run()
    
    print(f"\nComprehensive Import Fixing Complete!")
    print(f"Files processed: {results['files_processed']}")
    print(f"Fixes applied: {results['fixes_applied']}")
    
    # Test the results
    print("\nTesting import fixes...")
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout + result.stderr
        if "collected" in output:
            # Extract test count and error count
            lines = output.split('\n')
            for line in lines:
                if "collected" in line and "error" in line:
                    print(f"Test collection result: {line}")
                    break
        else:
            print("Test collection completed")
            
    except subprocess.TimeoutExpired:
        print("Test collection timed out")
    except Exception as e:
        print(f"Error running test collection: {e}")

if __name__ == "__main__":
    main() 