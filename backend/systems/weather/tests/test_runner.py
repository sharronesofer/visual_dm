"""
Weather System Test Runner

Provides convenience functions for running weather system tests
following Development Bible testing patterns.
"""

import pytest
import sys
import os
from pathlib import Path


def run_all_weather_tests(verbose: bool = True) -> int:
    """
    Run all weather system tests
    
    Args:
        verbose: Whether to run in verbose mode
        
    Returns:
        Exit code (0 = success, non-zero = failure)
    """
    # Get the current directory (weather/tests)
    current_dir = Path(__file__).parent
    
    # Test discovery pattern
    test_pattern = "test_*.py"
    
    # Pytest arguments
    args = [
        str(current_dir),
        "-v" if verbose else "",
        "--tb=short",
        "--strict-markers",
        f"--rootdir={current_dir.parent}",  # weather system root
    ]
    
    # Remove empty strings
    args = [arg for arg in args if arg]
    
    print(f"Running weather system tests from: {current_dir}")
    print(f"Test pattern: {test_pattern}")
    print(f"Pytest args: {' '.join(args)}")
    print("-" * 60)
    
    return pytest.main(args)


def run_specific_test_class(test_class_name: str, verbose: bool = True) -> int:
    """
    Run a specific test class
    
    Args:
        test_class_name: Name of the test class (e.g., 'TestWeatherBusinessService')
        verbose: Whether to run in verbose mode
        
    Returns:
        Exit code (0 = success, non-zero = failure)
    """
    current_dir = Path(__file__).parent
    
    # Map test class names to files
    test_file_map = {
        'TestWeatherBusinessService': 'test_weather_business_service.py',
        'TestWeatherRepositoryImpl': 'test_weather_repository.py', 
        'TestWeatherValidationServiceImpl': 'test_weather_validation_service.py',
        'TestWeatherEventHandler': 'test_weather_event_handler.py',
        'TestWeatherRouter': 'test_weather_router.py'
    }
    
    if test_class_name not in test_file_map:
        print(f"Unknown test class: {test_class_name}")
        print(f"Available classes: {', '.join(test_file_map.keys())}")
        return 1
    
    test_file = current_dir / test_file_map[test_class_name]
    test_target = f"{test_file}::{test_class_name}"
    
    args = [
        test_target,
        "-v" if verbose else "",
        "--tb=short",
        "--strict-markers",
    ]
    
    # Remove empty strings
    args = [arg for arg in args if arg]
    
    print(f"Running test class: {test_class_name}")
    print(f"Test file: {test_file}")
    print("-" * 60)
    
    return pytest.main(args)


def run_specific_test_method(test_class_name: str, test_method_name: str, verbose: bool = True) -> int:
    """
    Run a specific test method
    
    Args:
        test_class_name: Name of the test class
        test_method_name: Name of the test method
        verbose: Whether to run in verbose mode
        
    Returns:
        Exit code (0 = success, non-zero = failure)
    """
    current_dir = Path(__file__).parent
    
    # Map test class names to files
    test_file_map = {
        'TestWeatherBusinessService': 'test_weather_business_service.py',
        'TestWeatherRepositoryImpl': 'test_weather_repository.py', 
        'TestWeatherValidationServiceImpl': 'test_weather_validation_service.py',
        'TestWeatherEventHandler': 'test_weather_event_handler.py',
        'TestWeatherRouter': 'test_weather_router.py'
    }
    
    if test_class_name not in test_file_map:
        print(f"Unknown test class: {test_class_name}")
        return 1
    
    test_file = current_dir / test_file_map[test_class_name]
    test_target = f"{test_file}::{test_class_name}::{test_method_name}"
    
    args = [
        test_target,
        "-v" if verbose else "",
        "--tb=long",  # More detail for single test
        "--strict-markers",
    ]
    
    # Remove empty strings
    args = [arg for arg in args if arg]
    
    print(f"Running test: {test_class_name}.{test_method_name}")
    print(f"Test file: {test_file}")
    print("-" * 60)
    
    return pytest.main(args)


def run_with_coverage() -> int:
    """
    Run tests with coverage reporting
    
    Returns:
        Exit code (0 = success, non-zero = failure)
    """
    current_dir = Path(__file__).parent
    weather_system_dir = current_dir.parent
    
    args = [
        str(current_dir),
        "--cov=" + str(weather_system_dir),
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-branch",
        "-v",
        "--tb=short",
    ]
    
    print("Running weather system tests with coverage...")
    print(f"Coverage target: {weather_system_dir}")
    print("-" * 60)
    
    return pytest.main(args)


if __name__ == "__main__":
    """
    Command line interface for test runner
    
    Usage:
        python test_runner.py                           # Run all tests
        python test_runner.py --class TestWeatherBusinessService  # Run specific class
        python test_runner.py --coverage               # Run with coverage
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Weather System Test Runner")
    parser.add_argument("--class", dest="test_class", help="Run specific test class")
    parser.add_argument("--method", help="Run specific test method (requires --class)")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage reporting")
    parser.add_argument("--quiet", "-q", action="store_true", help="Run in quiet mode")
    
    args = parser.parse_args()
    
    verbose = not args.quiet
    
    if args.coverage:
        exit_code = run_with_coverage()
    elif args.test_class and args.method:
        exit_code = run_specific_test_method(args.test_class, args.method, verbose)
    elif args.test_class:
        exit_code = run_specific_test_class(args.test_class, verbose)
    else:
        exit_code = run_all_weather_tests(verbose)
    
    sys.exit(exit_code) 