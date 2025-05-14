#!/usr/bin/env python3
"""
Python Module Integration Script

This script helps integrate converted Python modules with the existing Python codebase.
It verifies imports, fixes module paths, and ensures compatibility between converted
modules and the existing backend code.

Usage:
  python integrate_py_modules.py --source-dir <directory_with_converted_files> --target-dir <backend_directory>
"""

import os
import re
import sys
import shutil
import argparse
import importlib.util
from typing import Dict, List, Set, Tuple, Optional, Any
from pathlib import Path

class PythonModuleIntegrator:
    """Helps integrate converted Python modules with existing Python codebase."""
    
    def __init__(self, source_dir: str, target_dir: str, dry_run: bool = False):
        """
        Initialize the integrator.
        
        Args:
            source_dir: Directory containing converted Python files
            target_dir: Target directory in the existing Python codebase
            dry_run: If True, don't make actual changes, just report what would happen
        """
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.dry_run = dry_run
        self.import_map: Dict[str, str] = {}
        self.processed_files: Set[str] = set()
        self.import_errors: List[Tuple[str, str]] = []
        self.integration_issues: List[Tuple[str, str]] = []
        
    def create_init_files(self, directory: Path) -> None:
        """
        Create __init__.py files in all subdirectories to make them proper Python packages.
        
        Args:
            directory: The directory to process recursively
        """
        for root, dirs, files in os.walk(directory):
            root_path = Path(root)
            init_file = root_path / "__init__.py"
            
            if not init_file.exists():
                if not self.dry_run:
                    with open(init_file, 'w') as f:
                        f.write('# Auto-generated during TypeScript to Python migration\n')
                print(f"Created {init_file}")
            
    def fix_import_statements(self, file_path: Path) -> int:
        """
        Fix import statements in the given Python file.
        
        Args:
            file_path: Path to the Python file to fix
            
        Returns:
            Number of imports fixed
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        fixed_imports = 0
        
        # Look for relative imports
        relative_import_pattern = r'from\s+(\..+?)\s+import'
        for match in re.finditer(relative_import_pattern, content):
            rel_import = match.group(1)
            # Process relative imports if needed
            # This is a placeholder for specific relative import handling
            
        # Look for absolute imports of converted modules
        absolute_import_pattern = r'from\s+([a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)+)\s+import'
        for match in re.finditer(absolute_import_pattern, content):
            abs_import = match.group(1)
            # Check if this import should be mapped to a new location
            if abs_import in self.import_map:
                new_import = self.import_map[abs_import]
                content = content.replace(f'from {abs_import} import', f'from {new_import} import')
                fixed_imports += 1
        
        # Write back the fixed file
        if content != original_content and not self.dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
        return fixed_imports
    
    def verify_imports(self, file_path: Path) -> List[str]:
        """
        Verify that all imports in the file can be resolved.
        
        Args:
            file_path: Path to the Python file to check
            
        Returns:
            List of import errors found
        """
        import_errors = []
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all import statements
        import_pattern = r'(?:from\s+([a-zA-Z0-9_\.]+)\s+import|import\s+([a-zA-Z0-9_\.]+))'
        for match in re.finditer(import_pattern, content):
            module_name = match.group(1) if match.group(1) else match.group(2)
            
            # Skip standard library and typing modules
            if module_name in ('typing', 'enum', 'os', 'sys', 'pathlib', 're') or module_name.startswith('typing.'):
                continue
                
            # Try to find the module
            try:
                # For modules with relative imports, we need special handling
                if module_name.startswith('.'):
                    # This is a simplified approach - in a real tool, you'd need more robust handling
                    parent_package = str(file_path.parent).replace('/', '.')
                    absolute_name = f"{parent_package}{module_name}"
                    if not self.module_exists(absolute_name):
                        import_errors.append(f"Could not resolve relative import: {module_name}")
                else:
                    if not self.module_exists(module_name):
                        import_errors.append(f"Could not resolve import: {module_name}")
            except Exception as e:
                import_errors.append(f"Error checking import {module_name}: {str(e)}")
        
        return import_errors
                
    def module_exists(self, module_name: str) -> bool:
        """
        Check if a Python module exists and can be imported.
        
        Args:
            module_name: Name of the module to check
            
        Returns:
            True if the module exists, False otherwise
        """
        try:
            spec = importlib.util.find_spec(module_name)
            return spec is not None
        except (ImportError, ValueError):
            return False
    
    def integrate_file(self, source_file: Path, target_file: Path) -> bool:
        """
        Integrate a single converted file into the target directory.
        
        Args:
            source_file: Source Python file
            target_file: Target location for the file
            
        Returns:
            True if integration was successful, False otherwise
        """
        try:
            # Create target directory if it doesn't exist
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the file
            if not self.dry_run:
                shutil.copy2(source_file, target_file)
            
            # Fix imports in the copied file
            fixed_imports = 0
            if not self.dry_run:
                fixed_imports = self.fix_import_statements(target_file)
            
            print(f"Integrated {source_file} -> {target_file} (fixed {fixed_imports} imports)")
            return True
        except Exception as e:
            print(f"Error integrating {source_file}: {str(e)}")
            self.integration_issues.append((str(source_file), str(e)))
            return False
    
    def build_import_map(self) -> None:
        """Build a mapping of old import paths to new ones based on file structure."""
        print("Building import mapping...")
        # This is a placeholder - in a real implementation, you would analyze
        # the source and target directories to create an appropriate mapping
        
        # Example mapping - customize based on project structure
        self.import_map = {
            "types.buildings": "backend.app.models.buildings",
            "types.items": "backend.app.models.items",
            "src.core.models": "backend.app.core.models",
            "src.poi.models": "backend.app.poi.models",
            # Add more mappings as needed
        }
        
    def integrate_modules(self) -> Tuple[int, int, int]:
        """
        Integrate all converted Python modules.
        
        Returns:
            Tuple of (files_processed, files_integrated, error_count)
        """
        print(f"Integrating Python modules from {self.source_dir} to {self.target_dir}")
        
        # First, build the import mapping
        self.build_import_map()
        
        # Create __init__.py files to make directories proper packages
        if not self.dry_run:
            self.create_init_files(self.target_dir)
        
        # Track statistics
        files_processed = 0
        files_integrated = 0
        
        # Walk the source directory
        for root, _, files in os.walk(self.source_dir):
            for file in files:
                if file.endswith('.py'):
                    files_processed += 1
                    source_file = Path(root) / file
                    
                    # Compute the target path
                    rel_path = os.path.relpath(source_file, self.source_dir)
                    target_file = self.target_dir / rel_path
                    
                    # Integrate the file
                    if self.integrate_file(source_file, target_file):
                        files_integrated += 1
                        
                        # Verify imports
                        if not self.dry_run:
                            errors = self.verify_imports(target_file)
                            if errors:
                                for error in errors:
                                    self.import_errors.append((str(target_file), error))
        
        return files_processed, files_integrated, len(self.import_errors)
    
    def print_summary(self, files_processed: int, files_integrated: int, error_count: int) -> None:
        """Print a summary of the integration process."""
        print("\n== Integration Summary ==")
        print(f"Files processed: {files_processed}")
        print(f"Files integrated: {files_integrated}")
        print(f"Files with errors: {error_count}")
        
        if self.import_errors:
            print("\n== Import Errors ==")
            for file, error in self.import_errors:
                print(f"{file}: {error}")
        
        if self.integration_issues:
            print("\n== Integration Issues ==")
            for file, error in self.integration_issues:
                print(f"{file}: {error}")

def main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description='Integrate converted Python modules with existing codebase')
    parser.add_argument('--source-dir', required=True, help='Directory containing converted Python files')
    parser.add_argument('--target-dir', required=True, help='Target directory in the existing Python codebase')
    parser.add_argument('--dry-run', action='store_true', help='Don\'t make actual changes, just report what would happen')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.source_dir):
        print(f"Error: {args.source_dir} is not a directory")
        return 1
    
    if not os.path.isdir(args.target_dir):
        print(f"Error: {args.target_dir} is not a directory")
        return 1
    
    integrator = PythonModuleIntegrator(args.source_dir, args.target_dir, args.dry_run)
    files_processed, files_integrated, error_count = integrator.integrate_modules()
    integrator.print_summary(files_processed, files_integrated, error_count)
    
    # Return non-zero exit code if there were errors
    return 1 if error_count > 0 else 0

if __name__ == '__main__':
    sys.exit(main()) 