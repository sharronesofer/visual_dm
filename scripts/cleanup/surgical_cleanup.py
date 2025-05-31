#!/usr/bin/env python3

import os
import shutil
from pathlib import Path

class SurgicalCleanup:
    def __init__(self, backend_dir, dry_run=True):
        self.backend_dir = Path(backend_dir)
        self.dry_run = dry_run
        self.backup_dir = self.backend_dir.parent / "systems_cleanup_backup"
        
        # Files to remove based on analysis
        self.files_to_remove = []
        self.directories_to_clean = []
        
    def create_backup(self):
        """Create backup before cleanup"""
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        print(f"🔄 Creating backup at {self.backup_dir}")
        shutil.copytree(self.backend_dir, self.backup_dir)
        print("✅ Backup created")
    
    def identify_files_to_remove(self):
        """Identify files that are clearly generated/mock implementations"""
        
        # Patterns that indicate generated/mock content
        remove_patterns = [
            # Empty or minimal files
            lambda content: len([line for line in content.split('\\n') if line.strip() and not line.strip().startswith('#')]) <= 3,
            
            # Files that are mostly pass statements
            lambda content: content.count('pass') >= content.count('def ') and content.count('def ') > 0,
            
            # Files with mostly NotImplementedError
            lambda content: content.count('NotImplementedError') >= content.count('def ') * 0.5 and content.count('def ') > 0,
            
            # Files that are mostly TODO comments
            lambda content: content.count('# TODO') >= 3 and len(content.split('\\n')) < 50,
            
            # Mock service files (these were likely auto-generated)
            lambda content: 'class ' in content and 'Service' in content and content.count('pass') > 3,
        ]
        
        keep_patterns = [
            # Files with substantial logic
            lambda content: any(pattern in content for pattern in ['if ', 'for ', 'while ', 'try:', 'except:']),
            
            # Files with real imports and usage
            lambda content: len([line for line in content.split('\\n') if 'import ' in line]) > 2 and 'pass' not in content,
            
            # Test files with real assertions
            lambda content: any(pattern in content for pattern in ['assert', 'assertEqual', 'assertTrue']),
            
            # Files with actual implementation
            lambda content: content.count('return ') > 2 or content.count('self.') > 5,
        ]
        
        for file_path in self.backend_dir.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if file should be kept
                should_keep = any(pattern(content) for pattern in keep_patterns)
                
                # Check if file should be removed
                should_remove = any(pattern(content) for pattern in remove_patterns)
                
                if should_remove and not should_keep:
                    self.files_to_remove.append(file_path)
                
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
    
    def remove_empty_directories(self):
        """Remove directories that become empty after file removal"""
        for root, dirs, files in os.walk(self.backend_dir, topdown=False):
            for directory in dirs:
                dir_path = Path(root) / directory
                if dir_path.exists() and not any(dir_path.iterdir()):
                    self.directories_to_clean.append(dir_path)
    
    def execute_cleanup(self):
        """Execute the cleanup process"""
        
        if not self.dry_run:
            self.create_backup()
        
        print(f"\\n🎯 SURGICAL CLEANUP {'(DRY RUN)' if self.dry_run else '(EXECUTING)'}")
        print("=" * 60)
        
        # Identify files to remove
        self.identify_files_to_remove()
        
        print(f"\\n📋 FILES TO REMOVE: {len(self.files_to_remove)}")
        
        # Show examples
        for i, file_path in enumerate(self.files_to_remove[:10]):
            rel_path = file_path.relative_to(self.backend_dir)
            size = file_path.stat().st_size
            print(f"   {i+1}. {rel_path} ({size} bytes)")
        
        if len(self.files_to_remove) > 10:
            print(f"   ... and {len(self.files_to_remove) - 10} more files")
        
        # Calculate savings
        total_size = sum(f.stat().st_size for f in self.files_to_remove)
        print(f"\\n💾 TOTAL SIZE TO REMOVE: {total_size / 1024:.1f} KB")
        
        # Execute removal
        if not self.dry_run:
            print("\\n🗑️ REMOVING FILES...")
            for file_path in self.files_to_remove:
                try:
                    file_path.unlink()
                    print(f"   ✅ Removed: {file_path.relative_to(self.backend_dir)}")
                except Exception as e:
                    print(f"   ❌ Error removing {file_path}: {e}")
            
            # Clean empty directories
            self.remove_empty_directories()
            print(f"\\n🧹 CLEANING EMPTY DIRECTORIES: {len(self.directories_to_clean)}")
            for dir_path in self.directories_to_clean:
                try:
                    dir_path.rmdir()
                    print(f"   ✅ Removed empty dir: {dir_path.relative_to(self.backend_dir)}")
                except Exception as e:
                    print(f"   ❌ Error removing dir {dir_path}: {e}")
        
        else:
            print("\\n🔍 DRY RUN COMPLETE - No files were actually removed")
            print("   Run with dry_run=False to execute cleanup")
        
        return len(self.files_to_remove), total_size

def main():
    cleanup = SurgicalCleanup("backend/systems", dry_run=True)
    files_removed, size_saved = cleanup.execute_cleanup()
    
    print(f"\\n🎊 CLEANUP SUMMARY:")
    print(f"   Files that would be removed: {files_removed}")
    print(f"   Size that would be saved: {size_saved / 1024:.1f} KB")
    print(f"\\n🚀 To execute cleanup: Change dry_run=False")

if __name__ == "__main__":
    main() 