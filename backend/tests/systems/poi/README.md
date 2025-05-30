# Poi System Tests

This directory contains tests for the poi system.

## Test Files

- `test_event_handlers.py`: Tests for the poi system
- `test_models.py`: Tests for the poi system
- `test_poi_state_transitions.py`: Tests for the POI state transition system.
- `test_schemas.py`: Tests for the poi system
- `test_services.py`: Tests for the poi system
- `test_tilemap_service.py`: Tests for the poi system
- `test_utils.py`: Tests for the poi system

## Running Tests

Tests are run as part of the standard test suite. You can also run them individually:

```bash
# Run all poi tests
pytest backend/tests/systems/poi/

# Run a specific test file
pytest backend/tests/systems/poi/test_file.py
```
