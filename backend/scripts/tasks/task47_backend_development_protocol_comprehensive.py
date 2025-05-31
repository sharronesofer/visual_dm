#!/usr/bin/env python3
"""
Task 47: Backend Development Protocol - Comprehensive Implementation
This script addresses all import errors, test organization, and structural compliance issues.
"""

import os
import ast
import re
import sys
import shutil
import glob
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
import subprocess
import json

class BackendDevelopmentProtocol:
    """Comprehensive implementation of Backend Development Protocol"""
    
    def __init__(self, backend_root: str = "backend"):
        self.backend_root = Path(backend_root)
        self.systems_root = self.backend_root / "systems"
        self.tests_root = self.backend_root / "tests"
        self.issues = []
        self.fixed_files = []
        self.moved_files = []
        self.deleted_files = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with level"""
        print(f"[{level}] {message}")
        
    def collect_issues(self) -> Dict[str, List]:
        """Collect all issues in the backend structure"""
        issues = {
            "import_errors": [],
            "misplaced_tests": [],
            "duplicate_tests": [],
            "missing_init_files": [],
            "non_canonical_imports": [],
            "structural_violations": []
        }
        
        # Analyze import errors
        self.analyze_import_errors(issues)
        
        # Find misplaced tests
        self.find_misplaced_tests(issues)
        
        # Find duplicate tests
        self.find_duplicate_tests(issues)
        
        # Check for missing __init__.py files
        self.check_missing_init_files(issues)
        
        # Analyze non-canonical imports
        self.analyze_non_canonical_imports(issues)
        
        return issues
    
    def analyze_import_errors(self, issues: Dict[str, List]):
        """Analyze import errors by running a quick test collection"""
        self.log("Analyzing import errors...")
        
        # Try to collect tests to find import errors
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            str(self.tests_root), 
            "--collect-only", "-q"
        ], 
        capture_output=True, text=True, cwd=self.backend_root.parent)
        
        if result.returncode != 0:
            # Parse the error output for specific import issues
            error_lines = result.stderr.split('\n')
            for line in error_lines:
                if "ModuleNotFoundError" in line or "ImportError" in line:
                    issues["import_errors"].append(line.strip())
                    
    def find_misplaced_tests(self, issues: Dict[str, List]):
        """Find test files that are not in the correct location"""
        self.log("Finding misplaced tests...")
        
        # Look for test files in systems directories
        for system_dir in self.systems_root.iterdir():
            if system_dir.is_dir() and system_dir.name != "__pycache__":
                # Look for test or tests directories
                test_dirs = list(system_dir.glob("test*"))
                for test_dir in test_dirs:
                    if test_dir.is_dir():
                        test_files = list(test_dir.glob("**/*.py"))
                        for test_file in test_files:
                            issues["misplaced_tests"].append(str(test_file))
                            
                # Look for test files directly in system directories
                test_files = list(system_dir.glob("test_*.py"))
                for test_file in test_files:
                    issues["misplaced_tests"].append(str(test_file))
                    
    def find_duplicate_tests(self, issues: Dict[str, List]):
        """Find duplicate test files"""
        self.log("Finding duplicate tests...")
        
        test_files = {}
        
        # Collect all test files
        for test_file in self.tests_root.glob("**/test_*.py"):
            relative_name = test_file.name
            if relative_name not in test_files:
                test_files[relative_name] = []
            test_files[relative_name].append(str(test_file))
            
        # Find duplicates
        for filename, paths in test_files.items():
            if len(paths) > 1:
                issues["duplicate_tests"].append({
                    "filename": filename,
                    "paths": paths
                })
                
    def check_missing_init_files(self, issues: Dict[str, List]):
        """Check for missing __init__.py files"""
        self.log("Checking for missing __init__.py files...")
        
        # Check all directories in systems
        for root, dirs, files in os.walk(self.systems_root):
            root_path = Path(root)
            if "__init__.py" not in files and any(f.endswith('.py') for f in files):
                issues["missing_init_files"].append(str(root_path))
                
        # Check all directories in tests
        for root, dirs, files in os.walk(self.tests_root):
            root_path = Path(root)
            if "__init__.py" not in files and any(f.endswith('.py') for f in files):
                issues["missing_init_files"].append(str(root_path))
                
    def analyze_non_canonical_imports(self, issues: Dict[str, List]):
        """Analyze non-canonical imports"""
        self.log("Analyzing non-canonical imports...")
        
        # Check all Python files in systems
        for py_file in self.systems_root.glob("**/*.py"):
            self.check_file_imports(py_file, issues)
            
        # Check all Python files in tests
        for py_file in self.tests_root.glob("**/*.py"):
            self.check_file_imports(py_file, issues)
            
    def check_file_imports(self, file_path: Path, issues: Dict[str, List]):
        """Check imports in a specific file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if not self.is_canonical_import(alias.name):
                            issues["non_canonical_imports"].append({
                                "file": str(file_path),
                                "line": node.lineno,
                                "import": alias.name
                            })
                            
                elif isinstance(node, ast.ImportFrom):
                    if node.module and not self.is_canonical_import(node.module):
                        issues["non_canonical_imports"].append({
                            "file": str(file_path),
                            "line": node.lineno,
                            "import": f"from {node.module}"
                        })
                        
        except Exception as e:
            self.log(f"Error analyzing {file_path}: {e}", "WARNING")
            
    def is_canonical_import(self, import_name: str) -> bool:
        """Check if an import follows canonical format"""
        if not import_name:
            return True
            
        # Allow standard library and third-party imports
        if not import_name.startswith('backend'):
            return True
            
        # Check if it follows backend.systems.* pattern
        if import_name.startswith('backend.systems.'):
            return True
            
        # Check for relative imports (these are OK within systems)
        if import_name.startswith('.'):
            return True
            
        return False
        
    def fix_poi_service_imports(self):
        """Fix the specific POI service import issues"""
        self.log("Fixing POI service imports...")
        
        poi_services_init = self.systems_root / "poi" / "services" / "__init__.py"
        if poi_services_init.exists():
            with open(poi_services_init, 'r') as f:
                content = f.read()
                
            # Fix the imports to use relative imports
            new_content = content.replace(
                "from backend.systems.poi.poi_service import POIService",
                "from backend.systems.poi_service import POIService"
            ).replace(
                "from backend.systems.poi.poi_state_service import POIStateService",
                "from backend.systems.poi_state_service import POIStateService"
            ).replace(
                "from backend.systems.poi.metropolitan_spread_service import MetropolitanSpreadService",
                "from backend.systems.metropolitan_spread_service import MetropolitanSpreadService"
            ).replace(
                "from backend.systems.poi.faction_influence_service import FactionInfluenceService",
                "from backend.systems.faction_influence_service import FactionInfluenceService"
            ).replace(
                "from backend.systems.poi.landmark_service import LandmarkService",
                "from backend.systems.landmark_service import LandmarkService"
            ).replace(
                "from backend.systems.poi.lifecycle_events_service import POILifecycleEventsService",
                "from backend.systems.lifecycle_events_service import POILifecycleEventsService"
            ).replace(
                "from backend.systems.poi.migration_service import POIMigrationService",
                "from backend.systems.migration_service import POIMigrationService"
            ).replace(
                "from backend.systems.poi.resource_management_service import ResourceManagementService",
                "from backend.systems.resource_management_service import ResourceManagementService"
            )
            
            if new_content != content:
                with open(poi_services_init, 'w') as f:
                    f.write(new_content)
                self.fixed_files.append(str(poi_services_init))
                self.log(f"Fixed POI services imports in {poi_services_init}")
                
    def fix_all_relative_imports(self):
        """Fix all relative import issues systematically"""
        self.log("Fixing all relative import issues...")
        
        # Common patterns to fix
        patterns = [
            # POI system fixes
            (r"from backend\.systems\.poi\.([^.]+) import", r"from .\1 import"),
            (r"from backend\.systems\.economy\.([^.]+) import", r"from .\1 import"),
            (r"from backend\.systems\.faction\.([^.]+) import", r"from .\1 import"),
            (r"from backend\.systems\.equipment\.([^.]+) import", r"from .\1 import"),
            (r"from backend\.systems\.region\.([^.]+) import", r"from .\1 import"),
        ]
        
        # Fix imports in all service __init__.py files
        for system_dir in self.systems_root.iterdir():
            if system_dir.is_dir() and system_dir.name != "__pycache__":
                services_init = system_dir / "services" / "__init__.py"
                if services_init.exists():
                    self.fix_imports_in_file(services_init, patterns)
                    
    def fix_imports_in_file(self, file_path: Path, patterns: List[Tuple[str, str]]):
        """Fix imports in a specific file using regex patterns"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)
                
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixed_files.append(str(file_path))
                self.log(f"Fixed imports in {file_path}")
                
        except Exception as e:
            self.log(f"Error fixing imports in {file_path}: {e}", "ERROR")
            
    def create_missing_init_files(self, missing_dirs: List[str]):
        """Create missing __init__.py files"""
        self.log("Creating missing __init__.py files...")
        
        for dir_path in missing_dirs:
            init_file = Path(dir_path) / "__init__.py"
            if not init_file.exists():
                with open(init_file, 'w') as f:
                    f.write('"""\nModule initialization file.\n"""\n')
                self.log(f"Created {init_file}")
                
    def relocate_misplaced_tests(self, misplaced_tests: List[str]):
        """Relocate misplaced test files to the correct location"""
        self.log("Relocating misplaced test files...")
        
        for test_file_path in misplaced_tests:
            test_file = Path(test_file_path)
            
            # Determine the correct location
            relative_path = test_file.relative_to(self.systems_root)
            
            # Extract system name from path
            system_parts = relative_path.parts
            if len(system_parts) >= 1:
                system_name = system_parts[0]
                
                # Create target directory in tests
                target_dir = self.tests_root / "systems" / system_name
                target_dir.mkdir(parents=True, exist_ok=True)
                
                # Create __init__.py if needed
                init_file = target_dir / "__init__.py"
                if not init_file.exists():
                    with open(init_file, 'w') as f:
                        f.write('"""\nTest module initialization.\n"""\n')
                        
                # Move the test file
                target_file = target_dir / test_file.name
                if not target_file.exists():
                    shutil.move(str(test_file), str(target_file))
                    self.moved_files.append(f"{test_file} -> {target_file}")
                    self.log(f"Moved {test_file} to {target_file}")
                else:
                    self.log(f"Target {target_file} already exists, skipping move")
                    
    def remove_empty_test_directories(self):
        """Remove empty test directories in systems"""
        self.log("Removing empty test directories...")
        
        for system_dir in self.systems_root.iterdir():
            if system_dir.is_dir() and system_dir.name != "__pycache__":
                test_dirs = list(system_dir.glob("test*"))
                for test_dir in test_dirs:
                    if test_dir.is_dir():
                        # Check if directory is empty or only contains __pycache__
                        contents = list(test_dir.iterdir())
                        non_cache_contents = [c for c in contents if c.name != "__pycache__"]
                        
                        if not non_cache_contents:
                            shutil.rmtree(test_dir)
                            self.deleted_files.append(str(test_dir))
                            self.log(f"Removed empty test directory {test_dir}")
                            
    def remove_duplicate_tests(self, duplicate_tests: List[Dict]):
        """Remove duplicate test files, keeping the one in the correct location"""
        self.log("Removing duplicate test files...")
        
        for duplicate in duplicate_tests:
            paths = duplicate["paths"]
            
            # Prefer the one in tests/ directory
            correct_path = None
            to_remove = []
            
            for path in paths:
                if "/tests/" in path:
                    correct_path = path
                else:
                    to_remove.append(path)
                    
            # If no path is in tests/, keep the first one
            if not correct_path:
                correct_path = paths[0]
                to_remove = paths[1:]
                
            # Remove duplicates
            for path in to_remove:
                try:
                    os.remove(path)
                    self.deleted_files.append(path)
                    self.log(f"Removed duplicate test file {path}")
                except Exception as e:
                    self.log(f"Error removing {path}: {e}", "ERROR")
                    
    def fix_systems_init_file(self):
        """Fix the main systems __init__.py file"""
        self.log("Fixing main systems __init__.py file...")
        
        systems_init = self.systems_root / "__init__.py"
        if systems_init.exists():
            # Create a proper __init__.py for systems
            new_content = '''"""
