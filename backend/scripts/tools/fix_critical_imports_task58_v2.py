#!/usr/bin/env python3
"""
Task 58: Critical Import Fixes (Phase 2)
Fix the most critical import issues found during validation.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set

class CriticalImportFixer:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.systems_dir = self.root_dir / "systems"
        self.tests_dir = self.root_dir / "tests"
        
        # Track what we've processed
        self.processed_files: Set[str] = set()
        
        # Critical import fixes - redirect to modules that actually exist
        self.critical_fixes = {
            # Database imports - redirect to correct locations
            "from backend.systems.shared.database import Base": "from backend.systems.shared.database.base import Base",
            "from backend.systems.shared.database import db": "from backend.systems.shared.database.database import db",
            "from backend.systems.shared.database import get_db_session": "from backend.systems.shared.database.session import get_db_session",
            "from backend.systems.shared.database import get_test_db_session": "from backend.systems.shared.database.session import get_test_db_session",
            
            # Data database imports - these need to be redirected 
            "from backend.systems.data.database import Base": "from backend.systems.shared.database.base import Base",
            "from backend.systems.data.database import db": "from backend.systems.shared.database.database import db",
            "from backend.systems.data.database import get_db_session": "from backend.systems.shared.database.session import get_db_session",
            
            # Economy manager - check if it exists, otherwise redirect
            "from backend.systems.economy.services.economy_manager import EconomyManager": "from backend.systems.economy.economy_manager import EconomyManager",
            
            # Router imports that don't exist - redirect to actual locations
            "from backend.systems.shop_router.routers import": "from backend.systems.economy.routers.shop_router import",
            "from backend.systems.economy_router.routers import": "from backend.systems.economy.routers.economy_router import",
            "from backend.systems.combat_actions.routers import": "from backend.systems.combat.routers.combat_actions import",
            "from backend.systems.relationship_router.routers import": "from backend.systems.character.routers.relationship_router import",
            "from backend.systems.faction_router.routers import": "from backend.systems.faction.routers.faction_router import",
            "from backend.systems.npc_router.routers import": "from backend.systems.npc.routers.npc_router import",
            
            # Shared models imports
            "from backend.systems.shared.models import": "from backend.systems.shared.models.base import",
            "from backend.systems.shared.enums import": "from backend.systems.shared.models.enums import",
            "from backend.systems.shared.config import": "from backend.systems.shared.utils.config import",
            
            # Event imports that need to be fixed
            "from backend.systems.events import *": "from backend.systems.events import EventDispatcher, EventBase",
            
            # Analytics imports
            "from backend.systems.analytics.services.analytics_service import": "from backend.systems.analytics.services.core.analytics_service import",
            
            # Tension war specific imports
            "from backend.systems.tension_war.services.tension_manager import": "from backend.systems.tension_war.managers.tension_manager import",
            "from backend.systems.tension_war.services.war_manager import": "from backend.systems.tension_war.managers.war_manager import",
            "from backend.systems.tension_war.services.peace_manager import": "from backend.systems.tension_war.managers.peace_manager import",
            "from backend.systems.tension_war.services.alliance_manager import": "from backend.systems.tension_war.managers.alliance_manager import",
            "from backend.systems.tension_war.services.proxy_war_manager import": "from backend.systems.tension_war.managers.proxy_war_manager import",
            "from backend.systems.tension_war.services.diplomatic_manager import": "from backend.systems.tension_war.managers.diplomatic_manager import",
        }

    def find_python_files(self) -> List[Path]:
        """Find all Python files in systems and tests directories."""
        files = []
        
        # Find files in systems directory
        if self.systems_dir.exists():
            for file_path in self.systems_dir.rglob("*.py"):
                if "__pycache__" not in str(file_path):
                    files.append(file_path)
        
        # Find files in tests directory  
        if self.tests_dir.exists():
            for file_path in self.tests_dir.rglob("*.py"):
                if "__pycache__" not in str(file_path):
                    files.append(file_path)
                    
        return files

    def fix_imports_in_content(self, content: str) -> Tuple[str, List[str]]:
        """Fix critical imports in file content."""
        changes = []
        lines = content.split('\n')
        modified_lines = []
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Apply critical fixes
            for old_import, new_import in self.critical_fixes.items():
                if old_import in line:
                    new_line = line.replace(old_import, new_import)
                    if new_line != line:
                        changes.append(f"Line {i+1}: '{line.strip()}' -> '{new_line.strip()}'")
                        line = new_line
                        break
            
            modified_lines.append(line)
        
        return '\n'.join(modified_lines), changes

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
        
        modified_content, changes = self.fix_imports_in_content(content)
        
        if changes:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                print(f"\n✅ Fixed critical imports in {file_path}:")
                for change in changes[:3]:  # Limit output
                    print(f"   {change}")
                if len(changes) > 3:
                    print(f"   ... and {len(changes) - 3} more changes")
                
                self.processed_files.add(str(file_path))
                return True
            except Exception as e:
                print(f"Error writing {file_path}: {e}")
                return False
        
        return False

    def run(self) -> Dict[str, any]:
        """Run the critical import fixing process."""
        print("🔧 Task 58: Critical Import Fixes (Phase 2)...")
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
            "files_with_errors": len(error_files),
            "modified_files": fixed_files,
            "error_files": error_files,
        }


def main():
    """Main execution function."""
    
    if not os.path.exists("systems"):
        print("❌ Error: systems directory not found. Run from backend directory.")
        sys.exit(1)
    
    fixer = CriticalImportFixer(".")
    results = fixer.run()
    
    print("\n" + "=" * 80)
    print("✅ Task 58: Critical Import Fixes Complete!")
    print(f"Modified {results['files_modified']} files")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 