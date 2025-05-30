# Unity Namespace and Assembly Reference Fix

## Problem Analysis

After resolving the circular dependency issues, Unity is now showing legitimate compilation errors where scripts cannot find classes and namespaces they depend on. This is because:

### Root Cause
1. **Namespace Mismatches**: Scripts are using `using` statements for namespaces that don't exist as expected
2. **Assembly Reference Issues**: Scripts are in assemblies that don't reference the assemblies containing the classes they need
3. **Incorrect Namespace Usage**: Scripts are importing namespaces incorrectly based on the actual assembly structure

### Current Assembly Structure
```
VDM.Runtime        - Assets/Scripts/Runtime/ (contains VDM.World, VDM.Net, etc. as subdirectories)
VDM.Character      - Assets/Scripts/Character/
VDM.Systems        - Assets/Scripts/Systems/
VDM.Services       - Assets/Scripts/Services/ 
VDM.Core           - Assets/Scripts/Core/
VDM.Modules        - Assets/Scripts/Modules/
VDM.DTOs           - Assets/Scripts/DTOs/
VDM.Common         - Assets/Scripts/Common/
VDM.UI             - Assets/Scripts/UI/
VDM.Combat         - Assets/Scripts/Combat/
VDM.Tests          - Assets/Scripts/Tests/
```

### Namespace Reality vs Expected
- **Scripts expect**: `using VDM.WebSocket;` (separate assembly)
- **Reality**: Classes are in `VDM.Net` namespace within `VDM.Runtime` assembly
- **Scripts expect**: `using VDM.World;` from different assemblies  
- **Reality**: Classes are in `VDM.World` namespace within `VDM.Runtime` assembly

## Fix Strategy

### Phase 1: Fix Namespace Imports
Replace incorrect namespace imports with correct ones:

1. **WebSocket References**:
   - Change `using VDM.WebSocket;` → `using VDM.Net;`
   - Classes: `WebSocketManager`, `WebSocketClient`, etc.

2. **World References**:
   - Change `using VDM.World;` → `using VDM.World;` (but from VDM.Runtime assembly)
   - Classes: `WorldStatePersistence`, `TimeSystemFacade`, etc.

3. **Character References**:
   - Change `using VDM.Character;` → ensure referring to VDM.Character assembly
   - Classes: `CharacterModel`, etc.

4. **Analytics References**:
   - Change `using VDM.Analytics;` → look for actual location
   - May be in VDM.Systems or VDM.Modules

5. **Data References**:
   - Change `using VDM.Data;` → look for actual location
   - May be in VDM.Systems or VDM.Runtime

### Phase 2: Fix Assembly References
Ensure assemblies reference the assemblies containing the classes they need:

1. **VDM.Services** needs to reference **VDM.Runtime** (for WebSocket classes)
2. **VDM.Core** may need additional references

### Phase 3: Fix Method Override Issues
Some scripts are trying to override methods that don't exist in their base classes:
- `InventoryService.Awake()`: no suitable method found to override
- `CharacterService.OnDestroy()`: no suitable method found to override
- These suggest inheritance issues

## Specific Fixes Needed

### File: Assets/Scripts/Services/CharacterService.cs
```csharp
// Current problematic imports:
using VDM.Character;  // Should work if referencing VDM.Character assembly

// Missing class: CharacterModel
// Need to find where CharacterModel is defined and ensure proper reference
```

### File: Assets/Scripts/Services/SaveLoadService.cs  
```csharp
// Current problematic imports:
using VDM.Utilities;  // Need to find actual location
using VDM.Analytics;  // Need to find actual location  
using VDM.WebSocket;  // Should be: using VDM.Net;

// Missing classes: SaveGameMetadataDTO, GameSaveDataDTO
// These should be in VDM.DTOs assembly
```

### File: Assets/Scripts/Core/ErrorHandlingService.cs
```csharp
// Current problematic import:
using VDM.Runtime;  // This should work, may need assembly reference fix
```

## Implementation Steps

1. **Map actual class locations** - Find where each missing class actually exists
2. **Fix namespace imports** - Update using statements to match reality  
3. **Fix assembly references** - Ensure assemblies reference what they need
4. **Fix inheritance issues** - Remove incorrect method overrides
5. **Test compilation** - Verify all errors are resolved

## Next Actions
1. Execute automated namespace fixes
2. Update assembly definition references as needed
3. Fix inheritance/override issues
4. Validate compilation success 