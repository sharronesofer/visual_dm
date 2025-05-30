# Visual DM Codebase Consolidation Plan

## Objectives
1. Consolidate duplicated code in the VDM codebase
2. Establish a clear "source of truth" for each system
3. Reorganize the asset directory structure for clarity
4. Remove circular dependencies between modules
5. Improve performance and maintainability

## Directory Structure Changes

### Current Structure Issues
- Duplicate directories: `/VDM/Assets/Scripts/VisualDM/` and `/VDM/Assets/VisualDM/`
- Nested folders causing confusion in imports
- Parallel implementations in different namespaces

### Target Structure
```
/VDM/Assets/
├── Scripts/
│   ├── Core/           # Core systems and managers
│   ├── Data/           # Data models and structures
│   ├── Systems/        # Game systems (entity, time, events)
│   ├── UI/             # User interface components 
│   ├── Utilities/      # Shared utility functions
│   ├── World/          # World generation and management
│   └── Tests/          # Unit tests
├── Prefabs/            # Game prefabs
├── Resources/          # Game resources
├── Scenes/             # Unity scenes
└── Editor/             # Editor scripts
```

## Implementation Plan

### Phase 1: Analysis and Preparation
1. Create backup of entire project
2. Establish test cases to ensure functionality is preserved
3. Document all interconnections between duplicated systems

### Phase 2: Consolidate Core Systems
For each duplicated system:

#### 1. ModDataManager Consolidation
- Source of truth: `/VDM/Assets/VisualDM/Consolidated/ModDataManager.cs`
- Adjust namespace to `VisualDM.Systems`
- Merge in unique functionality from:
  - `/VDM/Assets/Scripts/VisualDM/Systems/ModDataManager.cs`
  - `/VDM/Assets/Scripts/VisualDM/Data/ModDataManager.cs`
  - `/VDM/Assets/Scripts/Data/ModDataManager.cs`
  - `/VDM/Assets/Scripts/Core/GameManager.cs` (nested class)

#### 2. GameManager Consolidation
- Source of truth: `/VDM/Assets/VisualDM/Consolidated/GameManager.cs`
- Adjust namespace to `VisualDM.Core`
- Merge in unique functionality from:
  - `/VDM/Assets/Scripts/VisualDM/Systems/GameManager.cs`
  - `/VDM/Assets/Scripts/Core/GameManager.cs`

#### 3. EntityManager Consolidation
- Source of truth: `/VDM/Assets/Scripts/VisualDM/Systems/EntityManager.cs`
- Adjust namespace to `VisualDM.Systems`
- Incorporate reference implementation from `/VDM/Assets/Scripts/VisualDM/Examples/EntityManagerExample.cs`

#### 4. EventManager Consolidation
- Source of truth: `/VDM/Assets/VisualDM/Systems/EventManager.cs`
- Adjust namespace to `VisualDM.Systems`

#### 5. TimeManager Consolidation
- Source of truth: `/VDM/Assets/VisualDM/Systems/TimeManager.cs`
- Adjust namespace to `VisualDM.Systems`

#### 6. WorldGenerator Consolidation
- Source of truth: `/VDM/Assets/Scripts/World/WorldGenerator.cs` (static class)
- Integrate with `/VDM/Assets/Scripts/World/WorldGenerationClient.cs` (MonoBehaviour)
- Adjust namespace to `VisualDM.World`

### Phase 3: Directory Reorganization
1. Create new directory structure as outlined
2. Move consolidated files to appropriate directories
3. Update references in all scripts
4. Remove empty directories

### Phase 4: Python Backend Consolidation
For each duplicated backend system:

#### 1. EventDispatcher Consolidation
- Source of truth: `/backend/app/core/events/event_dispatcher.py`
- Remove duplicates from:
  - `/backend/core/events/event_dispatcher.py`
  - `/backend/src/core/events/event_dispatcher.py`
  - `/backend/consolidated/core/events/event_dispatcher.py`
  - `/backend/archive/src_core/events/event_dispatcher.py`

#### 2. WorldStateManager Consolidation
- Source of truth: `/backend/app/core/world_state/world_state_manager.py`
- Merge unique functionality from duplicates

#### 3. RumorSystem Consolidation
- Source of truth: `/backend/app/core/rumors/rumor_system.py`
- Merge unique functionality from duplicates

#### 4. TimeManager Consolidation
- Source of truth: `/backend/app/core/time_system/time_manager.py`
- Merge unique functionality from duplicates

### Phase 5: Testing and Verification
1. Run unit tests for each consolidated module
2. Test asset loading after reorganization
3. Measure performance improvements
4. Fix any issues discovered during testing

### Phase 6: Documentation
1. Update code comments to reflect new organization
2. Create documentation about consolidated systems
3. Document dependency flow between modules
4. Provide guidelines for extending functionality without duplication

## Implementation Schedule

| Phase | Timeline | Status |
|-------|----------|--------|
| 1. Analysis and Preparation | 2 days | Not Started |
| 2. Consolidate Core Systems | 5 days | Not Started |
| 3. Directory Reorganization | 3 days | Not Started |
| 4. Python Backend Consolidation | 4 days | Not Started |
| 5. Testing and Verification | 3 days | Not Started |
| 6. Documentation | 2 days | Not Started |

## Testing Strategy
- Unit tests for each consolidated module
- Integration tests for systems that interact
- Performance benchmarks (before/after)
- Asset reference verification
- Complete test suite run before and after changes 