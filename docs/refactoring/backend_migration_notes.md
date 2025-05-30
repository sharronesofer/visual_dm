# Backend Reorganization Migration Notes

## Overview

As part of improving the backend architecture, we have reorganized the directory structure to follow a more consistent domain-driven design.

## Changes Made

1. Analytics service moved from `backend/app/core/analytics/analytics_service.py` to `backend/systems/analytics/services/analytics_service.py`
2. GPT client moved from `backend/core/ai/gpt_client.py` to `backend/systems/ai/services/gpt_client.py`

## Migration Guide for Developers

Please update your import statements as follows:

- OLD: `from backend.app.core.analytics.analytics_service import AnalyticsService`
- NEW: `from backend.systems.analytics.services.analytics_service import AnalyticsService`

- OLD: `from backend.core.ai.gpt_client import GPTClient`
- NEW: `from backend.systems.ai.services.gpt_client import GPTClient`

While the old import paths will continue to work temporarily through backward compatibility modules,
they will generate deprecation warnings. These compatibility modules will be removed in a future release.

## Testing

After updating your imports, please run the test suite to ensure everything continues to work as expected.

## Additional Changes - GameDataRegistry Migration

3. GameDataRegistry moved from `backend/data/modding/loaders/game_data_registry.py` to `backend/systems/data/loaders/game_data_registry.py`

Please update your import statements as follows:

- OLD: `from backend.data.modding.loaders.game_data_registry import GameDataRegistry`
- NEW: `from backend.systems.data.loaders.game_data_registry import GameDataRegistry`

## AI and DM System Merge

The AI and DM systems have been merged into a single LLM (Language Learning Model) system:

- Previously separate AI client code and DM narrative logic are now unified
- New directory structure under `backend/systems/llm/`
- Import changes:

Previous AI imports:
- OLD: `from backend.systems.ai.services.gpt_client import GPTClient`
- NEW: `from backend.systems.llm.services.gpt_client import GPTClient`

Previous DM imports:
- OLD: `from backend.systems.dm.dm_core import DungeonMaster`
- NEW: `from backend.systems.llm.core.dm_core import DungeonMaster`

- OLD: `from backend.systems.dm.memory_system import Memory`
- NEW: `from backend.systems.llm.core.memory_system import Memory`

(Similar pattern for all DM modules)

The merge reflects their close relationship and dependency in the system, reducing duplication and improving cohesion.

# Visual DM Migration Notes

## Event-Driven Architecture Implementation (2023-11-10)

The Visual DM system has been migrated to align with the Development Bible's architectural guidance:

### Changes Implemented

1. **Event Dispatcher System**
   - Implemented a centralized `EventDispatcher` that follows the publish-subscribe pattern
   - Created typed event classes for all major system events (MemoryEvent, RumorEvent, MotifEvent)
   - Added support for both synchronous and asynchronous event handling

2. **Repository Pattern**
   - Replaced direct Firebase database access with repository abstractions
   - Implemented JSON storage with versioning for all entities
   - Created specialized repositories for players, NPCs, factions, regions, motifs, and rumors

3. **Middleware Chain**
   - Added middleware support to the event dispatcher
   - Implemented middleware for logging, validation, analytics, and throttling
   - Created a flexible middleware chain that can be dynamically configured

4. **Integration Tests**
   - Added comprehensive integration tests for the new architecture:
     - `test_event_integration.py`: Tests event dispatcher and component integration
     - `test_repository_integration.py`: Tests repository pattern implementation
     - `test_middleware_integration.py`: Tests middleware chain implementation

### Breaking Changes

1. All direct database access must be migrated to use repositories
2. Event handling now uses the publish-subscribe pattern instead of direct function calls
3. The DungeonMaster class now integrates with the event system for context generation

### Migration Path

To migrate existing code:

1. Replace direct database access with repository calls:
   ```python
   # Old code
   db.collection('players').document(player_id).get()
   
   # New code
   PlayerRepository.get_instance().get_player_data(player_id)
   ```

2. Replace direct function calls with event publishing:
   ```python
   # Old code
   memory_manager.create_memory(entity_id, memory_data)
   
   # New code
   event = MemoryEvent(
       event_type="memory.created", 
       entity_id=entity_id, 
       memory_data=memory_data
   )
   EventDispatcher.get_instance().publish_sync(event)
   ```

3. Subscribe to events instead of using callbacks:
   ```python
   # Old code
   memory_manager.on_memory_created(callback_fn)
   
   # New code
   def handle_memory_event(event):
       if event.event_type == "memory.created":
           # Handle the event
           pass
   
   EventDispatcher.get_instance().subscribe(MemoryEvent, handle_memory_event)
   ```

### Testing the New Architecture

The integration tests can be run to verify the new architecture:

```bash
cd backend
python -m unittest tests.systems.llm.test_event_integration
python -m unittest tests.systems.llm.test_repository_integration
python -m unittest tests.systems.llm.test_middleware_integration
```

### Resources

- See [systems/llm/README.md](systems/llm/README.md) for detailed documentation on the new architecture
- See [docs/Development_Bible.md](../docs/Development_Bible.md) for the overall architectural vision
