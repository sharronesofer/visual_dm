#!/usr/bin/env python3
"""
Backend File Organization Script

This script organizes misplaced files in the /backend directory according to the canonical 
structure defined in the Development Bible and Backend Development Protocol:

Canonical Structure:
backend/
├── systems/           # Core game systems (already correct)
├── tests/            # All tests (already correct)  
├── docs/             # Documentation and reports
├── scripts/          # Development and maintenance scripts
├── logs/             # Log files
├── main.py           # Main application entry point
├── requirements.txt  # Dependencies
└── __pycache__/      # Python cache (can remain)

Files to be organized:
- Task-related scripts and reports → scripts/
- Coverage reports and JSON data → scripts/coverage/
- Analysis and refactoring tools → scripts/analysis/
- Documentation and reports → docs/
- Development tools → scripts/tools/
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# Define the canonical directory structure
CANONICAL_STRUCTURE = {
    'docs': 'Documentation, reports, and analysis results',
    'scripts': 'Development and maintenance scripts',
    'scripts/coverage': 'Coverage reports and related files',
    'scripts/analysis': 'Code analysis tools and reports',
    'scripts/tools': 'Development and maintenance tools',
    'scripts/tasks': 'Task-specific implementation scripts',
    'logs': 'Log files and runtime data'
}

# File patterns and their target directories
FILE_MAPPINGS = {
    # Documentation and Reports
    'docs/': [
        r'.*\.md$',  # All markdown files (except specific ones)
        r'.*_report\.json$',
        r'.*_summary\.md$',
        r'TASK.*\.md$',
        r'.*COMPLETION.*\.md$',
        r'.*REFACTORING.*\.md$',
        r'.*DEPENDENCY.*\.md$',
        r'.*COMBAT.*\.md$',
    ],
    
    # Coverage data
    'scripts/coverage/': [
        r'\.coverage$',
        r'coverage.*\.json$',
        r'.*coverage.*\.py$',
        r'htmlcov/.*',
    ],
    
    # Analysis tools and reports
    'scripts/analysis/': [
        r'analyze_.*\.py$',
        r'assess_.*\.py$',
        r'.*analysis.*\.py$',
        r'.*assessment.*\.py$',
        r'.*refactoring.*\.json$',
        r'debug_.*\.py$',
        r'.*_analysis\.json$',
        r'backend_systems_.*',
    ],
    
    # Task-specific scripts
    'scripts/tasks/': [
        r'task\d+.*\.py$',
        r'testing_protocol.*\.py$',
    ],
    
    # Development tools
    'scripts/tools/': [
        r'fix_.*\.py$',
        r'organize_.*\.py$',
        r'cleanup.*\.py$',
        r'extract_.*\.py$',
        r'validate_.*\.py$',
    ],
    
    # Keep in root
    'backend/': [
        r'main\.py$',
        r'requirements\.txt$',
        r'__pycache__/.*',
        r'systems/.*',
        r'tests/.*',
        r'data/.*',  # User specified to ignore
        r'logs/.*',
    ]
}

class BackendFileOrganizer:
    def __init__(self, backend_path: str = "backend"):
        self.backend_path = Path(backend_path)
        self.dry_run = True
        self.moved_files = []
        self.errors = []
        
    def create_canonical_directories(self):
        """Create the canonical directory structure"""
        print("Creating canonical directory structure...")
        
        for dir_path, description in CANONICAL_STRUCTURE.items():
            full_path = self.backend_path / dir_path
            if not self.dry_run:
                full_path.mkdir(parents=True, exist_ok=True)
            print(f"  📁 {dir_path}/ - {description}")
    
    def get_file_list(self) -> List[Path]:
        """Get list of all files in backend directory (non-recursive for root level)"""
        files = []
        
        # Get root level files only
        for item in self.backend_path.iterdir():
            if item.is_file():
                files.append(item)
            elif item.is_dir() and item.name in ['htmlcov', '__pycache__', 'analytics_data']:
                # Include specific directories we want to move
                files.append(item)
        
        return files
    
    def determine_target_directory(self, file_path: Path) -> str:
        """Determine target directory for a file based on patterns"""
        import re
        
        file_name = file_path.name
        
        # Check each directory pattern
        for target_dir, patterns in FILE_MAPPINGS.items():
            for pattern in patterns:
                if re.match(pattern, file_name) or re.match(pattern, str(file_path)):
                    return target_dir
        
        # Special cases
        if 'task' in file_name.lower() and file_name.endswith('.py'):
            return 'scripts/tasks/'
        
        if any(word in file_name.lower() for word in ['coverage', 'cov']):
            return 'scripts/coverage/'
        
        if any(word in file_name.lower() for word in ['fix', 'cleanup', 'organize']):
            return 'scripts/tools/'
        
        if file_name.endswith('.md') or 'report' in file_name.lower():
            return 'docs/'
        
        # Default to scripts if it's a .py file
        if file_name.endswith('.py'):
            return 'scripts/'
        
        # For unknown files, suggest docs
        return 'docs/'
    
    def organize_files(self, dry_run: bool = True):
        """Organize all misplaced files"""
        self.dry_run = dry_run
        
        print(f"\n{'DRY RUN: ' if dry_run else ''}Organizing backend files...")
        print(f"Backend path: {self.backend_path}")
        
        # Create directories
        self.create_canonical_directories()
        
        # Get files to organize
        files = self.get_file_list()
        print(f"\nFound {len(files)} items to organize:")
        
        # Categorize files
        file_moves = {}
        for file_path in files:
            target_dir = self.determine_target_directory(file_path)
            
            # Skip files that should stay in root
            if target_dir == 'backend/':
                continue
                
            if target_dir not in file_moves:
                file_moves[target_dir] = []
            file_moves[target_dir].append(file_path)
        
        # Display plan
        print("\n📋 File organization plan:")
        for target_dir, files in file_moves.items():
            print(f"\n  📁 {target_dir}")
            for file_path in files:
                print(f"    📄 {file_path.name}")
        
        # Execute moves
        if not dry_run:
            print("\n🚀 Executing file moves...")
            for target_dir, files in file_moves.items():
                target_path = self.backend_path / target_dir
                target_path.mkdir(parents=True, exist_ok=True)
                
                for file_path in files:
                    try:
                        destination = target_path / file_path.name
                        if file_path.is_dir():
                            shutil.move(str(file_path), str(destination))
                        else:
                            shutil.move(str(file_path), str(destination))
                        self.moved_files.append((str(file_path), str(destination)))
                        print(f"    ✅ Moved {file_path.name} → {target_dir}")
                    except Exception as e:
                        error_msg = f"Failed to move {file_path.name}: {e}"
                        self.errors.append(error_msg)
                        print(f"    ❌ {error_msg}")
        
        # Summary
        print(f"\n📊 Summary:")
        if dry_run:
            total_moves = sum(len(files) for files in file_moves.values())
            print(f"  📋 {total_moves} files would be moved")
            print(f"  📁 {len(file_moves)} directories would be used")
        else:
            print(f"  ✅ {len(self.moved_files)} files moved successfully")
            print(f"  ❌ {len(self.errors)} errors occurred")
        
        return file_moves
    
    def generate_report(self, file_moves: Dict[str, List[Path]]):
        """Generate a detailed report of the organization"""
        report_path = self.backend_path / "file_organization_report.md"
        
        with open(report_path, 'w') as f:
            f.write("# Backend File Organization Report\n\n")
            f.write("This report documents the reorganization of backend files according to the canonical structure.\n\n")
            
            f.write("## Canonical Structure Created\n\n")
            for dir_path, description in CANONICAL_STRUCTURE.items():
                f.write(f"- `{dir_path}/` - {description}\n")
            
            f.write("\n## File Moves\n\n")
            for target_dir, files in file_moves.items():
                f.write(f"### {target_dir}\n\n")
                for file_path in files:
                    f.write(f"- `{file_path.name}`\n")
                f.write("\n")
            
            if self.moved_files:
                f.write("## Successful Moves\n\n")
                for source, dest in self.moved_files:
                    f.write(f"- `{source}` → `{dest}`\n")
            
            if self.errors:
                f.write("\n## Errors\n\n")
                for error in self.errors:
                    f.write(f"- {error}\n")
        
        print(f"\n📄 Report generated: {report_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Organize backend files according to canonical structure")
    parser.add_argument("--execute", action="store_true", help="Execute the moves (default is dry run)")
    parser.add_argument("--backend-path", default="backend", help="Path to backend directory")
    
    args = parser.parse_args()
    
    organizer = BackendFileOrganizer(args.backend_path)
    
    # Run organization
    file_moves = organizer.organize_files(dry_run=not args.execute)
    
    # Generate report
    organizer.generate_report(file_moves)
    
    if not args.execute:
        print("\n💡 This was a dry run. Use --execute to actually move files.")
        print("   python organize_backend_files.py --execute") 