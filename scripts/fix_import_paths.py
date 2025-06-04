#!/usr/bin/env python3
"""
Fix Import Paths Script

This script fixes all remaining import path issues after the JSON reorganization.
It updates hardcoded paths in Python files to use the new data structure.

Usage:
    python scripts/fix_import_paths.py [--dry-run] [--verbose]
"""

import os
import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

class ImportPathFixer:
    """Fixes import paths after JSON reorganization"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        
        # Define path mappings from old to new structure
        self.path_mappings = {
            # Old backend/data paths to new data paths
            r'data/builders': 'data/builders',
            r'data/system/runtime/': 'data/system/runtime/',
            
            # Specific file mappings
            r'data/character_recipes\.json': 'data/system/runtime/character_recipes.json',
            r'data/system/runtime/analytics/': 'data/system/runtime/analytics/',
            r'data/balance_constants\.json': 'data/system/mechanics/balance/balance_constants.json',
            r'data/adjacency\.json': 'data/builders/world_parameters/biomes/adjacency.json',
            r'data/races\.json': 'data/builders/content/races/races.json',
            r'data/equipment/equipment_expanded\.json': 'data/builders/content/equipment/equipment.json',
            r'data/abilities/abilities_fully_finalized_schema\.json': 'data/builders/content/abilities/abilities_legacy.json',
            r'data/spells/spells\.json': 'data/builders/content/spells/spells.json',
            r'data/systems/weather/weather_types\.json': 'data/builders/world_parameters/biomes/weather_types.json',
            r'data/systems/combat/combat_rules\.json': 'data/system/mechanics/combat/combat_rules.json',
            
            # Directory mappings
            r'data/system/runtime/goals/': 'data/system/runtime/goals/',
            r'data/system/runtime/quests/': 'data/system/runtime/quests/',
            r'data/world_log\.json': 'data/system/runtime/world_state/world_log.json',
            r'data/entity_data\.json': 'data/system/runtime/entity_data.json',
            r'data/test-world\.json': 'data/system/runtime/test-world.json',
        }
        
        # File patterns to search
        self.file_patterns = [
            "**/*.py",
            "**/*.js",
            "**/*.ts",
            "**/*.json",
            "**/*.md",
            "**/*.txt"
        ]
        
        # Directories to exclude
        self.exclude_dirs = {
            ".git", "__pycache__", "node_modules", ".venv", "venv",
            "archives", "build", "dist", ".cursor"
        }
    
    def should_process_file(self, file_path: Path) -> bool:
        """Check if a file should be processed"""
        # Skip if in excluded directory
        for part in file_path.parts:
            if part in self.exclude_dirs:
                return False
        
        # Skip binary files
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(100)  # Try to read first 100 chars
            return True
        except (UnicodeDecodeError, PermissionError):
            return False
    
    def fix_file_paths(self, file_path: Path, dry_run: bool = False, verbose: bool = False) -> Tuple[bool, List[str]]:
        """Fix paths in a single file"""
        changes = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply each path mapping
            for old_pattern, new_path in self.path_mappings.items():
                # Use regex to find and replace patterns
                matches = re.finditer(old_pattern, content)
                for match in matches:
                    old_text = match.group(0)
                    changes.append(f"  {old_text} → {new_path}")
                
                content = re.sub(old_pattern, new_path, content)
            
            # Only write if changes were made
            if content != original_content and not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                if verbose:
                    print(f"Updated: {file_path}")
                    for change in changes:
                        print(change)
                
                return True, changes
            elif content != original_content:
                if verbose:
                    print(f"Would update: {file_path}")
                    for change in changes:
                        print(change)
                return True, changes
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False, []
        
        return False, []
    
    def fix_all_paths(self, dry_run: bool = False, verbose: bool = False) -> Dict[str, int]:
        """Fix paths in all relevant files"""
        stats = {
            "files_processed": 0,
            "files_changed": 0,
            "total_changes": 0
        }
        
        print(f"{'DRY RUN: ' if dry_run else ''}Fixing import paths...")
        
        # Find all files to process
        files_to_process = []
        for pattern in self.file_patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file() and self.should_process_file(file_path):
                    files_to_process.append(file_path)
        
        print(f"Found {len(files_to_process)} files to process")
        
        # Process each file
        for file_path in files_to_process:
            stats["files_processed"] += 1
            changed, changes = self.fix_file_paths(file_path, dry_run, verbose)
            
            if changed:
                stats["files_changed"] += 1
                stats["total_changes"] += len(changes)
        
        return stats
    
    def create_path_mapping_report(self) -> str:
        """Create a report of all path mappings"""
        report = "# Path Mapping Report\n\n"
        report += "The following path mappings are applied:\n\n"
        
        for old_pattern, new_path in self.path_mappings.items():
            report += f"- `{old_pattern}` → `{new_path}`\n"
        
        return report

def main():
    parser = argparse.ArgumentParser(description="Fix import paths after JSON reorganization")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without making changes")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--report", action="store_true", help="Generate path mapping report")
    
    args = parser.parse_args()
    
    fixer = ImportPathFixer()
    
    if args.report:
        report = fixer.create_path_mapping_report()
        with open("data/PATH_MAPPING_REPORT.md", "w") as f:
            f.write(report)
        print("Path mapping report saved to data/PATH_MAPPING_REPORT.md")
        return
    
    stats = fixer.fix_all_paths(args.dry_run, args.verbose)
    
    print(f"\n{'DRY RUN ' if args.dry_run else ''}Results:")
    print(f"Files processed: {stats['files_processed']}")
    print(f"Files changed: {stats['files_changed']}")
    print(f"Total changes: {stats['total_changes']}")
    
    if args.dry_run:
        print("\nRun without --dry-run to apply changes")

if __name__ == "__main__":
    main() 