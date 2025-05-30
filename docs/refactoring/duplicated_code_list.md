# Duplicate Code Analysis in VDM Codebase

Based on the analysis of the VDM codebase, the following instances of duplicated or highly similar code have been identified. These duplications represent potential areas for refactoring to improve maintainability and reduce the risk of inconsistent implementations.

## 1. ID Generation Utilities

### Duplicated Classes:
- `VisualDM.Core.IdGenerator` in `/Scripts/Core/IdGenerator.cs`
- Similar functionality in `/Scripts/VDM/Core/IdUtility.cs` (inferred)

Both classes appear to provide methods for generating unique identifiers, GUIDs, and UUIDs, with several functions duplicated between them:
- `GenerateUniqueId()`
- `GenerateGuid()`
- `GenerateUuid()`
- `GenerateDeterministicGuid()`

The implementation in various places also shows duplication, such as:
- Direct calls to `Guid.NewGuid().ToString()` scattered throughout the codebase rather than using these utility classes
- Manual UUID generation in several model constructors (e.g. `MapLayer`, `MapAnnotation`)

## 2. Logging Utilities

### Duplicated Logging Classes:
- `VDM.Combat.CombatLogger`
- `VisualDM.Systems.Animation.Threading.AnimationMetrics`
- Likely other domain-specific logging utilities

These classes duplicate basic logging functionality with similar methods:
- `Log(string message)`
- `LogWarning(string message)`
- `LogError(string message)`

## 3. Utility Methods

### Duplicated Path Handling:
- `CoreUtility.EnsureDirectoryExists()` in `/Scripts/VDM/Core/CoreUtility.cs`
- `StorageUtils.NormalizePath()` in `/Scripts/Systems/Storage/StorageUtils.cs`
- `StorageUtils.ValidatePath()` in `/Scripts/Systems/Storage/StorageUtils.cs`

### Duplicated String Manipulation:
- `StorageUtils.SafeFilename()` in `/Scripts/Systems/Storage/StorageUtils.cs`
- Similar string sanitization methods likely scattered across multiple classes

## 4. UI Framework Components

### Duplicated Model-View-Controller Base Classes:
- Duplicated or similar MVC pattern implementations in both:
  - `/Scripts/VisualDM/UI/` namespace
  - Potentially another namespace with similar structure

Specific duplications:
- `UIModel`, `UIController`, `UIView` base classes 
- Navigation logic in `UIMVCManager` potentially duplicated elsewhere

## 5. Error Handling and Monitoring

### Duplicated Error Handling Patterns:
- Similar try/catch blocks with error logging in:
  - `Motif.SetLifespan()` & `Motif.SetVersion()` 
  - `MotifCache` methods
  - `MotifMigrationUtility` methods

These all follow the pattern:
```csharp
try {
    // Implementation
}
catch (Exception ex) {
    VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MethodName failed", "ClassPath.MethodName");
    VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
    return false; // or other failure indicator
}
```

## 6. Domain Models and Interfaces

### Duplicated or Overlapping Interfaces:
- Repository pattern interfaces like:
  - `IGlobalArcRepository` 
  - `IGlobalArcService`
  - Likely other similar repository interfaces across domains

### Similar Model Classes:
- Potential duplication between `VDM` and `VisualDM` namespaces for core entity models
- Similar property structures in related classes:
  - `CharacterClass` and `CharacterAbility` 
  - `InventoryItem` and `CharacterRelationship`

## 7. Duplicate Transaction Support

Multiple classes appear to implement similar transaction support with methods like:
- `BeginTransaction()`
- `CommitTransaction()`
- `RollbackTransaction()`

## 8. Clone/Copy Methods

Many entities implement similar deep-copy functionality:
- `Motif.Clone()`
- `MapLayer.Clone()`
- `MapAnnotation.Clone()`
- `CharacterModel.Clone()`
- `CombatEffect.Copy()`

## 9. Data Merging Logic

Duplicated JSON/object merging logic:
- `MergeJObjects()` in `ModSynchronizer`
- Likely similar merging functions in other data processing classes

## 10. Character Systems

