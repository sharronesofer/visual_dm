#!/usr/bin/env python3

"""
Script to update references to consolidated files in the Visual DM project.
This script reads the merge report and updates references in C# and Python files.
"""

import os
import re
import json
import logging
from datetime import datetime
import argparse
import fnmatch
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scripts/update_references.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ReferenceUpdater:
    def __init__(self, project_root, merge_report, backup_dir=None):
        self.project_root = project_root
        self.merge_report_path = merge_report
        self.merge_report = None
        
        # Set backup directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = backup_dir or os.path.join(project_root, "backups", f"reference_update_{timestamp}")
        os.makedirs(self.backup_dir, exist_ok=True)
        logger.info(f"Created backup directory: {self.backup_dir}")
        
        # Load merge report
        if merge_report and os.path.exists(merge_report):
            with open(merge_report, 'r') as f:
                self.merge_report = json.load(f)
                logger.info(f"Loaded merge report from {merge_report}")
        else:
            logger.error(f"Merge report not found at {merge_report}")
            raise FileNotFoundError(f"Merge report not found at {merge_report}")
        
        # Create reference maps
        self.cs_class_map = {}          # Map of class names to new paths
        self.cs_namespace_map = {}      # Map of namespaces to new paths
        self.cs_file_map = {}           # Map of old file paths to new paths
        self.py_module_map = {}         # Map of Python module names to new paths
        self.py_file_map = {}           # Map of old Python file paths to new paths
        self.manager_class_map = {}     # Map of manager class names 
        self.singleton_class_map = {}   # Map of singleton class names
        
        # Initialize reference maps from merge report
        self._initialize_reference_maps()
        
        # Track update statistics
        self.update_stats = {
            'cs_files_updated': 0,
            'py_files_updated': 0,
            'total_references_updated': 0,
            'failed_updates': 0,
            'references_by_type': {
                'class': 0,
                'namespace': 0,
                'singleton': 0,
                'manager': 0,
                'module': 0,
                'file': 0
            }
        }
    
    def _initialize_reference_maps(self):
        """Initialize reference maps from merge report."""
        # Check if it's the new format from merge_duplicates.py
        if 'merge_operations' in self.merge_report:
            self._initialize_from_merge_duplicates()
        # Fall back to old format
        elif 'operations' in self.merge_report:
            self._initialize_from_old_format()
        else:
            logger.error("Merge report format not recognized")
            raise ValueError("Merge report format not recognized")
    
    def _initialize_from_merge_duplicates(self):
        """Initialize reference maps from the new merge_duplicates.py format."""
        operations = self.merge_report.get('merge_operations', {})
        
        for source_file, info in operations.items():
            file_type = info.get('type', '')
            language = info.get('language', '')
            
            if language == 'cs':
                # Process C# files
                
                # Map exact duplicates
                if 'identical_copies' in info:
                    for duplicate in info.get('identical_copies', []):
                        self.cs_file_map[duplicate] = source_file
                
                # Process class duplicates
                if file_type == 'class_duplicate':
                    class_name = info.get('class_name', '')
                    if class_name:
                        self.cs_class_map[class_name] = source_file
                    for duplicate in info.get('similar_copies', []):
                        self.cs_file_map[duplicate] = source_file
                
                # Process singleton duplicates
                elif file_type == 'singleton_duplicate':
                    class_name = info.get('class_name', '')
                    if class_name:
                        self.cs_class_map[class_name] = source_file
                        self.singleton_class_map[class_name] = source_file
                    for duplicate in info.get('similar_copies', []):
                        self.cs_file_map[duplicate] = source_file
                
                # Process manager duplicates
                elif file_type == 'manager_duplicate':
                    prefix = info.get('manager_prefix', '')
                    if prefix:
                        manager_class = f"{prefix}Manager"
                        self.cs_class_map[manager_class] = source_file
                        self.manager_class_map[manager_class] = source_file
                    for duplicate in info.get('similar_copies', []):
                        self.cs_file_map[duplicate] = source_file
                
            elif language == 'python':
                # Process Python files
                
                # Map exact duplicates
                if 'identical_copies' in info:
                    for duplicate in info.get('identical_copies', []):
                        self.py_file_map[duplicate] = source_file
                
                # Process module duplicates
                if file_type == 'module_duplicate':
                    module_name = info.get('module_name', '')
                    if module_name:
                        self.py_module_map[module_name] = source_file
                    for duplicate in info.get('similar_copies', []):
                        self.py_file_map[duplicate] = source_file
        
        logger.info(f"Initialized reference maps with {len(self.cs_file_map)} C# files and {len(self.py_file_map)} Python files")
        logger.info(f"Mapped {len(self.cs_class_map)} C# classes, {len(self.singleton_class_map)} singletons, {len(self.manager_class_map)} managers, and {len(self.py_module_map)} Python modules")
    
    def _initialize_from_old_format(self):
        """Initialize reference maps from the old format."""
        operations = self.merge_report.get('operations', [])
        
        for op in operations:
            op_type = op.get('type')
            
            if op_type == 'exact_duplicate':
                file_type = op.get('file_type')
                primary = op.get('primary')
                destination = op.get('destination')
                duplicates = op.get('duplicates', [])
                
                if file_type == 'cs':
                    # Map each old file path to the new destination
                    self.cs_file_map[primary] = destination
                    for dup in duplicates:
                        self.cs_file_map[dup] = destination
                
                elif file_type == 'py':
                    # Map each old file path to the new destination
                    self.py_file_map[primary] = destination
                    for dup in duplicates:
                        self.py_file_map[dup] = destination
            
            elif op_type == 'class_duplicate' or op_type == 'singleton_duplicate':
                class_name = op.get('class_name')
                destination = op.get('destination')
                duplicates = op.get('duplicates', [])
                
                # Map class name to new path
                self.cs_class_map[class_name] = destination
                if op_type == 'singleton_duplicate':
                    self.singleton_class_map[class_name] = destination
                
                # Also map file paths
                primary = op.get('primary')
                self.cs_file_map[primary] = destination
                for dup in duplicates:
                    self.cs_file_map[dup] = destination
            
            elif op_type == 'manager_duplicate':
                consolidated_name = op.get('consolidated_name')
                original_names = op.get('original_names', [])
                destination = op.get('destination')
                
                # Map each manager class name to the consolidated name
                for name in original_names:
                    self.cs_class_map[name] = destination
                    self.manager_class_map[name] = destination
                
                # Map file paths
                primary = op.get('primary')
                self.cs_file_map[primary] = destination
                duplicates = op.get('duplicates', [])
                for dup in duplicates:
                    self.cs_file_map[dup] = destination
            
            elif op_type == 'module_duplicate':
                module = op.get('module')
                destination = op.get('destination')
                duplicates = op.get('duplicates', [])
                
                # Map module to new path
                self.py_module_map[module] = destination
                
                # Map file paths
                primary = op.get('primary')
                self.py_file_map[primary] = destination
                for dup in duplicates:
                    self.py_file_map[dup] = destination
            
            elif op_type == 'similar_py_files':
                name = op.get('name')
                destination = op.get('destination')
                duplicates = op.get('duplicates', [])
                
                # Map file paths
                primary = op.get('primary')
                self.py_file_map[primary] = destination
                for dup in duplicates:
                    self.py_file_map[dup] = destination
    
    def backup_file(self, file_path):
        """Create a backup of a file before modifying it."""
        if os.path.exists(file_path):
            rel_path = os.path.relpath(file_path, self.project_root)
            backup_path = os.path.join(self.backup_dir, rel_path)
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            with open(file_path, 'rb') as src, open(backup_path, 'wb') as dst:
                dst.write(src.read())
            
            logger.info(f"Backed up {rel_path} to {backup_path}")
            return backup_path
        return None
    
    def update_cs_references(self):
        """Update references in C# files."""
        # Find all C# files
        cs_files = []
        for root, _, files in os.walk(os.path.join(self.project_root, 'VDM')):
            for file in fnmatch.filter(files, '*.cs'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.project_root)
                
                # Don't update files that are in the consolidated directory
                if '/Consolidated/' in rel_path:
                    continue
                
                # Don't update files that are part of the duplicates
                if rel_path in self.cs_file_map:
                    continue
                
                cs_files.append(file_path)
        
        logger.info(f"Found {len(cs_files)} C# files to scan for references")
        
        for file_path in cs_files:
            self._update_cs_file(file_path)
    
    def update_py_references(self):
        """Update references in Python files."""
        # Find all Python files
        py_files = []
        for root, _, files in os.walk(os.path.join(self.project_root, 'backend')):
            for file in fnmatch.filter(files, '*.py'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.project_root)
                
                # Don't update files that are in the core directory
                if '/core/' in rel_path:
                    continue
                
                # Don't update files that are part of the duplicates
                if rel_path in self.py_file_map:
                    continue
                
                py_files.append(file_path)
        
        logger.info(f"Found {len(py_files)} Python files to scan for references")
        
        for file_path in py_files:
            self._update_py_file(file_path)
    
    def _extract_import_path(self, file_path, source_file):
        """Extract the appropriate import path for a C# file."""
        # Convert to Unity-style paths
        rel_source = os.path.relpath(os.path.join(self.project_root, source_file), os.path.dirname(file_path))
        rel_source = rel_source.replace('\\', '/')
        
        # Remove .cs extension if present
        if rel_source.endswith('.cs'):
            rel_source = rel_source[:-3]
        
        return rel_source
    
    def _update_cs_file(self, file_path):
        """Update references in a single C# file."""
        rel_path = os.path.relpath(file_path, self.project_root)
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading {rel_path}: {e}")
            self.update_stats['failed_updates'] += 1
            return
        
        original_content = content
        updated = False
        
        # Update using statements for consolidated files
        for old_path, new_path in self.cs_file_map.items():
            if old_path.endswith('.cs'):
                old_namespace = self._extract_namespace_from_file(os.path.join(self.project_root, old_path))
                new_namespace = self._extract_namespace_from_file(os.path.join(self.project_root, new_path))
                
                # Skip if namespaces are the same
                if old_namespace == new_namespace or not old_namespace or not new_namespace:
                    continue
                
                # Replace namespace in using statements
                pattern = rf'using\s+{re.escape(old_namespace)};'
                replacement = f'using {new_namespace};'
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content
                    updated = True
                    self.update_stats['references_by_type']['namespace'] += 1
        
        # Update class references
        for class_name, new_path in self.cs_class_map.items():
            # Skip if the class has no name
            if not class_name:
                continue
                
            # Replace class instantiations
            pattern = rf'new\s+{re.escape(class_name)}\s*\('
            replacement = f'new {class_name}('
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                updated = True
                self.update_stats['references_by_type']['class'] += 1
            
            # Replace type references
            pattern = rf'\b{re.escape(class_name)}\b'
            replacement = class_name
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                updated = True
                self.update_stats['references_by_type']['class'] += 1
        
        # Update singleton instance references
        for class_name, new_path in self.singleton_class_map.items():
            if not class_name:
                continue
                
            # Replace Instance references
            pattern = rf'\b{re.escape(class_name)}\.Instance\b'
            replacement = f'{class_name}.Instance'
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                updated = True
                self.update_stats['references_by_type']['singleton'] += 1
        
        # Update manager references
        for class_name, new_path in self.manager_class_map.items():
            if not class_name:
                continue
                
            # Replace manager references
            pattern = rf'\b{re.escape(class_name)}\b'
            replacement = class_name
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                updated = True
                self.update_stats['references_by_type']['manager'] += 1
        
        # If content was updated, backup and write the new content
        if updated:
            self.backup_file(file_path)
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Updated references in {rel_path}")
                self.update_stats['cs_files_updated'] += 1
                self.update_stats['total_references_updated'] += 1
            except Exception as e:
                logger.error(f"Error writing updated content to {rel_path}: {e}")
                self.update_stats['failed_updates'] += 1
    
    def _extract_namespace_from_file(self, file_path):
        """Extract the namespace from a C# file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                namespace_match = re.search(r'namespace\s+([a-zA-Z0-9_.]+)', content)
                if namespace_match:
                    return namespace_match.group(1)
        except:
            pass
        return ""
    
    def _update_py_file(self, file_path):
        """Update references in a single Python file."""
        rel_path = os.path.relpath(file_path, self.project_root)
        
        # Skip files in the modules we've merged
        for old_path in self.py_file_map.keys():
            if rel_path == old_path:
                logger.info(f"Skipping merged file: {rel_path}")
                return
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading {rel_path}: {e}")
            self.update_stats['failed_updates'] += 1
            return
        
        original_content = content
        updated = False
        
        # Update import statements for consolidated modules
        for module, new_path in self.py_module_map.items():
            # Skip if the module has no name
            if not module:
                continue
                
            # Extract new module path from destination
            new_module = os.path.splitext(os.path.relpath(new_path, os.path.join(self.project_root, 'backend')))[0]
            new_module = new_module.replace('/', '.')
            
            # Replace import statements
            module_parts = module.split('/')
            module_name = module_parts[-1]
            
            # Handle different import formats
            patterns = [
                rf'from\s+[.\w]+{re.escape(module_name)}\s+import',  # from path.module import
                rf'import\s+[.\w]+{re.escape(module_name)}\b',       # import path.module
                rf'from\s+[.\w]+{re.escape(module_name)}\b',         # from path.module
                rf'\b{re.escape(module_name)}\b'                      # Direct references to module name
            ]
            
            for pattern in patterns:
                new_content = re.sub(pattern, lambda m: m.group().replace(module_name, new_module), content)
                if new_content != content:
                    content = new_content
                    updated = True
                    self.update_stats['references_by_type']['module'] += 1
        
        # Update file path references
        for old_path, new_path in self.py_file_map.items():
            # Extract module names
            old_module = os.path.splitext(old_path)[0].replace('/', '.')
            new_module = os.path.splitext(new_path)[0].replace('/', '.')
            
            # Skip if modules are the same
            if old_module == new_module:
                continue
            
            # Replace import statements
            patterns = [
                rf'from\s+{re.escape(old_module)}\s+import',  # from path.module import
                rf'import\s+{re.escape(old_module)}\b',       # import path.module
                rf'from\s+{re.escape(old_module)}\b',         # from path.module
            ]
            
            for pattern in patterns:
                replacement = lambda m: m.group().replace(old_module, new_module)
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content
                    updated = True
                    self.update_stats['references_by_type']['file'] += 1
        
        # If content was updated, backup and write the new content
        if updated:
            self.backup_file(file_path)
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Updated references in {rel_path}")
                self.update_stats['py_files_updated'] += 1
                self.update_stats['total_references_updated'] += 1
            except Exception as e:
                logger.error(f"Error writing updated content to {rel_path}: {e}")
                self.update_stats['failed_updates'] += 1
    
    def generate_update_report(self):
        """Generate a report of reference update operations."""
        report_path = os.path.join(self.project_root, "scripts", "reference_update_report.json")
        txt_report_path = os.path.join(self.project_root, "scripts", "reference_update_report.txt")
        
        # Save JSON report
        with open(report_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'backup_dir': self.backup_dir,
                'stats': self.update_stats,
                'cs_class_map': self.cs_class_map,
                'cs_file_map': {k: v for k, v in self.cs_file_map.items() if k != v},
                'py_module_map': self.py_module_map,
                'py_file_map': {k: v for k, v in self.py_file_map.items() if k != v},
                'singleton_class_map': self.singleton_class_map,
                'manager_class_map': self.manager_class_map
            }, f, indent=2)
        
        # Generate human-readable report
        with open(txt_report_path, 'w') as f:
            f.write("# Reference Update Report\n\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Backup Directory: {self.backup_dir}\n\n")
            
            f.write("## Statistics\n\n")
            f.write(f"- C# Files Updated: {self.update_stats['cs_files_updated']}\n")
            f.write(f"- Python Files Updated: {self.update_stats['py_files_updated']}\n")
            f.write(f"- Total References Updated: {self.update_stats['total_references_updated']}\n")
            f.write(f"- Failed Updates: {self.update_stats['failed_updates']}\n\n")
            
            f.write("### References by Type\n\n")
            for ref_type, count in self.update_stats['references_by_type'].items():
                f.write(f"- {ref_type.capitalize()}: {count}\n")
            
            f.write("\n## C# Class Mappings\n\n")
            for class_name, new_path in self.cs_class_map.items():
                f.write(f"- Class `{class_name}` → `{new_path}`\n")
            
            f.write("\n## Singleton Mappings\n\n")
            for class_name, new_path in self.singleton_class_map.items():
                f.write(f"- Singleton `{class_name}` → `{new_path}`\n")
            
            f.write("\n## Manager Mappings\n\n")
            for class_name, new_path in self.manager_class_map.items():
                f.write(f"- Manager `{class_name}` → `{new_path}`\n")
            
            f.write("\n## Python Module Mappings\n\n")
            for module, new_path in self.py_module_map.items():
                f.write(f"- Module `{module}` → `{new_path}`\n")
        
        logger.info(f"Generated reference update reports: {report_path} and {txt_report_path}")
        return report_path, txt_report_path

def main():
    parser = argparse.ArgumentParser(description='Update references to consolidated files')
    parser.add_argument('--project-root', type=str, help='Root directory of the project')
    parser.add_argument('--merge-report', type=str, help='Merge report or plan file')
    parser.add_argument('--backup-dir', type=str, help='Custom backup directory (default is timestamped in project_root/backups)')
    parser.add_argument('--cs-only', action='store_true', help='Only update C# references')
    parser.add_argument('--py-only', action='store_true', help='Only update Python references')
    parser.add_argument('--dry-run', action='store_true', help='Dry run, do not modify files')
    
    args = parser.parse_args()
    
    # Use command line args if provided, otherwise use defaults
    project_root = args.project_root or os.getcwd()
    merge_report = args.merge_report or os.path.join(project_root, "scripts", "consolidation", "merge_plan.json")
    
    updater = ReferenceUpdater(
        project_root,
        merge_report,
        backup_dir=args.backup_dir
    )
    
    # Print analysis of what would be updated
    logger.info(f"Found {len(updater.cs_class_map)} C# classes to update references for")
    logger.info(f"Found {len(updater.py_module_map)} Python modules to update references for")
    
    if args.dry_run:
        logger.info("Dry run mode - no files will be modified")
        return
    
    # Update references
    if args.py_only:
        updater.update_py_references()
    elif args.cs_only:
        updater.update_cs_references()
    else:
        updater.update_cs_references()
        updater.update_py_references()
    
    # Generate update report
    updater.generate_update_report()
    
    logger.info(f"Reference update completed. Updated {updater.update_stats['total_references_updated']} references in {updater.update_stats['cs_files_updated'] + updater.update_stats['py_files_updated']} files.")

if __name__ == "__main__":
    main() 