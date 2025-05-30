# Character System Tests

This directory contains tests for the character system.

## Test Files

- `test_character_builder.py`: session = mock.MagicMock(spec=Session)
- `test_character_service.py`: Tests for the CharacterService class.
- `test_character_system_integration.py`: Integration tests for the character system services.
- `test_event_dispatcher.py`: Tests for the character system
- `test_goal_service.py`: Tests for the GoalService class.
- `test_mood_service.py`: Tests for the MoodService class.
- `test_relationship_service.py`: session = mock.MagicMock(spec=Session)
- `test_world_state_manager.py`: Tests for the character system

## Running Tests

Tests are run as part of the standard test suite. You can also run them individually:

```bash
# Run all character tests
pytest backend/tests/systems/character/

# Run a specific test file
pytest backend/tests/systems/character/test_file.py
```
