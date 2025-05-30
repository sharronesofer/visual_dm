#!/usr/bin/env python
"""
Test runner for the shared modules tests.
"""

import unittest
import os
import sys

# Add the project root to the Python path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
)


def run_tests():
    """Run all tests for the shared modules."""
    # Discover and run all tests in the current directory
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(start_dir=os.path.dirname(__file__))

    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # Return the number of failures and errors
    return len(result.failures) + len(result.errors)


if __name__ == "__main__":
    sys.exit(run_tests())
