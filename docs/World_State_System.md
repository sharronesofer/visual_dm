# World State System Documentation

The World State System (WSS) is a centralized mechanism for tracking, synchronizing, and persisting changes to the game world state across both the backend and frontend. It provides real-time updates via WebSockets and maintains consistency between all components of the game.

## Core Concepts

### State Variables

State variables are key-value pairs that represent a specific aspect of the world state. Each state variable has:

- **Key**: Unique identifier within its category and region
- **Value**: The current value of the variable (can be any JSON-serializable data)
- **Category**: The logical domain this variable belongs to (e.g., "environment", "politics", "economy")
- **Region**: The geographical area this variable applies to (e.g., "global", "kingdom_of_alaria", "dark_forest")

### State Categories

Categories help organize state variables by their functional domain:

- **ENVIRONMENT**: Weather, seasons, natural disasters, etc.
- **POLITICS**: Faction relationships, leadership changes, laws, etc.
- **ECONOMY**: Resource availability, market prices, trade routes, etc.
- **SOCIAL**: Cultural events, population changes, rumors, etc.
- **CONFLICT**: Wars, battles, threats, military deployments, etc.

### World Regions

Regions define the geographical scope of state variables:

- **GLOBAL**: Applies to the entire game world
- **KINGDOM**: Applies to a specific kingdom or major political region
- **CITY**: Applies to a specific city or settlement
- **LOCATION**: Applies to a specific location like a dungeon, forest, or landmark
- **PLAYER**: Player-specific state that follows them (not tied to geography)

### State Change Types

Defines how the value of a state variable changes:

- **SET**: Direct replacement of the current value
- **INCREMENT**: Numerical increase of the current value
- **DECREMENT**: Numerical decrease of the current value
- **TOGGLE**: Boolean flip (true → false, false → true)
- **APPEND**: Add to an array/list value
- **REMOVE**: Remove from an array/list value
- **MERGE**: Merge with an object/dictionary value

## Architecture

### Backend Components

1. **WorldStateManager**: Central backend authority for managing state variables
   - Maintains the current state in memory
   - Handles state change operations
   - Triggers events when state changes
   - Provides methods for querying state
   - Persistence to database

2. **WorldStateWebSocket**: Real-time communication channel
   - Subscribes clients to state updates by category or region
   - Broadcasts state changes to subscribed clients
   - Allows clients to request state variable changes
   - Sends initial state on connection

3. **WorldStateAPI**: RESTful endpoints for state operations
   - Get current state (with filtering)
   - Set state variables
   - Query state variable history
   - Bulk operations

### Frontend Components

1. **WorldStateWebSocketClient**: Unity client for real-time state synchronization
   - Connects to backend WebSocket
   - Manages subscriptions
   - Processes incoming state updates
   - Sends state change requests

2. **WorldStateManager**: Unity manager class that provides a simple API for other components
   - Maintains local state cache
   - Exposes events for state changes
   - Provides methods for getting/setting state variables
   - Handles reconnection and synchronization

## Usage Examples

### Backend (Python)

```python
# Setting a state variable
world_state_manager.set_state_variable(
    key="weather_condition",
    value="rain",
    category=StateCategory.ENVIRONMENT,
    region=WorldRegion.CITY,
    region_id="riverdale"
)

# Getting state variables by category
environment_states = world_state_manager.get_state_by_category(StateCategory.ENVIRONMENT)

# Getting state variables by region
city_states = world_state_manager.get_state_by_region(WorldRegion.CITY, "riverdale")

# Listening for state changes
@event_manager.on_event("world_state.variable_changed")
async def on_weather_change(event_data):
    variable = event_data.get("variable", {})
    if variable.get("key") == "weather_condition" and variable.get("category") == "ENVIRONMENT":
        print(f"Weather changed to: {variable.get('value')}")
```

### Frontend (C#)

```csharp
// Getting a state variable
string weatherCondition = WorldStateManager.Instance.GetStateVariable<string>(
    "weather_condition", 
    StateCategory.Environment,
    WorldRegion.City,
    "riverdale"
);

// Setting a state variable (sends to server)
WorldStateManager.Instance.SetStateVariable(
    "faction_reputation",
    75,
    StateCategory.Politics,
    WorldRegion.Kingdom,
    "alaria"
);

// Subscribing to state changes
WorldStateManager.Instance.OnStateVariableChanged += (key, value, category, region, regionId) => {
    if (key == "weather_condition" && category == StateCategory.Environment) {
        UpdateWeatherEffects((string)value);
    }
};

// Subscribing to a specific variable
WorldStateManager.Instance.SubscribeToVariable<int>(
    "faction_reputation",
    StateCategory.Politics,
    WorldRegion.Kingdom,
    "alaria",
    (newValue) => {
        UpdateFactionUI(newValue);
    }
);
```

## WebSocket Protocol

### Client Messages

```json
// Subscribe to a region
{
    "type": "subscribe_region",
    "data": {
        "regions": ["global", "kingdom_of_alaria"]
    }
}

// Subscribe to a category
{
    "type": "subscribe_category",
    "data": {
        "categories": ["ENVIRONMENT", "POLITICS"]
    }
}

// Get current state
{
    "type": "get_state",
    "data": {
        "regions": ["global", "kingdom_of_alaria"],
        "categories": ["ENVIRONMENT"]
    }
}

// Set a state variable
{
    "type": "set_state_variable",
    "data": {
        "key": "weather_condition",
        "value": "rain",
        "category": "ENVIRONMENT",
        "region": "CITY",
        "region_id": "riverdale",
        "source": "client"
    }
}
```

### Server Messages

```json
// Initial state on connection
{
    "type": "world_state_init",
    "data": {
        "state": {
            "ENVIRONMENT": {
                "GLOBAL": {
                    "season": "summer",
                    "time_of_day": "day"
                },
                "CITY:riverdale": {
                    "weather_condition": "rain"
                }
            }
        }
    }
}

// State variable changed
{
    "type": "world_state_variable_changed",
    "data": {
        "variable": {
            "key": "weather_condition",
            "value": "storm",
            "category": "ENVIRONMENT",
            "region": "CITY",
            "region_id": "riverdale",
            "timestamp": "2023-08-10T12:34:56.789Z",
            "source": "system"
        }
    }
}
```

## Best Practices

1. **Categorize Appropriately**: Use the most specific category that applies to keep state organization clean.

2. **Scope Properly**: Use the appropriate region level - don't use GLOBAL for state that only affects a specific area.

3. **Normalize State**: Break complex state into atomic variables rather than large nested objects.

4. **Subscribe Selectively**: Only subscribe to categories and regions that are relevant to the current game context.

5. **Frontend Caching**: Cache state on the frontend to reduce network traffic and improve performance.

6. **Validation**: Always validate state changes on the backend to prevent exploits.

7. **Persistence**: Critical state should be persisted to the database periodically.

8. **Error Handling**: Handle reconnection and synchronization gracefully after disconnections.

## Implementation Details

- **Database Schema**: State variables are stored in the `world_state` collection with category, region, and key as a compound index.

- **State Change History**: A time-series of state changes is maintained in the `world_state_history` collection for auditing and time-based queries.

- **Optimistic Updates**: The frontend applies changes optimistically, then reconciles with the server's authoritative state if needed.

- **Batching**: State changes are batched when multiple variables change in a single operation to reduce network overhead.

- **Compression**: For large state synchronization, compression is used to reduce bandwidth usage. 