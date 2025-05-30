# Rumor System Tests

This directory contains tests for the rumor system.

## Test Files

- `test_api.py`: Tests for the rumor API endpoints.
- `test_decay_and_propagation.py`: Tests for the decay and propagation utilities.
- `test_gpt_client.py`: Unit tests for the GPT client implementations.
- `test_npc_rumor_routes.py`: Tests for the NPC rumor routes module.
- `test_npc_rumor_utils.py`: Tests for the NPC rumor utilities module.
- `test_prompt_manager.py`: Tests for the rumor prompt manager module.
- `test_rumor_manager.py`: Tests for the rumor manager.
- `test_rumor_models.py`: Tests for rumor models.
- `test_rumor_repository.py`: Tests for the rumor repository.
- `test_rumor_service.py`: Tests for the rumor service.
- `test_transformer.py`: Tests for the rumor transformer.
- `test_truth_tracker.py`: Tests for the truth tracker module.

## Running Tests

Tests are run as part of the standard test suite. You can also run them individually:

```bash
# Run all rumor tests
pytest backend/tests/systems/rumor/

# Run a specific test file
pytest backend/tests/systems/rumor/test_file.py
```
