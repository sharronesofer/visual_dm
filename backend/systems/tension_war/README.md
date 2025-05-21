# Tension and War Management System

This module manages faction relationships, tension calculation, war declaration, and war outcome simulation. The system tracks and decays tension values between factions from -100 (alliance) to +100 (war/hostile).

## Core Components

- **TensionManager**: Manages all tension between factions, including calculation, updates, and decay
- **WarManager**: Manages war declaration, simulation, and outcomes
- **Unified Utils**: Core utility functions for both tension and war operations

## Architecture

The system follows a clean, modular architecture with:

- **Models**: Data models for tension and war 
- **Services**: Core business logic for tension and war management
- **Utils**: Common utility functions
- **Schemas**: Pydantic models for API requests/responses
- **Router**: FastAPI endpoints for the system

## API Endpoints

### Tension Management

- `GET /api/v1/tension/{region_id}`: Get current tension for a region
- `POST /api/v1/tension/{region_id}`: Modify tension for a faction in a region
- `POST /api/v1/tension/{region_id}/reset`: Reset tension in a region
- `POST /api/v1/tension/{region_id}/decay`: Apply tension decay

### War Management

- `POST /api/v1/war/initialize`: Initialize a new war
- `POST /api/v1/war/{region_id}/advance`: Advance war by one day
- `POST /api/v1/war/conquer-poi`: Record conquest of a POI
- `POST /api/v1/war/{region_id}/generate-raids`: Generate daily raids
- `GET /api/v1/war/{region_id}/status`: Get current war status

## Backward Compatibility

Legacy functions from `tension_utils.py` and `war_utils.py` are provided in `utils.py` for backward compatibility, but new code should use the `TensionManager` and `WarManager` classes.

The deprecated Flask routes in `tension_routes.py` and `war_routes.py` are maintained for compatibility but will be removed in a future version. Use the FastAPI routes in `router.py` for new development.

## Usage Example

```python
from backend.systems.tension_war.services import TensionManager, WarManager

# Initialize managers
tension_mgr = TensionManager()
war_mgr = WarManager()

# Get tension for a region
tension_data = tension_mgr.get_tension("northern_valleys")

# Modify tension
updated_tension = tension_mgr.modify_tension(
    region_id="northern_valleys",
    faction="mountain_kingdom",
    value=15,
    reason="border_dispute"
)

# Initialize a war
war_status = war_mgr.initialize_war(
    region_a="northern_valleys",
    region_b="eastern_hills",
    faction_a="mountain_kingdom",
    faction_b="forest_tribe"
)

# Advance the war
advanced_war = war_mgr.advance_war_day("northern_valleys")
```

See `examples.py` for more detailed usage examples.

## Code Structure

- `__init__.py`: Module initialization and exports
- `models.py`: Data models
- `services.py`: TensionManager and WarManager services
- `utils.py`: Utility functions and backward compatibility
- `schemas.py`: Pydantic models for API
- `router.py`: FastAPI routes
- `examples.py`: Usage examples
- `tension_routes.py`: Deprecated Flask routes (to be removed)
- `war_routes.py`: Deprecated Flask routes (to be removed)

## Future Improvements

- Add event emission for system integration
- Implement persistent storage
- Add advanced war outcome calculations
- Develop territory control visualization
