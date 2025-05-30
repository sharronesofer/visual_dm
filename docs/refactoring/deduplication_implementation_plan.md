# Deduplication Implementation Plan

This document outlines the detailed steps for safely deduplicating the backend codebase while ensuring no functionality is lost in the process.

## System Analysis Summary

### 1. GPT Client Duplication

**Files:**
- Centralized: `/backend/core/ai/gpt_client.py`
- Duplicate: `/backend/systems/rumor/gpt_client.py`

**Functional differences:**
- The centralized version is more robust with:
  - Singleton pattern implementation
  - Better error handling with retries
  - More detailed logging
  - Support for multiple LLM models 
  - More flexible messaging formats
  - Convenience methods like `generate_text()`

**Usage:**
- The rumor system's `rumor_transformer.py` and `api.py` have already been updated to use the centralized version
- However, we need to ensure any additional functionality needed by the rumor system is preserved

### 2. Event Dispatcher Duplication

**Files:**
- Canonical: `/backend/systems/events/models/event_dispatcher.py`
- Duplicate: `/backend/systems/events/services/event_dispatcher.py`

**Functional differences:**
- Both implement the singleton pattern
- Both support async and sync event dispatch
- The services version has additional middleware support and priority-based handlers
- The models version has a simpler approach with direct handler registration
- API differences: `dispatch` vs `publish`, `register_handler` vs `subscribe`

**Usage:**
- `rumor_service.py` has been updated to use the models version's `dispatch` method
- We need to preserve middleware and priority handler functionality when consolidating

### 3. Inventory & Equipment Systems Overlap

**Files:**
- Inventory System: Well-structured with clear validator pattern
- Equipment System: Uses inventory utilities but has unique equipment-specific functionality

**Relationship:**
- Not true duplication but rather complementary systems
- Equipment depends on inventory for basic operations
- Each system has its own valid domain concerns

## Implementation Plan

### Phase 1: Preserve and Merge GPT Client Functionality

1. **Review the rumor system's GPT client for unique functionality:**
   - The rumor system's client is simpler with fewer features
   - No unique functionality identified that isn't already in the centralized version

2. **Update remaining references if any:**
   - Verify all imports have been updated to use `backend.core.ai.gpt_client`
   - Check for any additional handlers in the rumor system that might use the client

3. **Add transitional wrapper (deprecated) if needed:**
   ```python
   # backend/systems/rumor/gpt_client_deprecated.py
   import warnings
   from backend.core.ai.gpt_client import GPTClient as CoreGPTClient, GPTRequest, GPTResponse
   
   warnings.warn(
       "The rumor.gpt_client module is deprecated. Use backend.core.ai.gpt_client instead.",
       DeprecationWarning, 
       stacklevel=2
   )
   
   class GPTClient(CoreGPTClient):
       """Deprecated GPTClient - use backend.core.ai.gpt_client.GPTClient instead."""
       pass
   ```

### Phase 2: Consolidate Event Dispatcher Functionality

1. **Enhance the models/event_dispatcher.py with priority and middleware:**
   ```python
   # Add to backend/systems/events/models/event_dispatcher.py
   
   def register_handler_with_priority(self, event_type: Type[T], handler: Callable[[T], None], priority: int = 0) -> None:
       """Register a handler with priority (higher priority handlers execute first)."""
       if event_type not in self._handlers_with_priority:
           self._handlers_with_priority = {}
       
       if event_type not in self._handlers_with_priority:
           self._handlers_with_priority[event_type] = []
       
       self._handlers_with_priority[event_type].append({
           'handler': handler,
           'priority': priority
       })
       
       # Sort by priority (descending)
       self._handlers_with_priority[event_type].sort(
           key=lambda x: x['priority'], reverse=True
       )
       
       logger.debug(f"Registered handler {handler.__name__} for {event_type.__name__} with priority {priority}")
   
   # Add middleware support
   def add_middleware(self, middleware: Callable[[EventBase, Callable], Any]) -> None:
       """Add middleware to process events before dispatching."""
       self._middlewares.append(middleware)
       logger.debug(f"Middleware {middleware.__name__} added to dispatcher")
   ```