### Duplicated Character Models:
- `VisualDM.Character.CharacterModel` in `/Scripts/Character/CharacterModel.cs`
- `VisualDM.Entities.SimulatedCharacter` in `/Scripts/Entities/SimulatedCharacter.cs`
- Possible third implementation referenced in `/Scripts/UI/UIManager.cs` as `Character`

These models have similar properties and behaviors:
- Common properties (Name, Stats, Inventory)
- Character attributes (Strength, Dexterity, etc.)
- Similar utility methods for stats calculation

### Duplicated Character Support Classes:
- `CharacterClass` nested in `CharacterModel`
- `CharacterAbility` nested in `CharacterModel`
- `CharacterStats` in `/Scripts/Entities/CharacterStats.cs`
- `CharacterEncumbrance` in `/Scripts/Entities/CharacterStats.cs`
- `InventoryItem` nested in `CharacterModel`
- `CharacterRelationship` nested in `CharacterModel`

## 11. Combat Systems

### Duplicated Combat Classes:
- Combat action structure duplicated across interfaces and implementations:
  - `CombatAction` class
  - `CombatActionBase` abstract class
  - `ICombatAction` (inferred interface)
- Duplicated error handling in combat effect implementations
- Similar event handling patterns across combat classes

### Duplicated Combat State Management:
- `CombatStateSnapshot` for history/rollback
- Likely overlap with the state management in `CombatManager`
- Duplicated combat event handlers (damage, healing, turn management)

### Combat Effect System:
- `CombatEffect` base class with extensive inheritance chain
- Multiple similar implementations of effect stacking logic
- Duplicated validation patterns (IsImmune, CanExecute)
- Similar implementations of modifier calculations (ModifyIncomingDamage, ModifyOutgoingDamage)

## 12. Inventory Systems

### Duplicated Inventory Implementations:
- `VisualDM.Systems.Inventory.Inventory` class in `/Scripts/Systems/Inventory/InventorySystem.cs`
- `InventoryManager` in `/Scripts/Inventory/InventoryManager.cs`
- Different `Item` class implementations (Inventory and CharacterModel)

### Duplicated Inventory Components:
- `Item` class in the Inventory namespace
- `InventorySlot` class in the Inventory namespace
- `InventoryItem` class in the Character namespace
- Similar transaction handling duplicated across inventory systems
- Duplicated weight and encumbrance calculations

### Related Inventory Utilities:
- `InventoryFeedbackSystem` contains UI feedback that duplicates similar patterns in other systems
- Overlapping inventory interfaces like `IInventorySystem`
- Similar serialization approaches for inventory data

## 13. Configuration Management

### Multiple Configuration Systems:
- `SystemsConfig` in `/Scripts/UI/Feedback/FeedbackManager.cs`
- `PersistenceConfig` in `/Scripts/Systems/Storage/PersistenceManager.cs`
- Configuration settings in `GameManager`
- `GrudgeConfig` in rivalry system
- Hardcoded configuration in `NetworkPopulationManager`

### Duplicated Initialization Patterns:
- `ConsolidatedGameLoader` intended to handle initialization but duplicates logic with:
  - `GameManager` singleton initialization
  - `ModularDataSystem` data initialization
  - Other module-specific initializers

### Configuration Loading Patterns:
- Multiple implementations of configuration loading and serialization
- Duplicate default configuration generation
- Similar validation patterns across configuration systems

## 14. Data Management

### Duplicated Data Systems:
- `ModularDataSystem` in `/Scripts/Data/ModularDataSystem.cs` 
- `VisualDM.Systems.DataManager` referenced in `ConsolidatedGameLoader`
- Possible third implementation elsewhere

### Data Storage Patterns:
- Similar persistence layers implemented across different systems
- Duplicated save/load operations
- Multiple serialization approaches for similar data

# Refactoring Plan

This section outlines a comprehensive approach to address the duplication issues identified above. The plan is organized into phases with specific patterns to apply for each category of duplication.

## Phase 1: Core Infrastructure Consolidation

### 1.1 Create Core Utility Library (Addressing Issues #1, #2, #3)

1. Create a new namespace `VDM.Core.Utils` with the following consolidated utility classes:
   - `IdUtils`: Single source for ID generation
   - `LogUtils`: Centralized logging with domain-specific tagging
   - `FileUtils`: Path handling, validation, and normalization
   - `StringUtils`: String manipulation and sanitization
   - `JsonUtils`: JSON operations including merging and transformation

