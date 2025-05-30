# Frontend Migration Plan - Task 2 Implementation

## Migration Matrix

This document provides the exact file-by-file migration plan for restructuring the Unity frontend to match the backend architecture.

## Phase 1: Foundation Systems (Data, Events, Time)

### Data System Migration
```
Source → Target
Data/CoreInterfaces.cs → Data/Models/CoreInterfaces.cs
Data/VDMDTOs.cs → Data/Models/VDMDTOs.cs  
Data/WeatherState.cs → Region/Models/WeatherState.cs (better fit)
StateValidator.cs → Data/Services/StateValidator.cs
SimpleValidation.cs → Data/Services/ValidationService.cs (merge)
```

### Events System Migration  
```
Source → Target
Events/IEvent.cs → Events/Models/IEvent.cs
Events/GameEvent.cs → Events/Models/GameEvent.cs
Events/SystemEvents.cs → Events/Models/SystemEvents.cs
Events/EventBus.cs → Events/Services/EventBus.cs
Events/EventManager.cs → Events/Services/EventManager.cs (refactor)
```

### Time System Migration
```
Source → Target  
Time/TimeUnits.cs → Time/Models/TimeUnits.cs
Time/Season.cs → Time/Models/Season.cs
Time/GameTime.cs → Time/Services/GameTime.cs
World/Time/TimeSpeed.cs → Time/Models/TimeSpeed.cs
World/CalendarSystem.cs → Time/Services/CalendarSystem.cs
```

## Phase 2: Combat System Consolidation

### Combat Files Migration
```
Source → Target
CombatManager.cs → Combat/Services/CombatManager.cs
TurnManager.cs → Combat/Services/TurnManager.cs
ActionProcessor.cs → Combat/Services/ActionProcessor.cs
TurnBasedCombatController.cs → Combat/UI/TurnBasedCombatController.cs
EntityTracker.cs → Combat/Services/EntityTracker.cs (or Character/)
```

### Combat Namespace Updates
```
OLD: VDM.Combat + VDM.CombatSystem
NEW: VDM.Combat (unified)

Files to update namespaces:
- All combat-related files
- Any files importing combat classes
```

## Phase 3: Character and Entity System

### Character/Entity Migration
```
Source → Target
Entities/CharacterStats.cs → Character/Models/CharacterStats.cs
Entities/EntityExtractor.cs → Character/Services/EntityExtractor.cs
Entities/RivalProfile.cs → Character/Models/RivalProfile.cs
Entities/NemesisProfile.cs → Character/Models/NemesisProfile.cs
Entities/BountyHunterDialogue.cs → Dialogue/Models/BountyHunterDialogue.cs
```

### NPC System Migration
```
Source → Target
Entities/NPCController.cs → NPC/UI/NPCController.cs
Entities/NPCBehaviorModifier.cs → NPC/Models/NPCBehaviorModifier.cs
Entities/NPCPersonality.cs → NPC/Models/NPCPersonality.cs
Entities/NPCMood.cs → NPC/Models/NPCMood.cs
Entities/NPCDecisionSystem.cs → NPC/Services/NPCDecisionSystem.cs (extract logic)
Entities/NPCSpawner.cs → NPC/Services/NPCSpawner.cs
```

## Phase 4: Faction and Arc Systems

### Faction System Migration  
```
Source → Target
Faction/Faction.cs → Faction/Models/Faction.cs (update namespace from VDM.Entities)
World/FactionRelationshipSystem.cs → Faction/Services/FactionRelationshipSystem.cs
```

### Arc System Creation
```
Source → Target
Faction/FactionArc.cs → Arc/Models/FactionArc.cs (update namespace)

NEW FILES TO CREATE:
Arc/Services/ArcApiService.cs
Arc/UI/ArcVisualizationComponent.cs
Arc/Models/ArcProgressionModel.cs
```

## Phase 5: Quest System Refactoring

