# Duplicate Type Analysis

This document tracks duplicate class and type definitions found in the codebase as part of Task #718.2.

## Identified Duplicate Classes

### ActionQueue
- **Files**:
  - `VDM/Assets/Scripts/Core/ActionQueue.cs`
  - `VDM/Assets/Scripts/Systems/Input/ActionQueue.cs`
  - Also referenced in: `VDM/Assets/Scripts/Systems/Input/ActionQueuePool.cs`
- **Analysis**:
  - **Core Version**:
    - Namespace: `VisualDM.Core`
    - Implementation: Comprehensive implementation with advanced features like action types, priority tiers, cancellation, interruption, and state saving
    - Dependencies: Uses `GameState`, `InputBuffer`, `IdGenerator` from Core namespace
    - More robust and feature-complete
  - **Systems/Input Version**:
    - Namespace: `VisualDM.Systems.Input`
    - Implementation: Simpler class with MonoBehaviour inheritance, basic priority queue for input events
    - More focused on input events specifically
    - Uses a pool system for better memory management
  - **Usage Considerations**: The namespaces suggest different intended use cases - core version for general-purpose action queuing, Input version specific to input event handling
- **Recommendation**: Keep both implementations but rename one to avoid confusion. Rename `VisualDM.Systems.Input.ActionQueue` to `VisualDM.Systems.Input.InputActionQueue` to better reflect its specific purpose.

### CharacterState
- **Files**:
  - `VDM/Assets/Scripts/Systems/Combat/InputValidator.cs`
  - `VDM/Assets/Scripts/Systems/Integration/ICharacterSystem.cs`
- **Next Steps**: Examine both implementations to determine if they are actual duplicates or just classes with the same name but different purposes.

### DialogueStateManager
- **Files**:
  - `VDM/Assets/Scripts/UI/DialogueStateManager.cs`
  - `VDM/Assets/Scripts/Core/DialogueStateManager.cs`
- **Next Steps**: Compare implementations to determine which version to keep or how to merge functionality.

### EventBus
- **Files**:
  - `VDM/Assets/Scripts/Core/EventBus.cs`
  - `VDM/Assets/Scripts/Systems/EventSystem/EventBus.cs`
- **Analysis**:
  - **Core Version**:
    - Namespace: `VisualDM.Core`
    - Implementation: Marked as DEPRECATED with an Obsolete attribute
    - Explicitly tells users to use the `VisualDM.Systems.EventSystem.EventBus` version
    - Has a throw exception in Awake() to prevent its usage
  - **Systems/EventSystem Version**:
    - Namespace: `VisualDM.Systems.EventSystem`
    - Implementation: More advanced with generic event types, handler priorities, filtering, weak references
    - Clearly the intended replacement for the Core version
- **Recommendation**: Remove the deprecated Core version since it's explicitly marked as obsolete and update any remaining references to use the `VisualDM.Systems.EventSystem.EventBus` version.

### Faction
- **Files**:
  - `VDM/Assets/Scripts/Entities/Faction.cs` (Likely the main implementation)
  - Referenced in multiple files:
    - `VDM/Assets/Scripts/World/FactionRelationshipSystem.cs`
    - `VDM/Assets/Scripts/World/FactionSystem.cs`
    - `VDM/Assets/Scripts/Systems/FactionLinkManager.cs`
    - `VDM/Assets/Scripts/Systems/FactionRelationshipManager.cs`
    - `VDM/Assets/Scripts/Systems/FactionArcMapper.cs`
    - `VDM/Assets/Scripts/Systems/FactionArc.cs`
    - `VDM/Assets/Scripts/Systems/FactionArcDTO.cs`
    - `VDM/Assets/Scripts/Entities/FactionArc.cs`
- **Next Steps**: Verify if all references point to the same type or if there are actual duplicates.

### FactionArc
- **Files**:
  - `VDM/Assets/Scripts/Entities/FactionArc.cs`
  - `VDM/Assets/Scripts/Systems/FactionArc.cs`
  - Referenced in:
    - `VDM/Assets/Scripts/Systems/FactionArcMapper.cs`
    - `VDM/Assets/Scripts/Systems/FactionArcDTO.cs`
- **Next Steps**: Compare implementations to determine which one to keep or how to merge functionality.

### HiddenObjective
- **Files**:
  - `VDM/Assets/Scripts/Systems/HiddenObjective.cs` (Only one file was returned, may be a false positive)
- **Next Steps**: Verify if this is actually duplicated somewhere else in the codebase.

### InputBuffer
- **Files**:
  - `VDM/Assets/Scripts/Core/InputBuffer.cs`
  - `VDM/Assets/Scripts/Systems/Input/InputBuffer.cs`
- **Analysis**:
  - **Core Version**:
    - Namespace: `VisualDM.Core`
    - Implementation: Regular C# class, not a MonoBehaviour
    - Has dependencies on `GameState` from the Core namespace
    - Less structured code with minimal documentation
  - **Systems/Input Version**:
    - Namespace: `VisualDM.Systems.Input`
    - Implementation: Inherits from MonoBehaviour for Unity integration
    - Has comprehensive XML documentation
    - Contains a nested GameState enum for context validation
    - Includes inspector-configurable parameters (BufferWindowDuration)
    - Overall more extensive validation and context awareness
  - **Similar Features**: Both implement circular buffer logic for input events, pruning of expired events, and input validation
