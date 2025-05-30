# Module Consolidation Log
Generated on Wed May 21 08:33:03 EDT 2025

- Backed up module: NPCs
- Backed up module: Characters
- Backed up module: NPC
- Backed up module: Characters
- Backed up module: Factions
- Backed up module: Faction
- Backed up module: Quests
- Backed up module: Quest
- Backed up module: TimeSystem
- Backed up module: Time
- Backed up module: WorldGen
- Backed up module: World
## Consolidating NPCs into Characters

- Copied unique file: RumorIndicator.cs
- Copied unique file: RumorResponseHandlerTests.cs
- Copied unique file: RumorDataTests.cs
- Copied unique file: RumorPropagationSystemTests.cs
- Copied unique file: RumorManager.cs
- Copied unique file: RumorResponseHandler.cs
- Copied unique file: BeliefCalculator.cs
- Copied unique file: RumorData.cs
- Copied unique file: RumorPropagationSystem.cs
- Copied unique file: MotifBehaviorModifier.cs
- Copied unique file: MotifDialogueProvider.cs
- Copied unique file: MotifManager.cs
- Copied unique file: Motif.cs
- Copied unique file: BeliefCalculatorTests.cs

## Consolidating NPC into Characters

- Copied unique file: NPCPersonality.cs
- Copied unique file: BountyHunterNPC.cs
- Copied unique file: SimulatedCharacter.cs
- Copied unique file: CharacterManagerTests.cs
- Copied unique file: CharacterSnapshot.cs
- Copied unique file: CharacterBuildOptimizerService.cs
- Copied unique file: NPCTemplate.cs
- Copied unique file: NPCBaseTests.cs
- Copied unique file: CharacterBuildOptimizerPanel.cs
- Copied unique file: BountyHunterNPCFactory.cs
- Copied unique file: CharacterBuildOptimizerTests.cs
- Copied unique file: CharacterStats.cs
- Copied unique file: NPCBase.cs
- Copied unique file: CharacterSheetController.cs
- Copied unique file: NPCPersonalityTests.cs
- Copied unique file: WitnessNPCController.cs
- Copied unique file: NPCDecisionSystem.cs
- Copied unique file: NPCMemorySystem.cs
- Copied unique file: NPCBehaviorModifier.cs
- Copied unique file: NPCTrust.cs
- Copied unique file: NPCController.cs
- Copied unique file: CharacterSheetModel.cs
- Copied unique file: CharacterBuild.cs
- Copied unique file: CharacterBuilderUI.cs
- Copied unique file: ICharacterSystem.cs
- Copied unique file: CharacterSheetDemo.cs
- Copied unique file: NPCTraitGenerator.cs
- Copied unique file: CharacterStatsTests.cs
- Copied unique file: NPCMood.cs
- Copied unique file: NPCSpawner.cs
- Copied unique file: NPCManagementPanel.cs
- Copied unique file: CharacterBuildOptimizer.cs
- Copied unique file: CharacterSheetView.cs
- Copied unique file: INPCTemplate.cs
- Copied unique file: Character.cs
- Copied unique file: NPCGenerator.cs
- Copied unique file: CharacterSheetFactory.cs

## Consolidating Factions into Faction

- Created merged file: Factions_Faction_FactionArc.cs
  - Source class:     public class FactionArc
  - Target class:     public class FactionArc : GlobalArc
  - Consolidated namespace: namespace VisualDM.Systems.Narrative

## Consolidating Quests into Quest

- Created merged file: Quests_Quest_QuestManager.cs
  - Source class:     public class QuestManager : BaseSystem
  - Target class:     public class QuestManager : MonoBehaviour
  - Consolidated namespace: namespace VisualDM.Systems.Quest
- Created merged file: Quests_Quest_QuestSystemTests.cs
  - Source class:     public class QuestSystemTests : TestFramework
  - Target class:     public class QuestSystemTests
  - Consolidated namespace: namespace VisualDM.Tests

## Consolidating TimeSystem into Time


## Consolidating WorldGen into World

- Copied unique file: RewardGenerator.cs
- Copied unique file: TestCaseGenerator.cs
- Copied unique file: EnemyLootGenerator.cs
- Copied unique file: NPCTraitGenerator.cs
- Copied unique file: IdGenerator.cs
- Copied unique file: ContainerLootGenerator.cs
- Copied unique file: NPCGenerator.cs