### Quest System Split
```
Source → Target
Data/Quest.cs → Split into:
  - Quest/Models/Quest.cs (data models only)
  - Quest/Models/QuestStage.cs
  - Quest/Models/QuestObjective.cs
  - Quest/Services/QuestService.cs (business logic)
  - Quest/Services/QuestValidator.cs
  - Quest/Services/QuestApiService.cs
```

## Phase 6: World System Reorganization

### World Generation Migration
```
Source → Target
World/WorldGenerator.cs → WorldGeneration/Services/WorldGenerator.cs
World/WorldGenerationClient.cs → WorldGeneration/Services/WorldGenerationClient.cs
World/DynamicGrid.cs → WorldGeneration/Services/DynamicGrid.cs
World/GridChunk.cs → WorldGeneration/Models/GridChunk.cs
World/ChunkManager.cs → WorldGeneration/Services/ChunkManager.cs
World/GridStreamer.cs → WorldGeneration/Services/GridStreamer.cs
World/HexCellPool.cs → WorldGeneration/Services/HexCellPool.cs
World/HexCoordinate.cs → WorldGeneration/Models/HexCoordinate.cs
World/HexGridUtils.cs → WorldGeneration/Utils/HexGridUtils.cs
World/TerrainTypeMapping.cs → WorldGeneration/Models/TerrainTypeMapping.cs
```

### World State Migration
```
Source → Target
World/WorldStateManager.cs → WorldState/Services/WorldStateManager.cs
World/WorldStateBatcher.cs → WorldState/Services/WorldStateBatcher.cs
World/WorldStateObserver.cs → WorldState/Services/WorldStateObserver.cs
World/WorldStateCausalityManager.cs → WorldState/Services/WorldStateCausalityManager.cs
World/WorldStateTransactionManager.cs → WorldState/Services/WorldStateTransactionManager.cs
World/WorldStateDebugTools.cs → WorldState/UI/WorldStateDebugTools.cs
World/WorldEventListener.cs → Events/Services/WorldEventListener.cs
World/WorldRumorIntegration.cs → Rumor/Services/WorldRumorIntegration.cs
```

### Region System Migration
```
Source → Target
World/RegionMapController.cs → Region/UI/RegionMapController.cs
World/RegionWeatherSystem.cs → Region/Services/RegionWeatherSystem.cs
World/CityMapController.cs → Region/UI/CityMapController.cs
World/HexMapCameraController.cs → Region/UI/HexMapCameraController.cs
World/MapData.cs → Region/Models/MapData.cs
World/LocationStateSystem.cs → Region/Services/LocationStateSystem.cs
World/WeatherEffectController.cs → Region/UI/WeatherEffectController.cs
```

### Information Systems Migration
```
Source → Target
World/InformationDistortionSystem.cs → Memory/Services/InformationDistortionSystem.cs
World/KnowledgeDiffusionSystem.cs → Memory/Services/KnowledgeDiffusionSystem.cs
```

## Phase 7: Supporting Systems

### Population System Migration
```
Source → Target
Population/PopulationMetricsTracker.cs → Population/Services/PopulationMetricsTracker.cs
(Update namespace from VDM.POI to VDM.Population)
```

### Storage System (Already Well-Organized)
```
Current: Storage/* 
Action: Keep structure, update namespaces if needed
```

## New Service Layer Creation

### API Service Classes to Create
```
Analytics/Services/AnalyticsApiService.cs
Arc/Services/ArcApiService.cs  
AuthUser/Services/AuthApiService.cs
Character/Services/CharacterApiService.cs
Combat/Services/CombatApiService.cs
Crafting/Services/CraftingApiService.cs
Dialogue/Services/DialogueApiService.cs
Diplomacy/Services/DiplomacyApiService.cs
Economy/Services/EconomyApiService.cs
Equipment/Services/EquipmentApiService.cs
Events/Services/EventApiService.cs
Faction/Services/FactionApiService.cs
Inventory/Services/InventoryApiService.cs
LLM/Services/LLMApiService.cs
Loot/Services/LootApiService.cs
Magic/Services/MagicApiService.cs
Memory/Services/MemoryApiService.cs
Motif/Services/MotifApiService.cs
NPC/Services/NPCApiService.cs
POI/Services/POIApiService.cs
Population/Services/PopulationApiService.cs
Quest/Services/QuestApiService.cs
Region/Services/RegionApiService.cs
Religion/Services/ReligionApiService.cs
Rumor/Services/RumorApiService.cs
Time/Services/TimeApiService.cs
WorldGeneration/Services/WorldGenerationApiService.cs
WorldState/Services/WorldStateApiService.cs
```

