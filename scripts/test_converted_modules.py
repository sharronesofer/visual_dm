#!/usr/bin/env python3
"""
Test Converted Python Modules

This script tests converted Python modules for correctness and compatibility.
It runs static type checking, linting, and can execute unit tests on the converted modules.

Usage:
  python test_converted_modules.py --modules-dir <directory_with_modules> [options]
"""

import os
import sys
import subprocess
import argparse
import importlib
from typing import List, Dict, Tuple, Any, Set
from pathlib import Path
import traceback
import json

class ConvertedModuleTester:
    """Tests converted Python modules for correctness and compatibility."""
    
    def __init__(self, modules_dir: str, report_file: str = None, 
                 run_mypy: bool = True, run_lint: bool = True, run_tests: bool = True):
        """
        Initialize the tester.
        
        Args:
            modules_dir: Directory containing modules to test
            report_file: Path to save the test report (optional)
            run_mypy: Whether to run mypy type checking
            run_lint: Whether to run linting (flake8)
            run_tests: Whether to run pytest for unit tests
        """
        self.modules_dir = Path(modules_dir)
        self.report_file = report_file
        self.run_mypy = run_mypy
        self.run_lint = run_lint
        self.run_tests = run_tests
        self.results: Dict[str, Dict[str, Any]] = {
            "mypy": {},
            "lint": {},
            "import": {},
            "tests": {}
        }
        
    def run_mypy_type_checking(self) -> Tuple[int, Dict[str, List[str]]]:
        """
        Run mypy static type checking on all Python modules.
        
        Returns:
            Tuple of (errors_count, errors_dict) where errors_dict maps file to error list
        """
        print("Running mypy type checking...")
        
        # First, ensure mypy is installed
        try:
            import mypy
        except ImportError:
            print("mypy not installed. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "mypy"])
        
        # Run mypy on the modules directory
        errors_dict: Dict[str, List[str]] = {}
        errors_count = 0
        
        try:
            result = subprocess.run(
                ["mypy", "--ignore-missing-imports", str(self.modules_dir)],
                capture_output=True,
                text=True
            )
            
            # Parse the output
            for line in result.stdout.splitlines():
                if ": error:" in line:
                    parts = line.split(":", 1)
                    if len(parts) >= 2:
                        file_path = parts[0]
                        error_msg = parts[1].strip()
                        
                        if file_path not in errors_dict:
                            errors_dict[file_path] = []
                        
                        errors_dict[file_path].append(error_msg)
                        errors_count += 1
            
            # Store in results
            self.results["mypy"] = {
                "success": errors_count == 0,
                "errors_count": errors_count,
                "errors": errors_dict
            }
            
            if errors_count == 0:
                print("✅ No type checking errors found")
            else:
                print(f"❌ Found {errors_count} type checking errors")
        
        except Exception as e:
            print(f"Error running mypy: {str(e)}")
            self.results["mypy"] = {
                "success": False,
                "errors_count": -1,
                "errors": {"general": [str(e)]}
            }
            errors_count = -1
        
        return errors_count, errors_dict
    
    def run_linting(self) -> Tuple[int, Dict[str, List[str]]]:
        """
        Run flake8 linting on all Python modules.
        
        Returns:
            Tuple of (errors_count, errors_dict) where errors_dict maps file to error list
        """
        print("Running flake8 linting...")
        
        # First, ensure flake8 is installed
        try:
            import flake8
        except ImportError:
            print("flake8 not installed. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "flake8"])
        
        # Run flake8 on the modules directory
        errors_dict: Dict[str, List[str]] = {}
        errors_count = 0
        
        try:
            result = subprocess.run(
                ["flake8", str(self.modules_dir)],
                capture_output=True,
                text=True
            )
            
            # Parse the output
            for line in result.stdout.splitlines():
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    file_path = parts[0]
                    line_num = parts[1]
                    error_msg = parts[2].strip()
                    
                    if file_path not in errors_dict:
                        errors_dict[file_path] = []
                    
                    errors_dict[file_path].append(f"Line {line_num}: {error_msg}")
                    errors_count += 1
            
            # Store in results
            self.results["lint"] = {
                "success": errors_count == 0,
                "errors_count": errors_count,
                "errors": errors_dict
            }
            
            if errors_count == 0:
                print("✅ No linting errors found")
            else:
                print(f"❌ Found {errors_count} linting errors")
        
        except Exception as e:
            print(f"Error running flake8: {str(e)}")
            self.results["lint"] = {
                "success": False,
                "errors_count": -1,
                "errors": {"general": [str(e)]}
            }
            errors_count = -1
        
        return errors_count, errors_dict
    
    def test_imports(self) -> Tuple[int, Dict[str, List[str]]]:
        """
        Test that all modules can be imported without errors.
        
        Returns:
            Tuple of (errors_count, errors_dict) where errors_dict maps file to error list
        """
        print("Testing module imports...")
        
        errors_dict: Dict[str, List[str]] = {}
        errors_count = 0
        imported_count = 0
        
        # Walk through all Python files
        for root, _, files in os.walk(self.modules_dir):
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.modules_dir)
                    
                    # Convert file path to module name
                    module_name = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
                    
                    # Try importing the module
                    try:
                        # Temporarily add the modules directory to sys.path
                        original_path = sys.path.copy()
                        sys.path.insert(0, str(self.modules_dir.parent))
                        
                        # Derive the proper module name based on directory structure
                        package_name = self.modules_dir.name
                        full_module_name = f"{package_name}.{module_name}"
                        
                        # Try importing
                        importlib.import_module(full_module_name)
                        imported_count += 1
                        
                        # Restore sys.path
                        sys.path = original_path
                    except Exception as e:
                        # Restore sys.path
                        sys.path = original_path
                        
                        # Record the error
                        if file_path not in errors_dict:
                            errors_dict[file_path] = []
                        
                        errors_dict[file_path].append(f"Import error: {str(e)}")
                        errors_count += 1
        
        # Store in results
        self.results["import"] = {
            "success": errors_count == 0,
            "errors_count": errors_count,
            "imported_count": imported_count,
            "errors": errors_dict
        }
        
        if errors_count == 0:
            print(f"✅ Successfully imported {imported_count} modules")
        else:
            print(f"❌ Found {errors_count} import errors out of {imported_count + errors_count} modules")
        
        return errors_count, errors_dict
    
    def run_unit_tests(self) -> Tuple[int, Dict[str, Any]]:
        """
        Run pytest unit tests on the modules.
        
        Returns:
            Tuple of (failures_count, test_results)
        """
        print("Running unit tests with pytest...")
        
        # First, ensure pytest is installed
        try:
            import pytest
        except ImportError:
            print("pytest not installed. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest"])
        
        # Check if there are any test files
        test_dir = self.modules_dir / "tests" if (self.modules_dir / "tests").exists() else self.modules_dir
        
        # Results dictionary
        test_results: Dict[str, Any] = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "failures": {}
        }
        
        try:
            # Run pytest with json report
            result = subprocess.run(
                [
                    "pytest", 
                    str(test_dir), 
                    "--verbose",
                    "-xvs",
                ],
                capture_output=True,
                text=True
            )
            
            # Parse the output (simplified parsing)
            test_results["tests_run"] = result.stdout.count("PASSED") + result.stdout.count("FAILED")
            test_results["tests_passed"] = result.stdout.count("PASSED")
            test_results["tests_failed"] = result.stdout.count("FAILED")
            
            # Store failures
            failures = {}
            for line in result.stdout.splitlines():
                if "FAILED" in line:
                    parts = line.split("FAILED")
                    if len(parts) >= 2:
                        test_name = parts[0].strip()
                        failures[test_name] = "Test failed"
            
            test_results["failures"] = failures
            
            # Store in results
            self.results["tests"] = {
                "success": test_results["tests_failed"] == 0 and test_results["tests_run"] > 0,
                "tests_run": test_results["tests_run"],
                "tests_passed": test_results["tests_passed"],
                "tests_failed": test_results["tests_failed"],
                "failures": test_results["failures"]
            }
            
            if test_results["tests_failed"] == 0:
                if test_results["tests_run"] > 0:
                    print(f"✅ All {test_results['tests_run']} tests passed")
                else:
                    print("⚠️ No tests were run")
            else:
                print(f"❌ {test_results['tests_failed']} tests failed out of {test_results['tests_run']}")
        
        except Exception as e:
            print(f"Error running tests: {str(e)}")
            self.results["tests"] = {
                "success": False,
                "error": str(e),
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "failures": {"general": str(e)}
            }
        
        return test_results["tests_failed"], test_results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all selected tests and return results.
        
        Returns:
            Dictionary with all test results
        """
        # Run tests in sequence
        if self.run_mypy:
            self.run_mypy_type_checking()
        
        if self.run_lint:
            self.run_linting()
        
        # Always test imports
        self.test_imports()
        
        if self.run_tests:
            self.run_unit_tests()
        
        # Generate overall success status
        overall_success = all(
            result.get("success", False) 
            for type_name, result in self.results.items()
            if type_name == "import" or  # Imports are essential
               (type_name == "mypy" and self.run_mypy) or
               (type_name == "lint" and self.run_lint) or
               (type_name == "tests" and self.run_tests)
        )
        
        # Add overall result
        self.results["overall"] = {
            "success": overall_success,
            "modules_directory": str(self.modules_dir)
        }
        
        # Write report if requested
        if self.report_file:
            try:
                with open(self.report_file, 'w') as f:
                    json.dump(self.results, f, indent=2)
                print(f"Test report written to {self.report_file}")
            except Exception as e:
                print(f"Error writing report: {str(e)}")
        
        return self.results
    
    def print_summary(self) -> None:
        """Print a summary of all test results."""
        print("\n== Test Summary ==")
        print(f"Modules directory: {self.modules_dir}")
        
        # Overall result
        overall = self.results.get("overall", {})
        if overall.get("success", False):
            print("✅ Overall: All critical tests passed")
        else:
            print("❌ Overall: Some tests failed")
        
        # Import tests
        import_results = self.results.get("import", {})
        print(f"\nImport tests: {import_results.get('imported_count', 0)} successful, {import_results.get('errors_count', 0)} failed")
        
        # Type checking
        if self.run_mypy:
            mypy_results = self.results.get("mypy", {})
            print(f"Type checking: {mypy_results.get('errors_count', 0)} errors")
        
        # Linting
        if self.run_lint:
            lint_results = self.results.get("lint", {})
            print(f"Linting: {lint_results.get('errors_count', 0)} errors")
        
        # Unit tests
        if self.run_tests:
            test_results = self.results.get("tests", {})
            print(f"Unit tests: {test_results.get('tests_passed', 0)} passed, {test_results.get('tests_failed', 0)} failed")

def main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description='Test converted Python modules')
    parser.add_argument('--modules-dir', required=True, help='Directory containing Python modules to test')
    parser.add_argument('--report-file', help='File to write test report (JSON format)')
    parser.add_argument('--skip-mypy', action='store_true', help='Skip mypy type checking')
    parser.add_argument('--skip-lint', action='store_true', help='Skip flake8 linting')
    parser.add_argument('--skip-tests', action='store_true', help='Skip unit tests')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.modules_dir):
        print(f"Error: {args.modules_dir} is not a directory")
        return 1
    
    tester = ConvertedModuleTester(
        modules_dir=args.modules_dir,
        report_file=args.report_file,
        run_mypy=not args.skip_mypy,
        run_lint=not args.skip_lint,
        run_tests=not args.skip_tests
    )
    
    results = tester.run_all_tests()
    tester.print_summary()
    
    # Return non-zero exit code if overall tests failed
    return 0 if results.get("overall", {}).get("success", False) else 1

if __name__ == '__main__':
    sys.exit(main()) 