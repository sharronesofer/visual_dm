# VDM Code Consolidation Plan

## Identified Duplications

Based on the code search, I've identified several areas of code duplication that should be consolidated:

1. **ID Generation**
   - `VisualDM.Core.IdGenerator` in `/Scripts/Core/IdGenerator.cs` (the primary implementation)
   - This file is already well-structured and can serve as the central implementation

2. **Error Handling**
   - `VisualDM.Core.ErrorHandlingService` in `/Scripts/Core/ErrorHandlingService.cs`
   - Multiple duplicate try/catch blocks with similar `LogException` calls across the codebase

3. **Character Systems**
   - `VisualDM.Character.CharacterModel` in `/Scripts/Character/CharacterModel.cs`
   - `VisualDM.Entities.SimulatedCharacter` in `/Scripts/Entities/SimulatedCharacter.cs`
   - Several character-related nested classes duplicating functionality

4. **Inventory Systems**
   - `VisualDM.Systems.Inventory.Inventory` in `/Scripts/Systems/Inventory/InventorySystem.cs`
   - `InventoryManager` in `/Scripts/Inventory/InventoryManager.cs`
   - Duplicated item and inventory UI functionality

## Consolidation Approach

Instead of creating new files, we will consolidate by:

1. Identifying the primary implementation for each area
2. Merging unique functionality from duplicate implementations
3. Adding compatibility shims for existing code (i.e., adapter pattern)
4. Gradually migrating dependent code to use the consolidated implementation

## 1. ID Generation Consolidation

### Primary Implementation
- Keep `VisualDM.Core.IdGenerator` as the primary implementation
- No new file needed as it's already well-structured

### Migration Path
1. Create unit tests to validate all ID generation functionality
2. Find and replace direct `Guid.NewGuid()` calls with `IdGenerator` calls
3. Create type-specific helpers for commonly-used ID patterns

## 2. Error Handling Consolidation

### Primary Implementation
- Enhance `VisualDM.Core.ErrorHandlingService` to include helper methods for common patterns:

```csharp
// Add to ErrorHandlingService.cs
public static bool TryExecute(Action action, string context = null, string userMessage = null)
{
    try
    {
        action();
        return true;
    }
    catch (Exception ex)
    {
        Instance.LogException(ex, userMessage, context);
        VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
        return false;
    }
}

public static T TryExecute<T>(Func<T> func, string context = null, string userMessage = null, T defaultValue = default)
{
    try
    {
        return func();
    }
    catch (Exception ex)
    {
        Instance.LogException(ex, userMessage, context);
        VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
        return defaultValue;
    }
}
```

### Migration Path
1. Update the error handling service first
2. Search for the common error handling pattern in the codebase:
   ```csharp
   try
   {
       // Implementation
   }
   catch (Exception ex)
   {
       VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "...", "...");
       VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
       return false; // or other failure indicator
   }
   ```
3. Replace with refactored pattern:
   ```csharp
   return ErrorHandlingService.TryExecute(() => {
       // Implementation
   }, "ClassName.MethodName", "User-friendly message");
   ```

## 3. Character System Consolidation

### Primary Implementation
- Choose `VisualDM.Character.CharacterModel` as the primary implementation since it's more comprehensive
- Add compatibility adapters for `SimulatedCharacter`

### Migration Path
1. Create `CharacterAdapter` class to adapt `CharacterModel` to `SimulatedCharacter` API
2. Update `CharacterModel` to include relevant functionality from `SimulatedCharacter`
3. Create a central `CharacterFactory` that instantiates appropriate character types
4. Gradually refactor code using `SimulatedCharacter` to use `CharacterModel` or the adapter

```csharp
// Example adapter pattern
public class CharacterAdapter : SimulatedCharacter
{
    private CharacterModel _model;
    
    public CharacterAdapter(CharacterModel model) 
    {
        _model = model;
        // Map properties from model to adapter
        Name = model.Name;
        Stats = MapStats(model.Stats);
        // etc.
    }
    
    // Override methods to delegate to the model
    public override bool ApplyFeat(VisualDM.Timeline.Models.Feat feat)
    {
        // Implement to delegate to CharacterModel
        return true;
    }
}
```

## 4. Inventory System Consolidation

### Primary Implementation
- Use `VisualDM.Systems.Inventory.Inventory` as the primary implementation
- It's more comprehensive with better transaction handling

### Migration Path
1. Create adapter for `InventoryManager` to use `Inventory`
2. Consolidate Item definitions between the two implementations
3. Update UI code to work with the consolidated inventory system
4. Consider adding extension methods to preserve interface compatibility

```csharp
// Example adapter
public class InventoryManagerAdapter : MonoBehaviour
{
    private Inventory _inventory;
    
    // Preserve the singleton pattern expected by existing code
    public static InventoryManagerAdapter Instance { get; private set; }
    
    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            _inventory = GetComponent<Inventory>() ?? gameObject.AddComponent<Inventory>();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    // Implement InventoryManager methods to delegate to Inventory
    public bool AddItem(string itemId, int quantity = 1)
    {
        Item item = ItemDatabase.GetItem(itemId);
        return item != null && _inventory.AddItem(item, quantity);
    }
    
    // etc.
}
```

## Implementation Order

1. **Phase 1** - Error Handling (Week 1) [IN PROGRESS]
   - Least likely to cause integration issues
   - Provides immediate code quality benefits
   - No UI dependencies
   - ✅ `ErrorHandlingService` enhanced with `TryExecute` methods for standardized patterns
   - ✅ Created refactoring guide in `error_handling_refactoring.md`
   - ✅ Refactored first examples in `MotifEventDispatcher` and `MotifTransactionManager`
   - ✅ Refactored `MotifRuleEngine` error handling with nested try/catch blocks
   - ✅ Refactored `MotifValidator` class for standardized error handling
   - ✅ Refactored `MotifTriggerManager` to use new error handling patterns

2. **Phase 2** - ID Generation (Week 2)
   - Simple utility that can be refactored with minimal risk
   - Creates foundation for other systems

3. **Phase 3** - Inventory System (Weeks 3-4)
   - More complex but fewer dependencies than Character system
   - Can be incrementally migrated with adapters

4. **Phase 4** - Character System (Weeks 5-6)
   - Most complex with many dependencies
   - Requires careful testing and migration

## Testing Strategy

1. Create unit tests for each consolidated system
2. Implement integration tests for critical workflows
3. Use A/B testing to validate equivalence between old and new implementations
4. Monitor error rates during and after migration

## Rollback Plan

For each consolidated system:
1. Retain old implementations during transition
2. Use feature flags to switch between implementations
3. Log detailed diagnostics during migration
4. Implement canary deployments for each phase 