# Event System Migration Guide

This guide provides instructions for migrating from the old event system implementations to the new unified event system located at `backend/app/core/events/`.

## Background

The Visual DM Development Bible specifies a central event dispatcher following a publish-subscribe pattern. Previously, there were multiple dispatcher implementations causing confusion:

- `EventDispatcher` in `backend/systems/events/event_dispatcher.py`
- `EnhancedEventDispatcher` in `backend/systems/events/enhanced_event_dispatcher.py`
- `dispatcher.py` in `backend/systems/events/dispatcher.py`

The new implementation consolidates these into a single, canonical implementation at `backend/app/core/events/`.

## Key Changes

1. **Canonical Location**: The event system is canonically located at `backend/systems/events/`
2. **Unified Interface**: Single `EventDispatcher` with consistent interfaces
3. **Type Safety**: All events now inherit from `EventBase` and use typed event classes
4. **Middleware Support**: Built-in middleware for logging, analytics, and filtering
5. **Consistent Naming**: Standardized event type strings in the `EventType` enum
6. **Thread Safety**: All operations are thread-safe by default

## Migration Steps

### Step 1: Update Imports

Replace old imports with new ones:

```python
# Old imports (deprecated)
from backend.systems.events import EventDispatcher
from backend.systems.events.base import EventBase
from backend.systems.events import EventType

# New imports (canonical)
from backend.systems.events import (
    EventDispatcher, EventBase, EventType,
    get_event_dispatcher  # convenience function
)
```

### Step 2: Use Canonical Event Types

Replace custom event classes with canonical ones:

```python
# Old way
from backend.systems.events.base import EventBase

class CustomEvent(EventBase):
    def __init__(self, event_type, data):
        self.event_type = event_type
        self.data = data

# New way
from backend.systems.events import CharacterEvent

class CharacterMovedEvent(CharacterEvent):
    event_type: str = EventType.CHARACTER_MOVED
    old_location_id: str
    new_location_id: str
```

### Step 3: Update Event Creation

Use Pydantic models instead of manual object creation:

```python
# Old way
event = CustomEvent(
    event_type="character.moved",
    data={"character_id": "123", "old_location": "A", "new_location": "B"}
)

# New way
from backend.systems.events import CharacterMoved

event = CharacterMoved(
    character_id="123",
    old_location_id="A",
    new_location_id="B"
)
```

### Step 4: Update Event Publishing

Use the canonical dispatcher:

```python
# Old way
dispatcher = EventDispatcher()  # or EventDispatcher.get_instance()
dispatcher.publish(event)

# New way
from backend.systems.events import get_event_dispatcher

dispatcher = get_event_dispatcher()
dispatcher.publish(event)
```

### Step 5: Update Event Subscriptions

Update subscription style:

```python
# Old way
def handler(event):
    print(f"Received event: {event.event_type}")

dispatcher = EventDispatcher.get_instance()
dispatcher.subscribe("character.moved", handler)

# New way
from backend.systems.events import EventType, get_event_dispatcher

def handler(event):
    print(f"Received event: {event.event_type}")

dispatcher = get_event_dispatcher()
dispatcher.subscribe(EventType.CHARACTER_MOVED, handler)
# or
dispatcher.subscribe("character.moved", handler)  # Still supported for backward compatibility
```

### Step 6: Use Middleware If Needed

```python
from backend.systems.events import (
    get_event_dispatcher, 
    LoggingMiddleware,
    FilteringMiddleware
)

# Add logging middleware
dispatcher = get_event_dispatcher()
dispatcher.add_middleware(LoggingMiddleware())

# Add filtering middleware to block certain event types
filter_middleware = FilteringMiddleware()
filter_middleware.block_type(EventType.MEMORY_RECALLED)  # Block memory recall events
dispatcher.add_middleware(filter_middleware)
```

### Step 7: Use Async Interface If Needed

```python
import asyncio
from backend.systems.events import get_event_dispatcher, CharacterMoved

async def publish_events():
    dispatcher = get_event_dispatcher()
    event = CharacterMoved(
        character_id="123",
        old_location_id="A",
        new_location_id="B"
    )
    await dispatcher.publish_async(event)

# Subscribe with async handler
async def async_handler(event):
    await asyncio.sleep(0.1)  # Simulate async operation
    print(f"Handled async event: {event.event_type}")

dispatcher = get_event_dispatcher()
dispatcher.subscribe_async(EventType.CHARACTER_MOVED, async_handler)
```

## Common Migration Issues

### Issue 1: Using Old Event Types

If you see errors like `AttributeError: 'module' object has no attribute 'EventType'`, you might be using old event type imports. Update to use the new `EventType` enum from `backend.systems.events`.

### Issue 2: Missing Event Fields

If you see validation errors like `pydantic.error_wrappers.ValidationError: 1 validation error for CharacterMoved`, you might be missing required fields in the event. Check the event class definition for required fields.

### Issue 3: Circular Imports

If you're getting circular import errors, you might need to refactor your code to avoid importing event dispatcher in your module's global scope. Consider:

```python
# Instead of this at module level
from backend.systems.events import get_event_dispatcher
dispatcher = get_event_dispatcher()

# Do this in your functions
def my_function():
    from backend.systems.events import get_event_dispatcher
    dispatcher = get_event_dispatcher()
    # Use dispatcher here
```

## Legacy Support

For backward compatibility, the old event system is still available but deprecated. You should migrate to the new system as soon as possible.

If you must use the old system temporarily, you can still import it from its original location, but it will log deprecation warnings:

```python
from backend.systems.events import EventDispatcher  # Will log deprecation warning
```

## Testing Your Migration

After migrating, you should test that your events are still being processed correctly:

1. Add a test subscriber to key events
2. Log all events being fired
3. Verify that the expected handlers are being called

## Need Help?

If you encounter issues during migration, please contact the development team for assistance. 