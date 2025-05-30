#!/usr/bin/env python3
"""
Task 58: Update Import Paths to Absolute References
Convert all relative imports to absolute import paths following canonical structure.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set

class CanonicalImportFixer:
    def __init__(self, root_dir: str = "backend"):
        self.root_dir = Path(root_dir)
        self.systems_dir = self.root_dir / "systems"
        self.tests_dir = self.root_dir / "tests"
        
        # Track what we've processed to avoid duplicates
        self.processed_files: Set[str] = set()
        
        # Common import mappings for reorganized modules
        self.import_mappings = {
            # App imports should be backend.systems
            r"from app\.models\.([^.]+) import": r"from backend.systems.\1.models import",
            r"from app\.([^.]+) import": r"from backend.systems.\1 import",
            
            # Utils imports should point to shared.utils
            r"from utils\.([^.]+) import": r"from backend.systems.shared.utils.\1 import",
            
            # Direct system imports without backend.systems prefix
            r"from systems\.([^.]+) import": r"from backend.systems.\1 import",
            
            # Fix specific incorrect imports found in the code
            r"from backend\.systems\.npc_loyalty_class import": r"from backend.systems.npc.npc_loyalty_class import",
            r"from backend\.systems\.models import": r"from backend.systems.shared.models import", 
            r"from backend\.systems\.enums import": r"from backend.systems.shared.enums import",
            r"from backend\.systems\.config import": r"from backend.systems.shared.config import",
            r"from backend\.systems\.services\.([^.]+) import": r"from backend.systems.\1.services import",
            r"from backend\.systems\.models\.([^.]+) import": r"from backend.systems.\1.models import",
            
            # Fix shortened imports that should be full paths
            r"from backend\.systems\.tension_manager import": r"from backend.systems.tension_war.services.tension_manager import",
            r"from backend\.systems\.war_manager import": r"from backend.systems.tension_war.services.war_manager import",
            r"from backend\.systems\.peace_manager import": r"from backend.systems.tension_war.services.peace_manager import",
            r"from backend\.systems\.alliance_manager import": r"from backend.systems.tension_war.services.alliance_manager import",
            r"from backend\.systems\.proxy_war_manager import": r"from backend.systems.tension_war.services.proxy_war_manager import",
            r"from backend\.systems\.diplomatic_manager import": r"from backend.systems.tension_war.services.diplomatic_manager import",
            
            # Fix utils imports that need proper paths
            r"from backend\.systems\.tension_utils import": r"from backend.systems.tension_war.utils.tension_utils import",
            r"from backend\.systems\.war_utils import": r"from backend.systems.tension_war.utils.war_utils import",
            r"from backend\.systems\.peace_utils import": r"from backend.systems.tension_war.utils.peace_utils import",
            r"from backend\.systems\.alliance_utils import": r"from backend.systems.tension_war.utils.alliance_utils import",
            r"from backend\.systems\.diplomatic_utils import": r"from backend.systems.tension_war.utils.diplomatic_utils import",
            
            # Fix equipment utils imports
            r"from backend\.systems\.inventory_utils import": r"from backend.systems.inventory.utils import",
            r"from backend\.systems\.identify_item_utils import": r"from backend.systems.equipment.utils.identify_item_utils import",
            r"from backend\.systems\.set_bonus_utils import": r"from backend.systems.equipment.utils.set_bonus_utils import",
            r"from backend\.systems\.durability_utils import": r"from backend.systems.equipment.utils.durability_utils import",
            
            # Fix arc imports
            r"from backend\.systems\.arc_generator import": r"from backend.systems.arc.services.arc_generator import",
            r"from backend\.systems\.arc_events import": r"from backend.systems.arc.events import",
            r"from backend\.systems\.arc_schemas import": r"from backend.systems.arc.schemas import",
            
            # Fix analytics imports
            r"from backend\.systems\.services\.analytics_service import": r"from backend.systems.analytics.services.analytics_service import",
            
            # Fix specific model imports
            r"from backend\.systems\.models\.npc_events import": r"from backend.systems.npc.models.npc_events import",
            
            # Fix shared imports
            r"from backend\.systems\.shared\.utils\.base_manager import": r"from backend.systems.shared.utils.base.base_manager import",
            
            # Fix database imports
            r"from backend\.systems\.shared\.database import": r"from backend.systems.data.database import",
            
            # Fix narrative imports
            r"from backend\.systems\.narrative\.utils import": r"from backend.systems.motif.utils import",
        }
        
        # Files to skip (only temporary files, scripts, etc. - be more specific)
        self.skip_patterns = {
            r".*task\d+.*\.py$",
            r".*fix_.*\.py$", 
            r".*debug.*\.py$",
            r".*__pycache__.*",
            r".*\.pyc$",
            r".*organize.*\.py$",
            r".*cleanup.*\.py$",
            r".*analyze.*\.py$",
            r".*assess.*\.py$",
            r".*remove_deprecated.*\.py$",
            r".*migration_example.*\.py$",
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
            
            # Additional fixes for specific patterns
            
            # Fix relative imports (from . import, from .. import)
            if re.match(r'^\s*from\s+\.+\s+import', line):
                # This should be rare if previous tasks were done correctly
                changes.append(f"Line {i+1}: Found relative import: '{line.strip()}' - MANUAL FIX NEEDED")
            
            # Fix imports from non-existent backend.systems modules 
            if re.search(r'from backend\.systems\.([^.]+)\s+import', line):
                # Check if this is importing from a top-level module that should be a submodule
                match = re.search(r'from backend\.systems\.([^.]+)\s+import\s+(.+)', line)
                if match:
                    module_name = match.group(1)
                    imports = match.group(2)
                    
                    # Common fixes for reorganized modules
                    fixes = {
                        'alliances': 'tension_war.utils.alliances',
                        'war': 'tension_war.models.war',
                        'peace': 'tension_war.models.peace', 
                        'alliance': 'tension_war.models.alliance',
                        'impact': 'tension_war.models.impact',
                        'repositories': 'shared.repositories',
                        'services': 'shared.services'
                    }
                    
                    if module_name in fixes:
                        new_line = f"from backend.systems.{fixes[module_name]} import {imports}"
                        if new_line != line:
                            changes.append(f"Line {i+1}: '{line.strip()}' -> '{new_line.strip()}'")
                            line = new_line
            
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
                for change in changes:
                    print(f"   {change}")
                
                self.processed_files.add(str(file_path))
                return True
            except Exception as e:
                print(f"Error writing {file_path}: {e}")
                return False
        
        return False

    def validate_imports(self) -> Dict[str, List[str]]:
        """Validate that all imports can be resolved."""
        validation_results = {"valid": [], "invalid": []}
        
        for file_path in self.find_python_files():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract import statements
                import_lines = []
                for line in content.split('\n'):
                    stripped = line.strip()
                    if stripped.startswith('from ') and ' import ' in stripped:
                        import_lines.append(stripped)
                    elif stripped.startswith('import '):
                        import_lines.append(stripped)
                
                # Check each import
                for import_line in import_lines:
                    if 'backend.systems' in import_line:
                        # This is a backend import that should be validated
                        try:
                            # Extract module path
                            if import_line.startswith('from '):
                                module_part = import_line.split(' import ')[0].replace('from ', '')
                                # Convert to file path
                                module_path = module_part.replace('.', '/') + '.py'
                                full_path = Path(module_path)
                                
                                # Check if module exists
                                if full_path.exists() or (full_path.parent / '__init__.py').exists():
                                    validation_results["valid"].append(f"{file_path}: {import_line}")
                                else:
                                    validation_results["invalid"].append(f"{file_path}: {import_line}")
                            else:
                                validation_results["valid"].append(f"{file_path}: {import_line}")
                        except Exception:
                            validation_results["invalid"].append(f"{file_path}: {import_line}")
                    else:
                        validation_results["valid"].append(f"{file_path}: {import_line}")
                        
            except Exception as e:
                validation_results["invalid"].append(f"{file_path}: Error reading file - {e}")
        
        return validation_results

    def run(self) -> Dict[str, any]:
        """Run the canonical import fixing process."""
        print("🔧 Task 58: Converting imports to canonical absolute references...")
        print("=" * 80)
        
        files = self.find_python_files()
        print(f"Found {len(files)} Python files to process")
        
        # Debug: show first few files
        print("Sample files found:")
        for file_path in files[:10]:
            print(f"   {file_path}")
        if len(files) > 10:
            print(f"   ... and {len(files) - 10} more")
        
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
            for file_path, error in error_files:
                print(f"   {file_path}: {error}")
        
        # Validate imports
        print(f"\n🔍 Validating imports...")
        validation_results = self.validate_imports()
        
        print(f"   Valid imports: {len(validation_results['valid'])}")
        print(f"   Invalid imports: {len(validation_results['invalid'])}")
        
        if validation_results['invalid']:
            print(f"\n⚠️  Invalid imports found:")
            for invalid_import in validation_results['invalid'][:10]:  # Show first 10
                print(f"   {invalid_import}")
            if len(validation_results['invalid']) > 10:
                print(f"   ... and {len(validation_results['invalid']) - 10} more")
        
        return {
            "files_processed": len(files),
            "files_modified": len(fixed_files),
            "files_with_errors": len(error_files),
            "modified_files": fixed_files,
            "error_files": error_files,
            "validation_results": validation_results
        }


def main():
    """Main execution function."""
    
    # Change to backend directory
    if not os.path.exists("systems"):
        print("❌ Error: systems directory not found. Run from backend directory.")
        sys.exit(1)
    
    fixer = CanonicalImportFixer(".")
    results = fixer.run()
    
    print("\n" + "=" * 80)
    print("✅ Task 58: Canonical Import Fixing Complete!")
    print(f"Modified {results['files_modified']} files")
    
    if results['files_with_errors']:
        print(f"⚠️  {results['files_with_errors']} files had errors - manual review needed")
        return 1
    
    if results['validation_results']['invalid']:
        print(f"⚠️  {len(results['validation_results']['invalid'])} invalid imports found - manual review needed")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 