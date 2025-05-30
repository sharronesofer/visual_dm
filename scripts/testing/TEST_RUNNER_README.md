# Visual DM Test Runner Guide

## Overview

The Visual DM test runner (`run_all_tests.py`) provides a unified interface for running backend tests across the repository. It supports both standard tests in the `backend/tests` directory and tests scattered throughout the backend code structure.

## Usage

### Basic Usage

Run all tests in the standard tests directory:
```bash
python run_all_tests.py
```

Run with verbose output:
```bash
python run_all_tests.py --verbose
```

### Advanced Options

Run ALL tests, including those outside the standard test directory:
```bash
python run_all_tests.py --all
```

Run only tests directly in backend/ (not in backend/tests/):
```bash
python run_all_tests.py --backend-only
```

Generate a coverage report:
```bash
python run_all_tests.py --coverage
```

Generate an HTML coverage report:
```bash
python run_all_tests.py --coverage --html
```

Run tests for a specific system:
```bash
python run_all_tests.py --system memory
```

Run a specific test file:
```bash
python run_all_tests.py --test backend/tests/systems/memory/test_memory_manager.py
```

Run tests in parallel:
```bash
python run_all_tests.py --parallel
```

Just discover and list all test files without running them:
```bash
python run_all_tests.py --discover
```

### Test Dependencies

Install all test dependencies with:
```bash
pip install -r requirements-dev.txt
```

## Common Test Issues and Solutions

### 1. Import Errors

If you encounter import errors:
- Check that the module path exists
- Update deprecated import paths
- Make sure __init__.py files are present where needed

### 2. Async Mock Issues

If tests fail with: `TypeError: object MagicMock can't be used in 'await' expression`:
- Use AsyncMock instead of MagicMock for async methods:
  ```python
  from unittest.mock import AsyncMock
  
  # In your fixture
  storage_mock = AsyncMock()
  storage_mock.get = AsyncMock(return_value={})
  ```

### 3. Test/Implementation Mismatches

If tests expect different behavior than implemented:
- Update tests to match the current implementation
- Or update the implementation to match the tests
- Review assertion thresholds if tests are just barely failing

### 4. Missing Dependencies

If a module can't be found:
- Check that all dependencies are installed
- Run `pip install -r requirements-dev.txt`

### 5. Configuration Issues

If pytest configuration seems wrong:
- Check pytest.ini for syntax errors
- Remove inline comments from configuration values
- Make sure values match expected types

## Maintaining Tests

When adding new functionality:
1. Add tests in the appropriate directory under `backend/tests/`
2. Use existing fixtures from conftest.py when applicable
3. Follow the naming convention: test_*.py for files, test_* for functions
4. Add appropriate markers for test categorization

## CI/CD Integration

Tests are automatically run on GitHub Actions for every push and pull request. The workflow:
1. Runs all tests on Python 3.9 and 3.10
2. Generates a coverage report
3. Uploads the coverage report to Codecov
4. Runs system-specific tests in parallel 