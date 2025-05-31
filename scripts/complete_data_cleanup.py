#!/usr/bin/env python3
"""
Complete Data Cleanup Script

This script completes the data directory reorganization by moving remaining
legacy directories to their proper locations in the new builder/system structure.

Usage:
    python scripts/complete_data_cleanup.py [--dry-run] [--verbose]
"""

import os
import shutil
import argparse
from pathlib import Path
from typing import Dict, List

class DataCleanupManager:
    """Manages the final cleanup of legacy data directories"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.data_root = self.project_root / "data"
        
        # Define where legacy directories should be moved
        self.directory_mappings = {
            # Builder content (customizable by builders)
            "abilities": "builders/content/abilities/legacy",
            "feats": "builders/content/abilities/legacy_feats", 
            "equipment": "builders/content/equipment/legacy",
            "weapons": "builders/content/equipment/weapons",
            "armor": "builders/content/equipment/armor",
            "items": "builders/content/equipment/items",
            "spells": "builders/content/spells/legacy",
            "monsters": "builders/content/creatures",
            "entities": "builders/content/races/entities",
            
            # World generation parameters
            "biomes": "builders/world_parameters/biomes/legacy",
            "world": "builders/world_parameters/generation",
            "worlds": "builders/world_parameters/seeds",
            "regions": "builders/world_parameters/regions",
            "narrative": "builders/world_parameters/narrative",
            
            # System mechanics (internal)
            "combat": "system/mechanics/combat/legacy",
            "crafting": "system/mechanics/crafting",
            "leveling": "system/mechanics/progression",
            "skills": "system/mechanics/progression/skills",
            "rules_json": "system/mechanics/rules",
            
            # System runtime (generated/temporary)
            "world_state": "system/runtime/world_state/legacy",
            "gameplay": "system/runtime/gameplay",
            "moods": "system/runtime/ai_behavior",
            "rumors": "system/runtime/narrative/rumors",
            
            # System validation/schemas
            "modding": "system/validation/legacy_modding",
            
            # Archive/backup
            "_versions": "system/archive/versions",
            "backups": "system/archive/backups",
            "odds_n_ends": "system/archive/misc",
            "ui": "system/archive/ui",
            "religion": "system/archive/religion"
        }
    
    def create_target_directories(self, dry_run: bool = False) -> None:
        """Create all target directories"""
        for target_path in self.directory_mappings.values():
            full_target = self.data_root / target_path
            if not dry_run:
                full_target.mkdir(parents=True, exist_ok=True)
            print(f"{'Would create' if dry_run else 'Created'}: {full_target}")
    
    def move_directory(self, source: str, target: str, dry_run: bool = False, verbose: bool = False) -> bool:
        """Move a directory from source to target location"""
        source_path = self.data_root / source
        target_path = self.data_root / target
        
        if not source_path.exists():
            if verbose:
                print(f"Source does not exist: {source_path}")
            return False
        
        if target_path.exists():
            if verbose:
                print(f"Target already exists: {target_path}")
            return False
        
        try:
            if not dry_run:
                # Ensure parent directory exists
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source_path), str(target_path))
            
            print(f"{'Would move' if dry_run else 'Moved'}: {source_path} → {target_path}")
            return True
            
        except Exception as e:
            print(f"Error moving {source_path} to {target_path}: {e}")
            return False
    
    def cleanup_all_directories(self, dry_run: bool = False, verbose: bool = False) -> Dict[str, int]:
        """Move all legacy directories to their new locations"""
        stats = {
            "directories_processed": 0,
            "directories_moved": 0,
            "errors": 0
        }
        
        print(f"{'DRY RUN: ' if dry_run else ''}Cleaning up legacy data directories...")
        
        # Create target directories first
        self.create_target_directories(dry_run)
        
        # Move each directory
        for source, target in self.directory_mappings.items():
            stats["directories_processed"] += 1
            
            if self.move_directory(source, target, dry_run, verbose):
                stats["directories_moved"] += 1
            else:
                stats["errors"] += 1
        
        return stats
    
    def create_cleanup_report(self) -> str:
        """Create a report of the cleanup operations"""
        report = "# Data Directory Cleanup Report\n\n"
        report += "The following legacy directories were moved to new locations:\n\n"
        
        for source, target in self.directory_mappings.items():
            report += f"- `data/{source}/` → `data/{target}/`\n"
        
        report += "\n## Directory Categories\n\n"
        report += "### Builder Content (Customizable)\n"
        report += "- abilities, feats, equipment, weapons, armor, items\n"
        report += "- spells, monsters, entities\n\n"
        
        report += "### World Generation Parameters\n"
        report += "- biomes, world, worlds, regions, narrative\n\n"
        
        report += "### System Mechanics (Internal)\n"
        report += "- combat, crafting, leveling, skills, rules_json\n\n"
        
        report += "### System Runtime (Generated)\n"
        report += "- world_state, gameplay, moods, rumors\n\n"
        
        report += "### Archive/Legacy\n"
        report += "- _versions, backups, odds_n_ends, ui, religion, modding\n"
        
        return report

def main():
    parser = argparse.ArgumentParser(description="Complete data directory cleanup")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be moved without making changes")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--report", action="store_true", help="Generate cleanup report")
    
    args = parser.parse_args()
    
    cleanup_manager = DataCleanupManager()
    
    if args.report:
        report = cleanup_manager.create_cleanup_report()
        with open("data/CLEANUP_REPORT.md", "w") as f:
            f.write(report)
        print("Cleanup report saved to data/CLEANUP_REPORT.md")
        return
    
    stats = cleanup_manager.cleanup_all_directories(args.dry_run, args.verbose)
    
    print(f"\n{'DRY RUN ' if args.dry_run else ''}Results:")
    print(f"Directories processed: {stats['directories_processed']}")
    print(f"Directories moved: {stats['directories_moved']}")
    print(f"Errors: {stats['errors']}")
    
    if args.dry_run:
        print("\nRun without --dry-run to apply changes")

if __name__ == "__main__":
    main() 