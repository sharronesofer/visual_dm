# Tension System - Comprehensive Implementation

## Overview

The Tension System manages two distinct but related types of tension according to the Development Bible:

1. **Environmental Tension** (0.0 - 1.0): Local unrest, crime, and regional instability
2. **Faction Relationship Tension** (-100 to +100): Political relationships between factions

## Architecture

The system follows clean architecture principles with clear separation between:
- **Domain Models**: Pure business logic (tension_state.py)
- **Business Services**: Core rules and calculations (tension_business_service.py)
- **Infrastructure**: Data persistence and external integrations
- **API Layer**: HTTP endpoints and request/response handling (tension_router.py)

## Environmental Tension (0.0 - 1.0 Scale)

### Core Features
- **Location-based tracking**: Each region and POI has its own tension state
- **Event-driven updates**: Events like combat, deaths, festivals affect local tension
- **Natural decay**: Tension naturally decreases over time unless reinforced
- **Configurable thresholds**: Different locations have different base tension levels

### Conflict Triggers
- **Revolts**: High environmental tension can trigger local uprisings
- **Instability**: Affects trade, safety, and faction operations in the region
- **Escalation**: Can influence faction relationships if multiple factions are present

## Faction Relationship Tension (-100 to +100 Scale)

### Core Features
- **Faction-to-faction tracking**: Direct relationship modeling between any two factions
- **War threshold**: Tension ≥ 70 automatically triggers war state
- **Alliance threshold**: Tension ≤ -50 indicates strong alliance
- **Natural decay**: Relationships slowly drift toward neutral (0) over time
- **Event propagation**: Political, economic, and military events affect relationships

### Relationship Types
- **War** (70-100): Active hostilities, combat engagement
- **Hostile** (30-69): Antagonistic but not actively fighting  
- **Neutral** (-29 to 29): No special relationship
- **Friendly** (-30 to -49): Positive relations but not formal alliance
- **Alliance** (-50 to -100): Strong cooperation and mutual defense

### War System Integration

Per the Development Bible, the tension system serves as the trigger mechanism for the war system:

1. **War Declaration**: When faction tension reaches 70+, war is automatically declared
2. **Alliance Formation**: When faction tension reaches -50 or below, alliances strengthen
3. **Peace Opportunities**: When war tension drops below 70, peace negotiations become possible

## Event Processing

### Environmental Events
Events affect both environmental tension and faction relationships:

```json
{
  "combat": {
    "environmental_impact": 0.2,
    "faction_tension_impact": 15
  },
  "festival": {
    "environmental_impact": -0.3,
    "faction_tension_impact": -10
  }
}
```

### Faction Events
Political events primarily affect faction relationships:

```json
{
  "alliance_formation": {
    "faction_tension_impact": -30
  },
  "betrayal": {
    "faction_tension_impact": 60
  }
}
```

## API Endpoints

### Environmental Tension
- `GET /tension/{region_id}/{poi_id}`: Get current environmental tension
- `POST /tension/{region_id}/{poi_id}/events`: Apply event to location
- `GET /tension/regions/summary`: Get regional tension overview

### Faction Relationships
- `GET /faction-relationships/{faction_a}/{faction_b}`: Get relationship status
- `POST /faction-relationships/{faction_a}/{faction_b}/update-tension`: Modify relationship
- `GET /faction-relationships/wars`: List active wars
- `GET /faction-relationships/alliances`: List active alliances
- `GET /faction-relationships/{faction_id}/status`: Get faction's diplomatic status

## Configuration

### Environmental Settings
```json
{
  "high_tension_threshold": 0.7,
  "environmental_tension_limits": {
    "absolute_min": 0.0,
    "absolute_max": 1.0
  }
}
```

### Faction Settings
```json
{
  "faction_tension_limits": {
    "absolute_min": -100,
    "absolute_max": 100,
    "neutral_point": 0,
    "war_threshold": 70,
    "alliance_threshold": -50
  }
}
```

## Business Rules

### Environmental Tension
1. **Natural Decay**: Tension decreases by decay_rate per hour
2. **Event Impact**: Scaled by location type and event severity
3. **Modifier System**: Temporary effects with expiration times
4. **Bounds Checking**: Always constrained to 0.0-1.0 range

### Faction Tension
1. **Bidirectional**: Relationship between A→B is same as B→A
2. **Daily Decay**: 1 point per day toward neutral (0)
3. **Alliance Stability**: Alliances decay slower than hostile relationships
4. **War Persistence**: War relationships resist decay while active
5. **Event Propagation**: Political events affect multiple relationships

### Conflict Generation
1. **Environmental Revolts**: Triggered at 0.5+ environmental tension
2. **Faction Wars**: Triggered at 70+ faction tension
3. **Peace Windows**: Available when war tension drops below 70
4. **Alliance Benefits**: Negative tension provides diplomatic and military bonuses

## Integration Points

### With Faction System
- Faction presence affects environmental tension modifiers
- Faction events propagate to relationship tension
- Alliance status affects faction behavior calculations

### With War System
- Tension system provides war triggers and status
- War events feedback into tension calculations
- Peace negotiations based on tension thresholds

### With Event System
- All game events can affect tension via configuration
- Tension state influences event outcomes and availability
- Event dispatcher handles tension-triggered conflicts

## Monitoring and Statistics

The system tracks:
- Total tension updates (environmental)
- Total faction relationship updates
- Wars triggered
- Alliances formed
- Conflicts generated
- Modifier expirations

## Development Bible Compliance

✅ **Faction Relationships**: -100 to +100 scale implemented
✅ **War Triggers**: Automatic war at 70+ tension
✅ **Alliance Support**: Negative values for alliances
✅ **Natural Decay**: Relationships drift toward neutral
✅ **Event Integration**: Political and military events affect relationships
✅ **API Contracts**: RESTful endpoints for all operations
✅ **Clean Architecture**: Business logic separated from infrastructure 