# Visual DM Events System

This directory contains the consolidated event system for Visual DM. The event system is a core architectural component that facilitates communication between different subsystems through a publish-subscribe pattern.

## Consolidation Notice

The event system components previously existed in two separate directories:
- `/backend/systems/event/` (singular)
- `/backend/systems/events/` (plural)

These have been consolidated into a single canonical implementation in `/backend/systems/events/` (plural). The singular version (`/backend/systems/event/`) is maintained for backward compatibility but will display deprecation warnings. Please update your imports to use the plural version.

## Core Components

- `EventBase`: Base class for all event types
- `EventDispatcher`: Central event bus implementing the pub-sub pattern
- `canonical_events.py`: Predefined event classes for all subsystems
- Middleware components for logging, error handling, and analytics

## Usage Examples

### 1. Subscribing to Events

```python
from backend.systems.events import EventDispatcher, MemoryCreated

def handle_memory_created(event: MemoryCreated):
    print(f"Memory created: {event.memory_id} for entity {event.entity_id}")

dispatcher = EventDispatcher.get_instance()
dispatcher.subscribe(MemoryCreated, handle_memory_created)
```

### 2. Publishing Events

```python
from backend.systems.events import EventDispatcher, MemoryCreated
from uuid import uuid4

dispatcher = EventDispatcher.get_instance()
memory_id = str(uuid4())
entity_id = "character-123"

# Create and publish an event
event = MemoryCreated(
    entity_id=entity_id,
    memory_id=memory_id,
    memory_type="observation",
    content={"text": "I saw something strange in the forest"},
    importance=0.75
)
dispatcher.publish(event)
```

### 3. Middleware Usage

```python
from backend.systems.events import EventDispatcher, LoggingMiddleware

dispatcher = EventDispatcher.get_instance()
logging_middleware = LoggingMiddleware()
dispatcher.add_middleware(logging_middleware)
```

## Architecture

The event system follows the publish-subscribe pattern where:

1. Subsystems can subscribe to specific event types
2. Events are published to the central dispatcher
3. The dispatcher delivers events to all subscribed handlers
4. Middleware can intercept events for logging, analytics, etc.

This architecture provides loose coupling between subsystems, allowing them to interact without direct dependencies on each other.

## Best Practices

1. **Create specific event classes** - Define clear, specific event classes instead of using generic ones
2. **Include all relevant data** - Events should contain all data needed by subscribers
3. **Use middleware for cross-cutting concerns** - Logging, error handling, etc.
4. **Keep handlers focused** - Event handlers should be small and focused on a single responsibility
5. **Consider async handlers** for I/O bound operations

## Available Event Types

See `canonical_events.py` for a complete list of predefined event types, including:

- Memory events (MemoryCreated, MemoryRecalled, etc.)
- Rumor events (RumorCreated, RumorSpread, etc.)
- Character events (CharacterCreated, CharacterLeveledUp, etc.)
- World state events (WorldStateChanged)
- And many more...

## Directory Structure

```
backend/systems/events/
├── core/                       # Core event system components
│   ├── event_base.py           # Base class for all events
│   ├── event_dispatcher.py     # Central event bus implementation
│   └── canonical_events.py     # Standard event types
├── middleware/                 # Event processing middleware 
│   ├── logging_middleware.py   # Event logging middleware
│   ├── error_middleware.py     # Error handling middleware
│   └── analytics_middleware.py # Analytics collection middleware
├── utils/                      # Helper utilities
│   └── event_utils.py          # Convenience methods and managers
├── tests/                      # Unit tests
└── __init__.py                 # Package exports
```

## Usage

### Basic Usage

```python
from backend.systems.events import EventDispatcher, SystemEvent, SystemEventType

# Subscribe to events
def handle_system_event(event):
    print(f"System event received: {event.event_type}")

dispatcher = EventDispatcher.get_instance()
dispatcher.subscribe(SystemEvent, handle_system_event)

# Publish an event
event = SystemEvent(
    event_type=SystemEventType.STARTUP.value,
    component="main_app"
)
dispatcher.publish_sync(event)
```

### Using the EventManager

The EventManager provides a simpler interface for working with events:

```python
from backend.systems.events import EventManager, MemoryEvent, MemoryEventType

# Create manager
manager = EventManager()

# Subscribe to events
manager.subscribe(MemoryEvent, handle_memory_event)

# Publish an event
event = MemoryEvent(
    event_type=MemoryEventType.CREATED.value,
    entity_id="npc_123",
    memory_id="memory_456",
    memory_type="observation",
    content="Saw the player in the tavern"
)
manager.publish(event)

# Clean up when done
manager.cleanup()
```

### Middleware

Add middleware to perform operations on all events:

```python
from backend.systems.events import EventDispatcher, logging_middleware

dispatcher = EventDispatcher.get_instance()
dispatcher.add_middleware(logging_middleware)
```

## Event Types

All event types inherit from `EventBase` and include:

- **SystemEvent**: System-level events (startup, shutdown, errors)
- **MemoryEvent**: Memory operations (created, accessed, etc.)
- **RumorEvent**: Rumor spread and mutations
- **MotifEvent**: Motif changes and activations
- **PopulationEvent**: Population metrics changes
- **POIEvent**: Point of Interest state changes
- **FactionEvent**: Faction-related events
- **QuestEvent**: Quest status updates
- **CombatEvent**: Combat operations
- **TimeEvent**: Time progression events
- **RelationshipEvent**: Entity relationship changes
- **StorageEvent**: Save/load operations
- **WorldStateEvent**: World state variable changes

See `core/canonical_events.py` for the full list of event types and their schemas.

## Testing

Run the tests with pytest:

```bash
pytest backend/systems/events/tests/
```

## Extending

To add a new event type:

1. Create a new class inheriting from `EventBase` in an appropriate module
2. Define the event schema using Pydantic fields
3. Optionally add an enum for standardized event types
4. Export the new event type in `__init__.py`
5. Write tests for the new event type

To add new middleware:

1. Create a new function in the middleware package
2. Follow the middleware signature: `async def my_middleware(event, next_middleware)`
3. Export the middleware in `middleware/__init__.py`
