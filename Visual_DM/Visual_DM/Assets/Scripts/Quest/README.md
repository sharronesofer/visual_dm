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