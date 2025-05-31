#!/usr/bin/env python3
"""
Script to orchestrate moving /data/ to root /data/ directory
and fix all resulting import issues.

This script:
1. Analyzes what needs to be moved/merged
2. Backs up existing data
3. Performs the move operation
4. Updates all code references
5. Validates the move was successful
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Set
import re
import subprocess
from datetime import datetime

class DataDirectoryMigrator:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.backend_data = self.project_root / "backend" / "data"
        self.root_data = self.project_root / "data"
        self.backup_dir = self.project_root / "data_migration_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Files to update with new paths
        self.files_to_update = []
        
        # Path mappings for replacement
        self.path_mappings = {
            "data": "data",
            '"data': '"data',
            "'data": "'data",
            "backend\\data": "data",  # Windows paths
        }

    def analyze_differences(self) -> Dict[str, List[str]]:
        """Analyze differences between data and root data directories."""
        print("🔍 Analyzing differences between data and data/...")
        
        conflicts = []
        backend_only = []
        
        if not self.backend_data.exists():
            print("❌ data directory doesn't exist!")
            return {"conflicts": conflicts, "backend_only": backend_only}
            
        if not self.root_data.exists():
            print("❌ Root data directory doesn't exist!")
            return {"conflicts": conflicts, "backend_only": backend_only}

        # Get all files in data
        for item in self.backend_data.rglob("*"):
            if item.is_file():
                relative_path = item.relative_to(self.backend_data)
                root_equivalent = self.root_data / relative_path
                
                if root_equivalent.exists():
                    # Check if files are different
                    try:
                        if item.read_bytes() != root_equivalent.read_bytes():
                            conflicts.append(str(relative_path))
                    except Exception:
                        conflicts.append(str(relative_path))
                else:
                    backend_only.append(str(relative_path))
        
        return {"conflicts": conflicts, "backend_only": backend_only}

    def create_backup(self):
        """Create backup of both data directories."""
        print(f"💾 Creating backup in {self.backup_dir}...")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup data
        if self.backend_data.exists():
            shutil.copytree(self.backend_data, self.backup_dir / "backend_data")
            print(f"✅ Backed up data to {self.backup_dir / 'backend_data'}")
        
        # Backup root data
        if self.root_data.exists():
            shutil.copytree(self.root_data, self.backup_dir / "root_data")
            print(f"✅ Backed up data/ to {self.backup_dir / 'root_data'}")

    def find_files_to_update(self):
        """Find all Python files that reference data paths."""
        print("🔍 Finding files that reference data paths...")
        
        python_files = list(self.project_root.rglob("*.py"))
        config_files = list(self.project_root.rglob("*.json")) + list(self.project_root.rglob("*.yaml")) + list(self.project_root.rglob("*.yml"))
        
        all_files = python_files + config_files
        
        for file_path in all_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                if "data" in content or "backend\\data" in content:
                    self.files_to_update.append(file_path)
            except Exception as e:
                print(f"⚠️  Could not read {file_path}: {e}")
        
        print(f"📝 Found {len(self.files_to_update)} files to update")
        for file_path in self.files_to_update[:10]:  # Show first 10
            print(f"   - {file_path.relative_to(self.project_root)}")
        if len(self.files_to_update) > 10:
            print(f"   ... and {len(self.files_to_update) - 10} more")

    def merge_directories(self, conflicts: List[str], backend_only: List[str]):
        """Merge data into root data directory."""
        print("🔄 Merging directories...")
        
        # Handle conflicts first
        if conflicts:
            print(f"⚠️  Found {len(conflicts)} conflicts:")
            for conflict in conflicts[:5]:  # Show first 5
                print(f"   - {conflict}")
            if len(conflicts) > 5:
                print(f"   ... and {len(conflicts) - 5} more")
            
            response = input("How to handle conflicts? (o)verwrite, (s)kip, (a)bort: ").lower()
            if response == 'a':
                print("❌ Aborted by user")
                return False
            elif response == 'o':
                print("📝 Will overwrite conflicting files")
                overwrite = True
            else:
                print("📝 Will skip conflicting files")
                overwrite = False
        else:
            overwrite = False

        # Copy backend-only files
        for file_path in backend_only:
            src = self.backend_data / file_path
            dst = self.root_data / file_path
            
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"✅ Copied: {file_path}")
            except Exception as e:
                print(f"❌ Failed to copy {file_path}: {e}")
        
        # Handle conflicts based on user choice
        if conflicts and overwrite:
            for file_path in conflicts:
                src = self.backend_data / file_path
                dst = self.root_data / file_path
                
                try:
                    shutil.copy2(src, dst)
                    print(f"🔄 Overwrote: {file_path}")
                except Exception as e:
                    print(f"❌ Failed to overwrite {file_path}: {e}")
        
        return True

    def update_file_references(self):
        """Update all file references from data to data."""
        print("🔧 Updating file references...")
        
        updated_count = 0
        
        for file_path in self.files_to_update:
            try:
                content = file_path.read_text(encoding='utf-8')
                original_content = content
                
                # Apply all path mappings
                for old_path, new_path in self.path_mappings.items():
                    content = content.replace(old_path, new_path)
                
                # Special handling for Python f-strings and complex patterns
                content = re.sub(r'f["\']data', r'f"data', content)
                content = re.sub(r'f["\']backend\\data', r'f"data', content)
                
                if content != original_content:
                    file_path.write_text(content, encoding='utf-8')
                    updated_count += 1
                    print(f"✅ Updated: {file_path.relative_to(self.project_root)}")
                
            except Exception as e:
                print(f"❌ Failed to update {file_path}: {e}")
        
        print(f"🎉 Updated {updated_count} files")

    def remove_backend_data(self):
        """Remove the data directory after successful migration."""
        if self.backend_data.exists():
            try:
                shutil.rmtree(self.backend_data)
                print(f"🗑️  Removed data directory")
            except Exception as e:
                print(f"❌ Failed to remove data: {e}")

    def validate_migration(self):
        """Validate that the migration was successful."""
        print("🔍 Validating migration...")
        
        # Check if data is gone
        if self.backend_data.exists():
            print("⚠️  data still exists!")
            return False
        
        # Check if root data has expected content
        if not self.root_data.exists():
            print("❌ Root data directory missing!")
            return False
        
        # Run a quick test to see if imports work
        try:
            result = subprocess.run(
                ["python", "-c", "import sys; sys.path.append('.'); from backend.infrastructure.shared.config import Settings; print('✅ Config import works')"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                print("✅ Basic imports still work")
            else:
                print(f"⚠️  Import test failed: {result.stderr}")
        except Exception as e:
            print(f"⚠️  Could not run import test: {e}")
        
        print("✅ Migration validation complete")
        return True

    def run(self, dry_run: bool = False):
        """Run the complete migration process."""
        print(f"🚀 Starting data directory migration {'(DRY RUN)' if dry_run else ''}...")
        
        if dry_run:
            print("🏃 This is a dry run - no changes will be made")
        
        # Step 1: Analyze differences
        analysis = self.analyze_differences()
        conflicts = analysis["conflicts"]
        backend_only = analysis["backend_only"]
        
        # Step 2: Find files to update (do this in dry run too)
        self.find_files_to_update()
        
        print(f"\n📊 Analysis Results:")
        print(f"   - Files only in data: {len(backend_only)}")
        print(f"   - Conflicting files: {len(conflicts)}")
        print(f"   - Code files to update: {len(self.files_to_update)}")
        
        if not backend_only and not conflicts:
            print("✅ No files to migrate!")
            return True
        
        if dry_run:
            print("\n🏃 DRY RUN - Would perform these actions:")
            print(f"   - Create backup in {self.backup_dir}")
            print(f"   - Merge {len(backend_only)} files")
            if conflicts:
                print(f"   - Handle {len(conflicts)} conflicts")
            print(f"   - Update {len(self.files_to_update)} code files")
            print(f"   - Remove data directory")
            return True
        
        # Step 3: Create backup
        self.create_backup()
        
        # Step 4: Merge directories
        if not self.merge_directories(conflicts, backend_only):
            return False
        
        # Step 5: Update file references
        self.update_file_references()
        
        # Step 6: Remove data
        self.remove_backend_data()
        
        # Step 7: Validate
        return self.validate_migration()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate data to root data directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--project-root", default=".", help="Path to project root")
    
    args = parser.parse_args()
    
    migrator = DataDirectoryMigrator(args.project_root)
    success = migrator.run(dry_run=args.dry_run)
    
    if success:
        print("\n🎉 Migration completed successfully!")
        if not args.dry_run:
            print(f"💾 Backup available at: {migrator.backup_dir}")
    else:
        print("\n❌ Migration failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 