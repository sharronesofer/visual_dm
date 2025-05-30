# Visual DM Backend Tests

This directory contains the primary test suite for the Visual DM backend. The tests are organized to match the backend directory structure and cover all major systems and functionality.

## Test Organization

```
tests/                      # Standard test directory
├── systems/                # Tests for specific system components
│   ├── auth_user/          # Auth user system tests
│   ├── character/          # Character system tests
│   ├── events/             # Events system tests 
│   ├── inventory/          # Inventory system tests
│   ├── rumor/              # Rumor system tests
│   └── ...
├── unit/                   # Unit tests for lower-level components
└── conftest.py             # Common fixtures for all tests

Additional tests may exist scattered throughout the backend/ directory structure:
- backend/**/*.py           # Any file matching test_*.py or *_test.py patterns
```

## Running Tests

### Using the test runner script

The easiest way to run tests is using the provided `run_all_tests.py` script at the project root:

```bash
# Run standard tests (in backend/tests/)
python run_all_tests.py

# Run ALL tests (including those outside standard test directory)
python run_all_tests.py --all

# Run ONLY tests directly in backend/ (not in backend/tests/)
python run_all_tests.py --backend-only

# Run with coverage report
python run_all_tests.py --coverage

# Run with HTML coverage report
python run_all_tests.py --coverage --html

# Run tests for a specific system
python run_all_tests.py --system memory

# Run a specific test file
python run_all_tests.py --test backend/tests/systems/memory/test_memory_manager.py

# Run tests in parallel
python run_all_tests.py --parallel

# Just discover and list all test files without running them
python run_all_tests.py --discover
```

### Using pytest directly

You can also use pytest directly:

```bash
# Run all tests in the standard test directory
pytest backend/tests/

# Run all tests in backend, including those outside the test directory
pytest backend/tests/ backend/systems/**/test_*.py backend/systems/**/*_test.py

# Run with coverage
pytest --cov=backend backend/tests/

# Run tests for a specific system
pytest backend/tests/systems/memory/

# Run a specific test file
pytest backend/tests/systems/memory/test_memory_manager.py

# Run a specific test
pytest backend/tests/test_events_system.py::TestBasicEventDispatcher::test_subscribe_and_publish
```

## Test Dependencies

Tests require the following packages:

- pytest
- pytest-asyncio (for testing async functionality)
- pytest-cov (for coverage reports)
- pytest-mock (for enhanced mocking)
- httpx (for API client tests)
- pytest-xdist (for parallel testing)

These can be installed with:

```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock httpx pytest-xdist
```

## Test Configuration

Tests are configured via the `pytest.ini` file at the project root. Key configurations include:

- Test discovery patterns
- Markers for categorizing tests
- Logging settings
- Coverage settings

## Common Fixtures

Common fixtures are defined in `conftest.py` and include:

- Directory paths (`tests_root_dir`, `backend_root_dir`, `data_dir`)
- Mock services (`mock_event_dispatcher`, `mock_storage`, `mock_gpt_client`)
- Sample data (`sample_memory_data`, `sample_rumor_data`, `sample_motif_data`)
- Setup/teardown fixtures (`reset_singletons`, `mock_dependencies`)
- Async fixtures (`event_loop`)

## Writing New Tests

When writing new tests:

1. **Preferred location:** Place tests in the appropriate directory under `systems/` to match the backend structure
2. **Alternative approach:** You can also create test files directly alongside the code they test:
   - Use `test_*.py` or `*_test.py` naming convention 
   - The test runner will find them automatically
3. Use the common fixtures from `conftest.py`
4. Follow the existing patterns for test class and method naming
5. Add appropriate markers for test categorization
6. Ensure 100% coverage for critical systems

## CI/CD Integration

Tests are automatically run on GitHub Actions for every push and pull request to the main and develop branches. The workflow:

1. Runs all tests (both standard tests and those scattered throughout backend/) on both Python 3.9 and 3.10
2. Generates a coverage report
3. Uploads the coverage report to Codecov
4. Runs individual system tests in parallel
5. Runs tests directly in backend/ (outside standard test directory) separately

## Contact

For questions about the test suite, contact the development team at [email protected] 