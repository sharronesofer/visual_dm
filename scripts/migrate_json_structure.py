#!/usr/bin/env python3
"""
JSON Structure Migration Script

This script helps migrate from the old JSON organization to the new two-tier 
builder/system structure. It moves files to appropriate locations and updates
references to use the new terminology (feats -> abilities, etc.).

Usage:
    python scripts/migrate_json_structure.py [--dry-run] [--force]
"""

import os
import json
import shutil
import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

class JSONStructureMigrator:
    """Handles migration from old to new JSON structure"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.data_root = self.project_root / "data"
        
        # Define migration mappings
        self.builder_mappings = {
            # Content files (builder-accessible)
            "data/builders/content/races/races.json": "data/builders/content/races/races.json",
            "data/builders/content/abilities/abilities.json": "data/builders/content/abilities/abilities.json",
            "data/builders/content/abilities/abilities_legacy.json": "data/builders/content/abilities/abilities_legacy.json",
            "data/builders/content/equipment/equipment.json": "data/builders/content/equipment/equipment.json",
            "data/items/equipment.json": "data/builders/content/equipment/items.json",
            "data/builders/content/spells/spells.json": "data/builders/content/spells/spells.json",
            "data/spells/more_spells.json": "data/builders/content/spells/extended_spells.json",
            "data/systems/faction/faction_types.json": "data/builders/content/factions/faction_types.json",
            "data/systems/religion/religion_templates.json": "data/builders/content/factions/religion_templates.json",
            
            # World parameters
            "data/builders/world_parameters/biomes/weather_types.json": "data/builders/world_parameters/biomes/weather_types.json",
            "data/biomes": "data/builders/world_parameters/biomes/biome_data",
            
            # Schemas
            "data/modding/schemas": "data/builders/schemas",
        }
        
        self.system_mappings = {
            # System mechanics files
            "data/system/mechanics/combat/combat_rules.json": "data/system/mechanics/combat/combat_rules.json",
            "data/systems/time": "data/system/mechanics/progression",
            "data/systems/economy": "data/system/mechanics/economy",
            "data/systems/events": "data/system/runtime/ai_behavior",
            
            # Runtime data
            "data/world/world_state": "data/system/runtime/world_state",
            "data/systems/memory": "data/system/runtime/memory",
            
            # Rules and validation
            "data/rules_json": "data/system/mechanics",
        }
        
    def analyze_structure(self) -> Dict[str, List[Path]]:
        """Analyze current structure and categorize files"""
        analysis = {
            "builder_content": [],
            "system_mechanics": [],
            "unknown": [],
            "already_migrated": []
        }
        
        for json_file in self.data_root.rglob("*.json"):
            relative_path = json_file.relative_to(self.data_root)
            
            # Check if already in new structure
            if str(relative_path).startswith(("builders/", "system/")):
                analysis["already_migrated"].append(json_file)
                continue
                
            # Categorize based on content and location
            if self._is_builder_content(json_file):
                analysis["builder_content"].append(json_file)
            elif self._is_system_content(json_file):
                analysis["system_mechanics"].append(json_file)
            else:
                analysis["unknown"].append(json_file)
                
        return analysis
    
    def _is_builder_content(self, file_path: Path) -> bool:
        """Determine if a file should be builder-accessible"""
        content_indicators = [
            "races", "abilities", "feats", "equipment", "items", 
            "spells", "faction", "religion", "weather", "biome"
        ]
        
        path_str = str(file_path).lower()
        return any(indicator in path_str for indicator in content_indicators)
    
    def _is_system_content(self, file_path: Path) -> bool:
        """Determine if a file should be system-internal"""
        system_indicators = [
            "combat", "mechanics", "rules", "calculations", 
            "world_state", "memory", "ai_behavior", "performance"
        ]
        
        path_str = str(file_path).lower()
        return any(indicator in path_str for indicator in system_indicators)
    
    def migrate_file(self, source: Path, destination: Path, dry_run: bool = False) -> bool:
        """Migrate a single file with content updates"""
        try:
            if not dry_run:
                # Create destination directory
                destination.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(source, destination)
                
                # Update content if JSON
                if destination.suffix.lower() == '.json':
                    self._update_json_content(destination)
                    
            print(f"{'[DRY RUN] ' if dry_run else ''}Migrated: {source} -> {destination}")
            return True
            
        except Exception as e:
            print(f"Error migrating {source}: {e}")
            return False
    
    def _update_json_content(self, file_path: Path):
        """Update JSON content for terminology changes"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update terminology
            content = re.sub(r'\b[Ff]eats?\b', 'abilities', content)
            content = re.sub(r'\b[Mm]odders?\b', 'builders', content)
            content = re.sub(r'\b[Mm]odding\b', 'world_building', content)
            
            # Update file paths in JSON
            content = re.sub(r'data/feats/', 'data/builders/content/abilities/', content)
            content = re.sub(r'data/equipment/', 'data/builders/content/equipment/', content)
            content = re.sub(r'data/spells/', 'data/builders/content/spells/', content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            print(f"Warning: Could not update content of {file_path}: {e}")
    
    def run_migration(self, dry_run: bool = False, force: bool = False) -> Dict[str, int]:
        """Run the complete migration process"""
        stats = {"success": 0, "failed": 0, "skipped": 0}
        
        print("Analyzing current JSON structure...")
        analysis = self.analyze_structure()
        
        print(f"\nFound:")
        print(f"  Builder content files: {len(analysis['builder_content'])}")
        print(f"  System mechanics files: {len(analysis['system_mechanics'])}")
        print(f"  Already migrated: {len(analysis['already_migrated'])}")
        print(f"  Unknown classification: {len(analysis['unknown'])}")
        
        if not force and not dry_run:
            response = input("\nProceed with migration? (y/N): ")
            if response.lower() != 'y':
                print("Migration cancelled.")
                return stats
        
        print(f"\n{'=' * 50}")
        print("MIGRATING BUILDER CONTENT")
        print("=" * 50)
        
        # Migrate builder content
        for file_path in analysis['builder_content']:
            dest_path = self._determine_builder_destination(file_path)
            if self.migrate_file(file_path, dest_path, dry_run):
                stats["success"] += 1
            else:
                stats["failed"] += 1
        
        print(f"\n{'=' * 50}")
        print("MIGRATING SYSTEM FILES")
        print("=" * 50)
        
        # Migrate system files  
        for file_path in analysis['system_mechanics']:
            dest_path = self._determine_system_destination(file_path)
            if self.migrate_file(file_path, dest_path, dry_run):
                stats["success"] += 1
            else:
                stats["failed"] += 1
        
        if analysis['unknown']:
            print(f"\n{'=' * 50}")
            print("UNKNOWN FILES (manual review needed)")
            print("=" * 50)
            for file_path in analysis['unknown']:
                print(f"  {file_path}")
                stats["skipped"] += 1
        
        return stats
    
    def _determine_builder_destination(self, file_path: Path) -> Path:
        """Determine destination for builder-accessible content"""
        relative_path = file_path.relative_to(self.data_root)
        path_str = str(relative_path).lower()
        
        if "race" in path_str:
            return self.data_root / "builders/content/races" / file_path.name
        elif any(x in path_str for x in ["ability", "feat"]):
            return self.data_root / "builders/content/abilities" / file_path.name
        elif any(x in path_str for x in ["equipment", "item"]):
            return self.data_root / "builders/content/equipment" / file_path.name
        elif "spell" in path_str:
            return self.data_root / "builders/content/spells" / file_path.name
        elif any(x in path_str for x in ["faction", "religion"]):
            return self.data_root / "builders/content/factions" / file_path.name
        elif any(x in path_str for x in ["weather", "biome", "climate"]):
            return self.data_root / "builders/world_parameters/biomes" / file_path.name
        elif "schema" in path_str:
            return self.data_root / "builders/schemas" / file_path.name
        else:
            return self.data_root / "builders/content/misc" / file_path.name
    
    def _determine_system_destination(self, file_path: Path) -> Path:
        """Determine destination for system-internal files"""
        relative_path = file_path.relative_to(self.data_root)
        path_str = str(relative_path).lower()
        
        if "combat" in path_str:
            return self.data_root / "system/mechanics/combat" / file_path.name
        elif any(x in path_str for x in ["world_state", "state"]):
            return self.data_root / "system/runtime/world_state" / file_path.name
        elif "memory" in path_str:
            return self.data_root / "system/runtime/memory" / file_path.name
        elif any(x in path_str for x in ["ai", "behavior", "dialogue"]):
            return self.data_root / "system/runtime/ai_behavior" / file_path.name
        elif any(x in path_str for x in ["economy", "trade", "price"]):
            return self.data_root / "system/mechanics/economy" / file_path.name
        elif any(x in path_str for x in ["progression", "level", "experience"]):
            return self.data_root / "system/mechanics/progression" / file_path.name
        elif any(x in path_str for x in ["magic", "spell"]) and "rule" in path_str:
            return self.data_root / "system/mechanics/magic" / file_path.name
        elif any(x in path_str for x in ["performance", "cache"]):
            return self.data_root / "system/runtime/performance" / file_path.name
        else:
            return self.data_root / "system/mechanics/misc" / file_path.name

def main():
    parser = argparse.ArgumentParser(description="Migrate JSON files to new structure")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be done without making changes")
    parser.add_argument("--force", action="store_true",
                       help="Skip confirmation prompts")
    parser.add_argument("--project-root", default=".",
                       help="Path to project root directory")
    
    args = parser.parse_args()
    
    migrator = JSONStructureMigrator(args.project_root)
    stats = migrator.run_migration(dry_run=args.dry_run, force=args.force)
    
    print(f"\n{'=' * 50}")
    print("MIGRATION SUMMARY")
    print("=" * 50)
    print(f"Successfully migrated: {stats['success']}")
    print(f"Failed migrations: {stats['failed']}")
    print(f"Files needing manual review: {stats['skipped']}")
    
    if args.dry_run:
        print("\nThis was a dry run. Use --force to execute the migration.")

if __name__ == "__main__":
    main() 