2. **Add compatibility layer for old method names:**
   ```python
   def subscribe(self, event_type: Type[T], handler: Callable[[T], None], priority: int = 0) -> None:
       """Alias for register_handler_with_priority for compatibility."""
       return self.register_handler_with_priority(event_type, handler, priority)
       
   def publish(self, event: EventBase) -> None:
       """Alias for dispatch for compatibility."""
       return self.dispatch(event)
   ```

3. **Create proxy wrapper (deprecated) for backward compatibility:**
   ```python
   # backend/systems/events/services/event_dispatcher_deprecated.py
   import warnings
   from backend.systems.events.models.event_dispatcher import EventDispatcher as ModelEventDispatcher
   
   warnings.warn(
       "The events.services.event_dispatcher module is deprecated. Use backend.systems.events.models.event_dispatcher instead.",
       DeprecationWarning, 
       stacklevel=2
   )
   
   class EventDispatcher(ModelEventDispatcher):
       """Deprecated EventDispatcher - use models.event_dispatcher.EventDispatcher instead."""
       pass
   ```

### Phase 3: Inventory & Equipment Systems Clarification

1. **Update the inventory_utils.py in equipment system:**
   ```python
   """
   Inventory utilities for managing equipment and items.
   This module now uses the canonical inventory system utilities.
   """
   
   import logging
   from typing import Dict, List, Optional
   from backend.systems.inventory.models.inventory_validator import InventoryValidator
   from backend.systems.inventory.models.inventory_utils import (
       calculate_total_weight,
       group_equipment_by_type,
       get_equipped_items
   )
   
   # Re-export canonical functions
   __all__ = [
       'calculate_total_weight',
       'group_equipment_by_type',
       'get_equipped_items',
       'calculate_equipment_bonuses',
       'load_equipment_rules'
   ]
   
   logger = logging.getLogger(__name__)
   
   # Keep equipment-specific functions
   def load_equipment_rules() -> Dict:
       """Load equipment rules from JSON file."""
       # Implementation unchanged
   
   def calculate_equipment_bonuses(equipped_items: List) -> Dict:
       """Calculate bonuses from equipped items."""
       # Implementation unchanged
   ```

2. **Update READMEs with clearer boundary explanations** (already done)

### Phase 4: Testing and Validation

1. **Create unit tests for consolidated functionality:**
   ```python
   # backend/tests/systems/events/test_event_dispatcher.py
   # Test both old and new interfaces
   
   # backend/tests/systems/rumor/test_gpt_client.py
   # Verify the centralized client works for rumor transformations
   ```

2. **Create integration tests to verify system interaction:**
   ```python
   # backend/tests/integration/test_rumor_events.py
   # Test rumor system with consolidated event dispatcher
   
   # backend/tests/integration/test_equipment_inventory.py
   # Test proper interaction between systems
   ```

### Phase 5: Cleanup

1. **After successful tests, remove deprecated wrappers:**
   - Delete transitional wrappers after sufficient grace period
   - Remove compatibility method aliases when no longer needed

2. **Update documentation to reflect changes:**
   - Update system diagrams showing correct dependencies
   - Revise development guides to reference canonical implementations

3. **Run the cleanup script to safely remove duplicate files:**
   ```bash
   # After all tests pass and all functionality is verified
   ./backend/cleanup_duplicates.sh
   ```

## Order of Operations

For each system:

1. Identify and document ALL functionality in both duplicate implementations
2. Enhance canonical implementation with any missing functionality
3. Create backward compatibility layer if needed
4. Update all imports to use canonical versions
5. Write tests to verify functionality is preserved
6. Run tests to validate changes
7. Delete deprecated versions only after all tests pass

## Verification Checklist

For each system being deduplicated:

- [ ] All functionality documented and understood
- [ ] Canonical implementation enhanced with all needed functionality
- [ ] All imports updated to use canonical version
- [ ] Unit tests pass for individual components
- [ ] Integration tests pass for system interactions
- [ ] Run-time behavior unchanged
- [ ] Application starts successfully
- [ ] No regression in existing features

## Next Steps

After completing the initial deduplication:

1. Continue with faction, dialogue, and memory systems analysis
2. Apply the same methodical process to each system
3. Update developer documentation with best practices
4. Implement automated detection for potential future duplication 