### Base Service Classes to Create
```
Core/Services/BaseApiService.cs
Core/Services/IApiService.cs
Core/Services/ServiceLocator.cs
Core/Services/ConfigurationManager.cs
Core/Integration/UnityEventBridge.cs
Core/Integration/ServiceManager.cs
```

## Directory Structure Creation

### New Directories to Create
```
Analytics/Models/
Analytics/Services/
Analytics/UI/
Analytics/Integration/

Arc/Models/
Arc/Services/
Arc/UI/
Arc/Integration/

AuthUser/Models/
AuthUser/Services/
AuthUser/UI/
AuthUser/Integration/

Crafting/Models/
Crafting/Services/
Crafting/UI/
Crafting/Integration/

Equipment/Models/
Equipment/Services/
Equipment/UI/
Equipment/Integration/

LLM/Models/
LLM/Services/
LLM/UI/
LLM/Integration/

Loot/Models/
Loot/Services/
Loot/UI/
Loot/Integration/

Magic/Models/
Magic/Services/
Magic/UI/
Magic/Integration/

[Continue for all missing systems...]
```

## Namespace Update Strategy

### Global Namespace Changes
```
OLD NAMESPACES → NEW NAMESPACES

VDM.CombatSystem → VDM.Combat
VDM.Systems → VDM.Events (for EventManager)
VDM.Systems.Events → VDM.Events.Models  
VDM.Systems.EventSystem → VDM.Events.Services
VDM.Systems.Narrative → VDM.Arc
VDM.Entities → VDM.Character (for character-related)
VDM.Entities → VDM.NPC (for NPC-related)
VDM.POI → VDM.Population (for PopulationMetricsTracker)
VDM.World.Time → VDM.Time
VDM.Data → Appropriate system namespaces
```

### Standard Namespace Pattern
```
VDM.{SystemName}.Models
VDM.{SystemName}.Services  
VDM.{SystemName}.UI
VDM.{SystemName}.Integration
```

## Migration Execution Order

### Week 1: Foundation
1. Create new directory structure
2. Move Data system files
3. Refactor Events system
4. Consolidate Time system
5. Update related imports

### Week 2: Core Systems  
1. Consolidate Combat system
2. Reorganize Character/Entity files
3. Create Faction service layer
4. Implement base service classes

### Week 3: Content Systems
1. Split Quest system  
2. Reorganize NPC system
3. Implement Arc system frontend
4. Create World system structure

### Week 4: Finalization
1. Move World subsystems
2. Create missing system structures
3. Implement service layer
4. Update all namespace references
5. Comprehensive testing

## Validation Checklist

### After Each Migration Phase:
- [ ] Zero compilation errors
- [ ] All namespace references updated  
- [ ] Unity can find all MonoBehaviour classes
- [ ] No circular dependencies
- [ ] Service layer abstraction working
- [ ] API integration patterns consistent

### Final Validation:
- [ ] All 30+ systems have frontend structure
- [ ] Clean separation of UI and business logic
- [ ] Consistent naming and organization
- [ ] Backend API integration ready
- [ ] Documentation updated
- [ ] Testing framework in place

## Risk Mitigation

### Backup Strategy:
1. Create Git branch for migration
2. Commit after each major phase
3. Keep original files until validation complete

### Rollback Plan:
1. Automated script to restore original structure
2. Namespace rollback automation
3. Import reference restoration

### Testing Strategy:
1. Compile test after each file move
2. Integration testing for API services
3. UI functionality validation
4. Performance benchmarking 