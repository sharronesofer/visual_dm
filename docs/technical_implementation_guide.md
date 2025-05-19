# Technical Implementation Guide

This guide provides an overview of the core technical systems implemented in the Visual DM backend and how to use them.

## Overview

The following core systems have been implemented:

1. **Event System** - Central event dispatcher for communication between systems
2. **Analytics Service** - Event capture and analysis for gameplay insights and LLM training
3. **Memory System** - Entity memory storage and retrieval with relevance and decay
4. **Rumor System** - Rumor creation, spread, and mutation throughout the game world
5. **World State** - Management of game world state with historical tracking
6. **Time System** - Game time management with calendar and scheduled events

All systems are exposed through a FastAPI REST API for easy integration with the Unity frontend.

## Event System

The Event System provides a central communications backbone for all other systems. It follows a publish-subscribe pattern with middleware support.

### Key Components

- **EventDispatcher**: Singleton class for event publication and subscription
- **EventBase**: Base class for all event types
- **Middleware**: Chain of handlers for cross-cutting concerns like logging

### Example Usage

```python
from app.core.events import EventDispatcher, EventBase

# Create a custom event
class PlayerMoveEvent(EventBase):
    player_id: str
    position_x: float
    position_y: float

# Subscribe to an event
dispatcher = EventDispatcher()
async def handle_player_move(event: PlayerMoveEvent):
    print(f"Player {event.player_id} moved to {event.position_x}, {event.position_y}")

dispatcher.subscribe(PlayerMoveEvent, handle_player_move)

# Publish an event
event = PlayerMoveEvent(
    event_type="player.move",
    player_id="player123",
    position_x=10.5,
    position_y=20.3
)
await dispatcher.publish(event)
```

## Analytics Service

The Analytics Service captures game events for analysis and LLM training. It integrates with the Event System through middleware.

### Key Components

- **AnalyticsService**: Singleton class for event recording and analysis
- **AnalyticsEvent**: Base class for analytics events

### Example Usage

```python
from app.core.analytics import AnalyticsService

# Get the analytics service
analytics = AnalyticsService()

# Record an event
await analytics.record(
    category="combat",
    action="attack",
    entity_id="player123",
    entity_type="player",
    metadata={
        "target_id": "enemy456",
        "weapon": "sword",
        "damage": 25
    }
)

# Generate a training dataset
await analytics.generate_llm_dataset(
    start_date="2024-06-01",
    categories=["combat", "dialogue"],
    output_file="combat_dialogue_dataset.jsonl"
)
```

## Memory System

The Memory System manages entity memories with relevance scores, categorization, and decay over time.

### Key Components

- **MemoryManager**: Singleton class for memory operations
- **Memory**: Class representing a single memory
- **MemoryCategory**: Enum for memory categorization

### Example Usage

```python
from app.core.memory import MemoryManager, MemoryCategory

# Get the memory manager
memory_mgr = MemoryManager()

# Create a memory
memory = await memory_mgr.create_memory(
    entity_id="npc123",
    summary="Witnessed the fall of Kingdom X",
    categories=[MemoryCategory.WAR, MemoryCategory.CATASTROPHE],
    details={
        "location": "Capital City",
        "participants": ["King X", "Invading Army Y"]
    },
    is_core=True
)

# Get entity memories
memories = await memory_mgr.get_entity_memories(
    entity_id="npc123",
    categories=[MemoryCategory.WAR],
    min_relevance=0.5
)

# Generate a memory summary for LLM context
summary = await memory_mgr.generate_memory_summary(
    entity_id="npc123",
    limit=10,
    include_core_only=True
)
```

## Rumor System

The Rumor System manages rumor creation, mutation, and propagation throughout the game world.

### Key Components

- **RumorSystem**: Singleton class for rumor operations
- **Rumor**: Class representing a rumor and its spread
- **RumorVariant**: Class representing a specific variant of a rumor

### Example Usage

```python
from app.core.rumors import RumorSystem, RumorCategory, RumorSeverity

# Get the rumor system
rumor_system = RumorSystem()

# Create a rumor
rumor_id = await rumor_system.create_rumor(
    originator_id="npc123",
    content="The king has fallen ill",
    categories=[RumorCategory.POLITICAL],
    severity=RumorSeverity.MAJOR,
    truth_value=0.8
)

# Spread a rumor to another entity
await rumor_system.spread_rumor(
    rumor_id=rumor_id,
    from_entity_id="npc123",
    to_entity_id="npc456",
    believability=0.7
)

# Get rumors heard by an entity
rumors = await rumor_system.get_rumors_heard_by_entity(
    entity_id="npc456",
    categories=[RumorCategory.POLITICAL]
)
```