2. Implementation approach:
```csharp
// Example for consolidated ID generation
namespace VDM.Core.Utils
{
    public static class IdUtils
    {
        public static string GenerateUniqueId() { /* implementation */ }
        public static string GenerateGuid() { /* implementation */ }
        public static string GenerateUuid(string format = "N") { /* implementation */ }
        public static string GenerateDeterministicGuid(string @namespace, string name) { /* implementation */ }
        
        // Extension methods to support various scenarios
        public static string NewIdFor<T>(this T entity) where T : class { /* implementation */ }
    }
}
```

### 1.2 Create Exception Handling Framework (Addressing Issue #5)

1. Implement a unified error handling framework:
   - `ExceptionHandler`: For standardized exception processing
   - `ErrorLogger`: For centralized error logging
   - `Try<T>` result pattern: For operations that can fail

2. Implementation approach:
```csharp
// Example for centralized error handling
public static class ExceptionHandler
{
    public static TResult Try<TResult>(Func<TResult> action, 
                                      string context = null, 
                                      TResult defaultValue = default)
    {
        try
        {
            return action();
        }
        catch (Exception ex)
        {
            ErrorLogger.LogException(ex, context);
            return defaultValue;
        }
    }
    
    // Overloads for different return types and behaviors
}
```

## Phase 2: Domain Model Consolidation

### 2.1 Standardize Character System (Addressing Issue #10)

1. Create a unified character domain model:
   - Base `ICharacter` interface
   - Core `Character` implementation
   - Supporting specialized interfaces (IPlayable, INonPlayable)
   - Clear separation between data model and behavior

2. Implementation approach:
```csharp
// Unified character model
namespace VDM.Domain.Characters
{
    public interface ICharacter
    {
        string Id { get; }
        string Name { get; }
        Stats Stats { get; }
        // Core character properties
    }
    
    public class Character : ICharacter
    {
        // Implementation of core character functionality
    }
    
    // Support classes in appropriate namespaces
    namespace Stats { /* Character stat implementations */ }
    namespace Classes { /* Character class implementations */ }
    namespace Abilities { /* Character ability implementations */ }
}
```

### 2.2 Unify Combat System (Addressing Issue #11)

1. Implement a coherent combat architecture:
   - Clear interfaces for all combat participants
   - Event-based communication system
   - State management with command pattern
   - Effects system with composable behaviors

2. Implementation approach:
```csharp
// Unified combat system
namespace VDM.Domain.Combat
{
    public interface ICombatAction 
    {
        string Name { get; }
        string Description { get; }
        bool CanExecute(ICombatant source, ICombatant target);
        void Execute(ICombatant source, ICombatant target);
    }
    
    // Implementation with proper separation of concerns
}
```

### 2.3 Consolidate Inventory System (Addressing Issue #12)

1. Create a single inventory implementation:
   - Use composition over inheritance
   - Interface-based design for flexibility
   - Clear separation between data and operations

2. Implementation approach:
```csharp
// Unified inventory system
namespace VDM.Domain.Inventory
{
    public interface IInventory
    {
        IReadOnlyList<IItem> Items { get; }
        bool AddItem(IItem item, int quantity = 1);
        bool RemoveItem(string itemId, int quantity = 1);
        // Core inventory operations
    }
    
    public class Inventory : IInventory
    {
        // Implementation with proper transaction support
    }
}
```

## Phase 3: Architecture Improvements

### 3.1 Implement Dependency Injection (Addressing Issues #4, #13, #14)

1. Introduce a proper DI container:
   - Service registration system
   - Lifecycle management for singleton services
   - Configuration injection
   - Testability support

2. Implementation approach:
```csharp
// Example for service registration
public class GameServiceProvider
{
    private static readonly Dictionary<Type, object> _services = new Dictionary<Type, object>();
    
    public static void RegisterSingleton<T>(T instance) where T : class
    {
        _services[typeof(T)] = instance;
    }
    
    public static T GetService<T>() where T : class
    {
        return _services.TryGetValue(typeof(T), out var service) ? (T)service : null;
    }
    
    // Additional DI container functionality
}
```

### 3.2 Create a Configuration System (Addressing Issue #13)

