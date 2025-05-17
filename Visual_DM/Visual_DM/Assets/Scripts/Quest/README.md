# Quest System (Visual_DM)

## Overview
This directory contains the core quest system for Visual DM, designed for runtime-generated Unity 2D games. The system is modular, extensible, and supports dynamic quest generation, multi-stage progression, requirements, rewards, hidden objectives, world state impact, and serialization.

## Class Responsibilities

- **Quest**: Main quest data structure. Holds id, title, description, stages, requirements, rewards, world impact, status, difficulty, and quest-level hidden objectives.
- **QuestStage**: Represents a stage in a quest, with objectives, completion conditions, branching, status, and stage-level hidden objectives.
- **Objective**: Base class for quest objectives (id, description).
- **HiddenObjective**: Inherits from Objective. Represents a hidden quest objective, with discovery conditions, isDiscovered flag, and bonus reward.
- **QuestRequirement**: Encapsulates prerequisites for a quest or stage (other quests, player stats, world state).
- **QuestReward**: Defines rewards (items, reputation, experience, special unlocks).
- **QuestTemplate**: Blueprint for generating quests with parameterization and difficulty scaling.
- **QuestManager**: Singleton runtime manager for registering, finding, and listing quests.
- **QuestSerialization**: Static helper for serializing/deserializing quests and templates to/from JSON.
- **QuestStageManager**: Manages active quest stages, handles transitions, evaluates completion, and triggers events.
- **ConditionEvaluator**: Static system for evaluating quest stage completion conditions, supporting custom logic.
- **QuestDependencyManager**: Tracks quest prerequisites, chains, and mutual exclusivity. Handles quest availability and unlocking.
- **RewardGenerator**: Generates rewards for quests based on difficulty, type, and player level.
- **WorldStateManager**: Singleton for tracking and updating global world state variables, with observer/event pattern.
- **FactionRelationshipSystem**: Singleton for tracking player reputation with factions, including thresholds and event-driven updates.
- **LocationStateSystem**: Singleton for tracking and updating the state of game locations, with enumerated states and event-driven updates.

## Class Diagram

```
Quest
 ├─ List<QuestStage> stages
 ├─ List<QuestRequirement> requirements
 ├─ List<QuestReward> rewards
 ├─ List<HiddenObjective> hiddenObjectives
 └─ WorldImpact worldImpact

QuestStage
 ├─ List<string> objectives
 ├─ List<string> completionConditions
 ├─ List<HiddenObjective> hiddenObjectives
 └─ List<string> nextStageIds

Objective
 ├─ string id
 └─ string description

HiddenObjective : Objective
 ├─ bool isDiscovered
 ├─ List<string> discoveryConditions
 └─ QuestReward bonusReward

QuestRequirement
 ├─ List<string> prerequisiteQuestIds
 ├─ Dictionary<string, float> requiredPlayerStats
 └─ List<string> requiredWorldStates

QuestReward
 ├─ List<string> itemIds
 ├─ Dictionary<string, float> reputationRewards
 ├─ float experience
 └─ List<string> specialRewards

QuestTemplate
 ├─ string templateId
 ├─ string baseTitle
 ├─ string baseDescription
 ├─ int baseDifficulty
 └─ Dictionary<string, object> parameters

QuestStageManager
 ├─ Dictionary<string, QuestStage> activeStages
 ├─ event OnStageCompleted
 ├─ event OnStageActivated

ConditionEvaluator
 ├─ RegisterEvaluator(key, delegate)
 ├─ Evaluate(condition)

QuestDependencyManager
 ├─ RegisterPrerequisites(questId, prereqIds)
 ├─ RegisterQuestChain(questId, nextQuestIds)
 ├─ RegisterMutualExclusives(questId, exclusiveIds)
 ├─ IsQuestAvailable(questId, ...)
 ├─ UnlockQuestsInChain(completedQuestId)
 └─ LockIncompatibleQuests(acceptedQuestId)

RewardGenerator
 ├─ GenerateReward(difficulty, questType, playerLevel)

WorldStateManager
 ├─ SetState(key, value)
 ├─ GetState(key)
 ├─ OnStateChanged (event)

FactionRelationshipSystem
 ├─ SetReputation(faction, value)
 ├─ ModifyReputation(faction, delta)
 ├─ GetReputation(faction)
 ├─ GetStanding(faction)
 ├─ OnReputationChanged (event)

LocationStateSystem
 ├─ SetState(locationId, state)
 ├─ GetState(locationId)
 ├─ OnLocationStateChanged (event)
```

## Usage Examples

### Generating a Quest from a Template
```csharp
var template = new QuestTemplate
{
    TemplateId = "fetch-001",
    BaseTitle = "Fetch the Artifact",
    BaseDescription = "Retrieve the lost artifact from the ruins.",
    BaseDifficulty = 2
};
var quest = template.GenerateQuest(new Dictionary<string, object> {
    { "title", "Fetch the Ancient Sword" },
    { "difficulty", 3 }
});
```

