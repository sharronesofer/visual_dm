# Population Control System

## Overview

The Population Control System manages the simulation of population growth, decline, and state transitions for Points of Interest (POIs) in the game world. It provides a realistic and dynamic population mechanic that responds to world events, player actions, and natural growth patterns.

## Core Components

### 1. PopulationManager (C#)

The central manager for population mechanics in the Unity client. Handles:
- Population growth and decline calculations
- POI state transitions based on population ratios
- Population cap enforcement (soft and hard caps)
- Event emission for population changes

### 2. Population Service (Python)

The backend service for population data persistence and calculation. Provides:
- REST API for population data access and modification
- Monthly update calculations
- Population state transition logic
- Data persistence and retrieval

### 3. WebSocket Integration

Real-time synchronization between frontend and backend using WebSockets:
- Population change notifications
- State transition events
- Configuration updates

## Key Features

### Population Growth Formula

Population growth is calculated monthly using the following formula:

```
growth_rate = base_rate * (current_population / target_population) * global_multiplier
growth = floor(growth_rate)
new_population = current_population + growth
```

This creates an S-curve growth pattern where:
- Very small populations grow slowly
- Mid-range populations grow fastest
- Populations approaching their target slow down

### Population Caps

- **Soft Cap**: When population reaches 90% of target, growth rate is multiplied by 0.5
- **Hard Cap**: Population cannot exceed target_population
- **Minimum Population**: Population cannot fall below min_population

### POI States

POIs transition between states based on their population ratio:

| State | Transition Condition |
|-------|----------------------|
| Normal | population_ratio > 0.6 |
| Declining | 0.3 < population_ratio < 0.6 |
| Abandoned | 0.1 < population_ratio < 0.3 |
| Ruins | population_ratio < 0.1 |
| Repopulating | recovering from Abandoned, population_ratio > 0.3 |
| Dungeon | Special state, no natural population growth |
| Special | For unique POIs with custom handling |

### Global Multiplier

A system-wide multiplier that affects all population growth rates. Can be used to simulate:
- Prosperity (values > 1.0)
- Famine/plague (values < 1.0)
- Population freezing (value = 0.0)

### Base Rates by POI Type

Default population growth rates by POI type:

| POI Type | Base Rate |
|----------|-----------|
| City | 10.0 |
| Town | 5.0 |
| Village | 2.0 |
| Religious | 3.0 |
| Embassy | 4.0 |
| Outpost | 3.0 |
| Market | 6.0 |
| Ruins | 0.0 |
| Dungeon | 0.0 |
| Custom | 1.0 |

## Integration Points

### Events

The system emits the following events:
- `PopulationChangedEvent`: When a POI's population changes
- `POIStateChangedEvent`: When a POI's state transitions
- `PopulationConfigChangedEvent`: When global settings change
- `MonthlyPopulationUpdateEvent`: When a monthly update occurs

### API Endpoints

- `GET /api/population/config`: Get global configuration
- `PUT /api/population/config/global-multiplier`: Update global multiplier
- `PUT /api/population/config/base-rate`: Update base rate for a POI type
- `GET /api/population`: Get all POI populations
- `GET /api/population/{poi_id}`: Get specific POI population
- `POST /api/population`: Create new POI population
- `PUT /api/population/{poi_id}`: Update POI population
- `PATCH /api/population/{poi_id}/population`: Change POI population
- `DELETE /api/population/{poi_id}`: Delete POI population
- `POST /api/population/monthly-update`: Trigger monthly update
- `GET /api/population/events`: Get recent population events
- `GET /api/population/by-state/{state}`: Get POIs by state
- `GET /api/population/by-type/{poi_type}`: Get POIs by type

### WebSocket Endpoints

- `ws://server/ws/population`: WebSocket endpoint for population updates
- Message types:
  - `population_changed`: When population changes
  - `poi_state_changed`: When POI state changes
  - `config_updated`: When configuration is updated

## Usage Examples

### Creating a New POI

```csharp
// Create a new POI
var newPoi = new POIPopulation
{
    POIId = "new_town_1",
    Type = POIType.Town,
    CurrentPopulation = 500,
    TargetPopulation = 2000,
    MinPopulation = 100,
    BaseRate = 5f,
    State = POIState.Normal
};

// Add to manager
populationManager.AllPOIs.Add(newPoi);
```

### Changing Population Manually

```csharp
// Change population due to player action
populationManager.SetPOIPopulation("town_1", 800, "migration");
```

### Setting Global Multiplier

```csharp
// Simulate a plague
populationManager.SetGlobalMultiplier(0.5f);

// Simulate prosperity
populationManager.SetGlobalMultiplier(1.5f);
```

### Monthly Update

```csharp
// Trigger a monthly update
populationManager.MonthlyUpdate();
```

## Best Practices

1. **Always initialize new POIs with valid data**:
   - Ensure POIId is unique
   - Set appropriate base rate for the POI type
   - Define reasonable target and min populations

2. **Use state transitions appropriately**:
   - Let the system handle normal state transitions
   - Only override states for special narrative events

3. **Use global multiplier for world-wide effects**:
   - Keep multiplier = 1.0 for normal conditions
   - Lower for disasters, higher for prosperity

4. **Listen for population events**:
   - Subscribe to population events for UI updates
   - Use events to trigger dependent systems

5. **Cache population data when appropriate**:
   - Only fetch full population data when needed
   - Use WebSocket updates for real-time changes

## Implementation Details

The system is implemented in both C# (Unity client) and Python (FastAPI backend) with WebSocket communication for real-time updates.

### Unity Components

- `PopulationManager.cs`: Core manager component
- `PopulationClient.cs`: Client for backend communication
- `NetworkPopulationManager.cs`: Handles synchronization with backend
- `POIPopulation.cs`: Data structure for POI population

### Backend Components

- `population.py`: Pydantic models
- `population_service.py`: Business logic service
- `population_router.py`: FastAPI endpoints
- `population_ws.py`: WebSocket handlers

## Testing

Comprehensive tests are implemented in:
- `PopulationSystemTests.cs`: Unity test suite
- `test_population.py`: Backend test suite

Tests cover all key functionality:
- Growth formula correctness
- Soft/hard cap behavior
- State transitions
- Event emission
- API endpoints
- WebSocket communication

## Future Enhancements

Planned future enhancements include:
- Resource consumption based on population
- Migration between nearby POIs
- Seasonal population fluctuations
- Impact of nearby POIs on growth rates
- War and disaster simulation
- Economic factors affecting growth 