# Time System

The Time System manages game time, calendar, seasons, weather, and time-based events in the simulation.

## Overview

This system provides a unified way to track and advance time within the game world, handle calendar operations, manage seasonal changes, and schedule time-based events.

## Key Features

- Game time management with configurable calendar
- Season progression with seasonal effects
- Weather system with varying conditions
- Event scheduling system for time-based triggers
- Data persistence for saving/loading time state

## Structure

The system follows a clean, consolidated architecture:

```
backend/systems/time/
├── __init__.py               # Main package exports and convenience functions
├── models/                   # Data models for time system
│   └── time_model.py         # All time-related Pydantic models
├── services/                 # Business logic services
│   └── time_manager.py       # Core time system manager (singleton)
├── repositories/             # Data persistence layer
│   └── time_repository.py    # Manages saving/loading time data
├── utils/                    # Utility functions
│   └── time_utils.py         # Helper functions for time operations
└── routers/                  # FastAPI endpoints
    └── time_router.py        # API routes for the time system
```

## Main Components

### TimeManager

Central singleton class that manages all time-related operations, including:

- Advancing game time
- Maintaining the calendar
- Tracking seasons
- Managing weather changes
- Scheduling and processing time events

### Game Time Model

The `GameTime` model represents the current state of time in the game world:

- Year, month, day
- Hour, minute, second, tick
- Current season and weather
- Timestamps for real-world tracking

### Time Events

The system supports scheduling events to occur at specific times:

- One-time events
- Recurring events (daily, weekly, etc.)
- Event callback data for handling

## Usage Examples

```python
# Import the time system
from backend.systems.time import time_manager, TimeUnit, EventType

# Get current game time
current_time = time_manager.get_time()
print(f"Current game time: Year {current_time.year}, Month {current_time.month}, Day {current_time.day}")

# Advance time
time_manager.advance_time(1, TimeUnit.DAY)

# Schedule an event
event_id = time_manager.schedule_event(
    name="Festival Start",
    description="Annual spring festival begins",
    callback_data={"event_type": "festival", "location": "town_square"},
    trigger_time=None,  # Use None for immediate scheduling based on offset
    time_offset=(3, TimeUnit.DAY),  # 3 days from now
    event_type=EventType.ONE_TIME
)

# Check current season
current_season = time_manager.get_time().season
print(f"Current season: {current_season}")

# Get current weather
weather = time_manager.get_current_weather()
print(f"Current weather: {weather}")
```

## API Endpoints

The time system exposes the following API endpoints:

- `GET /time/current` - Get current game time
- `POST /time/advance` - Advance game time
- `GET /time/events` - List scheduled events
- `POST /time/events` - Schedule a new event
- `DELETE /time/events/{event_id}` - Cancel an event
- `GET /time/calendar` - Get calendar configuration
- `GET /time/season` - Get current season
- `GET /time/weather` - Get current weather

## Integration with Other Systems

Other systems can integrate with the time system by:

1. Using the time manager to query current time, season, weather
2. Scheduling events to trigger at specific times
3. Subscribing to time-related events (time_advanced, season_changed, etc.)

Example:

```python
from backend.systems.time import time_manager, TimeUnit, EventType
from backend.core.event_system import event_system

# Listen for season changes
@event_system.subscribe("season_changed")
def handle_season_change(data):
    new_season = data["new_season"]
    print(f"Season changed to {new_season}")
    
    # Adjust NPC behaviors based on season
    if new_season == "winter":
        # Make NPCs stay indoors more
        pass
```
