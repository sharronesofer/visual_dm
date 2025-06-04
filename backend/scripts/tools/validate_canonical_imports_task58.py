#!/usr/bin/env python3
"""
Canonical Import Validation Script for Task 58

This script validates that all imports follow the canonical backend.systems.* structure
and tests that key systems can be imported successfully.
"""

import os
import sys
import importlib
import traceback
from pathlib import Path
from typing import List, Dict, Tuple, Set
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def get_backend_root() -> Path:
    """Get the backend directory path."""
    current_dir = Path(__file__).parent
    if current_dir.name == 'backend':
        return current_dir
    # If running from backend subdirectory, find backend root
    while current_dir.parent and current_dir.name != 'backend':
        current_dir = current_dir.parent
    if current_dir.name == 'backend':
        return current_dir
    
    # Fallback: look for backend directory
    for path in [Path.cwd(), Path.cwd().parent]:
        backend_path = path / 'backend'
        if backend_path.exists() and backend_path.is_dir():
            return backend_path
    
    raise RuntimeError("Could not find backend directory")

def find_python_files(root_path: Path) -> List[Path]:
    """Find all Python files in the backend systems and tests directories."""
    python_files = []
    
    # Search in systems directory
    systems_path = root_path / 'systems'
    if systems_path.exists():
        python_files.extend(systems_path.rglob('*.py'))
    
    # Search in tests directory
    tests_path = root_path / 'tests'
    if tests_path.exists():
        python_files.extend(tests_path.rglob('*.py'))
    
    return python_files

def check_import_syntax(file_path: Path) -> List[str]:
    """
    Check for syntax errors in a Python file by attempting to compile it.
    Returns list of error messages.
    """
    errors = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        compile(content, str(file_path), 'exec')
    except SyntaxError as e:
        errors.append(f"Syntax Error: {e}")
    except Exception as e:
        errors.append(f"Compilation Error: {e}")
    
    return errors

def validate_canonical_imports(root_path: Path) -> Dict[str, List[str]]:
    """
    Validate that all imports follow canonical backend.systems.* structure.
    Returns dict of file_path -> list of issues.
    """
    issues = {}
    python_files = find_python_files(root_path)
    
    # Patterns that indicate potential non-canonical imports
    problematic_patterns = [
        (r'from\s+app\.', 'Import from "app." should use "backend.systems."'),
        (r'import\s+app\.', 'Import of "app." should use "backend.systems."'),
        (r'from\s+systems\.(?!.*backend\.systems)', 'Import from "systems." should use "backend.systems."'),
        (r'import\s+systems\.(?!.*backend\.systems)', 'Import of "systems." should use "backend.systems."'),
        (r'from\s+\.\s+import', 'Relative import "from backend.systems import" should be absolute'),
        (r'from\s+\.\.+', 'Relative import with ".." should be absolute'),
    ]
    
    for file_path in python_files:
        file_issues = []
        
        # Check syntax first
        syntax_errors = check_import_syntax(file_path)
        if syntax_errors:
            file_issues.extend(syntax_errors)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                stripped_line = line.strip()
                
                # Skip comments and empty lines
                if not stripped_line or stripped_line.startswith('#'):
                    continue
                
                # Check each problematic pattern
                import re
                for pattern, message in problematic_patterns:
                    if re.search(pattern, stripped_line):
                        file_issues.append(f"Line {line_num}: {message} - {stripped_line}")
        
        except Exception as e:
            file_issues.append(f"Error reading file: {e}")
        
        if file_issues:
            issues[str(file_path.relative_to(root_path))] = file_issues
    
    return issues

