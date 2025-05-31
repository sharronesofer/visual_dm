#!/usr/bin/env python3
"""
Fix import issues that arose from moving /data/system/runtime/ to root /data/ directory.

This script identifies and fixes path references that point to the old backend/data location.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

class DataImportFixer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.fixes_applied = []
        
    def find_backend_data_references(self) -> List[Tuple[Path, List[int]]]:
        """Find all references to backend/data paths in Python files."""
        files_with_issues = []
        
        # Search in backend directory
        backend_dir = self.project_root / "backend"
        if backend_dir.exists():
            for py_file in backend_dir.rglob("*.py"):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    problematic_lines = []
                    for i, line in enumerate(lines, 1):
                        # Look for references to backend/data paths
                        if any(pattern in line for pattern in [
                            'backend/data',
                            'backend\\data',  # Windows paths
                            '"backend/data',
                            "'backend/data",
                            'backend.data',
                            'path.join.*backend.*data',
                            'Path.*backend.*data'
                        ]):
                            problematic_lines.append(i)
                    
                    if problematic_lines:
                        files_with_issues.append((py_file, problematic_lines))
                        
                except (UnicodeDecodeError, IOError):
                    continue
                    
        return files_with_issues
    
    def fix_file_references(self, file_path: Path) -> bool:
        """Fix data path references in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Pattern replacements for fixing paths
            replacements = [
                # Path string replacements
                (r'data/system/runtime/', 'data/'),
                (r'backend\\data\\', 'data/'),
                (r'"data/system/runtime/', '"data/'),
                (r"'data/system/runtime/", "'data/"),
                (r'"backend/data"', '"data"'),
                (r"'backend/data'", "'data'"),
                
                # Path construction replacements
                (r'Path\(__file__\)\..*?\.parent\.parent\.parent / "data"', 'Path("data")'),
                (r'Path\(__file__\)\..*?\.parent\.parent / "backend" / "data"', 'Path("data")'),
                (r'os\.path\.join\(.*?backend.*?data.*?\)', 'os.path.join("data")'),
                
                # Environment variable patterns
                (r'backend_data = .*?backend.*?data', 'data_dir = Path("data")'),
                
                # Common path patterns
                (r'backend\.data', 'data'),
                (r'backend/data', 'data'),
                (r'backend\\data', 'data'),
            ]
            
            for pattern, replacement in replacements:
                content = re.sub(pattern, replacement, content)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
                
        except (IOError, UnicodeDecodeError) as e:
            print(f"Error processing {file_path}: {e}")
            
        return False
    
    def run_fix(self) -> Dict[str, int]:
        """Run the complete fix process."""
        print("🔧 Fixing data directory import issues...")
        
        # Find files with issues
        files_with_issues = self.find_backend_data_references()
        
        if not files_with_issues:
            print("✅ No import issues found!")
            return {"files_checked": 0, "files_fixed": 0}
        
        print(f"📁 Found {len(files_with_issues)} files with potential issues:")
        for file_path, line_numbers in files_with_issues:
            rel_path = file_path.relative_to(self.project_root)
            print(f"   {rel_path} (lines: {', '.join(map(str, line_numbers))})")
        
        # Fix each file
        files_fixed = 0
        for file_path, _ in files_with_issues:
            if self.fix_file_references(file_path):
                files_fixed += 1
                rel_path = file_path.relative_to(self.project_root)
                print(f"   ✅ Fixed: {rel_path}")
                self.fixes_applied.append(str(rel_path))
        
        print(f"\n🎉 Fixed {files_fixed} out of {len(files_with_issues)} files")
        
        return {
            "files_checked": len(files_with_issues),
            "files_fixed": files_fixed,
            "fixes_applied": self.fixes_applied
        }

if __name__ == "__main__":
    fixer = DataImportFixer()
    results = fixer.run_fix()
    
    if results["files_fixed"] > 0:
        print("\n📝 Recommended next steps:")
        print("1. Run your test suite to verify all fixes work correctly")
        print("2. Check for any remaining manual fixes needed")
        print("3. Update any hardcoded paths in configuration files") 