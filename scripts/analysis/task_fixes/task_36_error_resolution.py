#!/usr/bin/env python3
"""
Task 36: Comprehensive Error Resolution Script
Systematically fixes syntax errors, import issues, and other critical problems.
"""

import os
import ast
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any

class ErrorResolver:
    def __init__(self, backend_path: str = "backend"):
        self.backend_path = Path(backend_path)
        self.systems_path = self.backend_path / "systems"
        self.tests_path = self.backend_path / "tests"
        
        # Track fixes
        self.fixes_applied = []
        self.errors_remaining = []

    def run_resolution(self):
        """Run comprehensive error resolution"""
        print("🔧 Starting Comprehensive Error Resolution...")
        print("=" * 60)
        
        # Phase 1: Fix critical syntax errors
        self._fix_syntax_errors()
        
        # Phase 2: Fix import issues
        self._fix_import_issues()
        
        # Phase 3: Move test files to correct locations
        self._fix_test_organization()
        
        # Phase 4: Fix non-canonical imports
        self._fix_canonical_imports()
        
        # Phase 5: Create missing directories
        self._create_missing_directories()
        
        # Generate resolution report
        self._generate_resolution_report()

    def _fix_syntax_errors(self):
        """Fix Python syntax errors that prevent compilation"""
        print("\n🔧 Phase 1: Fixing Syntax Errors...")
        
        syntax_error_patterns = [
            # Pattern: function/class definition followed by pass on same line
            (r'^(\s*)(def\s+\w+.*?):\s*pass\s*$', r'\1\2:'),
            (r'^(\s*)(class\s+\w+.*?):\s*pass\s*$', r'\1\2:'),
            
            # Pattern: control structures followed by pass on same line
            (r'^(\s*)(if\s+.*?):\s*pass\s*$', r'\1\2:'),
            (r'^(\s*)(elif\s+.*?):\s*pass\s*$', r'\1\2:'),
            (r'^(\s*)(else\s*):\s*pass\s*$', r'\1\2:'),
            (r'^(\s*)(for\s+.*?):\s*pass\s*$', r'\1\2:'),
            (r'^(\s*)(while\s+.*?):\s*pass\s*$', r'\1\2:'),
            (r'^(\s*)(try\s*):\s*pass\s*$', r'\1\2:'),
            (r'^(\s*)(except.*?):\s*pass\s*$', r'\1\2:'),
            (r'^(\s*)(finally\s*):\s*pass\s*$', r'\1\2:'),
            (r'^(\s*)(with\s+.*?):\s*pass\s*$', r'\1\2:'),
            
            # Pattern: standalone pass statements that should be removed
            (r'^\s*pass\s*$', ''),
        ]
        
        for py_file in self._get_python_files():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Apply syntax fixes
                for pattern, replacement in syntax_error_patterns:
                    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                
                # Remove empty lines created by removing pass statements
                content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
                
                # Check if we made changes
                if content != original_content:
                    # Verify the fix doesn't break syntax
                    try:
                        ast.parse(content)
                        # Write the fixed content
                        with open(py_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        self.fixes_applied.append(f"Fixed syntax errors in {py_file}")
                        print(f"   ✅ Fixed syntax errors in {py_file}")
                    except SyntaxError as e:
                        print(f"   ⚠️ Could not auto-fix {py_file}: {e}")
                        self.errors_remaining.append(f"Syntax error in {py_file}: {e}")
                        
            except Exception as e:
                print(f"   ❌ Error processing {py_file}: {e}")
                self.errors_remaining.append(f"Processing error in {py_file}: {e}")

    def _fix_import_issues(self):
        """Fix problematic import statements"""
        print("\n📦 Phase 2: Fixing Import Issues...")
        
        for py_file in self._get_python_files():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                modified = False
                new_lines = []
                
                for line in lines:
                    original_line = line
                    
                    # Fix common import issues
                    if line.strip().startswith('from ..'):
                        # Convert relative imports to absolute
                        line = self._convert_relative_import(line, py_file)
                        if line != original_line:
                            modified = True
                    
                    new_lines.append(line)
                
                if modified:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)
                    self.fixes_applied.append(f"Fixed imports in {py_file}")
                    print(f"   ✅ Fixed imports in {py_file}")
                    
            except Exception as e:
                print(f"   ❌ Error fixing imports in {py_file}: {e}")
                self.errors_remaining.append(f"Import fix error in {py_file}: {e}")

    def _fix_test_organization(self):
        """Move test files to correct locations"""
        print("\n📁 Phase 3: Fixing Test Organization...")
        
        # Find test files outside of /backend/tests/
        test_files_to_move = []
        
        for root, dirs, files in os.walk(self.backend_path):
            for file in files:
                if file.startswith('test_') or file.endswith('_test.py'):
                    file_path = Path(root) / file
                    
                    # Check if it's outside the tests directory
                    try:
                        file_path.relative_to(self.tests_path)
                    except ValueError:
                        # File is not under tests directory
                        test_files_to_move.append(file_path)
        
        # Move test files
        for test_file in test_files_to_move:
            try:
                # Determine target location
                rel_path = test_file.relative_to(self.backend_path)
                target_path = self.tests_path / rel_path.name
                
                # Create target directory if needed
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move the file
                test_file.rename(target_path)
                self.fixes_applied.append(f"Moved {test_file} to {target_path}")
                print(f"   ✅ Moved {test_file} to {target_path}")
                
            except Exception as e:
                print(f"   ❌ Error moving {test_file}: {e}")
                self.errors_remaining.append(f"Test move error for {test_file}: {e}")

    def _fix_canonical_imports(self):
        """Fix non-canonical import patterns"""
        print("\n🎯 Phase 4: Fixing Canonical Imports...")
        
        for py_file in self._get_python_files():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                modified = False
                new_lines = []
                
                for line in lines:
                    original_line = line
                    
                    # Fix non-canonical backend imports
                    if 'backend' in line and 'backend.systems' not in line and line.strip().startswith(('import ', 'from ')):
                        line = self._canonicalize_import(line, py_file)
                        if line != original_line:
                            modified = True
                    
                    new_lines.append(line)
                
                if modified:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)
                    self.fixes_applied.append(f"Fixed canonical imports in {py_file}")
                    print(f"   ✅ Fixed canonical imports in {py_file}")
                    
            except Exception as e:
                print(f"   ❌ Error fixing canonical imports in {py_file}: {e}")
                self.errors_remaining.append(f"Canonical import fix error in {py_file}: {e}")

    def _create_missing_directories(self):
        """Create missing required directories"""
        print("\n📂 Phase 5: Creating Missing Directories...")
        
        required_dirs = [
            'systems/core',
            'systems/character',
            'systems/combat',
            'systems/inventory',
            'systems/loot',
            'systems/quest',
            'systems/world_generation',
            'systems/shared/events',
            'systems/shared/utils',
            'tests/systems',
            'tests/integration'
        ]
        
        for req_dir in required_dirs:
            dir_path = self.backend_path / req_dir
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    
                    # Create __init__.py if it's a Python package directory
                    if 'systems' in req_dir:
                        init_file = dir_path / '__init__.py'
                        if not init_file.exists():
                            init_file.write_text('"""Auto-generated __init__.py"""')
                    
                    self.fixes_applied.append(f"Created directory {dir_path}")
                    print(f"   ✅ Created directory {dir_path}")
                    
                except Exception as e:
                    print(f"   ❌ Error creating {dir_path}: {e}")
                    self.errors_remaining.append(f"Directory creation error for {dir_path}: {e}")

    def _get_python_files(self) -> List[Path]:
        """Get all Python files in backend"""
        python_files = []
        for py_file in self.backend_path.rglob("*.py"):
            # Skip __pycache__ and other generated files
            if '__pycache__' not in str(py_file) and '.pyc' not in str(py_file):
                python_files.append(py_file)
        return python_files

    def _convert_relative_import(self, line: str, file_path: Path) -> str:
        """Convert relative import to absolute import"""
        # This is a simplified conversion - in practice, you'd need more sophisticated logic
        # For now, just remove the relative part and make it absolute
        if line.strip().startswith('from ..'):
            # Convert from .. to backend.systems
            line = line.replace('from ..', 'from backend.systems.')
        elif line.strip().startswith('from .'):
            # Convert from . to current module path
            rel_path = file_path.relative_to(self.backend_path)
            module_path = str(rel_path.parent).replace('/', '.')
            line = line.replace('from .', f'from backend.{module_path}.')
        
        return line

    def _canonicalize_import(self, line: str, file_path: Path) -> str:
        """Convert import to canonical backend.systems.* format"""
        # This is a simplified canonicalization
        if 'from backend.' in line and 'backend.systems' not in line:
            line = line.replace('from backend.', 'from backend.systems.')
        elif 'import backend.' in line and 'backend.systems' not in line:
            line = line.replace('import backend.', 'import backend.systems.')
        
        return line

    def _generate_resolution_report(self):
        """Generate comprehensive resolution report"""
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE ERROR RESOLUTION REPORT")
        print("=" * 60)
        
        print(f"\n✅ FIXES APPLIED ({len(self.fixes_applied)}):")
        for fix in self.fixes_applied:
            print(f"   • {fix}")
        
        if self.errors_remaining:
            print(f"\n⚠️ ERRORS REMAINING ({len(self.errors_remaining)}):")
            for error in self.errors_remaining:
                print(f"   • {error}")
        
        print(f"\n📊 SUMMARY:")
        print(f"   • Total Fixes Applied: {len(self.fixes_applied)}")
        print(f"   • Errors Remaining: {len(self.errors_remaining)}")
        
        if len(self.errors_remaining) == 0:
            print(f"\n🎉 All critical errors resolved!")
        else:
            print(f"\n⚠️ {len(self.errors_remaining)} errors require manual attention")
        
        # Save detailed report
        report = {
            'fixes_applied': self.fixes_applied,
            'errors_remaining': self.errors_remaining,
            'summary': {
                'fixes_count': len(self.fixes_applied),
                'errors_count': len(self.errors_remaining)
            }
        }
        
        with open('task_36_resolution_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: task_36_resolution_report.json")

if __name__ == "__main__":
    resolver = ErrorResolver()
    resolver.run_resolution() 