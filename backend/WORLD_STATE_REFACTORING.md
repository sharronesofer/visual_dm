# World State System Refactoring

## Overview

This document describes the refactoring performed on the `backend/systems/world_state` module to restore strict separation between business logic and technical infrastructure, as required by the project's architectural principles.

## Problem Statement

The `backend/systems/world_state` directory contained a mixture of business logic and technical infrastructure, violating the strict separation principle where:
- `/backend/systems` should contain **business logic ONLY**
- `/backend/infrastructure` should contain **technical functionality**

## Changes Made

### Files Moved from `backend/systems/world_state` to `backend/infrastructure/world_state`

#### 1. API Infrastructure
- **Moved**: `routers/` → `backend/infrastructure/world_state/api/`
  - `worldgen_api.py` - FastAPI routes for world generation
  - `world_routes.py` - FastAPI routes for world state operations
  - `__init__.py` - API module initialization

#### 2. Database Models
- **Moved**: `models/` → `backend/infrastructure/world_state/models/`
  - `models.py` - SQLAlchemy database models and Pydantic schemas
  - `world_models.py` - Additional world-specific models
  - `__init__.py` - Models module initialization

#### 3. Repository Layer
- **Moved**: `repositories/` → `backend/infrastructure/world_state/repositories/`
  - `__init__.py` - Repository module initialization

#### 4. Schema Definitions
- **Moved**: `schemas/` → `backend/infrastructure/world_state/schemas/`
  - `__init__.py` - Schema module initialization

#### 5. Technical Utilities
- **Moved**: Selected utilities → `backend/infrastructure/world_state/utils/`
  - `terrain_generator.py` - Technical terrain generation algorithms
  - `tick_utils.py` - Technical tick processing infrastructure
  - `cleanup.py` - Technical cleanup utilities
  - `legacy/` - Legacy technical infrastructure components
    - `world_state_loader.py` - Technical data loading infrastructure
    - `world_state_manager.py` - Technical state management infrastructure
    - `worldgen_utils.py` - Technical world generation utilities

### Files Remaining in `backend/systems/world_state` (Business Logic)

#### Core Business Logic
- `types.py` - Business domain types and enums
- `manager.py` - Business logic manager (compatibility wrapper)
- `loader.py` - Business logic loader (compatibility wrapper)
- `events.py` - Business events (compatibility wrapper)
- `services/` - Business services
- `events/` - Business event handlers
- `core/` - Core business logic components

#### Business Utilities
- `utils/world_utils.py` - Business logic utilities for world operations
- `utils/world_event_utils.py` - Business event utilities
- `utils/newspaper_system.py` - Business logic for in-game newspaper system
- `utils/optimized_worldgen.py` - Business logic wrapper for world generation

## Import Path Updates

### Updated Import Statements

All files that previously imported from the old locations have been updated:

```python
# OLD (Technical infrastructure mixed with business logic)
from backend.systems.world_state.models import World_StateEntity
from backend.systems.world_state.routers.world_routes import router
from backend.systems.world_state.utils.legacy.world_state_manager import WorldStateManager

# NEW (Proper separation)
from backend.infrastructure.world_state.models import World_StateEntity
from backend.infrastructure.world_state.api.world_routes import router
from backend.infrastructure.world_state.utils.legacy.world_state_manager import WorldStateManager
```

### Compatibility Wrappers

To maintain backward compatibility, wrapper modules were created in the business logic layer:

- `backend/systems/world_state/manager.py` - Imports from infrastructure and re-exports
- `backend/systems/world_state/loader.py` - Imports from infrastructure and re-exports
- `backend/systems/world_state/events.py` - Imports from infrastructure and re-exports

## Infrastructure Additions

### New Exception Classes

Added domain-specific exceptions to `backend/infrastructure/utils/`:

```python
class TensionError(Exception):
    """Exception raised for tension calculation errors."""
    pass

class GenerationError(Exception):
    """Exception raised for world generation errors."""
    pass
```

### Module Structure

#### Business Logic Structure (`backend/systems/world_state/`)
```
world_state/
├── __init__.py           # Business logic exports
├── types.py              # Domain types and enums
├── manager.py            # Business manager (wrapper)
├── loader.py             # Business loader (wrapper)
├── events.py             # Business events (wrapper)
├── services/             # Business services
├── events/               # Business event handlers
├── core/                 # Core business components
└── utils/                # Business utilities
```

#### Infrastructure Structure (`backend/infrastructure/world_state/`)
```
world_state/
├── __init__.py           # Infrastructure exports (minimal to avoid circular imports)
├── api/                  # FastAPI routes and endpoints
├── models/               # SQLAlchemy models and schemas
├── repositories/         # Data access layer
├── schemas/              # API schemas
└── utils/                # Technical utilities
    ├── terrain_generator.py
    ├── tick_utils.py
    ├── cleanup.py
    └── legacy/           # Legacy infrastructure
```

## Benefits Achieved

1. **Strict Separation**: Business logic and technical infrastructure are now properly separated
2. **Clear Boundaries**: Developers can easily identify what belongs where
3. **Maintainability**: Changes to technical infrastructure won't affect business logic and vice versa
4. **Testability**: Business logic can be tested independently of infrastructure concerns
5. **Compliance**: The codebase now follows the established architectural principles

## Testing

All imports have been verified to work correctly:
- ✅ `import systems.world_state` - Business logic imports successfully
- ✅ `import infrastructure.world_state` - Infrastructure imports successfully
- ✅ Cross-system imports work correctly
- ✅ Backward compatibility maintained through wrapper modules

## Future Considerations

1. **Gradual Migration**: The compatibility wrappers can be gradually removed as dependent systems are updated
2. **Further Separation**: Additional technical utilities may be identified and moved to infrastructure
3. **Documentation Updates**: System documentation should be updated to reflect the new structure
4. **Testing Enhancement**: Separate test suites for business logic vs infrastructure can be established

## Files Modified

### Import Updates
- `backend/main.py` - Updated router imports
- `backend/systems/quest/services/generator.py` - Updated world state manager import
- `backend/systems/dialogue/services/` - Updated world state imports
- `backend/systems/diplomacy/services/` - Updated world state imports
- `backend/infrastructure/services/world_service.py` - Updated type imports
- `backend/tests/systems/world_state/` - Updated test imports

### New Files Created
- `backend/infrastructure/world_state/__init__.py`
- `backend/infrastructure/world_state/utils/__init__.py`
- `backend/WORLD_STATE_REFACTORING.md` (this file)

### Exception Additions
- `backend/infrastructure/utils/__init__.py` - Added TensionError and GenerationError

This refactoring successfully restores the strict separation between business logic and technical infrastructure while maintaining full backward compatibility and system functionality. 