### Serializing and Deserializing a Quest
```csharp
string json = QuestSerialization.SerializeQuest(quest);
Quest loadedQuest = QuestSerialization.DeserializeQuest(json);
```

### Registering and Evaluating Completion Conditions
```csharp
// Register a custom evaluator for an inventory check
ConditionEvaluator.RegisterEvaluator("hasItem", itemId => Inventory.HasItem(itemId));

// Evaluate a condition string (e.g., "hasItem:sword01")
bool isMet = ConditionEvaluator.Evaluate("hasItem:sword01");
```

### Using QuestStageManager for Progression
```csharp
var stageManager = new QuestStageManager();
stageManager.OnStageCompleted += stage => Debug.Log($"Stage {stage.Id} completed!");
stageManager.ActivateStage(stage);
stageManager.CheckAndCompleteStage(stage, ConditionEvaluator.Evaluate);
```

### Registering and Checking Quest Dependencies
```csharp
var depManager = new QuestDependencyManager();
depManager.RegisterPrerequisites("quest2", new List<string> { "quest1" });
depManager.RegisterQuestChain("quest1", new List<string> { "quest2" });
depManager.RegisterMutualExclusives("quest2", new List<string> { "quest3" });

// Check if quest2 is available (assuming isQuestCompleted is a delegate)
bool available = depManager.IsQuestAvailable("quest2", isQuestCompleted);

// Unlock next quests after quest1 is completed
List<string> unlocked = depManager.UnlockQuestsInChain("quest1");

// Lock incompatible quests when quest2 is accepted
List<string> locked = depManager.LockIncompatibleQuests("quest2");
```

### Using Hidden Objectives
```csharp
// At the quest level
quest.RevealHiddenObjectives(ConditionEvaluator.Evaluate);

// At the stage level
foreach (var stage in quest.Stages)
{
    stage.RevealHiddenObjectives(ConditionEvaluator.Evaluate);
}

// Check if a hidden objective is discovered
foreach (var hidden in quest.HiddenObjectives)
{
    if (hidden.IsDiscovered)
    {
        // Grant bonus reward
        GrantReward(hidden.BonusReward);
    }
}
```

### World State Impact from Quest Outcomes
```csharp
// Update world state when a quest is completed
WorldStateManager.Instance.SetState("dragonDefeated", true);

// Listen for world state changes
WorldStateManager.Instance.OnStateChanged.AddListener((key, value) =>
{
    Debug.Log($"World state changed: {key} = {value}");
});

// Update faction reputation from quest reward
FactionRelationshipSystem.Instance.ModifyReputation("FactionA", 10f);

// Listen for reputation changes
FactionRelationshipSystem.Instance.OnReputationChanged.AddListener((faction, value) =>
{
    Debug.Log($"Reputation with {faction} is now {value}");
});

// Update location state after quest
LocationStateSystem.Instance.SetState("village01", LocationStateSystem.LocationState.Destroyed);

// Listen for location state changes
LocationStateSystem.Instance.OnLocationStateChanged.AddListener((locationId, state) =>
{
    Debug.Log($"Location {locationId} state changed to {state}");
});
```

## Event-Driven Quest Progression
- QuestStageManager uses C# events to notify listeners when stages are activated or completed.
- Integrate with gameplay systems by subscribing to these events for UI updates, rewards, or world changes.

## Event-Driven World State Impact
- WorldStateManager, FactionRelationshipSystem, and LocationStateSystem use events to notify systems of changes.
- Quest completion or objective fulfillment can trigger world state, faction, or location changes.
- Subscribe to these events for dynamic world updates, UI feedback, or gameplay consequences.

## Dependency-Driven Quest Unlocking
- QuestDependencyManager enables dynamic quest availability based on player progress, world state, and exclusivity rules.
- Use IsQuestAvailable to determine if a quest can be offered to the player.
- Use UnlockQuestsInChain to automatically unlock new quests as chains progress.
- Use LockIncompatibleQuests to enforce mutual exclusivity between quest lines.

## Hidden Objectives and Bonus Rewards
- Use HiddenObjective to add secret content to quests and stages.
- Discovery conditions can be based on inventory, actions, proximity, or knowledge.
- When a hidden objective is discovered, grant its bonus reward to the player.
- Use RevealHiddenObjectives to check and reveal hidden objectives at runtime.

## Extension Points
- Add new quest types by extending QuestTemplate and GenerateQuest logic.
- Add new reward/requirement types by extending QuestReward/QuestRequirement.
- Integrate with other systems (NPCs, world state) via WorldImpact and QuestManager.
- Add new condition types by registering custom evaluators with ConditionEvaluator.
- Extend QuestDependencyManager for more complex dependency logic as needed.
- Extend HiddenObjective for more advanced discovery mechanics or reward types.
- Extend WorldStateManager, FactionRelationshipSystem, and LocationStateSystem for additional world impact features.

