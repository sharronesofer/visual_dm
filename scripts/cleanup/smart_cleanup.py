#!/usr/bin/env python3

import os
import shutil
from pathlib import Path
from collections import defaultdict

class SmartCleanup:
    def __init__(self, backend_dir, dry_run=True):
        self.backend_dir = Path(backend_dir)
        self.dry_run = dry_run
        self.backup_dir = self.backend_dir.parent / "systems_smart_backup"
        
    def analyze_directory_structure(self):
        """Analyze the directory structure for excessive nesting"""
        print("🔍 ANALYZING DIRECTORY STRUCTURE")
        print("=" * 50)
        
        # Count directories by system
        system_dirs = defaultdict(list)
        for item in self.backend_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                system_name = item.name
                subdirs = list(item.rglob("*"))
                dir_count = len([d for d in subdirs if d.is_dir()])
                file_count = len([f for f in subdirs if f.is_file() and f.suffix == '.py'])
                
                system_dirs[system_name] = {
                    'path': item,
                    'subdirs': dir_count, 
                    'files': file_count
                }
        
        # Show systems with excessive structure
        print("\n📁 SYSTEMS BY COMPLEXITY:")
        for system, info in sorted(system_dirs.items(), key=lambda x: x[1]['subdirs'], reverse=True):
            print(f"   {system}: {info['subdirs']} dirs, {info['files']} files")
            
            # Check for redundant nested structure
            if info['subdirs'] > 15:  # Arbitrary threshold
                print(f"      ⚠️  Potentially over-structured")
        
        return system_dirs
    
    def find_redundant_files(self):
        """Find files that are likely redundant or bloated"""
        print("\n🔍 FINDING REDUNDANT FILES")
        print("=" * 50)
        
        redundant_candidates = []
        
        # Pattern 1: Multiple similar files in same directory
        for system_dir in self.backend_dir.iterdir():
            if not system_dir.is_dir():
                continue
                
            # Look for directories with too many similar files
            for subdir in system_dir.rglob("*"):
                if not subdir.is_dir():
                    continue
                    
                py_files = list(subdir.glob("*.py"))
                if len(py_files) > 10:  # Many files in one directory
                    # Check for patterns like service1.py, service2.py, etc.
                    base_names = defaultdict(list)
                    for f in py_files:
                        base = f.name.split('.')[0]
                        if any(pattern in base.lower() for pattern in ['service', 'router', 'schema', 'model']):
                            base_names[base.split('_')[0]].append(f)
                    
                    for base, files in base_names.items():
                        if len(files) > 3:  # Multiple similar files
                            redundant_candidates.extend(files[1:])  # Keep first, mark others
        
        # Pattern 2: Extremely large files (likely inflated)
        for py_file in self.backend_dir.rglob("*.py"):
            size = py_file.stat().st_size
            if size > 50000:  # > 50KB Python file is suspicious
                line_count = len(py_file.read_text().split('\n'))
                if line_count > 1500:  # > 1500 lines
                    redundant_candidates.append(py_file)
        
        # Pattern 3: Deep nesting patterns I likely created
        for py_file in self.backend_dir.rglob("*/*/*/*/*/*.py"):  # 5+ levels deep
            redundant_candidates.append(py_file)
            
        return list(set(redundant_candidates))
    
    def create_minimal_structure(self):
        """Propose a minimal structure for each system"""
        print("\n🎯 PROPOSED MINIMAL STRUCTURE")
        print("=" * 50)
        
        # Each system should have at most:
        minimal_structure = [
            "models.py",      # or models/ with 2-3 files max
            "services.py",    # or services/ with 2-3 files max  
            "router.py",      # single router file
            "schemas.py",     # single schema file
            "utils.py",       # single utils file
            "__init__.py"     # initialization
        ]
        
        print("📋 RECOMMENDED STRUCTURE PER SYSTEM:")
        for item in minimal_structure:
            print(f"   - {item}")
        
        # Analyze current vs recommended
        systems_analysis = {}
        for system_dir in self.backend_dir.iterdir():
            if not system_dir.is_dir():
                continue
                
            current_files = list(system_dir.rglob("*.py"))
            systems_analysis[system_dir.name] = {
                'current_count': len(current_files),
                'recommended_count': len(minimal_structure),
                'excess': len(current_files) - len(minimal_structure)
            }
        
        print(f"\n📊 CURRENT VS RECOMMENDED:")
        total_excess = 0
        for system, analysis in systems_analysis.items():
            if analysis['excess'] > 0:
                print(f"   {system}: {analysis['current_count']} files (excess: {analysis['excess']})")
                total_excess += analysis['excess']
        
        print(f"\n🎯 TOTAL EXCESS FILES: {total_excess}")
        return systems_analysis
    
    def execute_smart_cleanup(self):
        """Execute smart cleanup based on analysis"""
        print("\n🧹 SMART CLEANUP ANALYSIS")
        print("=" * 60)
        
        # Analyze current state
        dir_analysis = self.analyze_directory_structure()
        redundant_files = self.find_redundant_files()
        structure_analysis = self.create_minimal_structure()
        
        print(f"\n📋 CLEANUP SUMMARY:")
        print(f"   🗂️  Redundant files identified: {len(redundant_files)}")
        
        # Calculate potential savings
        total_size = 0
        total_lines = 0
        
        for file_path in redundant_files:
            if file_path.exists():
                size = file_path.stat().st_size
                try:
                    lines = len(file_path.read_text().split('\n'))
                    total_size += size
                    total_lines += lines
                except:
                    pass
        
        print(f"   💾 Potential size savings: {total_size / 1024:.1f} KB")
        print(f"   📄 Potential line savings: {total_lines:,} lines")
        
        if self.dry_run:
            print(f"\n🔍 DRY RUN - Files that would be removed:")
            for i, file_path in enumerate(redundant_files[:20]):
                rel_path = file_path.relative_to(self.backend_dir)
                try:
                    lines = len(file_path.read_text().split('\n'))
                    print(f"   {i+1}. {rel_path} ({lines} lines)")
                except:
                    print(f"   {i+1}. {rel_path} (unreadable)")
            
            if len(redundant_files) > 20:
                print(f"   ... and {len(redundant_files) - 20} more files")
        
        else:
            # Create backup
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            shutil.copytree(self.backend_dir, self.backup_dir)
            print(f"✅ Backup created at {self.backup_dir}")
            
            # Remove redundant files
            removed_count = 0
            for file_path in redundant_files:
                try:
                    if file_path.exists():
                        file_path.unlink()
                        removed_count += 1
                except Exception as e:
                    print(f"❌ Error removing {file_path}: {e}")
            
            print(f"✅ Removed {removed_count} redundant files")
        
        return len(redundant_files), total_size, total_lines

def main():
    cleanup = SmartCleanup("backend/systems", dry_run=True)
    files, size, lines = cleanup.execute_smart_cleanup()
    
    print(f"\n🎊 ANALYSIS COMPLETE:")
    print(f"   Files for removal: {files}")
    print(f"   Size savings: {size / 1024:.1f} KB") 
    print(f"   Line savings: {lines:,}")
    print(f"\n🚀 To execute: Change dry_run=False")

if __name__ == "__main__":
    main() 