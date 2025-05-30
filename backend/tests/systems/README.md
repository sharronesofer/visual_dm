# Visual DM Tests

This directory contains tests for the Visual DM backend systems.

## Test Organization

Tests are organized to match the backend directory structure:

```
tests/
├── systems/           # Tests for specific system components
│   ├── auth_user/     # Auth user system tests
│   ├── character/     # Character system tests
│   ├── events/        # Events system tests
│   ├── inventory/     # Inventory system tests 
│   ├── rumor/         # Rumor system tests
│   └── ...
├── integration/       # Cross-system integration tests
└── utils/             # Test utilities and fixtures
```

## Deduplication Tests

Special attention has been given to testing components that were deduplicated:

### Events System Tests

`tests/systems/events/test_event_dispatcher.py`: Tests the unified EventDispatcher implementation with:

- Tests for the canonical implementation (models.event_dispatcher)
- Tests for the compatibility layer (services.event_dispatcher_deprecated)
- Tests for middleware functionality
- Tests for priority-based handlers
- Cross-interface compatibility tests

### GPT Client Tests

`tests/systems/rumor/test_gpt_client.py`: Tests both GPT client implementations:

- Tests for the centralized client (core.ai.gpt_client)
- Tests for the compatibility wrapper (systems.rumor.gpt_client_deprecated)
- Integration tests with RumorTransformer
- Mock implementation to avoid actual API calls

## Running Tests

To run all tests:

```bash
pytest
```

To run specific system tests:

```bash
# Run just event dispatcher tests
pytest backend/tests/systems/events/test_event_dispatcher.py

# Run just GPT client tests
pytest backend/tests/systems/rumor/test_gpt_client.py
```

To run with verbose output:

```bash
pytest -v
```

## Test Coverage

To generate a test coverage report:

```bash
pytest --cov=backend --cov-report=html
```

This will create an HTML report in the `htmlcov` directory.

## Test Requirements

Tests require the following packages:

- pytest
- pytest-asyncio (for testing async functionality)
- pytest-cov (for coverage reports)
- httpx (for API client tests)

Install them with:

```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

## Mocking Strategy

Tests are designed to avoid external dependencies:

- API calls are mocked with `unittest.mock`
- Database calls use in-memory test databases
- File operations use temporary directories 