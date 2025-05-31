#!/usr/bin/env python3
"""
Task 47: Backend Development Protocol Implementation

This script implements comprehensive backend development protocol compliance:
1. Assessment and Error Resolution for /backend/systems/ and /backend/tests/
2. Structure and Organization Enforcement
3. Canonical Imports Enforcement
4. Module and Function Development protocols
5. Quality and Integration Standards

All operations follow Development_Bible.md and backend_systems_inventory.md
"""

import os
import sys
import shutil
import subprocess
import json
import glob
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ImportIssue:
    """Represents an import issue found in the codebase."""
    file_path: str
    line_number: int
    line_content: str
    issue_type: str
    suggested_fix: str

@dataclass
class TestIssue:
    """Represents a test organization issue."""
    file_path: str
    issue_type: str
    suggested_action: str

@dataclass
class ComplianceIssue:
    """Represents a Development_Bible.md compliance issue."""
    file_path: str
    issue_type: str
    description: str
    severity: str

class BackendDevelopmentProtocol:
    """Implements the comprehensive backend development protocol."""
    
    def __init__(self, backend_path: str = "backend"):
        self.backend_path = Path(backend_path)
        self.systems_path = self.backend_path / "systems"
        self.tests_path = self.backend_path / "tests"
        self.import_issues: List[ImportIssue] = []
        self.test_issues: List[TestIssue] = []
        self.compliance_issues: List[ComplianceIssue] = []
        self.fixed_files: Set[str] = set()
        
    def run_assessment(self) -> Dict:
        """Run comprehensive assessment of backend systems."""
        logger.info("Starting Backend Development Protocol Assessment...")
        
        # 1. Assessment and Error Resolution
        self._assess_import_issues()
        self._assess_test_organization()
        self._assess_compliance_issues()
        
        # 2. Structure and Organization Enforcement
        self._enforce_test_structure()
        self._remove_invalid_test_locations()
        self._identify_duplicates()
        
        # 3. Canonical Imports Enforcement
        self._fix_canonical_imports()
        self._eliminate_orphan_dependencies()
        
        # 4. Generate compliance report
        return self._generate_report()
    
    def _assess_import_issues(self):
        """Assess and catalog import issues across the codebase."""
        logger.info("Assessing import issues...")
        
        # Find all Python files
        python_files = list(self.backend_path.rglob("*.py"))
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for i, line in enumerate(lines, 1):
                    line = line.strip()
                    if self._is_problematic_import(line):
                        issue = ImportIssue(
                            file_path=str(file_path),
                            line_number=i,
                            line_content=line,
                            issue_type=self._categorize_import_issue(line),
                            suggested_fix=self._suggest_import_fix(line)
                        )
                        self.import_issues.append(issue)
                        
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
    
    def _is_problematic_import(self, line: str) -> bool:
        """Check if an import line is problematic."""
        if not (line.startswith('from ') or line.startswith('import ')):
            return False
            
        # Check for common problematic patterns
        problematic_patterns = [
            r'from backend\.systems\.shared\.time_utils',  # Non-existent module
            r'from backend\.systems\.shared\.json_storage_utils',  # Wrong path
            r'from backend\.systems\.shared\.dictionary_utils',  # Wrong path
            r'from backend\.systems\.shared\.firebase_utils',  # Wrong path
            r'from backend\.systems\.shared\.base_manager',  # Wrong path
            r'import backend\.systems\.__init__',  # Invalid import pattern
            r'from \.\.utils\.',  # Relative import to utils
            r'from backend\.utils\.',  # Non-canonical utils import
        ]
        
        for pattern in problematic_patterns:
            if re.search(pattern, line):
                return True
                
        return False
    
    def _categorize_import_issue(self, line: str) -> str:
        """Categorize the type of import issue."""
        if 'time_utils' in line:
            return "wrong_path_time_utils"
        elif 'json_storage_utils' in line:
            return "wrong_path_json_storage_utils"
        elif 'dictionary_utils' in line:
            return "wrong_path_dictionary_utils"
        elif 'firebase_utils' in line:
            return "wrong_path_firebase_utils"
        elif 'base_manager' in line:
            return "wrong_path_base_manager"
        elif '__init__' in line:
            return "invalid_init_import"
        elif '../utils' in line:
            return "relative_utils_import"
        elif 'backend.utils' in line:
            return "non_canonical_utils_import"
        else:
            return "unknown_import_issue"
    
    def _suggest_import_fix(self, line: str) -> str:
        """Suggest a fix for the problematic import."""
        fixes = {
            "wrong_path_time_utils": "from backend.infrastructure.shared.utils.core.time_utils",
            "wrong_path_json_storage_utils": "from backend.infrastructure.shared.utils.core.json_storage_utils",
            "wrong_path_dictionary_utils": "from backend.infrastructure.shared.utils.core.dictionary_utils", 
            "wrong_path_firebase_utils": "from backend.infrastructure.shared.utils.core.firebase_utils",
            "wrong_path_base_manager": "from backend.infrastructure.shared.utils.core.base_manager",
            "invalid_init_import": "# Remove this invalid import",
            "relative_utils_import": "# Convert to canonical backend.systems.* import",
            "non_canonical_utils_import": "# Convert to canonical backend.systems.* import"
        }
        
        issue_type = self._categorize_import_issue(line)
        return fixes.get(issue_type, "# Review and fix this import")
    
    def _assess_test_organization(self):
        """Assess test file organization and structure."""
        logger.info("Assessing test organization...")
        
        # Find test files in wrong locations
        invalid_test_locations = []
        
        # Check for test files in /backend/systems/*/test(s) directories
        test_dirs_in_systems = list(self.systems_path.rglob("test*"))
        for test_dir in test_dirs_in_systems:
            if test_dir.is_dir():
                test_files = list(test_dir.rglob("test_*.py"))
                for test_file in test_files:
                    issue = TestIssue(
                        file_path=str(test_file),
                        issue_type="invalid_location",
                        suggested_action=f"Move to {self.tests_path}"
                    )
                    self.test_issues.append(issue)
        
        # Check for duplicate tests
        self._find_duplicate_tests()
    
    def _find_duplicate_tests(self):
        """Find duplicate test files."""
        logger.info("Finding duplicate tests...")
        
        # Get all test files
        test_files = list(self.backend_path.rglob("test_*.py"))
        
        # Group by basename
        basename_groups = {}
        for test_file in test_files:
            basename = test_file.name
            if basename not in basename_groups:
                basename_groups[basename] = []
            basename_groups[basename].append(test_file)
        
        # Find duplicates
        for basename, files in basename_groups.items():
            if len(files) > 1:
                for i, file_path in enumerate(files[1:], 1):  # Keep first, mark others as duplicates
                    issue = TestIssue(
                        file_path=str(file_path),
                        issue_type="duplicate",
                        suggested_action=f"Compare with {files[0]} and delete if duplicate"
                    )
                    self.test_issues.append(issue)
    
    def _assess_compliance_issues(self):
        """Assess compliance with Development_Bible.md."""
        logger.info("Assessing Development_Bible.md compliance...")
        
        # Check for common compliance issues
        python_files = list(self.backend_path.rglob("*.py"))
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for missing docstrings
                if not content.strip().startswith('"""') and not content.strip().startswith("'''"):
                    if 'def ' in content or 'class ' in content:
                        issue = ComplianceIssue(
                            file_path=str(file_path),
                            issue_type="missing_module_docstring",
                            description="Module lacks proper docstring",
                            severity="medium"
                        )
                        self.compliance_issues.append(issue)
                
                # Check for proper async patterns
                if 'def ' in content and 'async def' not in content and 'FastAPI' in str(file_path):
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if 'def ' in line and 'router' in line.lower():
                            issue = ComplianceIssue(
                                file_path=str(file_path),
                                issue_type="missing_async_pattern",
                                description=f"Line {i}: Router endpoint should be async",
                                severity="high"
                            )
                            self.compliance_issues.append(issue)
                            
            except Exception as e:
                logger.error(f"Error assessing compliance for {file_path}: {e}")
    
    def _enforce_test_structure(self):
        """Enforce proper test structure organization."""
        logger.info("Enforcing test structure...")
        
        # Ensure tests directory exists
        self.tests_path.mkdir(exist_ok=True)
        
        # Create __init__.py if missing
        init_file = self.tests_path / "__init__.py"
        if not init_file.exists():
            with open(init_file, 'w') as f:
                f.write('"""Backend tests package."""\n')
    
    def _remove_invalid_test_locations(self):
        """Remove or relocate test files from invalid locations."""
        logger.info("Removing invalid test locations...")
        
        for issue in self.test_issues:
            if issue.issue_type == "invalid_location":
                source_path = Path(issue.file_path)
                if source_path.exists():
                    # Determine target path in tests directory
                    relative_path = source_path.relative_to(self.systems_path)
                    target_path = self.tests_path / relative_path
                    
                    # Create target directory
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move the file
                    try:
                        shutil.move(str(source_path), str(target_path))
                        logger.info(f"Moved {source_path} to {target_path}")
                        self.fixed_files.add(str(source_path))
                    except Exception as e:
                        logger.error(f"Error moving {source_path}: {e}")
    
    def _identify_duplicates(self):
        """Identify and handle duplicate files."""
        logger.info("Identifying duplicates...")
        
        # For now, just log duplicates - manual review needed
        duplicates = [issue for issue in self.test_issues if issue.issue_type == "duplicate"]
        if duplicates:
            logger.warning(f"Found {len(duplicates)} duplicate test files - manual review required")
    
    def _fix_canonical_imports(self):
        """Fix canonical import issues."""
        logger.info("Fixing canonical imports...")
        
        # First, fix the core issue in shared/utils/core/__init__.py
        self._fix_shared_utils_core_init()
        
        # Then fix other import issues
        for issue in self.import_issues:
            self._fix_import_issue(issue)
    
    def _fix_shared_utils_core_init(self):
        """Fix the core import issue in shared/utils/core/__init__.py."""
        file_path = self.systems_path / "shared" / "utils" / "core" / "__init__.py"
        
        if not file_path.exists():
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix the problematic imports
            fixes = [
                ("from backend.infrastructure.shared.time_utils", 
                 "from backend.infrastructure.shared.utils.core.time_utils"),
                ("from backend.infrastructure.shared.json_storage_utils", 
                 "from backend.infrastructure.shared.utils.core.json_storage_utils"),
                ("from backend.infrastructure.shared.dictionary_utils", 
                 "from backend.infrastructure.shared.utils.core.dictionary_utils"),
                ("from backend.infrastructure.shared.firebase_utils", 
                 "from backend.infrastructure.shared.utils.core.firebase_utils"),
                ("from backend.infrastructure.shared.base_manager", 
                 "from backend.infrastructure.shared.utils.core.base_manager"),
            ]
            
            for old_import, new_import in fixes:
                content = content.replace(old_import, new_import)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.info(f"Fixed imports in {file_path}")
            self.fixed_files.add(str(file_path))
            
        except Exception as e:
            logger.error(f"Error fixing {file_path}: {e}")
    
    def _fix_import_issue(self, issue: ImportIssue):
        """Fix a specific import issue."""
        file_path = Path(issue.file_path)
        
        if not file_path.exists() or str(file_path) in self.fixed_files:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Apply the fix
            if issue.line_number <= len(lines):
                old_line = lines[issue.line_number - 1]
                if issue.suggested_fix.startswith("#"):
                    # Comment out or remove the line
                    lines[issue.line_number - 1] = f"# {old_line}"
                else:
                    # Replace with suggested fix
                    # Extract the imported items
                    import_items = self._extract_import_items(old_line)
                    new_line = f"{issue.suggested_fix} import {import_items}\n"
                    lines[issue.line_number - 1] = new_line
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
                
            self.fixed_files.add(str(file_path))
            logger.info(f"Fixed import in {file_path}:{issue.line_number}")
            
        except Exception as e:
            logger.error(f"Error fixing import in {file_path}: {e}")
    
    def _extract_import_items(self, import_line: str) -> str:
        """Extract the items being imported from an import line."""
        if " import " in import_line:
            return import_line.split(" import ", 1)[1].strip()
        else:
            # Handle 'import module' case
            return import_line.replace("import ", "").strip()
    
    def _eliminate_orphan_dependencies(self):
        """Eliminate orphan or non-canonical module dependencies."""
        logger.info("Eliminating orphan dependencies...")
        
        # Check for imports from non-existent modules
        for issue in self.import_issues:
            if "non_canonical" in issue.issue_type or "orphan" in issue.issue_type:
                self._fix_import_issue(issue)
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if a file should be skipped during processing."""
        skip_patterns = [
            "__pycache__",
            ".pyc",
            ".git",
            "htmlcov",
            ".pytest_cache",
            "logs",
            "analytics_data"
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _generate_report(self) -> Dict:
        """Generate comprehensive assessment report."""
        logger.info("Generating assessment report...")
        
        report = {
            "assessment_summary": {
                "total_import_issues": len(self.import_issues),
                "total_test_issues": len(self.test_issues),
                "total_compliance_issues": len(self.compliance_issues),
                "files_fixed": len(self.fixed_files)
            },
            "import_issues": [
                {
                    "file": issue.file_path,
                    "line": issue.line_number,
                    "type": issue.issue_type,
                    "original": issue.line_content,
                    "suggested_fix": issue.suggested_fix
                }
                for issue in self.import_issues
            ],
            "test_issues": [
                {
                    "file": issue.file_path,
                    "type": issue.issue_type,
                    "action": issue.suggested_action
                }
                for issue in self.test_issues
            ],
            "compliance_issues": [
                {
                    "file": issue.file_path,
                    "type": issue.issue_type,
                    "description": issue.description,
                    "severity": issue.severity
                }
                for issue in self.compliance_issues
            ],
            "fixed_files": list(self.fixed_files)
        }
        
        return report
    
    def run_tests(self) -> Dict:
        """Run comprehensive test suite to verify fixes."""
        logger.info("Running test suite to verify fixes...")
        
        try:
            # Run pytest with coverage
            result = subprocess.run([
                "python", "-m", "pytest", 
                str(self.tests_path),
                "--tb=short",
                "-v",
                "--maxfail=10"
            ], 
            capture_output=True, 
            text=True, 
            cwd=str(self.backend_path)
            )
            
            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
            
        except Exception as e:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False
            }
    
    def save_report(self, report: Dict, filename: str = "task47_backend_protocol_report.json"):
        """Save the assessment report to file."""
        output_path = self.backend_path / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Report saved to {output_path}")

def main():
    """Main execution function."""
    protocol = BackendDevelopmentProtocol()
    
    # Run assessment and fixes
    report = protocol.run_assessment()
    
    # Save initial report
    protocol.save_report(report, "task47_backend_protocol_assessment.json")
    
    # Run tests to verify fixes
    test_results = protocol.run_tests()
    report["test_results"] = test_results
    
    # Save final report
    protocol.save_report(report, "task47_backend_protocol_final_report.json")
    
    # Print summary
    print("\n" + "="*60)
    print("BACKEND DEVELOPMENT PROTOCOL - TASK 47 SUMMARY")
    print("="*60)
    print(f"Import Issues Found: {report['assessment_summary']['total_import_issues']}")
    print(f"Test Issues Found: {report['assessment_summary']['total_test_issues']}")
    print(f"Compliance Issues Found: {report['assessment_summary']['total_compliance_issues']}")
    print(f"Files Fixed: {report['assessment_summary']['files_fixed']}")
    print(f"Test Suite Result: {'PASSED' if test_results['success'] else 'FAILED'}")
    print("="*60)
    
    if test_results['success']:
        print("✅ Backend Development Protocol implementation completed successfully!")
    else:
        print("⚠️  Backend Development Protocol completed with test failures - manual review required")
        print("\nTest output (last 20 lines):")
        print("\n".join(test_results['stderr'].split('\n')[-20:]))

if __name__ == "__main__":
    main() 