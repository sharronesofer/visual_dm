# Shared Modules Test Plan

This document outlines the testing strategy for the `/backend/systems/shared` directory, which contains shared components, models, and utilities used across multiple backend systems.

## Tested Modules

The following modules have been tested:

1. **dictionary_utils.py**
   - Deep dictionary operations (get, set, merge, update)
   - Dictionary filtering and manipulation
   - Dictionary flattening and unflattening

2. **validation_utils.py**
   - Password strength validation
   - Username format validation
   - Email format validation

3. **base_manager.py**
   - Logging operations
   - Error handling

4. **json_storage_utils.py**
   - VersionedJsonStorage class
   - JSON data versioning and migration
   - Backup management
   - Standalone JSON utility functions

## Testing Approach

- **Unit Tests**: Each module has comprehensive unit tests that test individual functions and classes in isolation.
- **Mock Testing**: External dependencies like file system and logging are mocked to ensure tests are fast and deterministic.
- **Edge Cases**: Tests include edge cases, error conditions, and boundary values.
- **Test Coverage**: Tests aim for high code coverage, especially for critical data handling functions.

## Running Tests

To run all the tests for the shared modules:

```bash
# From the project root directory
python -m backend.tests.systems.shared.run_tests

# Or navigate to the test directory and run
cd backend/tests/systems/shared
python run_tests.py
```

## Future Test Needs

The following modules still need tests:

1. **memory_utils.py** - Tests for memory-related utility functions
   - Memory scoring and decay
   - Memory relevance calculation
   - Memory summarization

2. **analytics_utils.py** - Tests for analytics utility functions
   - Event tracking and logging
   - Data aggregation utilities
   - Dataset generation

3. **time_utils.py** - Tests for time-related utilities
   - Calendar operations
   - Time progression
   - Event scheduling

4. **motif_utils.py** - Tests for motif-related utilities
   - Motif selection and application
   - Motif effect calculation
   - Motif context generation

5. **random_utils.py** - Tests for random generation utilities
   - Weighted random selection
   - Distribution tests
   - Seed-based randomization

6. **event_bus_utils.py** - Tests for event bus utilities
   - Event subscription and publishing
   - Event filtering
   - Middleware functionality

7. Models directory - Tests for shared models
   - Base model functionality
   - Model validation
   - Model serialization/deserialization

## Test Development Plan

1. Prioritize testing core utility modules first (completed)
2. Add tests for event system next (event_bus_utils.py)
3. Add tests for time and analytics modules
4. Complete testing for remaining modules
5. Add integration tests for modules that work together

## Best Practices

- Keep test files organized with same structure as source
- Use descriptive test method names that explain what's being tested
- Include docstrings that describe test purpose
- Use setUp/tearDown for common test fixtures
- Mock external dependencies
- Test both normal operation and error conditions

---

Last Updated: [Current Date] 