Visual DM Backend Systems

This package contains the core system modules for Visual DM.
All systems follow the canonical backend.systems.* import structure.
"""

# Core event system - these are the primary exports
from backend.infrastructure.events import (
    EventBase,
    EventDispatcher,
    EventPriority,
    get_event_dispatcher,
)

# System utilities
from backend.infrastructure.shared.models.base import CoreBaseModel as BaseModel

__all__ = [
    "EventBase",
    "EventDispatcher", 
    "EventPriority",
    "get_event_dispatcher",
    "BaseModel",
]
'''
            
            with open(systems_init, 'w') as f:
                f.write(new_content)
            self.fixed_files.append(str(systems_init))
            self.log(f"Fixed systems __init__.py")
            
    def run_tests_validation(self) -> bool:
        """Run tests to validate fixes"""
        self.log("Running test validation...")
        
        # Try to collect tests
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            str(self.tests_root), 
            "--collect-only", "-q"
        ], 
        capture_output=True, text=True, cwd=self.backend_root.parent)
        
        if result.returncode == 0:
            self.log("Test collection successful!")
            return True
        else:
            self.log(f"Test collection failed: {result.stderr}", "ERROR")
            return False
            
    def generate_report(self, issues: Dict[str, List]) -> str:
        """Generate a comprehensive report"""
        report = []
        report.append("=" * 80)
        report.append("TASK 47: BACKEND DEVELOPMENT PROTOCOL - EXECUTION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Issues found
        report.append("ISSUES IDENTIFIED:")
        report.append("-" * 40)
        for issue_type, issue_list in issues.items():
            report.append(f"{issue_type.upper()}: {len(issue_list)} issues")
            
        report.append("")
        
        # Actions taken
        report.append("ACTIONS TAKEN:")
        report.append("-" * 40)
        report.append(f"Files Fixed: {len(self.fixed_files)}")
        report.append(f"Files Moved: {len(self.moved_files)}")
        report.append(f"Files Deleted: {len(self.deleted_files)}")
        
        report.append("")
        
        # Detailed actions
        if self.fixed_files:
            report.append("FIXED FILES:")
            for file_path in self.fixed_files:
                report.append(f"  - {file_path}")
            report.append("")
            
        if self.moved_files:
            report.append("MOVED FILES:")
            for move_info in self.moved_files:
                report.append(f"  - {move_info}")
            report.append("")
            
        if self.deleted_files:
            report.append("DELETED FILES/DIRECTORIES:")
            for file_path in self.deleted_files:
                report.append(f"  - {file_path}")
            report.append("")
            
        return "\n".join(report)
        
    def execute_protocol(self):
        """Execute the complete Backend Development Protocol"""
        self.log("Starting Backend Development Protocol execution...")
        
        # Phase 1: Analysis
        self.log("PHASE 1: Comprehensive Analysis")
        issues = self.collect_issues()
        
        # Phase 2: Structural Fixes
        self.log("PHASE 2: Structural Fixes")
        
        # Fix specific known issues first
        self.fix_poi_service_imports()
        self.fix_all_relative_imports()
        self.fix_systems_init_file()
        
        # Create missing __init__.py files
        if issues["missing_init_files"]:
            self.create_missing_init_files(issues["missing_init_files"])
            
        # Phase 3: Test Organization
        self.log("PHASE 3: Test Organization")
        
        # Relocate misplaced tests
        if issues["misplaced_tests"]:
            self.relocate_misplaced_tests(issues["misplaced_tests"])
            
        # Remove duplicate tests
        if issues["duplicate_tests"]:
            self.remove_duplicate_tests(issues["duplicate_tests"])
            
        # Remove empty test directories
        self.remove_empty_test_directories()
        
        # Phase 4: Validation
        self.log("PHASE 4: Validation")
        test_success = self.run_tests_validation()
        
        # Phase 5: Reporting
        self.log("PHASE 5: Report Generation")
        report = self.generate_report(issues)
        
        # Save report
        report_file = self.backend_root / "task47_execution_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
            
        self.log(f"Report saved to {report_file}")
        self.log("Backend Development Protocol execution completed!")
        
        return test_success, report

def main():
    """Main execution function"""
    protocol = BackendDevelopmentProtocol()
    success, report = protocol.execute_protocol()
    
    print("\n" + "=" * 80)
    print(report)
    print("=" * 80)
    
    if success:
        print("\n✅ Backend Development Protocol completed successfully!")
    else:
        print("\n❌ Backend Development Protocol completed with issues.")
        print("   Please review the error messages above.")
        
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 