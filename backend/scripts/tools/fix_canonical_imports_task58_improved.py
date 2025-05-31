#!/usr/bin/env python3
"""
Task 58: Update Import Paths to Absolute References (Improved)
Convert all relative imports to absolute import paths following canonical structure.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set

class ImprovedCanonicalImportFixer:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.systems_dir = self.root_dir / "systems"
        self.tests_dir = self.root_dir / "tests"
        
        # Track what we've processed to avoid duplicates
        self.processed_files: Set[str] = set()
        
        # Comprehensive import mappings for reorganized modules
        self.import_mappings = {
            # Fix app imports - these should be backend.systems
            r"from backend.systems.region.models import",
            r"from app\.models\.([^.]+) import": r"from backend.systems.\1.models import",
            r"from app\.([^.]+) import": r"from backend.systems.\1 import",
            
            # Fix utils imports - should point to shared.utils or system-specific utils
            r"from backend.infrastructure.shared.utils.cache import async_cached",
            r"from backend.infrastructure.shared.utils.\1 import",
            
            # Direct system imports without backend.systems prefix
            r"from systems\.([^.]+) import": r"from backend.systems.\1 import",
            
            # Fix backend.systems imports that are missing proper module structure
            r"from backend.infrastructure.shared.models import", 
            r"from backend.infrastructure.shared.enums import",
            r"from backend.infrastructure.shared.config import",
            
            # Fix service imports that are in wrong locations
            r"from backend\.systems\.services\.([^.]+) import": r"from backend.systems.\1.services import",
            r"from backend\.systems\.models\.([^.]+) import": r"from backend.systems.\1.models import",
            
            # Fix specific manager imports
            r"from backend.systems.tension_war.services.tension_manager import",
            r"from backend.systems.tension_war.services.war_manager import",
            r"from backend.systems.tension_war.services.peace_manager import",
            r"from backend.systems.tension_war.services.alliance_manager import",
            r"from backend.systems.tension_war.services.proxy_war_manager import",
            r"from backend.systems.tension_war.services.diplomatic_manager import",
            r"from backend.systems.economy.services.economy_manager import",
            
            # Fix utils imports that need proper paths
            r"from backend.systems.tension_war.utils.tension_utils import",
            r"from backend.systems.tension_war.utils.war_utils import",
            r"from backend.systems.tension_war.utils.peace_utils import",
            r"from backend.systems.tension_war.utils.alliance_utils import",
            r"from backend.systems.tension_war.utils.diplomatic_utils import",
            
            # Fix equipment utils imports
            r"from backend.systems.inventory.utils import",
            r"from backend.systems.equipment.utils.identify_item_utils import",
            r"from backend.systems.equipment.utils.set_bonus_utils import",
            r"from backend.systems.equipment.utils.durability_utils import",
            
            # Fix arc imports
            r"from backend.systems.arc.services.arc_generator import",
            r"from backend.systems.arc.events import",
            r"from backend.systems.arc.schemas import",
            
            # Fix analytics imports
            r"from backend.infrastructure.analytics.services.analytics_service import",
            
            # Fix specific model imports
            r"from backend.systems.npc.models.npc_events import",
            
            # Fix shared imports
            r"from backend.infrastructure.shared.utils.base.base_manager import",
            
            # Fix database imports
            r"from backend.infrastructure.data.database import",
            r"from backend.infrastructure.shared.database import",
            
            # Fix narrative imports
            r"from backend.systems.motif.utils import",
            
            # Fix router imports
            r"from backend\.systems\.routers\.([^.]+) import": r"from backend.systems.\1.routers import",
            
            # Common reorganized imports
            r"from backend.systems.tension_war.models.alliance import",
            r"from backend.systems.tension_war.models.war import",
            r"from backend.systems.tension_war.models.peace import", 
            r"from backend.systems.tension_war.models.alliance import",
            r"from backend.systems.tension_war.models.impact import",
            
            # Fix incorrect event import backend.infrastructure.events import",
        }
        
        # Files to skip - be more conservative and only skip clear temporary files
        self.skip_patterns = {
            r".*__pycache__.*",
            r".*\.pyc$",
            r".*\.backup$",
            r".*\.bak$",
            r".*\.tmp$",
        }

    def should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped based on skip patterns."""
        file_str = str(file_path)
        return any(re.match(pattern, file_str) for pattern in self.skip_patterns)

    def find_python_files(self) -> List[Path]:
        """Find all Python files in systems and tests directories."""
        files = []
        
        # Find files in systems directory
        if self.systems_dir.exists():
            for file_path in self.systems_dir.rglob("*.py"):
                if not self.should_skip_file(file_path):
                    files.append(file_path)
        
        # Find files in tests directory
        if self.tests_dir.exists():
            for file_path in self.tests_dir.rglob("*.py"):
                if not self.should_skip_file(file_path):
                    files.append(file_path)
                    
        return files

    def fix_imports_in_content(self, content: str) -> Tuple[str, List[str]]:
        """Fix imports in file content and return modified content plus changes made."""
        original_content = content
        changes = []
        
        lines = content.split('\n')
        modified_lines = []
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Apply all import mappings
            for pattern, replacement in self.import_mappings.items():
                if re.search(pattern, line):
                    new_line = re.sub(pattern, replacement, line)
                    if new_line != line:
                        changes.append(f"Line {i+1}: '{line.strip()}' -> '{new_line.strip()}'")
                        line = new_line
                        break  # Only apply one fix per line to avoid conflicts
            
            # Additional specific fixes
            
            # Fix relative imports (from backend.systems import, from backend.systems import)
            if re.match(r'^\s*from\s+\.+\s+import', line):
                changes.append(f"Line {i+1}: Found relative import: '{line.strip()}' - NEEDS MANUAL FIX")
            
            modified_lines.append(line)
        
        modified_content = '\n'.join(modified_lines)
        
        return modified_content, changes

    def fix_file(self, file_path: Path) -> bool:
        """Fix imports in a single file. Returns True if changes were made."""
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
                
                print(f"\n✅ Fixed imports in {file_path}:")
                for change in changes[:5]:  # Limit output
                    print(f"   {change}")
                if len(changes) > 5:
                    print(f"   ... and {len(changes) - 5} more changes")
                
                self.processed_files.add(str(file_path))
                return True
            except Exception as e:
                print(f"Error writing {file_path}: {e}")
                return False
        
        return False

    def run(self) -> Dict[str, any]:
        """Run the canonical import fixing process."""
        print("🔧 Task 58: Converting imports to canonical absolute references (Improved)...")
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
        
        if error_files:
            print(f"\n⚠️  Files with errors:")
            for file_path, error in error_files[:10]:
                print(f"   {file_path}: {error}")
            if len(error_files) > 10:
                print(f"   ... and {len(error_files) - 10} more")
        
        return {
            "files_processed": len(files),
            "files_modified": len(fixed_files),
            "files_with_errors": len(error_files),
            "modified_files": fixed_files,
            "error_files": error_files,
        }

def main():
    """Main execution function."""
    
    # Verify we're in the correct directory
    if not os.path.exists("systems"):
        print("❌ Error: systems directory not found. Run from backend directory.")
        sys.exit(1)
    
    fixer = ImprovedCanonicalImportFixer(".")
    results = fixer.run()
    
    print("\n" + "=" * 80)
    print("✅ Task 58: Improved Canonical Import Fixing Complete!")
    print(f"Modified {results['files_modified']} files")
    
    if results['files_with_errors']:
        print(f"⚠️  {results['files_with_errors']} files had errors - manual review needed")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 