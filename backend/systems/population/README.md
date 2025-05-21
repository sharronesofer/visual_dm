# Population Control System

The Population Control System manages NPC generation and population thresholds for all Points of Interest (POIs). It implements dynamic birth rate adjustment, population caps, and integration with state transitions.

## Features

- Dynamic NPC generation based on current/target population
- Configurable birth rates per POI type
- Soft and hard population caps
- Minimum thresholds to prevent ghost towns
- Admin controls for manual tuning

## Key Components

- POI-specific population tracking
- Monthly population adjustment formula
- Resource integration for population support
- State transition triggers based on population changes

## Integration Points

- Drives POI state transitions based on population
- Interacts with resource systems for population support
- Provides population context for narrative events

Refer to the Development Bible for detailed design documentation.
