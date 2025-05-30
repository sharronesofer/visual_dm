# Analytics System Tests

This directory contains tests for the analytics system, which captures, stores, and processes game events for analysis and LLM training.

## Test Files

- `test_analytics_service.py`: Tests for the AnalyticsService class, ensuring compliance with Development Bible requirements.
- `test_event_integration.py`: Tests for integration between analytics system and central event system.
- `test_schemas.py`: Tests for analytics schema validation.
- `test_utils.py`: Tests for analytics utility functions.

## Running Tests

Tests are run as part of the standard test suite. You can also run them individually:

```bash
# Run all analytics tests
pytest backend/tests/systems/analytics/

# Run a specific test file
pytest backend/tests/systems/analytics/test_analytics_service.py

# Run a specific test case
pytest backend/tests/systems/analytics/test_analytics_service.py::TestAnalyticsService::test_singleton_pattern
```

## Mocking and Dependencies

Most of these tests use mocks to isolate the analytics system from its dependencies, such as the event system and file system. This allows testing the analytics system in isolation.

- `unittest.mock` is used for most mocking.
- `tempfile` is used to create temporary directories for testing file operations.
- Event system components are mocked to test integration points. 