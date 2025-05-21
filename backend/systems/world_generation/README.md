# World Generation System

## Overview

The World Generation System is responsible for procedurally generating and managing world components including continents, regions, cities, and POIs (Points of Interest). It follows a modular architecture with clearly defined components for different aspects of world generation.

## Key Components

### Utility Layer (`world_generation_utils.py`)

This file contains all utility functions for world generation, organized into logical sections:

1. **Continent Generation**
   - `generate_continent_region_coordinates`: Creates a contiguous set of region coordinates for a continent
   - `get_continent_boundary`: Computes the bounding box of a continent
   - `map_region_to_latlon`/`get_region_latlon`: Maps game coordinates to real-world lat/lon

2. **Region Generation**
   - `generate_region`: Generates a complete region with tiles, POIs, and metadata
   - `walk_region`: Creates a region's tilemap using a random walk algorithm
   - `generate_settlements`: Places settlements within a region based on population
   - `generate_non_settlement_pois`: Places dungeons, exploration sites, etc.

3. **POI and Monster Management**
   - `refresh_cleared_pois`: Resets POIs marked as cleared
   - `generate_monsters_for_tile`: Creates monsters for a tile based on danger level
   - `attempt_rest`: Resolves rest attempts at POIs
   - `generate_social_poi`: Creates social POIs (cities, towns, etc.)
   - `generate_tile`: Generates individual tiles

4. **Helper Functions**
   - `pick_poi_type`/`choose_poi_type`: Select POI types based on weights or tile danger
   - `pick_valid_tile`: Finds valid tile locations based on constraints
   - `claim_region_hexes_for_city`: Handles visual metropolis sprawl

### Service Layer (`continent_service.py`)

The service layer implements business logic for continent operations:

- `create_new_continent`: Creates a new continent with procedurally generated regions
- `get_continent_details`: Retrieves details of a continent
- `list_all_continents`: Lists all continents
- `update_continent_metadata`: Updates metadata for a continent
- `delete_continent`: Deletes a continent

### Repository Layer (`continent_repository.py`)

The repository layer handles data persistence:

- `create_continent`: Persists a new continent
- `get_continent_by_id`: Retrieves a continent by ID
- `list_all_continents`: Retrieves all continents
- `update_continent`: Updates an existing continent
- `delete_continent`: Deletes a continent

### API Layer (`router.py`)

The API layer exposes FastAPI endpoints for continent operations:

- `POST /world/continents`: Creates a new continent
- `GET /world/continents/{continent_id}`: Retrieves a continent
- `GET /world/continents`: Lists all continents
- `PATCH /world/continents/{continent_id}/metadata`: Updates continent metadata
- `DELETE /world/continents/{continent_id}`: Deletes a continent

### Flask API Layer (`worldgen_routes.py`)

Legacy Flask endpoints for world generation operations:

- `POST /refresh_pois`: Refreshes POIs
- `GET /monster_spawns/<int:x>/<int:y>`: Generates monsters for a tile
- `POST /generate_encounter`: Generates a combat encounter
- `POST /generate_location_gpt`: Generates a location using GPT
- `POST /generate_region`: Generates a new region

### Data Model (`models.py`)

Contains Pydantic models for request/response validation:

- `CoordinateSchema`: Represents region coordinates
- `ContinentSchema`: Represents a continent
- `ContinentBoundarySchema`: Represents continent boundaries
- `ContinentCreationRequestSchema`: Represents continent creation requests

## Recent Refactoring (2025)

In the 2025 update, the world generation system was refactored to consolidate duplicate utilities and improve code organization:

1. **Consolidated Utilities**: 
   - Merged `region_generation_utils.py` and `worldgen_utils.py` into a single `world_generation_utils.py`
   - Enhanced the region generation functions with improved monster generation and POI management
   - Organized utility functions into logical sections with consistent naming

2. **Standardized Imports**:
   - Updated module exports in `__init__.py` to expose all necessary components
   - Fixed import references in dependent files
   - Maintained backward compatibility for existing integrations

3. **Documentation**:
   - Added comprehensive docstrings to all functions
   - Updated README.md with system overview and component descriptions
   - Added type hints for better IDE support and code quality

## Usage Examples

### Creating a New Continent

```python
from backend.systems.world_generation.continent_service import continent_service
from backend.systems.world_generation.models import ContinentCreationRequestSchema

request = ContinentCreationRequestSchema(
    name="New Continent",
    num_regions_target=60,
    seed="custom-seed-123",
    metadata={"creator": "admin"}
)

continent = continent_service.create_new_continent(request)
print(f"Created continent: {continent.continent_id}")
```

### Generating a Region

```python
from backend.systems.world_generation.world_generation_utils import generate_region

region = generate_region(seed_x=10, seed_y=20)
print(f"Generated region: {region['region_id']}")
print(f"Contains {len(region['poi_list'])} POIs")
```

## Integration Points

- **Event System**: The world generation system emits events for major operations
- **Analytics**: All generation operations can be logged for analytics
- **Weather System**: Regions map to real-world coordinates for weather integration
- **Combat System**: Combat encounters integrate with the generated world
- **GPT Integration**: Certain generation functions can use GPT for enhanced content
