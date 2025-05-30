# Crafting System Tests

This directory contains tests for the crafting system.

## Test Files

- `test_crafting_service.py`: Unit tests for the CraftingService.
- `test_integration.py`: Integration tests for the crafting system.
- `test_models.py`: Unit tests for crafting system models.
- `test_schemas.py`: Tests for schema validation in the crafting system.

## Running Tests

Tests are run as part of the standard test suite. You can also run them individually:

```bash
# Run all crafting tests
pytest backend/tests/systems/crafting/

# Run a specific test file
pytest backend/tests/systems/crafting/test_file.py
```
