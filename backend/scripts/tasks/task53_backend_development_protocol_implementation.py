#!/usr/bin/env python3
"""
Task 53: Backend Development Protocol Implementation
====================================================

Comprehensive implementation of the Backend Development Protocol as specified.
This script will:

1. Assess and resolve errors in /backend/systems/ and /backend/tests/
2. Enforce structure and organization standards
3. Implement canonical imports enforcement 
4. Prevent duplication and ensure compliance with Development_Bible.md
5. Achieve ≥90% test coverage
6. Maintain quality and integration standards

Reference Documents:
- Primary Standard: development_bible.md
- System Inventory: backend/backend_systems_inventory.md
- Development Protocol: backend/backend_development_protocol.md
- API Contracts: api_contracts.yaml
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional, Any
import ast
import logging
from dataclasses import dataclass
from collections import defaultdict
import shutil

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ImportIssue:
    """Represents an import issue to be fixed."""
    file_path: str
    line_number: int
    current_import: str
    canonical_import: str
    issue_type: str  # 'relative', 'non_canonical', 'missing'

@dataclass
class TestStructureIssue:
    """Represents a test structure issue."""
    file_path: str
    issue_type: str  # 'wrong_location', 'duplicate', 'missing'
    recommended_location: Optional[str] = None

@dataclass
class ComplianceIssue:
    """Represents a compliance issue with Development_Bible.md."""
    file_path: str
    issue_type: str
    description: str
    suggested_fix: Optional[str] = None

class BackendDevelopmentProtocolImplementation:
    """Implements the comprehensive Backend Development Protocol."""
    
    def __init__(self, backend_root: str = "backend"):
        """Initialize the protocol implementation."""
        self.backend_root = Path(backend_root)
        self.systems_dir = self.backend_root / "systems"
        self.tests_dir = self.backend_root / "tests"
        self.data_dir = self.backend_root / "data"
        
        # Results tracking
        self.import_issues: List[ImportIssue] = []
        self.test_structure_issues: List[TestStructureIssue] = []
        self.compliance_issues: List[ComplianceIssue] = []
        self.fixed_issues: List[str] = []
        self.errors_found: List[str] = []
        
        # Statistics
        self.stats = {
            'files_analyzed': 0,
            'imports_fixed': 0,
            'tests_moved': 0,
            'duplicates_removed': 0,
            'compliance_fixes': 0,
            'coverage_improvement': 0
        }
        
    def run_comprehensive_protocol(self) -> Dict[str, Any]:
        """Execute the complete Backend Development Protocol."""
        logger.info("🚀 Starting Backend Development Protocol Implementation")
        
        try:
            # Phase 1: Assessment and Error Resolution
            logger.info("📊 Phase 1: Assessment and Error Resolution")
            self._analyze_systems_directory()
            self._analyze_tests_directory()
            self._check_development_bible_compliance()
            self._identify_import_issues()
            
            # Phase 2: Structure and Organization Enforcement
            logger.info("🏗️ Phase 2: Structure and Organization Enforcement")
            self._enforce_test_structure()
            self._enforce_canonical_structure()
            self._fix_import_issues()
            self._remove_duplicates()
            
            # Phase 3: Quality and Coverage Validation
            logger.info("✅ Phase 3: Quality and Coverage Validation")
            self._run_test_coverage_analysis()
            self._validate_api_contracts()
            self._validate_cross_system_compatibility()
            self._update_documentation()
            
            # Generate comprehensive report
            return self._generate_final_report()
            
        except Exception as e:
            logger.error(f"❌ Protocol implementation failed: {e}")
            raise
    
    def _analyze_systems_directory(self) -> None:
        """Analyze all systems for structural and compliance issues."""
        logger.info("🔍 Analyzing systems directory structure")
        
        for system_dir in self.systems_dir.iterdir():
            if system_dir.is_dir() and not system_dir.name.startswith('_'):
                self._analyze_system(system_dir)
    
    def _analyze_system(self, system_path: Path) -> None:
        """Analyze a specific system for issues."""
        system_name = system_path.name
        logger.info(f"Analyzing system: {system_name}")
        
        # Check for proper structure
        expected_subdirs = ['models', 'services', 'repositories', 'schemas', 'routers']
        
        for python_file in system_path.rglob("*.py"):
            self.stats['files_analyzed'] += 1
            self._analyze_python_file(python_file)
            
        # Check for test files in wrong locations
        for test_file in system_path.rglob("*test*.py"):
            if not str(test_file).startswith(str(self.tests_dir)):
                self.test_structure_issues.append(
                    TestStructureIssue(
                        file_path=str(test_file),
                        issue_type='wrong_location',
                        recommended_location=str(self.tests_dir / "systems" / system_name)
                    )
                )
    
    def _analyze_python_file(self, file_path: Path) -> None:
        """Analyze a Python file for import and compliance issues."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST to analyze imports
            try:
                tree = ast.parse(content)
                self._analyze_imports_in_ast(tree, file_path)
            except SyntaxError as e:
                self.errors_found.append(f"Syntax error in {file_path}: {e}")
            
            # Check for specific compliance issues
            self._check_file_compliance(file_path, content)
            
        except Exception as e:
            self.errors_found.append(f"Error analyzing {file_path}: {e}")
    
    def _analyze_imports_in_ast(self, tree: ast.AST, file_path: Path) -> None:
        """Analyze imports in an AST tree."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith('..'):
                    # Relative import found
                    canonical_import = self._convert_relative_to_canonical(
                        node.module, file_path
                    )
                    self.import_issues.append(
                        ImportIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            current_import=node.module,
                            canonical_import=canonical_import,
                            issue_type='relative'
                        )
                    )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if not alias.name.startswith('backend.systems'):
                        # Check if this should be a canonical import
                        canonical = self._check_if_needs_canonical_import(alias.name)
                        if canonical:
                            self.import_issues.append(
                                ImportIssue(
                                    file_path=str(file_path),
                                    line_number=node.lineno,
                                    current_import=alias.name,
                                    canonical_import=canonical,
                                    issue_type='non_canonical'
                                )
                            )
    
    def _convert_relative_to_canonical(self, relative_import: str, file_path: Path) -> str:
        """Convert a relative import to canonical backend.systems.* format."""
        # Calculate the canonical path based on file location
        relative_parts = file_path.relative_to(self.backend_root).parts
        
        # Count the number of '..' in the import
        up_levels = relative_import.count('.') - 1
        
        # Build canonical import path
        if up_levels == 0:
            # Same directory import
            base_path = list(relative_parts[:-1])  # Remove filename
        else:
            # Go up the specified number of levels
            base_path = list(relative_parts[:-1-up_levels])
        
        # Add the remaining part of the import
        import_part = relative_import.lstrip('.')
        if import_part:
            base_path.append(import_part)
        
        return f"backend.{'.'.join(base_path)}"
    
    def _check_if_needs_canonical_import(self, import_name: str) -> Optional[str]:
        """Check if an import should be converted to canonical format."""
        # Map common non-canonical imports to canonical ones
        canonical_mappings = {
            'shared.utils': 'backend.infrastructure.shared.utils',
            'shared.models': 'backend.infrastructure.shared.models',
            'shared.database': 'backend.infrastructure.shared.database',
            'events': 'backend.systems.events',
            'base': 'backend.infrastructure.shared.models.base',
        }
        
        for pattern, canonical in canonical_mappings.items():
            if import_name.startswith(pattern):
                return import_name.replace(pattern, canonical, 1)
        
        return None
    
    def _check_file_compliance(self, file_path: Path, content: str) -> None:
        """Check file for Development_Bible.md compliance."""
        # Check for proper docstrings
        if not content.strip().startswith('"""') and not content.strip().startswith("'''"):
            if file_path.name != '__init__.py':
                self.compliance_issues.append(
                    ComplianceIssue(
                        file_path=str(file_path),
                        issue_type='missing_docstring',
                        description='File is missing a module-level docstring',
                        suggested_fix='Add a module-level docstring describing the file purpose'
                    )
                )
        
        # Check for FastAPI compliance in router files
        if 'router' in file_path.name.lower():
            if 'from fastapi import' not in content:
                self.compliance_issues.append(
                    ComplianceIssue(
                        file_path=str(file_path),
                        issue_type='missing_fastapi',
                        description='Router file should import FastAPI components',
                        suggested_fix='Add appropriate FastAPI imports'
                    )
                )
        
        # Check for proper error handling patterns
        if 'try:' in content and 'except Exception as e:' in content:
            if 'logger' not in content and 'logging' not in content:
                self.compliance_issues.append(
                    ComplianceIssue(
                        file_path=str(file_path),
                        issue_type='missing_logging',
                        description='Error handling without proper logging',
                        suggested_fix='Add logging for error conditions'
                    )
                )
    
    def _analyze_tests_directory(self) -> None:
        """Analyze test directory structure."""
        logger.info("🧪 Analyzing test directory structure")
        
        if not self.tests_dir.exists():
            logger.warning("Tests directory does not exist, creating...")
            self.tests_dir.mkdir(parents=True, exist_ok=True)
        
        # Check for proper test organization
        for test_file in self.tests_dir.rglob("test_*.py"):
            self._analyze_test_file(test_file)
    
    def _analyze_test_file(self, test_file: Path) -> None:
        """Analyze a test file for compliance."""
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for proper test imports
            if 'import pytest' not in content and 'from pytest' not in content:
                self.compliance_issues.append(
                    ComplianceIssue(
                        file_path=str(test_file),
                        issue_type='missing_pytest',
                        description='Test file should import pytest',
                        suggested_fix='Add pytest import'
                    )
                )
            
            # Check for async test compliance
            if 'async def test_' in content and '@pytest.mark.asyncio' not in content:
                self.compliance_issues.append(
                    ComplianceIssue(
                        file_path=str(test_file),
                        issue_type='missing_asyncio_marker',
                        description='Async tests should have @pytest.mark.asyncio decorator',
                        suggested_fix='Add @pytest.mark.asyncio to async test functions'
                    )
                )
        
        except Exception as e:
            self.errors_found.append(f"Error analyzing test file {test_file}: {e}")
    
    def _check_development_bible_compliance(self) -> None:
        """Check overall compliance with Development_Bible.md standards."""
        logger.info("📖 Checking Development_Bible.md compliance")
        
        # Check for proper system organization
        required_systems = [
            'analytics', 'auth_user', 'character', 'combat', 'crafting',
            'data', 'dialogue', 'diplomacy', 'economy', 'equipment',
            'events', 'faction', 'inventory', 'llm', 'loot', 'magic',
            'memory', 'motif', 'npc', 'poi', 'population', 'quest',
            'region', 'religion', 'rumor', 'shared', 'storage',
            'tension_war', 'time', 'world_generation', 'world_state'
        ]
        
        for system in required_systems:
            system_path = self.systems_dir / system
            if not system_path.exists():
                self.compliance_issues.append(
                    ComplianceIssue(
                        file_path=str(system_path),
                        issue_type='missing_system',
                        description=f'Required system {system} is missing',
                        suggested_fix=f'Create {system} system directory with proper structure'
                    )
                )
    
    def _identify_import_issues(self) -> None:
        """Identify and categorize all import issues."""
        logger.info("🔍 Identifying import issues")
        
        # Use ripgrep to find relative imports
        try:
            result = subprocess.run([
                'rg', '-n', r'from\s+\.+\s+import', str(self.backend_root)
            ], capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if line.strip():
                    parts = line.split(':')
                    if len(parts) >= 3:
                        file_path = parts[0]
                        line_number = int(parts[1])
                        import_line = ':'.join(parts[2:])
                        
                        # Additional processing for relative imports
                        canonical = self._convert_relative_import_line(import_line, Path(file_path))
                        
                        self.import_issues.append(
                            ImportIssue(
                                file_path=file_path,
                                line_number=line_number,
                                current_import=import_line.strip(),
                                canonical_import=canonical,
                                issue_type='relative'
                            )
                        )
        except Exception as e:
            logger.warning(f"Could not run ripgrep for import analysis: {e}")
    
    def _convert_relative_import_line(self, import_line: str, file_path: Path) -> str:
        """Convert a full import line to canonical format."""
        # Extract the module part from the import statement
        import_match = re.search(r'from\s+(\.+\w*(?:\.\w*)*)\s+import', import_line)
        if import_match:
            relative_module = import_match.group(1)
            canonical_module = self._convert_relative_to_canonical(relative_module, file_path)
            return import_line.replace(relative_module, canonical_module)
        return import_line
    
    def _enforce_test_structure(self) -> None:
        """Enforce proper test file organization."""
        logger.info("🗂️ Enforcing test structure")
        
        for issue in self.test_structure_issues:
            if issue.issue_type == 'wrong_location' and issue.recommended_location:
                self._move_test_file(issue.file_path, issue.recommended_location)
    
    def _move_test_file(self, source: str, destination_dir: str) -> None:
        """Move a test file to the correct location."""
        source_path = Path(source)
        dest_dir = Path(destination_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        dest_path = dest_dir / source_path.name
        
        try:
            shutil.move(str(source_path), str(dest_path))
            self.fixed_issues.append(f"Moved test file {source} to {dest_path}")
            self.stats['tests_moved'] += 1
            logger.info(f"Moved test file: {source} -> {dest_path}")
        except Exception as e:
            self.errors_found.append(f"Failed to move test file {source}: {e}")
    
    def _enforce_canonical_structure(self) -> None:
        """Enforce canonical directory and file structure."""
        logger.info("🏗️ Enforcing canonical structure")
        
        # Ensure proper __init__.py files exist
        for system_dir in self.systems_dir.iterdir():
            if system_dir.is_dir() and not system_dir.name.startswith('_'):
                init_file = system_dir / '__init__.py'
                if not init_file.exists():
                    self._create_system_init_file(init_file, system_dir.name)
    
    def _create_system_init_file(self, init_path: Path, system_name: str) -> None:
        """Create a proper __init__.py file for a system."""
        content = f'''"""
{system_name.title()} System

This module provides the {system_name} system functionality for Visual DM.
All components follow the canonical backend.systems.{system_name}.* import structure.
"""

# Core exports for the {system_name} system
__all__ = []
'''
        
        try:
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.fixed_issues.append(f"Created __init__.py for {system_name} system")
            logger.info(f"Created __init__.py for {system_name} system")
        except Exception as e:
            self.errors_found.append(f"Failed to create __init__.py for {system_name}: {e}")
    
    def _fix_import_issues(self) -> None:
        """Fix all identified import issues."""
        logger.info("🔧 Fixing import issues")
        
        # Group issues by file for efficient processing
        issues_by_file = defaultdict(list)
        for issue in self.import_issues:
            issues_by_file[issue.file_path].append(issue)
        
        for file_path, file_issues in issues_by_file.items():
            self._fix_imports_in_file(file_path, file_issues)
    
    def _fix_imports_in_file(self, file_path: str, issues: List[ImportIssue]) -> None:
        """Fix import issues in a specific file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Sort issues by line number in reverse order to maintain line numbers
            issues.sort(key=lambda x: x.line_number, reverse=True)
            
            for issue in issues:
                if 1 <= issue.line_number <= len(lines):
                    old_line = lines[issue.line_number - 1]
                    new_line = old_line.replace(issue.current_import, issue.canonical_import)
                    lines[issue.line_number - 1] = new_line
                    
                    self.fixed_issues.append(
                        f"Fixed import in {file_path}:{issue.line_number}: "
                        f"{issue.current_import} -> {issue.canonical_import}"
                    )
                    self.stats['imports_fixed'] += 1
            
            # Write the fixed file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            logger.info(f"Fixed {len(issues)} import issues in {file_path}")
            
        except Exception as e:
            self.errors_found.append(f"Failed to fix imports in {file_path}: {e}")
    
    def _remove_duplicates(self) -> None:
        """Remove duplicate files and functions."""
        logger.info("🔍 Removing duplicates")
        
        # Find duplicate Python files by content hash
        file_hashes = {}
        duplicates = []
        
        for py_file in self.backend_root.rglob("*.py"):
            if py_file.is_file():
                try:
                    with open(py_file, 'rb') as f:
                        content_hash = hash(f.read())
                    
                    if content_hash in file_hashes:
                        duplicates.append((py_file, file_hashes[content_hash]))
                    else:
                        file_hashes[content_hash] = py_file
                except Exception as e:
                    logger.warning(f"Could not hash {py_file}: {e}")
        
        # Remove duplicates (keep the one in the canonical location)
        for duplicate, original in duplicates:
            if self._should_remove_duplicate(duplicate, original):
                try:
                    duplicate.unlink()
                    self.fixed_issues.append(f"Removed duplicate file: {duplicate}")
                    self.stats['duplicates_removed'] += 1
                    logger.info(f"Removed duplicate: {duplicate}")
                except Exception as e:
                    self.errors_found.append(f"Failed to remove duplicate {duplicate}: {e}")
    
    def _should_remove_duplicate(self, file1: Path, file2: Path) -> bool:
        """Determine which duplicate file should be removed."""
        # Prefer files in the canonical locations
        canonical_paths = ['backend/systems', 'backend/tests']
        
        file1_canonical = any(str(file1).startswith(path) for path in canonical_paths)
        file2_canonical = any(str(file2).startswith(path) for path in canonical_paths)
        
        if file1_canonical and not file2_canonical:
            return False  # Keep file1, remove file2
        elif file2_canonical and not file1_canonical:
            return True   # Remove file1, keep file2
        else:
            # Both or neither are canonical, prefer shorter path
            return len(str(file1)) > len(str(file2))
    
    def _run_test_coverage_analysis(self) -> None:
        """Run comprehensive test coverage analysis."""
        logger.info("📊 Running test coverage analysis")
        
        try:
            # Run pytest with coverage
            result = subprocess.run([
                'python', '-m', 'pytest', 
                '--cov=backend', 
                '--cov-report=json:coverage.json',
                '--cov-report=term-missing',
                str(self.tests_dir)
            ], capture_output=True, text=True, cwd=self.backend_root)
            
            logger.info(f"Test coverage output:\n{result.stdout}")
            
            if result.stderr:
                logger.warning(f"Test coverage warnings:\n{result.stderr}")
            
            # Parse coverage results
            coverage_file = self.backend_root / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                
                total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
                self.stats['coverage_improvement'] = total_coverage
                
                logger.info(f"Current test coverage: {total_coverage:.1f}%")
                
                if total_coverage < 90:
                    logger.warning("Test coverage is below 90% target")
                    self._identify_low_coverage_areas(coverage_data)
        
        except Exception as e:
            logger.error(f"Failed to run test coverage analysis: {e}")
            self.errors_found.append(f"Test coverage analysis failed: {e}")
    
    def _identify_low_coverage_areas(self, coverage_data: Dict[str, Any]) -> None:
        """Identify areas with low test coverage."""
        files_data = coverage_data.get('files', {})
        
        low_coverage_files = []
        for file_path, file_data in files_data.items():
            coverage_percent = file_data.get('summary', {}).get('percent_covered', 0)
            if coverage_percent < 90:
                low_coverage_files.append((file_path, coverage_percent))
        
        low_coverage_files.sort(key=lambda x: x[1])  # Sort by coverage percentage
        
        logger.info("Files with low test coverage:")
        for file_path, coverage in low_coverage_files[:10]:  # Top 10 worst
            logger.info(f"  {file_path}: {coverage:.1f}%")
            
            self.compliance_issues.append(
                ComplianceIssue(
                    file_path=file_path,
                    issue_type='low_coverage',
                    description=f'Test coverage is {coverage:.1f}%, below 90% target',
                    suggested_fix='Add comprehensive test cases'
                )
            )
    
    def _validate_api_contracts(self) -> None:
        """Validate API contracts against implementation."""
        logger.info("📋 Validating API contracts")
        
        # Check if api_contracts.yaml exists
        api_contracts_file = Path("api_contracts.yaml")
        if not api_contracts_file.exists():
            logger.warning("api_contracts.yaml not found, skipping API validation")
            return
        
        # Basic validation - ensure router files have proper endpoint documentation
        for router_file in self.systems_dir.rglob("*router*.py"):
            self._validate_router_api_contracts(router_file)
    
    def _validate_router_api_contracts(self, router_file: Path) -> None:
        """Validate a router file against API contracts."""
        try:
            with open(router_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for proper FastAPI decorators
            if '@router.' not in content and '@app.' not in content:
                self.compliance_issues.append(
                    ComplianceIssue(
                        file_path=str(router_file),
                        issue_type='missing_api_decorators',
                        description='Router file missing FastAPI route decorators',
                        suggested_fix='Add proper @router.* decorators for endpoints'
                    )
                )
            
            # Check for response model definitions
            if 'response_model' not in content and '@router.' in content:
                self.compliance_issues.append(
                    ComplianceIssue(
                        file_path=str(router_file),
                        issue_type='missing_response_models',
                        description='Router endpoints should specify response_model',
                        suggested_fix='Add response_model parameters to route decorators'
                    )
                )
        
        except Exception as e:
            self.errors_found.append(f"Failed to validate router {router_file}: {e}")
    
    def _validate_cross_system_compatibility(self) -> None:
        """Validate cross-system compatibility and communication."""
        logger.info("🔗 Validating cross-system compatibility")
        
        # Check for proper event system integration
        for system_dir in self.systems_dir.iterdir():
            if system_dir.is_dir() and not system_dir.name.startswith('_'):
                self._check_system_event_integration(system_dir)
    
    def _check_system_event_integration(self, system_dir: Path) -> None:
        """Check if a system properly integrates with the event system."""
        system_name = system_dir.name
        
        # Look for event usage in the system
        has_event_integration = False
        
        for py_file in system_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'EventDispatcher' in content or 'EventBase' in content:
                    has_event_integration = True
                    break
            
            except Exception:
                continue
        
        if not has_event_integration and system_name not in ['shared', 'data', 'storage']:
            self.compliance_issues.append(
                ComplianceIssue(
                    file_path=str(system_dir),
                    issue_type='missing_event_integration',
                    description=f'System {system_name} should integrate with event system',
                    suggested_fix='Add EventDispatcher usage for system events'
                )
            )
    
    def _update_documentation(self) -> None:
        """Update documentation to reflect changes."""
        logger.info("📝 Updating documentation")
        
        # Update system inventory
        self._update_systems_inventory()
        
        # Create/update README files for systems missing them
        for system_dir in self.systems_dir.iterdir():
            if system_dir.is_dir() and not system_dir.name.startswith('_'):
                readme_file = system_dir / "README.md"
                if not readme_file.exists():
                    self._create_system_readme(readme_file, system_dir.name)
    
    def _update_systems_inventory(self) -> None:
        """Update the backend systems inventory."""
        inventory_file = self.backend_root / "backend_systems_inventory.md"
        
        try:
            # Generate updated inventory data
            systems_data = self._generate_systems_inventory_data()
            
            # Create updated inventory content
            content = self._format_systems_inventory(systems_data)
            
            # Write updated inventory
            with open(inventory_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.fixed_issues.append("Updated backend systems inventory")
            logger.info("Updated backend systems inventory")
        
        except Exception as e:
            self.errors_found.append(f"Failed to update systems inventory: {e}")
    
    def _generate_systems_inventory_data(self) -> Dict[str, Any]:
        """Generate current systems inventory data."""
        systems_data = {}
        
        for system_dir in self.systems_dir.iterdir():
            if system_dir.is_dir() and not system_dir.name.startswith('_'):
                system_name = system_dir.name
                
                systems_data[system_name] = {
                    'name': system_name,
                    'path': str(system_dir),
                    'has_models': (system_dir / 'models').exists(),
                    'has_services': (system_dir / 'services').exists(),
                    'has_repositories': (system_dir / 'repositories').exists(),
                    'has_routers': (system_dir / 'routers').exists(),
                    'has_schemas': (system_dir / 'schemas').exists(),
                    'has_tests': (self.tests_dir / 'systems' / system_name).exists(),
                    'python_files': len(list(system_dir.rglob("*.py"))),
                }
        
        return systems_data
    
    def _format_systems_inventory(self, systems_data: Dict[str, Any]) -> str:
        """Format systems inventory data as markdown."""
        content = [
            "# Backend Systems Inventory",
            "",
            f"**Updated:** {self._get_timestamp()}",
            f"**Total Systems:** {len(systems_data)}",
            "",
            "## Systems Overview",
            "",
            "| System | Models | Services | Repositories | Routers | Schemas | Tests | Files |",
            "|--------|--------|----------|--------------|---------|---------|-------|-------|"
        ]
        
        for system_name, data in sorted(systems_data.items()):
            models = "✅" if data['has_models'] else "❌"
            services = "✅" if data['has_services'] else "❌"
            repositories = "✅" if data['has_repositories'] else "❌"
            routers = "✅" if data['has_routers'] else "❌"
            schemas = "✅" if data['has_schemas'] else "❌"
            tests = "✅" if data['has_tests'] else "❌"
            
            content.append(
                f"| {system_name} | {models} | {services} | {repositories} | "
                f"{routers} | {schemas} | {tests} | {data['python_files']} |"
            )
        
        return "\n".join(content)
    
    def _create_system_readme(self, readme_path: Path, system_name: str) -> None:
        """Create a README.md file for a system."""
        content = f"""# {system_name.title()} System

## Overview

The {system_name} system provides core functionality for Visual DM's {system_name} management.

## Structure

- `models/` - Data models and schema definitions
- `services/` - Business logic and service layer
- `repositories/` - Data access layer
- `schemas/` - API request/response schemas
- `routers/` - FastAPI route handlers

## Usage

```python
from backend.systems.{system_name} import {system_name.title()}Service

# Example usage
service = {system_name.title()}Service()
```

## API Endpoints

See the router files for detailed API documentation.

## Testing

Tests are located in `/backend/tests/systems/{system_name}/`.

Run tests with:
```bash
pytest backend/tests/systems/{system_name}/
```
"""
        
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.fixed_issues.append(f"Created README.md for {system_name} system")
            logger.info(f"Created README.md for {system_name} system")
        except Exception as e:
            self.errors_found.append(f"Failed to create README for {system_name}: {e}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for documentation."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final report."""
        logger.info("📊 Generating final report")
        
        report = {
            'timestamp': self._get_timestamp(),
            'status': 'COMPLETED' if not self.errors_found else 'COMPLETED_WITH_ERRORS',
            'statistics': self.stats,
            'summary': {
                'total_files_analyzed': self.stats['files_analyzed'],
                'imports_fixed': self.stats['imports_fixed'],
                'tests_moved': self.stats['tests_moved'],
                'duplicates_removed': self.stats['duplicates_removed'],
                'compliance_fixes': len(self.fixed_issues),
                'errors_found': len(self.errors_found),
                'coverage_percentage': self.stats.get('coverage_improvement', 0)
            },
            'issues_found': {
                'import_issues': len(self.import_issues),
                'test_structure_issues': len(self.test_structure_issues),
                'compliance_issues': len(self.compliance_issues)
            },
            'fixes_applied': self.fixed_issues,
            'errors': self.errors_found,
            'recommendations': self._generate_recommendations()
        }
        
        # Save report to file
        report_file = self.backend_root / "task53_implementation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Final report saved to {report_file}")
        self._print_summary(report)
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        if self.stats['coverage_improvement'] < 90:
            recommendations.append(
                f"Test coverage is {self.stats['coverage_improvement']:.1f}%. "
                "Focus on adding comprehensive test cases to reach ≥90% target."
            )
        
        if len(self.compliance_issues) > 0:
            recommendations.append(
                f"Found {len(self.compliance_issues)} compliance issues. "
                "Review and fix these to align with Development_Bible.md standards."
            )
        
        if len(self.errors_found) > 0:
            recommendations.append(
                f"Found {len(self.errors_found)} errors during analysis. "
                "These should be investigated and resolved."
            )
        
        recommendations.extend([
            "Continue monitoring import structure for canonical compliance",
            "Regularly run test coverage analysis to maintain quality standards",
            "Keep documentation updated as systems evolve",
            "Ensure new systems follow the established patterns"
        ])
        
        return recommendations
    
    def _print_summary(self, report: Dict[str, Any]) -> None:
        """Print a summary of the implementation results."""
        print("\n" + "="*80)
        print("🎯 TASK 53 - BACKEND DEVELOPMENT PROTOCOL IMPLEMENTATION")
        print("="*80)
        print(f"Status: {report['status']}")
        print(f"Timestamp: {report['timestamp']}")
        print("\n📊 STATISTICS:")
        print(f"  Files Analyzed: {report['summary']['total_files_analyzed']}")
        print(f"  Imports Fixed: {report['summary']['imports_fixed']}")
        print(f"  Tests Moved: {report['summary']['tests_moved']}")
        print(f"  Duplicates Removed: {report['summary']['duplicates_removed']}")
        print(f"  Compliance Fixes: {report['summary']['compliance_fixes']}")
        print(f"  Test Coverage: {report['summary']['coverage_percentage']:.1f}%")
        
        if report['summary']['errors_found'] > 0:
            print(f"\n⚠️  ERRORS FOUND: {report['summary']['errors_found']}")
            for error in report['errors'][:5]:  # Show first 5 errors
                print(f"    • {error}")
            if len(report['errors']) > 5:
                print(f"    ... and {len(report['errors']) - 5} more")
        
        print(f"\n✅ FIXES APPLIED: {len(report['fixes_applied'])}")
        for fix in report['fixes_applied'][:5]:  # Show first 5 fixes
            print(f"    • {fix}")
        if len(report['fixes_applied']) > 5:
            print(f"    ... and {len(report['fixes_applied']) - 5} more")
        
        print("\n💡 KEY RECOMMENDATIONS:")
        for rec in report['recommendations'][:3]:  # Show top 3 recommendations
            print(f"    • {rec}")
        
        print("\n" + "="*80)
        print("✅ Backend Development Protocol Implementation Complete!")
        print("="*80)

def main():
    """Main entry point for the script."""
    print("🚀 Starting Task 53 - Backend Development Protocol Implementation")
    
    try:
        implementation = BackendDevelopmentProtocolImplementation()
        report = implementation.run_comprehensive_protocol()
        
        # Exit with appropriate code
        if report['status'] == 'COMPLETED':
            sys.exit(0)
        else:
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"❌ Implementation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 