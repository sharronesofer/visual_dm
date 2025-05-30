#!/usr/bin/env python3
"""
Test runner for the Visual DM backend.
Run with --help to see all options.
"""

import os
import sys
import argparse
import subprocess
import time
import coverage
from datetime import datetime

# Ensure the backend directory is in the Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)


def discover_tests(module=None, pattern="test_*.py"):
    """
    Discover all test files in the backend/tests directory.
    
    Args:
        module: Optional module name to filter tests by (e.g., 'memory', 'world')
        pattern: File pattern to match for test files
        
    Returns:
        List of test file paths
    """
    tests_dir = os.path.join(SCRIPT_DIR, "backend", "tests")
    
    if not os.path.exists(tests_dir):
        print(f"Tests directory not found: {tests_dir}")
        return []
    
    if module:
        # Look for tests in the specific module
        module_dir = os.path.join(tests_dir, "systems", module)
        if os.path.exists(module_dir):
            tests_dir = module_dir
        else:
            print(f"Module tests directory not found: {module_dir}")
            return []
    
    test_files = []
    
    for root, _, files in os.walk(tests_dir):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                if module is None or module in root:
                    test_files.append(os.path.join(root, file))
    
    return test_files


def run_tests(files=None, verbose=False, coverage_enabled=False, system=None):
    """
    Run the discovered test files using pytest.
    
    Args:
        files: List of test files to run (if None, discovers them)
        verbose: Whether to enable verbose output
        coverage_enabled: Whether to collect coverage data
        system: Specific system module to test (e.g., 'memory')
        
    Returns:
        Boolean indicating if tests passed
    """
    if not files:
        files = discover_tests(module=system)
        
    if not files:
        print("No test files found.")
        return False
    
    # Create reports directory if it doesn't exist
    reports_dir = os.path.join(SCRIPT_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    # Create coverage directory if coverage is enabled
    coverage_dir = os.path.join(reports_dir, "coverage")
    if coverage_enabled:
        os.makedirs(coverage_dir, exist_ok=True)
    
    # Generate timestamp for report files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(reports_dir, f"backend_test_results_{timestamp}.txt")
    
    # Build pytest command
    cmd = ["pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage_enabled:
        cov = coverage.Coverage(
            source=["backend/systems"],
            omit=["*/__pycache__/*", "*/tests/*", "*/migrations/*"]
        )
        cov.start()
    
    # Add specific files to test
    cmd.extend(files)
    
    print(f"Running tests with command: {' '.join(cmd)}")
    print(f"Writing results to: {report_file}")
    
    # Capture the start time
    start_time = time.time()
    
    # Run the tests
    with open(report_file, "w") as f:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        f.write(result.stdout)
        print(result.stdout)
    
    # Capture the end time and calculate duration
    end_time = time.time()
    duration = end_time - start_time
    
    # Generate coverage report if enabled
    if coverage_enabled:
        try:
            cov.stop()
            coverage_report_path = os.path.join(coverage_dir, f"coverage_report_{timestamp}")
            
            # Generate HTML report
            cov.html_report(directory=f"{coverage_report_path}_html")
            
            # Generate XML report for CI integration
            cov.xml_report(outfile=f"{coverage_report_path}.xml")
            
            # Get and print the coverage percentage
            coverage_percentage = round(cov.report() * 100, 2)
            
            with open(report_file, "a") as f:
                f.write(f"\n\nCode Coverage: {coverage_percentage}%\n")
                f.write(f"Detailed coverage report: {coverage_report_path}_html/index.html\n")
                
            print(f"\nCode Coverage: {coverage_percentage}%")
            print(f"Detailed coverage report: {coverage_report_path}_html/index.html")
            
        except Exception as e:
            print(f"Error generating coverage report: {e}")
    
    # Append summary to the report
    with open(report_file, "a") as f:
        f.write(f"\n\nTest Duration: {duration:.2f} seconds\n")
        f.write(f"Exit Code: {result.returncode}\n")
    
    print(f"\nTest Duration: {duration:.2f} seconds")
    print(f"Exit Code: {result.returncode}")
    print(f"Test results saved to: {report_file}")
    
    return result.returncode == 0


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="Run backend tests for Visual DM")
    parser.add_argument("--discover", action="store_true", help="Only discover tests, don't run them")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--coverage", action="store_true", help="Generate code coverage report")
    parser.add_argument("--system", help="Run tests for a specific system module (e.g., 'memory')")
    parser.add_argument("--file", help="Run a specific test file")
    
    args = parser.parse_args()
    
    if args.discover:
        files = discover_tests(module=args.system)
        print(f"Discovered {len(files)} test files:")
        for file in files:
            print(f"  - {file}")
        return 0
    
    if args.file:
        files = [args.file]
    else:
        files = None
    
    success = run_tests(
        files=files,
        verbose=args.verbose,
        coverage_enabled=args.coverage,
        system=args.system
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 