# Economy System Refactoring Plan

## Current Issues
- The economy directory structure contains many empty directories with just `__init__.py` files
- Actual economy-related code is scattered across multiple systems (world_state, events, etc.)
- No clear organization or consolidated API for economy functionality
- Duplicate functionality or placeholder implementations across the codebase

## Refactored Structure

```
backend/systems/economy/
├── __init__.py              # Exports primary functionality
├── models/                  # Models for economy-related data
│   ├── __init__.py
│   ├── resource.py          # Consolidated resource model
│   ├── trade_route.py       # Consolidated trade route model
│   └── market.py            # Market/price model
├── services/                # Business logic for economy
│   ├── __init__.py
│   ├── resource_service.py  # Resource management
│   ├── trade_service.py     # Trade route management
│   └── market_service.py    # Market/prices management
├── events/                  # Event handlers for economy
│   ├── __init__.py
│   ├── trade_events.py      # Trade event handling
│   └── resource_events.py   # Resource event handling
└── utils/                   # Utility functions
    ├── __init__.py
    └── economy_utils.py     # General utilities
```

## Consolidation Plan

1. **Models**: 
   - Consolidate Resource model from `events/models/world/data_models.py` and `events/models/world/orm_models.py`
   - Move TradeRoute model from `events/models/trade_route.py`
   - Create Market model for pricing and market mechanics

2. **Services**:
   - Consolidate trade-related functionality from `world_state/tick_utils/region_processing.py`
   - Add resource management from `events/managers/resource_manager.py`
   - Add market-related functionality from scattered implementations

3. **Events**:
   - Consolidate trade event handling from `world_state/tick_utils/event_handling.py`
   - Consolidate event generation from `world_state/tick_utils/event_generation.py`

4. **Utils**:
   - Create utilities for commonly used functions
   - Remove duplicated code and provide canonical implementations

## Implementation Steps

1. Create the new directory structure
2. Move/consolidate existing files, taking the most robust implementation of each function
3. Update imports in existing code to point to the new locations
4. Delete the old empty directories
5. Add appropriate tests for the refactored code
6. Update documentation to reflect the new structure

This refactored approach will:
- Provide a clear, consolidated API for economy-related functionality
- Remove duplicate code and empty directories
- Improve maintainability and organization
- Make future extensions easier 