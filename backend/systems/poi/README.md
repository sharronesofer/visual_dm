# Point of Interest (POI) System

This system manages all Points of Interest in the game world, including cities, towns, dungeons, ruins, and other significant locations.

## Architecture

The POI system follows a clear separation of concerns with the following components:

### Models

- `PointOfInterest`: The primary model representing a POI in the game world
- `POIState`: Enum representing the possible states of a POI (normal, declining, abandoned, etc.)
- `POIType`: Enum representing the different types of POIs (city, town, dungeon, etc.)

### Services

- `POIService`: Primary service for managing POIs, including creation, updates, and queries
- `POIStateService`: Specialized service for managing POI state transitions and state-related operations
- `TilemapService`: Service for generating, enriching, and rendering POI tilemaps

### Utilities

- `calculate_poi_distance`: Consolidated utility for calculating distance between POIs or coordinates
- Various helper functions for POI operations

## POI State Transition System

The POI State Transition System enables Points of Interest to dynamically change states based on population metrics and war damage. Possible state transitions include:

- `NORMAL` → `DECLINING`: When population drops below threshold or war damage occurs
- `DECLINING` → `ABANDONED`: When population reaches zero
- `ABANDONED` → `RUINS` or `DUNGEON`: Based on time and other factors
- `ABANDONED` → `REPOPULATING`: When new population moves in
- `REPOPULATING` → `NORMAL`: When population stabilizes

See `POIStateService` for implementation details.

## Tilemap Generation

The tilemap generation system creates detailed indoor/outdoor maps for POIs with the following features:

1. Room structure generation based on POI type and size
2. Room connections and layout
3. Object and NPC/monster placement
4. Thematic enrichment based on POI type and tags
5. Rendering for client consumption

The `TilemapService` handles all tilemap-related operations in a consolidated way.

## Usage Examples

### Creating a new POI

```python
from backend.systems.poi import POIService, POICreationSchema

# Create POI data
poi_data = POICreationSchema(
    name="Oakvale",
    description="A small village in the forest",
    region_id="region_123",
    position={"x": 150, "y": 75},
    poi_type="village",
    tags=["forest", "peaceful"],
    population=120,
    max_population=200
)

# Create the POI
poi = POIService.create_poi(poi_data)
```

### Updating POI state

```python
from backend.systems.poi import POIService, POIStateService

# Get existing POI from database
poi = get_poi_from_db(poi_id)

# Update population, which may trigger state changes
poi = POIStateService.update_population(poi, 50)

# Or explicitly transition to a new state
poi = POIStateService.transition_state(poi, "ruins")

# Save the updated POI
save_poi_to_db(poi)
```

### Generating a tilemap

```python
from backend.systems.poi import POIService

# Get existing POI from database
poi = get_poi_from_db(poi_id)

# Generate a tilemap for the POI
tilemap = POIService.generate_poi_tilemap(poi)

# The tilemap can now be sent to the client
```

### Finding nearby POIs

```python
from backend.systems.poi import POIService

# Get existing POI from database
poi = get_poi_from_db(poi_id)
all_pois = get_all_pois_from_db()

# Find POIs within 20 units
nearby = POIService.find_nearby_pois(poi, all_pois, max_distance=20.0)
```

## Extensibility

The POI system is designed to be easily extensible:

1. Add new POI types by extending the `POIType` enum
2. Add new POI states by extending the `POIState` enum
3. Add new tilemap features by extending the `TilemapService`
4. Add new state transition rules by modifying `POIStateService.evaluate_state()`
