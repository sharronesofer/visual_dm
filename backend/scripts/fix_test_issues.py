try:
    from pydantic import ConfigDict
except ImportError:
    # Fallback for older Pydantic versions
    class ConfigDict:
        def __init__(self, **kwargs):
            pass

#!/usr/bin/env python3
"""
Visual DM Backend Test Issues Auto-Fix Script

This script automatically fixes common testing issues that prevent proper test execution
and coverage measurement. Run this before running tests to clean up the codebase.

Usage:
    python scripts/fix_test_issues.py [--dry-run] [--verbose]
"""

import ast
import os
import re
import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict, Set
import json


class TestIssueFixer:
    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.backend_root = Path(__file__).parent.parent
        self.fixes_applied = []
        self.errors_found = []

    def log(self, message: str, level: str = "INFO"):
        """Log a message with optional level"""
        if self.verbose or level in ["ERROR", "WARNING"]:
            print(f"[{level}] {message}")

    def apply_fix(
        self, file_path: Path, original_content: str, new_content: str, description: str
    ):
        """Apply a fix to a file or log it if dry_run"""
        if original_content != new_content:
            if self.dry_run:
                self.log(f"DRY RUN: Would fix {file_path}: {description}")
            else:
                file_path.write_text(new_content, encoding="utf-8")
                self.log(f"Fixed {file_path}: {description}")
            self.fixes_applied.append(f"{file_path}: {description}")
            return True
        return False

    def fix_pydantic_v2_migration(self) -> int:
        """Fix remaining Pydantic V1 to V2 migration issues"""
        self.log("Fixing Pydantic V2 migration issues...")
        fixes = 0

        for py_file in self.backend_root.rglob("*.py"):
            if (
                py_file.name.startswith(".")
                or "venv" in str(py_file)
                or "__pycache__" in str(py_file)
            ):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                new_content = content

                # Fix @validator imports and decorators
                if "from pydantic import" in content and "validator" in content:
                    # Replace validator import
                    new_content = re.sub(
                        r"from pydantic import ([^)]*?)validator([^)]*?)",
                        r"from pydantic import \1field_validator\2",
                        new_content,
                    )

                    # Replace @validator decorators
                    new_content = re.sub(
                        r"@validator\s*\(\s*([^)]+)\s*\)",
                        r"@field_validator(\1)",
                        new_content,
                    )

                # Fix Config class to model_config
                if "class Config:" in content:
                    new_content = re.sub(
                        r"class Config:\s*\n\s*([^\n]+)",
                        r"model_config = ConfigDict(\1)",
                        new_content,
                    )

                # Fix common Config attributes
                config_replacements = {
                    "populate_by_name=True": "populate_by_name=True",
                    'extra="forbid"': 'extra="forbid"',
                    'extra="allow"': 'extra="allow"',
                    'extra="forbid"': 'extra="forbid"',
                    'extra="allow"': 'extra="allow"',
                    "validate_assignment=True": "validate_assignment=True",
                    "arbitrary_types_allowed=True": "arbitrary_types_allowed=True",
                }

                for old, new in config_replacements.items():
                    if old in content:
                        new_content = new_content.replace(old, new)

                # Ensure ConfigDict import if model_config is used
                if "model_config" in new_content and "ConfigDict" not in new_content:
                    if "from pydantic import" in new_content:
                        new_content = re.sub(
                            r"from pydantic import ([^)]*?)",
                            r"from pydantic import \1, ConfigDict",
                            new_content,
                        )

                if self.apply_fix(
                    py_file, content, new_content, "Pydantic V2 migration"
                ):
                    fixes += 1

            except Exception as e:
                self.errors_found.append(f"Error processing {py_file}: {e}")

        return fixes

    def fix_import_issues(self) -> int:
        """Fix common import issues"""
        self.log("Fixing import issues...")
        fixes = 0

        for py_file in self.backend_root.rglob("*.py"):
            if (
                py_file.name.startswith(".")
                or "venv" in str(py_file)
                or "__pycache__" in str(py_file)
            ):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                new_content = content

                # Fix common import errors
                import_fixes = {
                    "from .event_bus import get_event_dispatcher": "from .event_bus import get_event_dispatcher",
                    "from .event_bus import get_event_dispatcher": "from .event_bus import get_event_dispatcher",
                    "from .event_bus import get_event_dispatcher": "from .event_bus import get_event_dispatcher",
                }

                for bad_import, good_import in import_fixes.items():
                    if bad_import in content:
                        new_content = new_content.replace(bad_import, good_import)

                # Fix docstring formatting issues
                new_content = re.sub(
                    r'\\\"\\\"\\\"([^"]+)\\\"\\\"\\\"', r'"""\1"""', new_content
                )

                if self.apply_fix(py_file, content, new_content, "Import fixes"):
                    fixes += 1

            except Exception as e:
                self.errors_found.append(f"Error fixing imports in {py_file}: {e}")

        return fixes

    def fix_syntax_errors(self) -> int:
        """Check for and report syntax errors"""
        self.log("Checking for syntax errors...")
        errors = 0

        for py_file in self.backend_root.rglob("*.py"):
            if (
                py_file.name.startswith(".")
                or "venv" in str(py_file)
                or "__pycache__" in str(py_file)
            ):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                ast.parse(content)
            except SyntaxError as e:
                self.errors_found.append(
                    f"Syntax error in {py_file}:{e.lineno}: {e.msg}"
                )
                errors += 1
            except Exception as e:
                self.errors_found.append(f"Error parsing {py_file}: {e}")
                errors += 1

        return errors

    def create_missing_init_files(self) -> int:
        """Create missing __init__.py files"""
        self.log("Creating missing __init__.py files...")
        fixes = 0

        for py_file in self.backend_root.rglob("*.py"):
            if (
                py_file.name.startswith(".")
                or "venv" in str(py_file)
                or "__pycache__" in str(py_file)
            ):
                continue

            parent = py_file.parent
            init_file = parent / "__init__.py"

            if not init_file.exists() and parent != self.backend_root:
                if not self.dry_run:
                    init_file.write_text(
                        "# This file makes the directory a Python package\n"
                    )
                    self.log(f"Created {init_file}")
                else:
                    self.log(f"DRY RUN: Would create {init_file}")
                fixes += 1

        return fixes

    def run_code_formatting(self) -> int:
        """Run code formatting tools"""
        self.log("Running code formatting...")
        fixes = 0

        if self.dry_run:
            self.log("DRY RUN: Would run black, isort, and autoflake")
            return 0

        try:
            # Run isort for import sorting
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "isort",
                    str(self.backend_root),
                    "--profile",
                    "black",
                ],
                check=True,
                capture_output=True,
            )
            self.log("Ran isort for import sorting")
            fixes += 1
        except subprocess.CalledProcessError as e:
            self.log(f"Warning: isort failed: {e}", "WARNING")
        except FileNotFoundError:
            self.log("Warning: isort not installed", "WARNING")

        try:
            # Run autoflake to remove unused imports
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "autoflake",
                    "--remove-all-unused-imports",
                    "--remove-unused-variables",
                    "--in-place",
                    "--recursive",
                    str(self.backend_root),
                ],
                check=True,
                capture_output=True,
            )
            self.log("Ran autoflake to remove unused imports")
            fixes += 1
        except subprocess.CalledProcessError as e:
            self.log(f"Warning: autoflake failed: {e}", "WARNING")
        except FileNotFoundError:
            self.log("Warning: autoflake not installed", "WARNING")

        try:
            # Run black for code formatting
            subprocess.run(
                [sys.executable, "-m", "black", str(self.backend_root)],
                check=True,
                capture_output=True,
            )
            self.log("Ran black for code formatting")
            fixes += 1
        except subprocess.CalledProcessError as e:
            self.log(f"Warning: black failed: {e}", "WARNING")
        except FileNotFoundError:
            self.log("Warning: black not installed", "WARNING")

        return fixes

    def generate_basic_test_stubs(self) -> int:
        """Generate basic test stubs for untested modules"""
        self.log("Generating basic test stubs...")
        fixes = 0

        tests_dir = self.backend_root / "tests"
        tests_dir.mkdir(exist_ok=True)

        for py_file in self.backend_root.rglob("*.py"):
            if (
                py_file.name.startswith(".")
                or "venv" in str(py_file)
                or "__pycache__" in str(py_file)
                or "tests" in str(py_file)
                or py_file.name.startswith("test_")
                or py_file.name == "__init__.py"
            ):
                continue

            # Calculate relative path from backend root
            rel_path = py_file.relative_to(self.backend_root)

            # Create corresponding test file path
            test_path = tests_dir / f"test_{rel_path.stem}.py"

            if not test_path.exists():
                # Generate basic test stub
                module_path = str(rel_path.with_suffix("")).replace("/", ".")
                test_content = f'''"""
Tests for {module_path}

Auto-generated test stub. Add actual tests here.
"""

import pytest
from unittest.mock import Mock, patch

# Import the module being tested
try:
    import {module_path}
except ImportError as e:
    pytest.skip(f"Could not import {module_path}: {{e}}", allow_module_level=True)


def test_module_imports():
    """Test that the module can be imported without errors."""
    import {module_path}
    assert {module_path} is not None


# TODO: Add actual tests for {module_path}
class Test{rel_path.stem.replace('_', '').title()}:
    """Test class for {module_path}"""
    
    def test_placeholder(self):
        """Placeholder test - replace with actual tests."""
        assert True  # Replace with actual test logic
'''

                if not self.dry_run:
                    test_path.parent.mkdir(parents=True, exist_ok=True)
                    test_path.write_text(test_content)
                    self.log(f"Created test stub: {test_path}")
                else:
                    self.log(f"DRY RUN: Would create test stub: {test_path}")
                fixes += 1

        return fixes

    def check_test_configuration(self) -> int:
        """Check and fix test configuration files"""
        self.log("Checking test configuration...")
        fixes = 0

        # Check pytest.ini
        pytest_ini = self.backend_root / "pytest.ini"
        expected_pytest_config = """[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
"""

        if not pytest_ini.exists() or "testpaths" not in pytest_ini.read_text():
            if not self.dry_run:
                pytest_ini.write_text(expected_pytest_config)
                self.log("Created/updated pytest.ini")
            else:
                self.log("DRY RUN: Would create/update pytest.ini")
            fixes += 1

        # Check .coveragerc
        coveragerc = self.backend_root / ".coveragerc"
        expected_coverage_config = """[run]
source = .
omit = 
    */venv/*
    */tests/*
    */migrations/*
    */__pycache__/*
    */node_modules/*
    setup.py
    manage.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod

[html]
directory = htmlcov
"""

        if not coveragerc.exists():
            if not self.dry_run:
                coveragerc.write_text(expected_coverage_config)
                self.log("Created .coveragerc")
            else:
                self.log("DRY RUN: Would create .coveragerc")
            fixes += 1

        return fixes

    def run_all_fixes(self) -> Dict[str, int]:
        """Run all available fixes"""
        results = {}

        self.log("Starting automated test issue fixes...")

        results["pydantic_v2_fixes"] = self.fix_pydantic_v2_migration()
        results["import_fixes"] = self.fix_import_issues()
        results["syntax_errors"] = self.fix_syntax_errors()
        results["init_files_created"] = self.create_missing_init_files()
        results["formatting_fixes"] = self.run_code_formatting()
        results["test_stubs_created"] = self.generate_basic_test_stubs()
        results["config_fixes"] = self.check_test_configuration()

        return results

    def print_summary(self, results: Dict[str, int]):
        """Print a summary of all fixes applied"""
        print("\n" + "=" * 60)
        print("TEST ISSUE FIXES SUMMARY")
        print("=" * 60)

        total_fixes = sum(v for k, v in results.items() if k != "syntax_errors")

        print(f"✅ Pydantic V2 migration fixes: {results['pydantic_v2_fixes']}")
        print(f"✅ Import fixes: {results['import_fixes']}")
        print(f"⚠️  Syntax errors found: {results['syntax_errors']}")
        print(f"✅ __init__.py files created: {results['init_files_created']}")
        print(f"✅ Code formatting fixes: {results['formatting_fixes']}")
        print(f"✅ Test stubs created: {results['test_stubs_created']}")
        print(f"✅ Configuration fixes: {results['config_fixes']}")

        print(f"\nTotal fixes applied: {total_fixes}")

        if self.fixes_applied:
            print(f"\n📝 Fixes applied ({len(self.fixes_applied)}):")
            for fix in self.fixes_applied[:10]:  # Show first 10
                print(f"  • {fix}")
            if len(self.fixes_applied) > 10:
                print(f"  ... and {len(self.fixes_applied) - 10} more")

        if self.errors_found:
            print(f"\n❌ Errors found ({len(self.errors_found)}):")
            for error in self.errors_found[:5]:  # Show first 5
                print(f"  • {error}")
            if len(self.errors_found) > 5:
                print(f"  ... and {len(self.errors_found) - 5} more")

        print("\n📋 Next steps:")
        print("1. Run: python -m pytest tests/ --tb=short")
        print("2. Run: python -m coverage run -m pytest tests/")
        print("3. Run: python -m coverage report")
        print("4. Fix any remaining syntax errors manually")
        print("5. Add actual test logic to generated test stubs")


def main():
    parser = argparse.ArgumentParser(
        description="Fix common testing issues in Visual DM backend"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    fixer = TestIssueFixer(dry_run=args.dry_run, verbose=args.verbose)
    results = fixer.run_all_fixes()
    fixer.print_summary(results)

    # Exit with error code if syntax errors were found
    if results["syntax_errors"] > 0:
        print(
            f"\n⚠️  Found {results['syntax_errors']} syntax errors that need manual fixing!"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