## Best Practices
- Use properties for encapsulation.
- Favor composition over inheritance.
- Document all public APIs.
- Keep all scripts in this directory for quest-related logic.

# Arc-to-Quest Generation System Architecture

## Overview
This system transforms narrative arcs (Global, Regional, Faction, Character) into playable quests and missions. It is designed for extensibility, narrative coherence, and integration with existing quest and arc systems.

## Core Components

### 1. ArcQuestGenerationContext
- Encapsulates all data needed for quest generation from an arc (arc reference, stage, type, player/world state, motif, etc.).

### 2. IArcToQuestMapper
- Interface for mapping arcs to quests.
- `List<Quest> GenerateQuests(ArcQuestGenerationContext context);`
- Implementations can specialize for different arc types or narrative motifs.

### 3. ArcQuestMappingRule
- Abstract base class for rules that determine how arc objectives/stages are translated into quest objectives/types.
- Supports extensibility for custom mapping logic.

## Extension Points
- Add new `IArcToQuestMapper` implementations for custom arc types or motifs.
- Add new `ArcQuestMappingRule` subclasses for new quest types or mapping strategies.
- Integrate with dependency management, motif system, and quest lifecycle management via context and hooks.

## Integration
- Designed to work with QuestTemplate, QuestManager, and arc classes in VisualDM.Narrative.
- Supports bidirectional updates between arc progression and quest completion.

## Example Usage
```csharp
var context = new ArcQuestGenerationContext {
    Arc = myGlobalArc,
    ArcStage = myGlobalArc.Stages[0],
    ArcType = "Global",
    PlayerState = playerStateDict,
    WorldState = worldStateDict,
    Motif = "Rebellion"
};
IArcToQuestMapper mapper = new GlobalArcToQuestMapper();
List<Quest> quests = mapper.GenerateQuests(context);
```

## Next Steps
- Implement concrete mappers and mapping rules for each arc type.
- Integrate with quest lifecycle and persistence systems.
- Provide designer configuration interfaces for tuning quest generation.

## Developer Tools and Testing Utilities

### ArcToQuestDebugTools
- Static utility for visualizing and debugging arc-to-quest relationships.
- Methods:
  - `PrintArcToQuestMapping(GlobalArc arc, List<Quest> quests)`: Logs mapping from arcs to generated quests and their stages.
  - `PrintQuestChains(QuestDependencyManager depManager, List<Quest> quests)`: Logs quest chains and dependencies (requires public accessors in depManager).
  - `ValidateQuestGeneration(GlobalArc arc, List<Quest> quests)`: Validates that generated quests match arc stages (basic check).

## Designer Configuration and Usage Examples

### Tuning Quest Generation Parameters
- Designers can create or edit `QuestTemplate` assets to define base titles, descriptions, objectives, and parameters for each quest type and arc type.
- Use the `ArcType` and `QuestType` fields to specialize templates for Global, Regional, Faction, or Character arcs, and for quest types like Collection, Elimination, Exploration, Dialogue, etc.
- Parameterize objectives using the `ObjectiveTemplates` list and provide dynamic content via the `Parameters` dictionary.

### Structuring Arcs for Optimal Quest Generation
- Ensure each arc (GlobalArc, RegionalArc, etc.) has well-defined stages with unique names and descriptions.
- Use motif themes and metadata to influence quest generation for narrative coherence.
- Integrate with the MotifSystem by specifying motif themes in arc metadata or quest generation context.

### Example: Creating a Motif-Aware Quest Template
```csharp
var template = new QuestTemplate
{
    ArcType = "Global",
    QuestType = "Story",
    BaseTitle = "Defend the City",
    BaseDescription = "Protect the city from invading forces.",
    ObjectiveTemplates = new List<string> { "Defeat all invaders", "Secure the city gates" },
    Parameters = new Dictionary<string, object> { { "motif", "Defense" } }
};
```

### Example: Generating Quests from an Arc with Motif Integration
```csharp
var motifPool = ... // Get MotifPool instance
var motif = MotifIntegrationUtility.GetMotifForTheme(motifPool, "Defense");
var context = new ArcQuestGenerationContext {
    Arc = myGlobalArc,
    ArcStage = myGlobalArc.Stages[0],
    ArcType = "Global",
    Motif = "Defense",
    MotifData = motif
};
IArcToQuestMapper mapper = new GlobalArcToQuestMapper();
List<Quest> quests = mapper.GenerateQuests(context);
ArcToQuestDebugTools.PrintArcToQuestMapping(myGlobalArc, quests);
```

### Best Practices
- Document all new templates and mapping rules for future maintainers.
- Use the debug tools to validate quest generation before playtesting.
- Regularly update documentation as new arc types, quest types, or motif integrations are added. 