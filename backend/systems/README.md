# Backend Systems Directory

This directory contains the core functional systems of the Visual DM backend, each responsible for a distinct domain aspect of the game.

## System Organization

Each system follows a consistent internal structure:

- **models/**: Data models and domain entities
- **services/**: Business logic and application services
- **repositories/**: Data access and storage
- **schemas/**: Pydantic schemas for validation and API interfaces
- **utils/**: Utility functions specific to the system
- **routers/**: API endpoints (FastAPI routers)

## Deduplication Efforts

The codebase has undergone significant deduplication to ensure single sources of truth for shared functionality:

### Centralized Components

1. **GPT Client**: 
   - Canonical implementation: `backend/core/ai/gpt_client.py`
   - Provides a unified interface for all AI text generation needs
   - Features robust error handling, configuration options, and retry logic

2. **Event System**:
   - Canonical implementation: `backend/systems/events/models/event_dispatcher.py`
   - Implements a publisher-subscriber pattern for loosely coupled system communication
   - Supports both synchronous and asynchronous event handling

### Cross-System Dependencies

Systems with clear dependencies on other systems should:

1. Import the required functionality from the canonical source
2. Not create duplicated or alternative implementations
3. Follow the established dependency hierarchy

### Inventory & Equipment Relationship

The inventory and equipment systems have related functionality with the following boundaries:

- **Inventory System**: Manages general item storage, transfers, and generic item metadata
- **Equipment System**: Handles specific equippable item properties, equipping mechanics, and equipment effects
- All equipment-related functionality should use the canonical inventory utilities for base item operations

## Recently Refactored Systems

The following systems have recently been refactored to eliminate duplication:

1. **Events System**: Consolidated event dispatching to a single implementation
2. **Rumor System**: Updated to use the centralized GPT client
3. **Auth System**: Improved as a central authentication service

## Next Systems For Review

The following systems are scheduled for deduplication review:

1. world_state
2. faction
3. dialogue
4. memory
5. combat

## Adding New Functionality

When adding new functionality:

1. Check if similar functionality already exists in another system
2. Consider whether the functionality belongs in a specific system or as a shared component
3. Use the established patterns and interfaces for consistency
4. Document cross-system dependencies in the system README

## Event System Consolidation (2024)

The event system has been consolidated:

- **Canonical location**: `/backend/systems/events/` (plural)
- **Legacy location**: `/backend/systems/event/` (singular) - DEPRECATED

The singular `event` folder currently contains backward compatibility layers that redirect to the canonical implementations in the plural `events` folder. This ensures existing code continues to work while we transition.

### Migration Plan:

1. **Current state**: Backward compatibility layer is in place
2. **Developer action**: Update imports in your code from `backend.systems.event` to `backend.systems.events`
3. **Future**: Once all imports are updated, the singular folder will be removed

### Example Migration:

**OLD (deprecated):**
```python
from backend.systems.event import EventDispatcher
from backend.systems.event.canonical_events import MemoryCreated
```

**NEW (preferred):**
```python
from backend.systems.events import EventDispatcher
from backend.systems.events.canonical_events import MemoryCreated
```

## Other Systems

[... existing content continues ...] 