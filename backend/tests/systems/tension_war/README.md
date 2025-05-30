# Tension War System Tests

This directory contains tests for the tension_war system.

## Test Files

- `test_alliance_manager.py`: Tests for the AllianceManager service
- `test_models.py`: Tests for the models in the tension_war system.
- `test_proxy_war_manager.py`: Tests for the ProxyWarManager service
- `test_tension_manager.py`: Tests for the TensionManager service in the tension_war system.
- `test_utils.py`: Tests for utility functions in the tension_war system.
- `test_war_manager.py`: Tests for the WarManager service in the tension_war system.

## Running Tests

Tests are run as part of the standard test suite. You can also run them individually:

```bash
# Run all tension_war tests
pytest backend/tests/systems/tension_war/

# Run a specific test file
pytest backend/tests/systems/tension_war/test_file.py
```
