#!/usr/bin/env python3
"""
Task 58: Fix Critical Import Issues
Focus on the most critical import issues that prevent the system from working.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set

class CriticalImportFixer:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.systems_dir = self.root_dir / "systems"
        
        # Track what we've processed
        self.processed_files: Set[str] = set()
        
        # Critical fixes for imports that point to non-existent modules
        self.critical_fixes = {
            # Fix imports to actual existing modules
            "from backend.infrastructure.shared.models import": "from backend.infrastructure.shared.models.base import",
            "from backend.infrastructure.shared.services import": "from backend.infrastructure.shared.services.base import",
            "from backend.infrastructure.shared.repositories import": "from backend.infrastructure.shared.repositories.base import",
            
            # Fix module references that don't exist as separate modules
            "from backend.infrastructure.shared.models.": "from backend.infrastructure.shared.models.",
            "from backend.infrastructure.services.": "from backend.systems.",
            "from backend.infrastructure.repositories.": "from backend.infrastructure.shared.repositories.",
            
            # Fix event system imports
            "# REMOVED: deprecated event_base import
            "from backend.systems.event_dispatcher import": "from backend.infrastructure.events.event_dispatcher import",
            
            # Fix specific modules that were moved
            "from backend.systems.economy_manager import": "from backend.systems.economy.managers.economy_manager import",
            "from backend.systems.routers.shop_router import": "from backend.systems.economy.routers.shop_router import",
            "from backend.systems.routers.economy_router import": "from backend.systems.economy.routers.economy_router import",
            
            # Fix system-specific imports
            "from backend.systems.character_service.services import": "from backend.systems.character.services.character_service import",
            "from backend.systems.npc_service.services import": "from backend.systems.npc.services.npc_service import",
            "from backend.infrastructure.analytics_service.services import": "from backend.infrastructure.analytics.services.analytics_service import",
            
            # Fix model imports
            "from backend.systems.relationship.models import": "from backend.systems.character.models.relationship import",
            "from backend.systems.relationship_events.models import": "from backend.systems.character.models.relationship_events import",
            "from backend.systems.mood.models import": "from backend.systems.character.models.mood import",
            "from backend.systems.goal.models import": "from backend.systems.character.models.goal import",
            "from backend.systems.user_models.models import": "from backend.infrastructure.auth_user.models.user_models import",
            "from backend.systems.faction.models import": "from backend.systems.faction.models.faction import",
            "from backend.systems.faction_goal.models import": "from backend.systems.faction.models.faction_goal import",
            "from backend.systems.rumor.models import": "from backend.systems.rumor.models.rumor import",
            "from backend.systems.time_model.models import": "from backend.systems.time.models.time_model import",
            "from backend.systems.calendar_model.models import": "from backend.systems.time.models.calendar_model import",
            "from backend.systems.weather_model.models import": "from backend.systems.time.models.weather_model import",
            "from backend.systems.event_model.models import": "from backend.systems.time.models.event_model import",
            "from backend.systems.item.models import": "from backend.systems.inventory.models.item import",
            "from backend.systems.inventory_item.models import": "from backend.systems.inventory.models.inventory_item import",
            "from backend.systems.item_category.models import": "from backend.systems.inventory.models.item_category import",
            "from backend.systems.recipe.models import": "from backend.systems.crafting.models.recipe import",
            "from backend.systems.ingredient.models import": "from backend.systems.crafting.models.ingredient import",
            "from backend.systems.result.models import": "from backend.systems.crafting.models.result import",
            "from backend.systems.station.models import": "from backend.systems.crafting.models.station import",
            
            # Fix service imports
            "from backend.systems.recipe_service.services import": "from backend.systems.crafting.services.recipe_service import",
            "from backend.systems.station_service.services import": "from backend.systems.crafting.services.station_service import",
            "from backend.systems.crafting_knowledge_service.services import": "from backend.systems.crafting.services.crafting_knowledge_service import",
            "from backend.systems.crafting_experience_service.services import": "from backend.systems.crafting.services.crafting_experience_service import",
            "from backend.systems.crafting_achievement_service.services import": "from backend.systems.crafting.services.crafting_achievement_service import",
            "from backend.systems.crafting_service.services import": "from backend.systems.crafting.services.crafting_service import",
            "from backend.systems.time_manager.services import": "from backend.systems.time.services.time_manager import",
            "from backend.systems.event_scheduler.services import": "from backend.systems.time.services.event_scheduler import",
            "from backend.systems.calendar_service.services import": "from backend.systems.time.services.calendar_service import",
            "from backend.systems.weather_service.services import": "from backend.systems.time.services.weather_service import",
            "from backend.infrastructure.data_service.services import": "from backend.infrastructure.data.services.data_service import",
            "from backend.systems.party_service.services import": "from backend.systems.character.services.party_service import",
            "from backend.systems.relationship_service.services import": "from backend.systems.character.services.relationship_service import",
            "from backend.systems.auth_service.services import": "from backend.infrastructure.auth_user.services.auth_service import",
            "from backend.systems.validation_service.services import": "from backend.infrastructure.auth_user.services.validation_service import",
            "from backend.systems.auth_relationships.services import": "from backend.infrastructure.auth_user.services.auth_relationship_service import",
            
            # Fix data/database imports
            "from backend.infrastructure.data.database import": "from backend.infrastructure.shared.database import",
            "from backend.systems.base.models import": "from backend.infrastructure.shared.models.base import",
            
            # Fix arc imports
            "from backend.systems.arc.schemas import": "from backend.systems.arc.schemas.arc_schemas import",
            "from backend.systems.arc.events import": "from backend.systems.arc.events.arc_events import",
            "from backend.systems.arc_manager.services import": "from backend.systems.arc.services.arc_manager import",
            "from backend.systems.arc_generator.services import": "from backend.systems.arc.services.arc_generator import",
            "from backend.systems.quest_integration.services import": "from backend.systems.arc.services.quest_integration import",
            "from backend.systems.progression_tracker.services import": "from backend.systems.arc.services.progression_tracker import",
            
            # Fix faction services
            "from backend.systems.consolidated_faction_service.services import": "from backend.systems.faction.services.consolidated_faction_service import",
            "from backend.systems.consolidated_relationship_service.services import": "from backend.systems.faction.services.consolidated_relationship_service import",
            "from backend.systems.consolidated_membership_service.services import": "from backend.systems.faction.services.consolidated_membership_service import",
        }

    def find_python_files(self) -> List[Path]:
        """Find all Python files in systems directory."""
        files = []
        if self.systems_dir.exists():
            for file_path in self.systems_dir.rglob("*.py"):
                # Skip temporary and script files
                if not any(skip in str(file_path) for skip in ['task', 'fix_', 'debug', '__pycache__']):
                    files.append(file_path)
        return files

    def fix_file(self, file_path: Path) -> bool:
        """Fix critical imports in a single file."""
        if str(file_path) in self.processed_files:
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return False
        
        original_content = content
        changes = []
        
        # Apply critical fixes
        for old_import, new_import in self.critical_fixes.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
                if content != original_content:
                    changes.append(f"  {old_import} -> {new_import}")
                    original_content = content
        
        if changes:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"\n✅ Fixed critical imports in {file_path}:")
                for change in changes:
                    print(change)
                
                self.processed_files.add(str(file_path))
                return True
            except Exception as e:
                print(f"Error writing {file_path}: {e}")
                return False
        
        return False

    def run(self) -> Dict[str, any]:
        """Run the critical import fixing process."""
        print("🔧 Task 58: Fixing Critical Import Issues...")
        print("=" * 80)
        
        files = self.find_python_files()
        print(f"Found {len(files)} Python files to process")
        
        fixed_files = []
        error_files = []
        
        for file_path in files:
            try:
                if self.fix_file(file_path):
                    fixed_files.append(str(file_path))
            except Exception as e:
                error_files.append((str(file_path), str(e)))
                print(f"❌ Error processing {file_path}: {e}")
        
        print(f"\n📊 Summary:")
        print(f"   Files processed: {len(files)}")
        print(f"   Files modified: {len(fixed_files)}")
        print(f"   Files with errors: {len(error_files)}")
        
        return {
            "files_processed": len(files),
            "files_modified": len(fixed_files),
            "modified_files": fixed_files,
            "error_files": error_files
        }

def main():
    """Main execution function."""
    
    if not os.path.exists("systems"):
        print("❌ Error: systems directory not found. Run from backend directory.")
        sys.exit(1)
    
    fixer = CriticalImportFixer()
    results = fixer.run()
    
    print("\n" + "=" * 80)
    print("✅ Task 58: Critical Import Fixing Complete!")
    print(f"Modified {results['files_modified']} files")
    
    if results['error_files']:
        print(f"⚠️  {len(results['error_files'])} files had errors - manual review needed")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 