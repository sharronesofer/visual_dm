#!/usr/bin/env python3
"""
Backend Structure Fix Script
Uses backend/tests/systems/ as the blueprint for proper organization.

The tests show us EXACTLY what the canonical structure should be:
- 34 systems with 962 test files
- Perfect 1:1 mapping to Development Bible
- Shows what functionality belongs in each system
"""

import os
import shutil
import json
import re
from pathlib import Path
from collections import defaultdict

class BackendReorganizer:
    def __init__(self, backend_path="backend"):
        self.backend_path = Path(backend_path)
        self.systems_path = self.backend_path / "systems"
        self.tests_path = self.backend_path / "tests" / "systems"
        
        # Canonical systems from tests (our source of truth)
        self.canonical_systems = self._get_canonical_systems()
        self.current_dirs = self._get_current_directories()
        self.mapping_plan = {}
        self.infrastructure_dirs = []
        
    def _get_canonical_systems(self):
        """Get canonical systems from test directory structure"""
        if not self.tests_path.exists():
            raise FileNotFoundError(f"Tests directory not found: {self.tests_path}")
        
        systems = []
        for item in self.tests_path.iterdir():
            if item.is_dir() and not item.name.startswith('__'):
                systems.append(item.name)
        
        print(f"🎯 Found {len(systems)} canonical systems in tests")
        return sorted(systems)
    
    def _get_current_directories(self):
        """Get current backend/systems directories"""
        if not self.systems_path.exists():
            raise FileNotFoundError(f"Systems directory not found: {self.systems_path}")
        
        dirs = []
        for item in self.systems_path.iterdir():
            if item.is_dir() and not item.name.startswith('__'):
                dirs.append(item.name)
        
        print(f"📁 Found {len(dirs)} current directories (should be {len(self.canonical_systems)})")
        return sorted(dirs)
    
    def analyze_mapping(self):
        """Analyze how current directories should map to canonical systems"""
        print("\n🔍 ANALYZING DIRECTORY MAPPING...")
        
        for current_dir in self.current_dirs:
            canonical_target = self._find_canonical_target(current_dir)
            
            if canonical_target:
                if canonical_target not in self.mapping_plan:
                    self.mapping_plan[canonical_target] = []
                self.mapping_plan[canonical_target].append(current_dir)
            else:
                # Check if it's infrastructure
                if self._is_infrastructure_directory(current_dir):
                    self.infrastructure_dirs.append(current_dir)
                else:
                    print(f"⚠️  No mapping found for: {current_dir}")
        
        self._print_mapping_summary()
        return self.mapping_plan
    
    def _is_infrastructure_directory(self, dir_name):
        """Check if directory is infrastructure/utility rather than a game system"""
        infrastructure_patterns = [
            'api', 'core', 'utils', 'schemas', 'models', 'routers', 'router',
            'services', 'service', 'cache', 'logging', 'migrations', 'migration',
            'validators', 'validator', 'generators', 'generator', 'processors',
            'performance', 'stats', 'error_reporting', 'notification',
            'repositories', 'repository', 'loaders', 'loader', 'synchronizers',
            'managers', 'dispatcher', 'examples', 'main', 'mods', 'features',
            'calculators', 'effects', 'enums', 'result', 'history', 'goal',
            'object_pool', 'state_manager', 'prompt_manager', 'system_hooks',
            'seed_loader', 'user_models', 'user_schemas', 'user_repository',
            'auth_schemas', 'auth_service', 'auth_relationships',
            'consolidated_manager', 'consolidated_membership_service',
            'consolidated_relationship_service', 'consolidated_state_models',
            'consolidated_world_models', 'remove_deprecated_utils',
            'fix_utils_imports', 'verify_utils_imports', 'unified_effects'
        ]
        
        return any(pattern in dir_name.lower() for pattern in infrastructure_patterns)
    
    def _find_canonical_target(self, current_dir):
        """Find which canonical system a current directory should map to"""
        
        # Direct match
        if current_dir in self.canonical_systems:
            return current_dir
        
        # Remove common suffixes/prefixes
        base_patterns = [
            # Remove service/router/manager suffixes
            (r'(.+)_service$', r'\1'),
            (r'(.+)_router$', r'\1'),
            (r'(.+)_manager$', r'\1'),
            (r'(.+)_integration$', r'\1'),
            (r'(.+)_utils$', r'\1'),
            (r'(.+)_facade$', r'\1'),
            (r'(.+)_routes$', r'\1'),
            (r'(.+)_actions$', r'\1'),
            
            # Handle plurals -> singular
            (r'([^s]+)s$', r'\1'),
            
            # Handle compound names
            (r'(.+)_(.+)', r'\1'),  # Take first part if compound
        ]
        
        for pattern, replacement in base_patterns:
            match = re.match(pattern, current_dir)
            if match:
                candidate = re.sub(pattern, replacement, current_dir)
                if candidate in self.canonical_systems:
                    return candidate
        
        # Fuzzy matching for common variations
        for canonical in self.canonical_systems:
            if canonical in current_dir or current_dir in canonical:
                return canonical
            
            # Check for common variations
            if current_dir.replace('_', '') == canonical.replace('_', ''):
                return canonical
        
        return None
    
    def _print_mapping_summary(self):
        """Print summary of mapping plan"""
        print("\n📋 MAPPING PLAN SUMMARY:")
        
        total_current = len(self.current_dirs)
        total_canonical = len(self.canonical_systems)
        mapped_dirs = sum(len(dirs) for dirs in self.mapping_plan.values())
        infrastructure_count = len(self.infrastructure_dirs)
        
        print(f"Current directories: {total_current}")
        print(f"Canonical systems: {total_canonical}")
        print(f"Directories to consolidate: {mapped_dirs}")
        print(f"Infrastructure directories: {infrastructure_count}")
        print(f"Reduction: {total_current} → {total_canonical + 1} (systems + infrastructure)")
        
        print("\n🎯 CONSOLIDATION PLAN:")
        for canonical, dirs in sorted(self.mapping_plan.items()):
            if len(dirs) > 1:
                print(f"• {canonical}/ ← {', '.join(dirs)} ({len(dirs)} dirs)")
            else:
                print(f"• {canonical}/ ← {dirs[0]}")
        
        if self.infrastructure_dirs:
            print(f"\n🏗️ INFRASTRUCTURE CONSOLIDATION:")
            print(f"• infrastructure/ ← {', '.join(self.infrastructure_dirs[:10])}")
            if len(self.infrastructure_dirs) > 10:
                print(f"  ... and {len(self.infrastructure_dirs) - 10} more")
    
    def create_backup(self):
        """Create backup of current systems directory"""
        backup_path = self.backend_path / "systems_backup"
        
        if backup_path.exists():
            shutil.rmtree(backup_path)
        
        shutil.copytree(self.systems_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
        return backup_path
    
    def execute_reorganization(self, dry_run=True):
        """Execute the reorganization plan"""
        print(f"\n🚀 EXECUTING REORGANIZATION (dry_run={dry_run})...")
        
        if not dry_run:
            self.create_backup()
        
        reorganization_stats = {
            'systems_created': 0,
            'infrastructure_created': 0,
            'directories_consolidated': 0,
            'files_moved': 0
        }
        
        new_systems_path = self.systems_path.parent / "systems_new"
        
        if not dry_run:
            if new_systems_path.exists():
                shutil.rmtree(new_systems_path)
            new_systems_path.mkdir()
        
        # Process each canonical system
        for canonical_system, source_dirs in self.mapping_plan.items():
            canonical_dir = new_systems_path / canonical_system
            
            print(f"\n📁 Creating {canonical_system}/...")
            
            if not dry_run:
                canonical_dir.mkdir(exist_ok=True)
            
            # Consolidate all source directories into canonical structure
            for source_dir in source_dirs:
                source_path = self.systems_path / source_dir
                
                if source_path.exists():
                    file_count = self._consolidate_directory(source_path, canonical_dir, dry_run)
                    reorganization_stats['files_moved'] += file_count
                    reorganization_stats['directories_consolidated'] += 1
                    
                    print(f"  ✅ Consolidated {source_dir}/ ({file_count} files)")
            
            reorganization_stats['systems_created'] += 1
        
        # Handle infrastructure directories
        if self.infrastructure_dirs:
            infrastructure_dir = new_systems_path / "infrastructure"
            print(f"\n🏗️ Creating infrastructure/...")
            
            if not dry_run:
                infrastructure_dir.mkdir(exist_ok=True)
            
            for infra_dir in self.infrastructure_dirs:
                source_path = self.systems_path / infra_dir
                
                if source_path.exists():
                    # Create subdirectory in infrastructure
                    target_dir = infrastructure_dir / infra_dir
                    if not dry_run:
                        target_dir.mkdir(exist_ok=True)
                    
                    file_count = self._consolidate_directory(source_path, target_dir, dry_run)
                    reorganization_stats['files_moved'] += file_count
                    reorganization_stats['directories_consolidated'] += 1
                    
                    print(f"  ✅ Moved {infra_dir}/ to infrastructure/ ({file_count} files)")
            
            reorganization_stats['infrastructure_created'] = 1
        
        # Handle unmapped directories
        unmapped = set(self.current_dirs) - set(
            dir_name for dirs in self.mapping_plan.values() for dir_name in dirs
        ) - set(self.infrastructure_dirs)
        
        if unmapped:
            print(f"\n⚠️  UNMAPPED DIRECTORIES: {', '.join(unmapped)}")
            print("These need manual review!")
        
        self._print_reorganization_summary(reorganization_stats, dry_run)
        
        if not dry_run:
            print(f"\n✅ New structure created in: {new_systems_path}")
            print("Review the new structure, then:")
            print(f"  mv {self.systems_path} {self.systems_path}_old")
            print(f"  mv {new_systems_path} {self.systems_path}")
        
        return reorganization_stats
    
    def _consolidate_directory(self, source_path, target_path, dry_run=True):
        """Consolidate a source directory into target canonical structure"""
        file_count = 0
        
        if not source_path.exists():
            return 0
        
        for item in source_path.rglob('*'):
            if item.is_file():
                # Calculate relative path from source
                rel_path = item.relative_to(source_path)
                target_file = target_path / rel_path
                
                if not dry_run:
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Handle naming conflicts
                    counter = 1
                    original_target = target_file
                    while target_file.exists():
                        stem = original_target.stem
                        suffix = original_target.suffix
                        target_file = original_target.parent / f"{stem}_{counter}{suffix}"
                        counter += 1
                    
                    shutil.copy2(item, target_file)
                
                file_count += 1
        
        return file_count
    
    def _print_reorganization_summary(self, stats, dry_run):
        """Print reorganization summary"""
        print(f"\n📊 REORGANIZATION SUMMARY ({'DRY RUN' if dry_run else 'EXECUTED'}):")
        print(f"• Canonical systems created: {stats['systems_created']}")
        print(f"• Infrastructure directory created: {stats['infrastructure_created']}")
        print(f"• Directories consolidated: {stats['directories_consolidated']}")
        print(f"• Files moved: {stats['files_moved']}")
        
        if dry_run:
            print("\n🎯 Ready to execute! Run with dry_run=False to proceed.")
    
    def validate_reorganization(self, new_systems_path):
        """Validate the reorganized structure against tests"""
        print("\n🔍 VALIDATING REORGANIZATION...")
        
        # Check that all canonical systems exist
        missing_systems = []
        for canonical in self.canonical_systems:
            canonical_dir = Path(new_systems_path) / canonical
            if not canonical_dir.exists():
                missing_systems.append(canonical)
        
        if missing_systems:
            print(f"❌ Missing systems: {', '.join(missing_systems)}")
        else:
            print("✅ All canonical systems present")
        
        # Check for infrastructure directory
        infra_dir = Path(new_systems_path) / "infrastructure"
        if infra_dir.exists():
            print("✅ Infrastructure directory created")
        
        return len(missing_systems) == 0

def main():
    """Main execution"""
    print("🏛️ BACKEND STRUCTURE REORGANIZATION")
    print("Using tests as canonical blueprint")
    
    # Initialize reorganizer
    reorganizer = BackendReorganizer()
    
    print(f"\n📊 CURRENT STATE:")
    print(f"• Canonical systems (from tests): {len(reorganizer.canonical_systems)}")
    print(f"• Current directories: {len(reorganizer.current_dirs)}")
    print(f"• Reduction needed: {len(reorganizer.current_dirs) - len(reorganizer.canonical_systems)} directories")
    
    # Analyze mapping
    mapping_plan = reorganizer.analyze_mapping()
    
    # Execute dry run first
    print("\n" + "="*60)
    print("DRY RUN - NO CHANGES MADE")
    print("="*60)
    
    dry_run_stats = reorganizer.execute_reorganization(dry_run=True)
    
    # Auto-execute if user wants (remove interactive prompt)
    print("\n🚀 EXECUTING ACTUAL REORGANIZATION...")
    actual_stats = reorganizer.execute_reorganization(dry_run=False)
    
    # Validate results
    new_systems_path = "backend/systems_new"
    if Path(new_systems_path).exists():
        reorganizer.validate_reorganization(new_systems_path)
        
        print("\n🎯 FINAL INSTRUCTIONS:")
        print("1. Review the new structure in backend/systems_new/")
        print("2. Run tests to ensure everything works")
        print("3. If satisfied, execute:")
        print("   mv backend/systems backend/systems_old")
        print("   mv backend/systems_new backend/systems")
        print("4. Update import statements")
        print("5. Celebrate! 🎉")

if __name__ == "__main__":
    main() 