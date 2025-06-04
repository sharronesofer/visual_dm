# Point of Interest (POI) System

This system manages all Points of Interest in the game world, including cities, towns, dungeons, ruins, and other significant locations.

## Architecture

The POI system follows a clear separation of concerns with business logic separated from infrastructure:

### Business Logic (backend/systems/poi/)

- `PoiBusinessService`: Primary business service for managing POIs with pure business rules
- `POIStateBusinessService`: Specialized business service for managing POI state transitions
- Business domain models: `PoiData`, `CreatePoiData`, `UpdatePoiData`, `POIStateData`
- Protocol interfaces for dependency injection

### Infrastructure (backend/infrastructure/)

- `PoiRepository`: Database operations and data persistence
- `POIGenerator`: Procedural POI generation algorithms
- `UnityFrontendIntegration`: Unity client integration and real-time updates
- `TilemapService`: Tilemap generation for POI interiors/exteriors (intentionally delegated to infrastructure layer)
- `StateTransitionConfigLoader`: Configuration file loading

### Models (backend/infrastructure/systems/poi/models/)

- `PointOfInterest`: The primary database model representing a POI
- `POIState`: Enum representing the possible states of a POI (active, declining, abandoned, etc.)
- `POIType`: Enum representing the different types of POIs (city, town, dungeon, etc.)

## POI State Transition System

The POI State Transition System enables Points of Interest to dynamically change states based on population metrics and war damage. State transitions are now configuration-driven:

- `active` → `declining`: When population drops below threshold or war damage occurs
- `declining` → `abandoned`: When population reaches zero
- `abandoned` → `ruins` or `dungeon`: Based on time and other factors
- `abandoned` → `repopulating`: When new population moves in
- `repopulating` → `active`: When population stabilizes

Configuration is loaded from `data/systems/poi/state_transitions.json`.

## POI Types and States

**POI Types:** `city`, `village`, `town`, `settlement`, `outpost`, `fortress`, `temple`, `market`, `mine`, `other`

**POI States:** `active`, `inactive`, `abandoned`, `ruined`, `under_construction`, `declining`, `growing`, `normal`, `ruins`, `dungeon`, `repopulating`, `special`

**Interaction Types:** `trade`, `diplomacy`, `combat`, `exploration`, `quest`, `social`, `neutral`

## Tilemap Generation

The tilemap generation system creates detailed indoor/outdoor maps for POIs with the following features:

1. Room structure generation based on POI type and size
2. Room connections and layout
3. Object and NPC/monster placement
4. Thematic enrichment based on POI type and tags
5. Rendering for client consumption

**Note:** The `TilemapService` is intentionally implemented in the infrastructure layer (`backend/infrastructure/tilemap_generators/`) following the Development Bible's clean separation of concerns. The placeholder in `backend/systems/poi/services/tilemap_placeholder.py` is correct architecture - business logic delegates tilemap generation to infrastructure components.

## Usage Examples

### Creating a new POI

```python
from backend.systems.poi.services import PoiBusinessService, CreatePoiData
from backend.infrastructure.poi_repositories import PoiRepository
from backend.infrastructure.poi_validators import PoiValidationService

# Set up dependencies
repository = PoiRepository(db_session)
validator = PoiValidationService()
poi_service = PoiBusinessService(repository, validator)

# Create POI data
poi_data = CreatePoiData(
    name="Oakvale",
    description="A small village in the forest",
    poi_type="village",
    properties={"region_id": "region_123", "position": {"x": 150, "y": 75}},
    population=120,
    max_population=200
)

# Create the POI
poi = poi_service.create_poi(poi_data)
```

### Updating POI state

```python
from backend.systems.poi.services import POIStateBusinessService
from backend.infrastructure.poi_validators import StateTransitionConfigLoader

# Set up dependencies
config_loader = StateTransitionConfigLoader()
state_service = POIStateBusinessService(config_loader)

# Update population, which may trigger state changes
result = state_service.update_population(poi_id, 50)

# Or explicitly transition to a new state
result = state_service.transition_state(poi_id, "ruins")
```

### Generating a tilemap

```python
from backend.infrastructure.tilemap_generators import TilemapService

# Set up tilemap service
tilemap_service = TilemapService(db_session)

# Generate a tilemap for the POI
tilemap = tilemap_service.generate_tilemap(poi_id)

# Convert to JSON for client
tilemap_json = tilemap_service.get_tilemap_json(tilemap)
```

### Finding nearby POIs

```python
from backend.infrastructure.poi_repositories import PoiRepository

# Set up repository
repository = PoiRepository(db_session)

# Find POIs within 20 units of coordinates
nearby = repository.get_nearby_pois(x=150, y=75, radius=20.0)
```

## Extensibility

The POI system is designed to be easily extensible:

1. Add new POI types by extending the `POIType` enum
2. Add new POI states by extending the `POIState` enum
3. Add new tilemap features by extending the `TilemapService` in infrastructure layer
4. Add new state transition rules by modifying the JSON configuration files
5. Implement new business logic in the business services while keeping infrastructure separate

## Compliance with Development Bible

This system follows the Development Bible's architectural requirements:

- **✅ Clean Separation:** Business logic in `/systems/`, infrastructure in `/infrastructure/`
- **✅ Protocol-Based DI:** Uses `Protocol` interfaces for dependency injection
- **✅ Pure Business Logic:** No infrastructure concerns in business services
- **✅ Configuration-Driven:** Uses JSON configuration for rules and parameters
- **✅ Event-Driven:** Publishes events for cross-system integration