1. Create a unified configuration system:
   - Hierarchical configuration with inheritance
   - Runtime configuration changes
   - Validation and schema support
   - Serialization consistency

2. Implementation approach:
```csharp
// Centralized configuration
namespace VDM.Core.Configuration
{
    public interface IConfigurationProvider
    {
        T GetConfiguration<T>(string key) where T : class, new();
        void SetConfiguration<T>(string key, T configuration) where T : class;
        // Configuration operations
    }
    
    public class ConfigurationManager : IConfigurationProvider
    {
        // Implementation with proper serialization and defaults
    }
}
```

### 3.3 Implement Common Interfaces and Patterns (Addressing Issues #6, #7, #8, #9)

1. Establish standard interfaces for common operations:
   - `ICloneable<T>` for proper generic cloning
   - `ITransaction` for transactional operations
   - `IPersistable` for storage operations
   - Generic repository interfaces

2. Implementation approach:
```csharp
// Example for standardized interfaces
namespace VDM.Core.Patterns
{
    public interface ICloneable<T>
    {
        T Clone();
    }
    
    public interface ITransaction
    {
        void BeginTransaction();
        void CommitTransaction();
        void RollbackTransaction();
        bool InTransaction { get; }
    }
    
    // Additional pattern interfaces
}
```

## Phase 4: Component-Specific Refactoring

### 4.1 UI Framework Standardization (Addressing Issue #4)

1. Implement a unified UI architecture:
   - Consistent MVC/MVVM pattern
   - UI component registry
   - Event-based communication
   - Standardized navigation

2. Implementation approach:
```csharp
// Unified UI framework
namespace VDM.UI.Framework
{
    public abstract class ViewModel
    {
        public event Action PropertyChanged;
        
        protected void NotifyPropertyChanged()
        {
            PropertyChanged?.Invoke();
        }
    }
    
    public abstract class View
    {
        // Base view implementation
    }
    
    // Additional UI framework components
}
```

### 4.2 Data Layer Consolidation (Addressing Issue #14)

1. Create a unified data access layer:
   - Repository pattern implementation
   - Caching strategy
   - Async operations support
   - Transaction handling

2. Implementation approach:
```csharp
// Unified data layer
namespace VDM.Data
{
    public interface IRepository<T> where T : class
    {
        Task<T> GetByIdAsync(string id);
        Task<IEnumerable<T>> GetAllAsync();
        Task SaveAsync(T entity);
        Task DeleteAsync(string id);
    }
    
    // Implementation with proper error handling and transactions
}
```

## Implementation Roadmap

### Sprint 1: Foundation (Weeks 1-2)
- Create core utility library (Phase 1.1)
- Set up exception handling framework (Phase 1.2)
- Define common interfaces (Phase 3.3)

### Sprint 2: Architecture (Weeks 3-4)
- Implement dependency injection (Phase 3.1)
- Create configuration system (Phase 3.2)
- Begin data layer consolidation (Phase 4.2)

### Sprint 3: Domain Models Part 1 (Weeks 5-6)
- Standardize character system (Phase 2.1)
- Consolidate inventory system (Phase 2.3)
- Continue data layer implementation

### Sprint 4: Domain Models Part 2 (Weeks 7-8)
- Unify combat system (Phase 2.2)
- Implement UI framework standardization (Phase 4.1)
- Complete data layer consolidation

### Sprint 5: Migration and Testing (Weeks 9-10)
- Migrate existing code to new architecture
- Develop automated tests for new components
- Document architecture patterns

### Sprint 6: Final Integration (Weeks 11-12)
- Resolve integration issues
- Performance optimization
- Documentation and knowledge transfer

## Code Migration Strategy

To minimize disruption during the refactoring process:

1. **Parallel Implementation**: 
   - Create new components alongside existing ones
   - Use adapter pattern to connect legacy and new systems
   - Gradually migrate functionality

2. **Feature Flags**:
   - Toggle between old and new implementations
   - Enable incremental testing
   - Facilitate rollback if issues arise

3. **Comprehensive Testing**:
   - Unit tests for all new components
   - Integration tests for system boundaries
   - Performance benchmarks to ensure improvements

By following this structured approach, the duplication issues in the VDM codebase can be systematically addressed while improving overall code quality, maintainability, and performance. 