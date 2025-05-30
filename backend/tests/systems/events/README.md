# Events System Tests

This directory contains tests for the events system.

## Test Files

- `test_batch_processor.py`: Tests for the BatchEventProcessor and EventBatch classes.
- `test_dispatcher.py`: Tests for the EventDispatcher class.
- `test_enhanced_event_dispatcher.py`: Tests for the EnhancedEventDispatcher class.
- `test_event_dispatcher.py`: Unit tests for the Event Dispatcher system.
- `test_event_manager.py`: Tests for the EventManager utility class.
- `test_middleware.py`: Tests for the event system middleware components.

## Running Tests

Tests are run as part of the standard test suite. You can also run them individually:

```bash
# Run all events tests
pytest backend/tests/systems/events/

# Run a specific test file
pytest backend/tests/systems/events/test_file.py
```
