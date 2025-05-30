# Motif System Tests

This directory contains tests for the motif system.

## Test Files

- `test_consolidated_manager.py`: Test Consolidated Motif Manager
- `test_motif_integration.py`: Tests for the motif system
- `test_motif_manager.py`: Tests for the motif system
- `test_motif_models.py`: Tests for the motif system
- `test_motif_repository.py`: Tests for the motif system
- `test_motif_router.py`: service = MagicMock(spec=MotifService)
- `test_motif_service.py`: Tests for the motif system

## Running Tests

Tests are run as part of the standard test suite. You can also run them individually:

```bash
# Run all motif tests
pytest backend/tests/systems/motif/

# Run a specific test file
pytest backend/tests/systems/motif/test_file.py
```
