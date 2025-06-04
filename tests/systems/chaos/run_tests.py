#!/usr/bin/env python3
"""
Test runner for Chaos System tests

Provides convenient ways to run different test suites for the chaos system.
"""

import sys
import argparse
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {description}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Run Chaos System tests")
    parser.add_argument(
        "--suite", 
        choices=["all", "unit", "integration", "performance", "compliance"], 
        default="all",
        help="Test suite to run"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Verbose output"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true", 
        help="Run with coverage reporting"
    )
    parser.add_argument(
        "--parallel", "-j", 
        type=int, 
        default=1, 
        help="Number of parallel test processes"
    )
    parser.add_argument(
        "--quick", 
        action="store_true", 
        help="Skip slow tests"
    )
    parser.add_argument(
        "--failfast", "-x", 
        action="store_true", 
        help="Stop on first failure"
    )
    parser.add_argument(
        "--profile", 
        action="store_true", 
        help="Profile test execution"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    base_cmd = ["python", "-m", "pytest"]
    
    # Add verbosity
    if args.verbose:
        base_cmd.append("-v")
    
    # Add coverage
    if args.coverage:
        base_cmd.extend([
            "--cov=backend.systems.chaos", 
            "--cov-report=html:tests/coverage_html",
            "--cov-report=term-missing"
        ])
    
    # Add parallel execution
    if args.parallel > 1:
        base_cmd.extend(["-n", str(args.parallel)])
    
    # Add fail fast
    if args.failfast:
        base_cmd.append("-x")
    
    # Add profiling
    if args.profile:
        base_cmd.append("--profile")
    
    # Test directory
    test_dir = Path(__file__).parent
    
    success = True
    
    if args.suite == "all" or args.suite == "unit":
        # Unit tests
        cmd = base_cmd + [
            str(test_dir / "test_warning_system.py"),
            str(test_dir / "test_narrative_moderator.py"),
            str(test_dir / "test_chaos_manager.py")
        ]
        
        if args.quick:
            cmd.extend(["-m", "not slow"])
        
        if not run_command(cmd, "Unit Tests"):
            success = False
    
    if args.suite == "all" or args.suite == "integration":
        # Integration tests
        cmd = base_cmd + [
            str(test_dir / "test_integration.py"),
            "-m", "integration or not integration"  # Run all integration tests
        ]
        
        if args.quick:
            cmd.extend(["-m", "integration and not slow"])
        
        if not run_command(cmd, "Integration Tests"):
            success = False
    
    if args.suite == "all" or args.suite == "performance":
        # Performance tests
        cmd = base_cmd + [
            str(test_dir / "test_integration.py"),
            "-m", "performance"
        ]
        
        if not args.quick:  # Skip performance tests in quick mode
            if not run_command(cmd, "Performance Tests"):
                success = False
    
    if args.suite == "all" or args.suite == "compliance":
        # Bible compliance tests
        cmd = base_cmd + [
            str(test_dir / "test_integration.py"),
            "-m", "bible_compliance"
        ]
        
        if not run_command(cmd, "Bible Compliance Tests"):
            success = False
    
    # Summary
    print(f"\n{'='*60}")
    if success:
        print("✅ All test suites completed successfully!")
    else:
        print("❌ Some test suites failed!")
        sys.exit(1)
    
    # Coverage report info
    if args.coverage:
        coverage_html = test_dir / "coverage_html" / "index.html"
        print(f"\n📊 Coverage report generated: {coverage_html}")
    
    print(f"{'='*60}")


if __name__ == "__main__":
    main() 