## World State

The World State system manages game world state with hierarchical organization, categorization, and historical tracking.

### Key Components

- **WorldStateManager**: Singleton class for state operations
- **StateVariable**: Class representing a state variable
- **StateCategory**: Enum for state categorization
- **WorldRegion**: Enum for regional organization

### Example Usage

```python
from app.core.world_state import WorldStateManager, StateCategory, WorldRegion

# Get the world state manager
world_state = WorldStateManager()

# Set a state variable
await world_state.set(
    key="kingdoms.northland.ruler",
    value="King Thorstein",
    category=StateCategory.POLITICAL,
    region=WorldRegion.NORTHERN,
    tags=["ruler", "nobility"],
    reason="Coronation ceremony",
    entity_id="event123"
)

# Get a state variable
ruler = await world_state.get("kingdoms.northland.ruler")

# Query states by category
political_states = await world_state.query(
    category=StateCategory.POLITICAL,
    region=WorldRegion.NORTHERN
)

# Get state history
history = await world_state.get_history("kingdoms.northland.ruler")
```

## Time System

The Time System manages game time with calendar support, variable progression speeds, and scheduled events.

### Key Components

- **TimeManager**: Singleton class for time operations
- **GameDateTime**: Class representing a game date and time
- **TimeSpeed**: Enum for time progression speeds
- **TimeUnit**: Enum for time units

### Example Usage

```python
from app.core.time_system import TimeManager, TimeUnit, TimeSpeed

# Get the time manager
time_mgr = TimeManager()

# Get current game time
current_time = time_mgr.get_current_time()
formatted_time = time_mgr.format_time_for_display(current_time)

# Set time speed
await time_mgr.set_time_speed(TimeSpeed.NORMAL)

# Set specific time
await time_mgr.set_time(GameDateTime(
    year=1204,
    month=3,
    day=15,
    hour=14,
    minute=30
))

# Schedule an event
event_id = await time_mgr.schedule_event(
    name="Market Day",
    target_time=GameDateTime(hour=9, minute=0),
    callback="time.market_day",
    recurring=True,
    recursion_unit=TimeUnit.DAY,
    recursion_amount=7,
    metadata={"location": "Town Square"}
)

# Cancel a scheduled event
await time_mgr.cancel_scheduled_event(event_id)
```

## REST API

All systems are exposed through a FastAPI REST API for integration with the Unity frontend. The API is organized under `/api/v1` with the following endpoints:

- `/api/v1/events/*` - Event system endpoints
- `/api/v1/world-state/*` - World state endpoints
- `/api/v1/time/*` - Time system endpoints

Use the Swagger UI at `/docs` to explore the full API documentation.

## Integration with Unity

To integrate these systems with the Unity frontend:

1. Use the REST API endpoints to interact with the backend systems
2. For events, use the `/api/v1/events/publish` endpoint to publish events
3. For world state queries, use the `/api/v1/world-state` endpoints
4. For time management, use the `/api/v1/time` endpoints

### Example Unity Integration

```csharp
// Example Unity C# code for interacting with the API
using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class BackendService : MonoBehaviour
{
    private string baseUrl = "http://localhost:8000";
    
    // Publish an event
    public IEnumerator PublishEvent(string eventType, object eventData)
    {
        string url = $"{baseUrl}/api/v1/events/publish";
        string jsonData = JsonUtility.ToJson(new
        {
            event_type = eventType,
            event_data = eventData
        });
        
        using (UnityWebRequest request = UnityWebRequest.Post(url, jsonData))
        {
            request.SetRequestHeader("Content-Type", "application/json");
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("Event published successfully");
            }
            else
            {
                Debug.LogError($"Error publishing event: {request.error}");
            }
        }
    }
    
    // Get current game time
    public IEnumerator GetCurrentTime(Action<string> callback)
    {
        string url = $"{baseUrl}/api/v1/time/current";
        
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                var response = JsonUtility.FromJson<TimeResponse>(request.downloadHandler.text);
                callback(response.formatted_time);
            }
            else
            {
                Debug.LogError($"Error getting time: {request.error}");
            }
        }
    }
}

// Example usage
void Start()
{
    StartCoroutine(backendService.GetCurrentTime(time => {
        Debug.Log($"Current game time: {time}");
    }));
}
```

## Conclusion

These core technical systems provide a solid foundation for the Visual DM game. They are designed to be modular, extensible, and well-integrated with each other through the event system. Each system follows industry best practices for its domain and provides both async and sync interfaces for flexibility.

For more detailed information, refer to the API documentation at `/docs` and the class-level documentation in the codebase. 