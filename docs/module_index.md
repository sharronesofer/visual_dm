# Visual DM Module Index

This document provides an overview of the restructured Visual DM codebase.

## Analytics Module

Files:


- AnalyticsServiceWebSocketClient.cs
- AnalyticsService.cs
- AnalyticsManager.cs
- AnalyticsEvent.cs
- AnalyticsController.cs
- AnalyticsClient.cs
## Characters Module

Files:

- CharacterBuilderClient.cs
- CharacterModel.cs
- CharacterBuilderUI.cs

## Combat Module

Files:

- ActionPerformanceMonitor.cs
- ActionPipeline.cs
- ActionRequest.cs
- AttackActionHandler.cs
- CombatAction.cs
- CombatActionHandlerRegistry.cs
- CombatActionType.cs
- CombatDebugInterface.cs
- CombatEffect.cs
- CombatEffectPipeline.cs
- CombatEventBus.cs
- CombatLogger.cs
- CombatManager.cs
- CombatStateSnapshot.cs
- Combatant.cs
- DefendActionHandler.cs
- EffectPipeline.cs
- EffectType.cs
- EffectVisualizer.cs
- AuraEffect.cs
- CounterEffect.cs
- ICombatActionHandler.cs
- InputValidator.cs
- ObjectPool.cs
- PriorityResolver.cs
- SpecialActionHandler.cs
- TimingConfiguration.cs
- TurnQueue.cs

## Diplomacy Module

Files:

- DiplomacyManagerTests.cs

## Economy Module

Files:

- ResourceDefinition.cs

## Events Module

Files:

- EventDispatcher.cs
- EventManager.cs
- EventAndQuestManagers.cs
- IEvent.cs
- MotifEvents.cs
- PopulationEvents.cs
- SystemEvents.cs

## Factions Module

Files:

- Faction.cs
- FactionArc.cs
- FactionArcDTO.cs
- FactionArcMapper.cs
- FactionLinkManager.cs
- FactionManagerTests.cs
- FactionRelationshipManager.cs
- FactionRelationshipSystem.cs
- FactionSystem.cs

## Memory Module

Files:

- MemoryEventDispatcher.cs
- MemoryIntegrationPoints.cs
- MemoryManager.cs
- MemoryQuery.cs
- NPCMemorySystem.cs

## Motif Module

Files:

- Motif.cs
- MotifAdapter.cs
- MotifApiClient.cs
- MotifCacheManager.cs
- MotifConflictResolver.cs
- MotifDashboardUI.cs
- MotifDialogueAdapter.cs
- MotifDispatcher.cs
- MotifEnvironmentAdapter.cs
- MotifEventDispatcher.cs
- MotifEvents.cs
- MotifManager.cs
- MotifModels.cs
- MotifMusicAdapter.cs
- MotifNpcBehaviorAdapter.cs
- MotifPool.cs
- MotifRuleEngine.cs
- MotifSpatialIndex.cs
- MotifTransactionManager.cs
- MotifTriggerManager.cs
- MotifValidator.cs
- MotifVisualAdapter.cs
- OptimizedMotifAdapter.cs
- OptimizedMotifEngine.cs

## NPCs Module

Files:

- BeliefCalculator.cs
- BeliefCalculatorTests.cs
- Motif.cs
- MotifBehaviorModifier.cs
- MotifDialogueProvider.cs
- MotifManager.cs
- RumorData.cs
- RumorDataTests.cs
- RumorIndicator.cs
- RumorManager.cs
- RumorPropagationSystem.cs
- RumorPropagationSystemTests.cs
- RumorResponseHandler.cs
- RumorResponseHandlerTests.cs

## POI Module

Files:

- IPOIStateContext.cs
- POIState.cs
- POIStateAbandoned.cs
- POIStateDeclining.cs
- POIStateDungeon.cs
- POIStateIndicator.cs
- POIStateManager.cs
- POIStateNormal.cs
- POIStateRuins.cs
- POIStateTransitionRuleSet.cs
- PopulationMetricsTracker.cs

## Population Module

Files:

- NetworkPopulationManager.cs
- PopulationClient.cs
- PopulationManager.cs

## Quests Module

Files:

- ArcToQuestDebugTools.cs
- ArcToQuestMapper.cs
- CollectionQuestTemplate.cs
- CombatQuestIntegration.cs
- CombatQuestTemplate.cs
- ExplorationQuestTemplate.cs
- GlobalArc.cs
- GlobalArcManager.cs
- GlobalArcMapper.cs
- Quest.cs
- QuestArchiveManager.cs
- QuestDependencyGraph.cs
- QuestDependencyManager.cs
- QuestDesignerTools.cs
- QuestDesignerToolsTests.cs
- QuestDropManager.cs
- QuestItemDropConfig.cs
- QuestItemDropConfigEditor.cs
- QuestItemDropData.cs
- QuestManagementPanel.cs
- QuestManager.cs
- QuestManagerAPI.cs
- QuestMemorySystem.cs
- QuestMemorySystemTests.cs
- QuestProgress.cs
- QuestSerialization.cs
- QuestStage.cs
- QuestStageManager.cs
- QuestState.cs
- QuestStateMachine.cs
- QuestSystemTests.cs
- QuestTemplate.cs
- QuestTests.cs
- QuestVersionHistory.cs

