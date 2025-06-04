#!/usr/bin/env python3
"""
Region System Migration Script

Helps migrate from the old region system structure to the new architecture:
- Consolidates world generation utilities to backend/systems/world_generation (canonical location)
- Consolidates tension system to backend/systems/tension (unified system)
- Removes old tension_war directories
- Updates import statements throughout codebase
- Cleans up infrastructure and data references
- Removes deprecated files

Run this script to automatically migrate your codebase.
"""

import os
import shutil
import re
from pathlib import Path
from typing import List, Dict, Tuple


class RegionSystemMigrator:
    """Handles migration from old region system to new architecture."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backup_region_migration"
        self.changes_made = []
        
    def migrate(self, create_backup: bool = True) -> None:
        """Run the complete migration process."""
        print("Starting Region System Migration...")
        
        if create_backup:
            self._create_backup()
        
        # Step 1: Clean up old directories
        self._cleanup_old_directories()
        
        # Step 2: Update import statements throughout codebase
        self._update_import_statements()
        
        # Step 3: Remove deprecated files
        self._remove_deprecated_files()
        
        # Step 4: Create configuration files
        self._create_configuration_files()
        
        # Step 5: Update infrastructure references
        self._cleanup_infrastructure_references()
        
        self._print_migration_summary()
        
    def _create_backup(self) -> None:
        """Create backup of current region system."""
        print("Creating backup...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        # Backup the old structures
        backup_sources = [
            "backend/systems/region",
            "backend/systems/tension_war",
            "backend/systems/world_generation",
            "backend/infrastructure/systems/tension_war",
            "backend/infrastructure/systems/world_generation"
        ]
        
        for source in backup_sources:
            source_path = self.project_root / source
            if source_path.exists():
                dest_path = self.backup_dir / source
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(source_path, dest_path)
                
        print(f"Backup created at: {self.backup_dir}")
    
    def _cleanup_old_directories(self) -> None:
        """Remove old directory structures that have been replaced."""
        print("Cleaning up old directories...")
        
        directories_to_remove = [
            "backend/systems/tension_war",
            "backend/infrastructure/systems/tension_war", 
            "backend/infrastructure/systems/world_generation",
            "backend/world_generation"  # In case it was incorrectly placed here
        ]
        
        for dir_path in directories_to_remove:
            full_path = self.project_root / dir_path
            if full_path.exists():
                shutil.rmtree(full_path)
                self.changes_made.append(f"Removed old directory: {dir_path}")
        
        # Ensure canonical locations exist
        canonical_dirs = [
            "backend/systems/world_generation",
            "backend/systems/tension"
        ]
        
        for dir_path in canonical_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                print(f"Warning: Canonical directory {dir_path} does not exist!")
    
    def _update_import_statements(self) -> None:
        """Update import statements throughout the codebase."""
        print("Updating import statements...")
        
        # Define import mapping rules
        import_replacements = [
            # World generation imports - canonical location
            (
                r"from backend\.world_generation",
                "from backend.systems.world_generation"
            ),
            (
                r"import backend\.world_generation",
                "import backend.systems.world_generation"
            ),
            (
                r"from backend\.systems\.region\.utils\.worldgen",
                "from backend.systems.world_generation"
            ),
            (
                r"from backend\.systems\.region\.services\.world_generation_service",
                "from backend.systems.world_generation.services.world_generator"
            ),
            
            # Tension system imports - unified system
            (
                r"from backend\.systems\.tension_war",
                "from backend.systems.tension"
            ),
            (
                r"import backend\.systems\.tension_war",
                "import backend.systems.tension"
            ),
            (
                r"from backend\.systems\.region\.utils\.tension",
                "from backend.systems.tension"
            ),
            (
                r"from backend\.infrastructure\.systems\.tension_war",
                "from backend.systems.tension"
            ),
            
            # Specific class imports
            (
                r"WorldGenerator",
                "WorldGenerator"
            ),
            (
                r"UnifiedTensionManager",
                "UnifiedUnifiedTensionManager"
            ),
            (
                r"RegionEventService",
                "RegionEventService"
            ),
            
            # Infrastructure imports
            (
                r"from backend\.infrastructure\.systems\.world_generation",
                "from backend.systems.world_generation"
            )
        ]
        
        # Find all Python files to update
        python_files = list(self.project_root.rglob("*.py"))
        updated_files = []
        
        for file_path in python_files:
            # Skip backup directory
            if "backup_region_migration" in str(file_path):
                continue
                
            if self._update_file_imports(file_path, import_replacements):
                updated_files.append(file_path)
        
        if updated_files:
            self.changes_made.append(f"Updated imports in {len(updated_files)} files")
            for file_path in updated_files[:5]:  # Show first 5 files
                self.changes_made.append(f"  - {file_path.relative_to(self.project_root)}")
            if len(updated_files) > 5:
                self.changes_made.append(f"  - ... and {len(updated_files) - 5} more files")
    
    def _update_file_imports(self, file_path: Path, replacements: List[Tuple[str, str]]) -> bool:
        """Update imports in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            for pattern, replacement in replacements:
                content = re.sub(pattern, replacement, content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
                
        except Exception as e:
            print(f"Warning: Could not update {file_path}: {e}")
            
        return False
    
    def _remove_deprecated_files(self) -> None:
        """Remove deprecated files that have been replaced."""
        print("Removing deprecated files...")
        
        deprecated_files = [
            "backend/systems/region/utils/worldgen.py",
            "backend/systems/region/utils/tension.py",
            "backend/systems/region/services/world_generation_service.py"
        ]
        
        for file_path in deprecated_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                full_path.unlink()
                self.changes_made.append(f"Removed deprecated file: {file_path}")
        
        # Remove empty utils directory if it exists
        utils_dir = self.project_root / "backend/systems/region/utils"
        if utils_dir.exists() and not any(utils_dir.iterdir()):
            utils_dir.rmdir()
            self.changes_made.append("Removed empty utils directory")
    
    def _create_configuration_files(self) -> None:
        """Create default configuration files for the new systems."""
        print("Creating default configuration files...")
        
        # Create world generation config directory
        world_config_dir = self.project_root / "backend/systems/world_generation/config/data"
        world_config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create tension config directory  
        tension_config_dir = self.project_root / "backend/systems/tension/config/data"
        tension_config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize config managers to create default files
        try:
            from backend.infrastructure.world_generation_config import BiomeConfigManager, WorldTemplateManager
            
            # Create default configuration files
            biome_mgr = BiomeConfigManager()
            biome_mgr.save_default_config_file()
            
            template_mgr = WorldTemplateManager()
            template_mgr.save_default_templates_file()
            
            self.changes_made.append("Created default configuration files")
            
        except ImportError as e:
            print(f"Warning: Could not create default config files: {e}")
            self.changes_made.append("Configuration files need to be created manually")
    
    def _cleanup_infrastructure_references(self) -> None:
        """Clean up infrastructure system references."""
        print("Cleaning up infrastructure references...")
        
        # Remove old infrastructure directories
        infra_cleanup_dirs = [
            "backend/infrastructure/systems/tension_war",
            "backend/infrastructure/systems/world_generation"
        ]
        
        for dir_path in infra_cleanup_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                shutil.rmtree(full_path)
                self.changes_made.append(f"Cleaned up infrastructure: {dir_path}")
    
    def _print_migration_summary(self) -> None:
        """Print summary of migration changes."""
        print("\n" + "="*60)
        print("MIGRATION COMPLETED")
        print("="*60)
        
        if self.changes_made:
            print("\nChanges made:")
            for change in self.changes_made:
                print(f"  ✓ {change}")
        
        print("\nNext steps:")
        print("  1. Review the changes and test your application")
        print("  2. Update any remaining import statements if needed")
        print("  3. Configure the new systems in your application startup")
        print("  4. Consider customizing the JSON configuration files")
        
        print("\nCanonical locations:")
        print("  - World Generation: backend.systems.world_generation")
        print("  - Tension System: backend.systems.tension")
        
        print(f"\nBackup location: {self.backup_dir}")
        print("\nMigration completed successfully!")


def main():
    """Run the migration script."""
    import sys
    
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        # Try to detect project root
        current_dir = Path.cwd()
        project_root = current_dir
        
        # Look for common project root indicators
        for parent in [current_dir] + list(current_dir.parents):
            if (parent / "backend").exists() and (parent / "backend/systems").exists():
                project_root = parent
                break
    
    print(f"Using project root: {project_root}")
    
    migrator = RegionSystemMigrator(str(project_root))
    
    try:
        migrator.migrate(create_backup=True)
    except Exception as e:
        print(f"Migration failed: {e}")
        print("Please check the backup directory and fix any issues manually.")
        sys.exit(1)


if __name__ == "__main__":
    main() 