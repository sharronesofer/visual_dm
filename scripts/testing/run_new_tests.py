#!/usr/bin/env python
"""
Test Runner for Development Bible Implementation Tests

This script runs the tests created specifically to verify implementation
of key concepts from the Development Bible.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Make sure backend is in the path
backend_dir = Path(__file__).parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Development Bible test files
DEV_BIBLE_TESTS = [
    "backend/tests/systems/poi/test_poi_state_transitions.py",
    "backend/tests/systems/region/test_biome_adjacency.py",
    "backend/tests/systems/data/test_schema_validation.py",
    "backend/tests/systems/faction/test_region_political_integration.py"
]

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run tests for Development Bible implementation"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate a coverage report"
    )
    
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML coverage report"
    )
    
    parser.add_argument(
        "--xml",
        action="store_true",
        help="Generate XML coverage report"
    )
    
    parser.add_argument(
        "--individual",
        action="store_true",
        help="Run tests individually rather than all at once"
    )
    
    parser.add_argument(
        "--test",
        choices=["poi", "region", "data", "faction", "all"],
        default="all",
        help="Choose which test category to run"
    )
    
    return parser.parse_args()

def run_tests(args):
    """Run the tests based on passed arguments."""
    print(f"Running Development Bible implementation tests...")
    
    # Determine which tests to run
    tests_to_run = []
    if args.test == "all":
        tests_to_run = DEV_BIBLE_TESTS
    elif args.test == "poi":
        tests_to_run = [t for t in DEV_BIBLE_TESTS if "poi" in t]
    elif args.test == "region":
        tests_to_run = [t for t in DEV_BIBLE_TESTS if "region" in t]
    elif args.test == "data":
        tests_to_run = [t for t in DEV_BIBLE_TESTS if "data" in t]
    elif args.test == "faction":
        tests_to_run = [t for t in DEV_BIBLE_TESTS if "faction" in t]
    
    # Check if tests exist
    existing_tests = []
    for test_file in tests_to_run:
        if os.path.exists(test_file):
            existing_tests.append(test_file)
        else:
            print(f"Warning: {test_file} not found. Skipping.")
    
    if not existing_tests:
        print("Error: No test files found!")
        return 1
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        cmd.append("-v")
    
    if args.coverage:
        cmd.extend(["--cov=backend", "--cov-report=term"])
        
        if args.html:
            cmd.append("--cov-report=html")
        
        if args.xml:
            cmd.append("--cov-report=xml")
    
    # Run tests individually or all at once
    if args.individual:
        success = True
        for test_file in existing_tests:
            print(f"\nRunning {test_file}...")
            test_cmd = cmd + [test_file]
            result = subprocess.run(test_cmd)
            if result.returncode != 0:
                success = False
        return 0 if success else 1
    else:
        cmd.extend(existing_tests)
        result = subprocess.run(cmd)
        return result.returncode

def main():
    """Main entry point."""
    args = parse_args()
    return run_tests(args)

if __name__ == "__main__":
    sys.exit(main()) 