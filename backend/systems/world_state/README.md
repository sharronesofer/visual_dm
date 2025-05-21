# World State System

The World State system is responsible for tracking and modifying the game world state. It provides interfaces for updating state variables, handling state-related events, and integrating with game mods.

## Directory Structure

The system follows a modular, event-driven architecture aligned with the Visual DM Development Bible. It is organized into the following directories:

- **core/** - Core components of the world state system
  - `manager.py` - Central manager for all world state operations (singleton pattern)
  - `loader.py` - Handles loading and persistence of world state data
  - `types.py` - Type definitions for the world state system
  - `events.py` - Event definitions for world state changes

- **mods/** - Mod handling and synchronization
  - `mod_synchronizer.py` - Manages loading and applying mods to the world state

- **events/** - Event handling components
  - `handlers.py` - Event handlers that react to world state changes

- **api/** - API components
  - `router.py` - FastAPI router for HTTP endpoints

- **utils/** - Utility functions
  - `tick_utils.py` - Utilities for processing world ticks
  - `world_event_utils.py` - Utilities for creating and managing world events

## Key Components

### WorldStateManager

The central manager for all world state operations. It provides methods for:
- Getting and setting state variables
- Tracking state changes over time
- Emitting events when state changes
- Processing world ticks

### WorldStateLoader

Handles loading and persistence of world state data, including:
- Loading the world state from disk
- Saving the world state to disk
- Loading and saving events
- Tracking historical state changes

### ModSynchronizer

Manages synchronization between game mods and the world state, including:
- Discovering available mods
- Loading mod data
- Validating mod data
- Applying mods to the world state

### Event Handlers

Event handlers react to world state changes, including:
- Processing world state events
- Creating world events based on state changes
- Applying effects based on state changes

## Usage

The system exposes a singleton instance of the WorldStateManager for easy access:

```python
from backend.systems.world_state import world_state_manager

# Get a state variable
value = world_state_manager.get_value("some.variable")

# Set a state variable
world_state_manager.set_value("some.variable", new_value)

# Process a world tick
world_state_manager.process_tick()
```

## API Endpoints

The system provides the following API endpoints:

- **GET /api/world-state** - Get the current world state
- **GET /api/world-state/history** - Get historical data for world state values
- **PATCH /api/world-state** - Update a specific value in the world state
- **POST /api/world-state/events** - Create a new world event
- **GET /api/world-state/events** - Get world events with optional filtering
- **GET /api/world-state/events/{event_id}** - Get a specific world event by ID
- **GET /api/world-state/related-events/{event_id}** - Get events related to the specified event
- **POST /api/world-state/process-tick** - Manually trigger a world tick processing cycle
- **POST /api/world-state/chaos-event** - Inject a chaos event into the world
- **GET /api/world-state/regions** - Get a list of valid world regions
- **GET /api/world-state/categories** - Get a list of valid state categories