- **Recommendation**: Similar to ActionQueue, both implementations seem to serve different use cases. Consider:
  1. Keeping both implementations but renaming the Systems/Input version to `UnityInputBuffer` to reflect its MonoBehaviour nature
  2. Or gradually migrating to use only the Systems/Input version and deprecating the Core version

### InteractionMetricsConfig
- **Files**:
  - `VDM/Assets/Scripts/Core/InteractionMetricsCollector.cs`
  - `VDM/Assets/Scripts/Core/InteractionMetricsConfig.cs`
- **Analysis**: The outline of InteractionMetricsCollector.cs shows that it contains an InteractionMetricsConfig class definition (lines 13-64) that appears to be distinct from the InteractionMetricsCollector class (lines 64-onward). This is not a duplicate class but rather two related classes in the same file.
- **Recommendation**: Not a duplicate; this is a case of a helper class defined in the same file as its primary consumer class. No action needed.

### Item
- **Files**:
  - `VDM/Assets/Scripts/Systems/Inventory/InventorySystem.cs` (Likely the main implementation)
  - Referenced in:
    - `VDM/Assets/Scripts/UI/ItemManagementPanel.cs`
    - `VDM/Assets/Scripts/Systems/Loot/Item.cs`
    - `VDM/Assets/Scripts/Systems/Theft/ItemValueManager.cs`
    - `VDM/Assets/Scripts/Systems/RewardCalculationEngine.cs`
  - **Analysis**: The outline of InventoryUI.cs shows that it references an Item class (line 21), which is likely the class from Systems/Loot/Item.cs. Need to confirm this is actually a duplicate or just references to the same class.
- **Next Steps**: Verify if all references point to the same type or if there are actual duplicates.

### ObjectPool
- **Files**:
  - `VDM/Assets/Scripts/Systems/CombatSystem/ObjectPool.cs`
  - `VDM/Assets/Scripts/Systems/ObjectPool.cs`
- **Next Steps**: Compare implementations to determine which one to keep or how to merge functionality.

### PathCache
- **Files**:
  - `VDM/Assets/Scripts/Systems/Pathfinding/PathCache.cs` (Likely the main implementation)
  - Referenced in:
    - `VDM/Assets/Scripts/World/PathfindingTypes.cs`
    - `VDM/Assets/Scripts/Systems/Pathfinding/Tests/PathCacheTests.cs`
- **Next Steps**: Verify if all references point to the same type or if there are actual duplicates.

### Region
- **Files**:
  - `VDM/Assets/Scripts/World/RegionSystem.cs` (Likely the main implementation)
  - Referenced in:
    - `VDM/Assets/Scripts/World/RegionWorldState.cs`
    - `VDM/Assets/Scripts/Systems/RegionalArcMapper.cs`
    - `VDM/Assets/Scripts/Systems/GlobalArcService.cs`
    - `VDM/Assets/Scripts/Systems/RegionalArc.cs`
    - `VDM/Assets/Scripts/Systems/RegionalArcDTO.cs`
  - **Analysis**: The outline of RegionSystem.cs shows that it contains a Region class that serves as a model for regions in the world. The references to this class from other files appear to be legitimate uses of the Region model, not duplications.
- **Recommendation**: Not a duplicate; this is a case of a legitimate model class being used across various systems. No action needed.

### ValidationResult
- **Files**:
  - `VDM/Assets/Scripts/UI/FileValidationService.cs`
  - `VDM/Assets/Scripts/Core/ValidationFramework.cs`
  - `VDM/Assets/Scripts/Systems/QuestDesignerTools.cs`
- **Next Steps**: Compare implementations to determine if these are all the same type or if they serve different purposes.

### WorldEvent
- **Files**:
  - `VDM/Assets/Scripts/World/EventSystem.cs`
  - `VDM/Assets/Scripts/World/WorldEventListener.cs`
- **Next Steps**: Compare implementations to determine which one to keep or how to merge functionality.

### WorldStateManager
- **Files**:
  - `VDM/Assets/Scripts/World/WorldStateManager.cs` (Likely the main implementation)
  - Referenced in:
    - `VDM/Assets/Scripts/World/RegionWorldState.cs`
    - `VDM/Assets/Scripts/World/WorldStateObserver.cs`
- **Next Steps**: Verify if all references point to the same type or if there are actual duplicates.

## Action Plan

For each duplicate class:

1. **Analysis Phase**:
   - Examine the implementations in each file
   - Document their differences and similarities
   - Identify which implementation is more complete/correct
   - Determine usage patterns across the codebase

2. **Decision Phase**:
   - Decide which version to keep
   - Plan how to merge functionality if needed
   - Document references that need to be updated

3. **Implementation Phase**:
   - Update files as needed
   - Fix any references to the removed/merged classes
   - Ensure functionality is preserved

## Completion Criteria

This task will be considered complete when:
- All duplicate class definitions have been analyzed
- All duplicates have been resolved (merged or one version kept)
- All references have been updated to point to the correct implementation
- Documentation of changes has been updated 