# Python Event System

This directory contains the Python implementation of the Visual_DM Event System.

## Key Files

- `event_bus.py`: Core implementation of the EventBus with type-safe events, prioritization, and async support

## Usage

The EventBus is available as a singleton instance:

```python
from backend.core.events.event_bus import event_bus, EventPriority

# Subscribe to events
event_bus.subscribe("event_type", handler_function)
event_bus.subscribe_async("event_type", async_handler_function)

# Publish events
event_bus.emit("event_type", event_data)
await event_bus.emit_async("event_type", event_data)
```

## Documentation

For complete documentation including examples and best practices, see:

- [Event System Documentation](/docs/event_system.md)
- [Python Example](/backend/examples/event_bus_example.py)
- [Python Tests](/backend/tests/core/events/test_event_bus.py) 