def test_system_imports() -> Dict[str, str]:
    """
    Test that key backend systems can be imported successfully.
    Returns dict of system_name -> status/error.
    """
    results = {}
    
    # Core systems to test
    test_imports = [
        'backend.systems',
        'backend.infrastructure.shared',
        'backend.systems.events', 
        'backend.systems.data',
        'backend.systems.character',
        'backend.systems.combat',
        'backend.systems.world_generation',
        'backend.systems.inventory',
        'backend.systems.equipment',
        'backend.systems.magic',  # Business logic only
        'backend.infrastructure.magic',  # Technical infrastructure
        'backend.systems.region',
        'backend.systems.population',
        'backend.systems.npc',
        'backend.systems.faction',
        'backend.systems.poi',
        'backend.systems.world_state',
        'backend.systems.dialogue',
        'backend.systems.diplomacy', 
        'backend.systems.memory',
        'backend.systems.economy',
        'backend.systems.crafting',
        'backend.systems.loot',
        'backend.systems.quest',
        'backend.systems.rumor',
        'backend.systems.religion',
        'backend.systems.motif',
        'backend.systems.arc',
        'backend.systems.analytics',
        'backend.infrastructure.auth.auth_user',
        'backend.infrastructure.llm',
    ]
    
    for system in test_imports:
        try:
            importlib.import_module(system)
            results[system] = "✅ SUCCESS"
        except ImportError as e:
            results[system] = f"❌ ImportError: {e}"
        except Exception as e:
            results[system] = f"⚠️ Other Error: {e}"
    
    return results

def check_structural_compliance(root_path: Path) -> List[str]:
    """
    Check structural compliance with backend development protocol.
    Returns list of structural issues.
    """
    issues = []
    
    # Check that all tests are in /backend/tests/
    systems_path = root_path / 'systems'
    if systems_path.exists():
        for test_dir in ['test', 'tests']:
            test_paths = list(systems_path.rglob(test_dir))
            for test_path in test_paths:
                if test_path.is_dir():
                    issues.append(f"Test directory found in systems: {test_path.relative_to(root_path)}")
        
        # Check for test files in systems
        test_files = list(systems_path.rglob('test_*.py'))
        for test_file in test_files:
            issues.append(f"Test file found in systems: {test_file.relative_to(root_path)}")
    
    # Check that tests directory exists and is properly organized
    tests_path = root_path / 'tests'
    if not tests_path.exists():
        issues.append("Missing /backend/tests/ directory")
    elif not (tests_path / 'systems').exists():
        issues.append("Missing /backend/tests/systems/ directory")
    
    return issues

def main():
    """Main validation function."""
    try:
        backend_root = get_backend_root()
        logger.info(f"Validating backend at: {backend_root}")
        
        # Check structural compliance
        logger.info("Checking structural compliance...")
        structural_issues = check_structural_compliance(backend_root)
        if structural_issues:
            logger.warning("Structural compliance issues:")
            for issue in structural_issues:
                logger.warning(f"  {issue}")
        else:
            logger.info("✅ Structural compliance: PASS")
        
        # Validate canonical imports
        logger.info("Validating canonical imports...")
        import_issues = validate_canonical_imports(backend_root)
        if import_issues:
            logger.warning(f"Found import issues in {len(import_issues)} files:")
            for file_path, issues in list(import_issues.items())[:10]:  # Show first 10
                logger.warning(f"  {file_path}:")
                for issue in issues[:3]:  # Show first 3 issues per file
                    logger.warning(f"    {issue}")
                if len(issues) > 3:
                    logger.warning(f"    ... and {len(issues) - 3} more issues")
            if len(import_issues) > 10:
                logger.warning(f"  ... and {len(import_issues) - 10} more files with issues")
        else:
            logger.info("✅ Canonical imports: PASS")
        
        # Test system imports
        logger.info("Testing system imports...")
        import_results = test_system_imports()
        success_count = sum(1 for status in import_results.values() if status.startswith("✅"))
        total_count = len(import_results)
        
        logger.info(f"System import results: {success_count}/{total_count} successful")
        
        for system, status in import_results.items():
            if not status.startswith("✅"):
                logger.warning(f"  {system}: {status}")
        
        # Final summary
        all_passed = not structural_issues and not import_issues and success_count == total_count
        
        if all_passed:
            logger.info("🎉 ALL VALIDATIONS PASSED!")
            logger.info("✅ Task 58 Complete: All imports are canonical and systems are working")
        else:
            logger.warning("⚠️ Some validations failed. See details above.")
        
        return all_passed
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 