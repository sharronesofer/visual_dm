# Visual DM Memory System Refactoring Plan

## Key Phases

1. **Analysis Phase** (Task 101)
   - Document all deviations from Development Bible
   - Map current implementation to required changes

2. **Core Model Updates** (Tasks 102-104)
   - Add core memory support
   - Remove non-entity memory functions
   - Update memory decay system

3. **Storage & Repository** (Tasks 105, 108, 112)
   - Implement JSON storage
   - Create clean repository pattern
   - Migrate existing memories

4. **Event System** (Tasks 106, 109)
   - Standardize memory events
   - Implement event-based information sharing

5. **Simplification** (Task 107)
   - Simplify cognitive frames system

6. **Testing & Documentation** (Tasks 110, 111)
   - Create comprehensive tests
   - Update documentation

## Current Progress

- ✅ **Added `is_core` property to Memory model** (Task 102)
- ✅ **Removed non-entity memory functions** (Task 103)
  - Removed update_faction_memory, update_region_memory, update_world_memory, and update_poi_memory
  - Updated process_gpt_memory_entry to use entity-based memories instead
- ✅ **Updated memory decay system to respect core memories** (Task 104)
  - Modified run_memory_decay to check for is_core flag
  - Added logic to skip decay for core memories
- ✅ **Simplified cognitive frames system** (Task 107)
  - Reduced number of frames to a core set
  - Simplified metadata and removed complex relationships
  - Updated utility functions to use simplified system
- ✅ **Implemented JSON storage for memory system** (Task 105)
  - Created StorageManager abstract base class
  - Implemented JSONStorageManager with versioning support
  - Updated memory_manager.py to use JSON storage
  - Ensured proper serialization/deserialization of memory objects

## Next Steps

1. **Task 106: Standardize Memory Events**
   - Review current event emissions in memory_manager.py
   - Ensure all memory operations emit appropriate events
   - Standardize event data structure

2. **Task 108: Create Clean Repository Pattern**
   - Implement a proper repository pattern for memory access
   - Update memory_manager.py to use the repository
   - Ensure all memory access goes through the repository

3. **Task 109: Implement Event-Based Information Sharing**
   - Replace direct memory sharing with event-based mechanism
   - Ensure memory information is only shared through events
   - Update relevant utility functions

## Implementation Strategy

- Maintain backward compatibility where possible
- Use incremental implementation with feature flags
- Focus on entity-local memory isolation
- Follow clean repository pattern principles
- Implement event-based communication
- Create thorough tests for all components

## Next Steps

1. Complete Task 101 (Analysis) to finalize the refactoring plan
2. Proceed with Task 102 (Core Memory Support) which has already been started
3. Continue with Task 103 (Remove Non-Entity Memory Functions)
4. Follow the task sequence as defined in the task dependencies

This refactoring will align the memory system with the Development Bible specifications and create a more maintainable, consistent system for entity memories. 