## Region Module

Files:

- RegionManagerTests.cs
- RegionMapController.cs
- RegionSystem.cs
- RegionWeatherSystem.cs
- RegionWorldState.cs
- RegionalArc.cs
- RegionalArcDTO.cs
- RegionalArcMapper.cs
- WorldRegionRenderer.cs

## Religion Module

Files:

- ReligionManagerTests.cs

## Rumor Module

Files:

- BelievabilityCalculator.cs
- RumorManager.cs
- RumorPropagationManager.cs
- RumorSystem.cs

## Storage Module

Files:

- AutosaveManager.cs
- CloudStorageProvider.cs
- EncryptionService.cs
- FileSystemStorageProvider.cs
- IStorable.cs
- PersistenceManager.cs
- SQLiteStorageProvider.cs
- SerializationHelper.cs
- StorageExceptions.cs
- StorageFactory.cs
- StorageProvider.cs
- StorageUtils.cs

## TimeSystem Module

Files:

- CalendarPanel.cs
- TimeManager.cs
- CalendarSystem.cs
- TimeSpeed.cs
- TimeSystemFacade.cs
- TimeSystemWebSocketClient.cs
- WorldTimeSystem.cs

## War Module

Files:

- SerializableWarState.cs
- TensionModifierTemplate.cs
- WarEvent.cs
- WarManager.cs
- WarOutcomeTemplate.cs

## World Module

Files:

- CalendarSystem.cs
- WeatherManager.cs
- StateManagerClient.cs
- StateManager.cs
- ChunkManager.cs
- CityMapController.cs
- CollisionSystem.cs
- DynamicGrid.cs
- EconomySystem.cs
- EventNotificationSystem.cs
- EventSystem.cs
- FactionRelationshipSystem.cs
- FactionSystem.cs
- GameLoader.cs
- GridChunk.cs
- GridInterop.cs
- GridManager.cs
- GridStreamer.cs
- GridTypes.cs
- HexCellPool.cs
- HexCoordinate.cs
- HexGridUtils.cs
- HexMapCameraController.cs
- InformationDistortionSystem.cs
- KnowledgeDiffusionSystem.cs
- LocationStateSystem.cs
- MapData.cs
- MapManager.cs
- MapWebSocketClient.cs
- PathfindingSystem.cs
- PathfindingTypes.cs
- RecurringEventSystem.cs
- RegionMapController.cs
- RegionSystem.cs
- RegionWeatherSystem.cs
- RegionWorldState.cs
- SeasonSystem.cs
- TerrainTypeMapping.cs
- TimeSpeed.cs
- TimeSystemFacade.cs
- TimeSystemWebSocketClient.cs
- WeatherEffectController.cs
- WeatherSystem.cs
- WorldEventListener.cs
- WorldGenerationClient.cs
- WorldGenerator.cs
- WorldManager.cs
- WorldRegionRenderer.cs
- WorldRumorIntegration.cs
- WorldStateBatcher.cs
- WorldStateCausalityManager.cs
- WorldStateDebugTools.cs
- WorldStateManager.cs
- WorldStateObserver.cs
- WorldStatePersistence.cs
- WorldStateSystem.cs
- WorldStateTransactionManager.cs
- WorldStateWebSocketClient.cs
- WorldTimeSystem.cs


## Core Module

Files:


- SystemManager.cs
- SystemInitializer.cs
- NamespaceCompatibility.cs
- BaseSystem.cs
## Data Module

Files:


- WeatherState.cs
- Location.cs
- Item.cs
- Inventory.cs
- GameTime.cs
- GameEvent.cs
- Entity.cs
- CharacterStats.cs
- Character.cs
## Modding Module

Files:


## Networking Module

Files:


- WebSocketManager.cs
- NetworkSynchronizer.cs
- NetworkPlayer.cs
- NetworkManager.cs
- NetworkGameState.cs
- MultiplayerUI.cs
- MultiplayerManager.cs
## Testing Module

Files:


- ValidationRule.cs
- TestSuite.cs
- TestResult.cs
- TestManagerBootstrap.cs
- TestManager.cs
- TestBase.cs
- PerformanceTest.cs
- EntityDataValidationRule.cs
- EntityCreationPerformanceTest.cs
- DataConsistencyTestSuite.cs
## UI Module

Files:


- CharacterSheetView.cs
- CharacterSheetModel.cs
- CharacterSheetFactory.cs
- CharacterSheetDemo.cs
- CharacterSheetController.cs
## Consolidated Module

Files:


## Legacy Module

Files:

