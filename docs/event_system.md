# Event System Documentation

This document provides an overview of the Event System implementation for Visual_DM, which has been migrated from TypeScript to both Python and C#.

## Overview

The Event System provides a flexible, type-safe publisher-subscriber pattern for component communication across the application. The system has been implemented with matching APIs and functionality in both Python (backend) and C# (Unity frontend) to ensure consistent usage patterns and behavior.

## Key Features

Both implementations share these core features:

- **Type-safe events**: Events can be strongly typed (classes, primitives, or custom types)
- **Prioritized handlers**: Event handlers are called in priority order
- **Event filtering**: Handlers can specify filters to process only certain events
- **Asynchronous support**: Both synchronous and asynchronous event handlers are supported
- **Memory safety**: Uses weak references to prevent memory leaks
- **Error isolation**: Errors in one handler don't affect other handlers

## Python Implementation

The Python implementation is found in `backend/core/events/event_bus.py` and provides:

```python
# Get the singleton instance
from backend.core.events.event_bus import event_bus

# Subscribe to events
event_bus.subscribe(EventType, handler_function, EventPriority.NORMAL)
event_bus.subscribe_async(EventType, async_handler_function)

# Publish events
event_bus.emit(EventType, event_data)
await event_bus.emit_async(EventType, event_data)  # Waits for async handlers

# Unsubscribe from events
event_bus.unsubscribe(EventType, handler_function)
event_bus.unsubscribe_async(EventType, async_handler_function)
```

### Python-specific Features

- **Pydantic model support**: Integrates well with Pydantic models for structured events
- **Asyncio integration**: Leverages Python's asyncio for async event handling
- **Logging integration**: Built-in logging for debugging and monitoring

## C# Unity Implementation

The C# implementation for Unity is found in `UnityClient/Assets/Scripts/Core/EventBus.cs` and provides:

```csharp
// Get the singleton instance
var eventBus = EventBus.Instance;

// Subscribe to events
eventBus.Subscribe<EventType>(handlerFunction, EventPriority.Normal);
eventBus.SubscribeAsync<EventType>(asyncHandlerFunction);

// Publish events
eventBus.Publish(eventData);
await eventBus.PublishAsync(eventData);  // Waits for async handlers

// Unsubscribe from events
eventBus.Unsubscribe<EventType>(handlerFunction);
eventBus.UnsubscribeAsync<EventType>(asyncHandlerFunction);
```

### C#-specific Features

- **ScriptableObject Event Channels**: Implements a Unity-friendly event channel system using ScriptableObjects
- **Thread safety**: Ensures events are processed on the main Unity thread
- **Extension methods**: Provides utility extension methods for common operations
- **Simplified API**: Offers a static `EventSystem` class for even simpler usage

### Event Channels

The Unity implementation includes ScriptableObject-based event channels for Unity-specific integration:

- `VoidEventChannel`: For events with no parameters
- `StringEventChannel`: For string events
- `GameObjectEventChannel`: For GameObject events
- `Vector3EventChannel`: For position/direction events

These can be created in the Unity Editor and assigned in the Inspector, providing a visual way to wire up events.

## Usage Examples

### Python Example

```python
from backend.core.events.event_bus import event_bus, EventPriority
from pydantic import BaseModel

# Define an event class
class UserEvent(BaseModel):
    user_id: str
    action: str

# Subscribe to events
def handle_user_event(event: UserEvent):
    print(f"User {event.user_id} performed {event.action}")

event_bus.subscribe(UserEvent, handle_user_event, EventPriority.HIGH)

# Publish events
event_bus.emit(UserEvent, UserEvent(user_id="user123", action="login"))
```

### C# Example

```csharp
using VisualDM.Core;

// Define an event class
public class UserEvent
{
    public string UserId;
    public string Action;
}

// Subscribe to events using the simplified API
void Start()
{
    EventSystem.Subscribe<UserEvent>(HandleUserEvent, EventPriority.High);
}

void HandleUserEvent(UserEvent evt)
{
    Debug.Log($"User {evt.UserId} performed {evt.Action}");
}

// Publish events
void LoginUser()
{
    EventSystem.Publish(new UserEvent { UserId = "user123", Action = "login" });
}
```

## Best Practices

1. **Define clear event types**: Create specific event classes rather than using generic types
2. **Keep events small and focused**: Events should contain only the necessary data
3. **Use prioritization appropriately**: Higher priority for UI updates, lower for logging/analytics
4. **Unsubscribe when done**: Always unsubscribe when a component is destroyed
5. **Validate event data**: Check for required fields before acting on events
6. **Handle errors gracefully**: Event handlers should catch and handle their own exceptions
7. **Use async handlers for long operations**: Don't block the main thread in event handlers

## Testing

Both implementations include comprehensive test suites:

- Python: `backend/tests/core/events/test_event_bus.py`
- C#: `UnityClient/Assets/Scripts/Tests/Core/EventBusTests.cs`

These tests demonstrate usage patterns and verify all functionality works as expected.

## Additional Resources

- Example usage: `backend/examples/event_bus_example.py`
- Unity example: `UnityClient/Assets/Scripts/Examples/EventBusUsage.cs` 