# Quest and Arc System Usage Examples

This document provides examples and usage patterns for the Quest and Arc Generation Framework.

## Basic Setup

```typescript
import { 
  questManager, 
  arcManager, 
  questGenerator,
  QuestStatus,
  ObjectiveType,
  ObjectiveStatus
} from '../';

// The system uses singleton instances that are already initialized
// No additional setup required
```

## Creating and Managing Quests

### Creating a Quest Manually

```typescript
import { questManager, QuestStatus, ObjectiveType, ObjectiveStatus } from '../';
import { UUID } from '../../../core/types';

// Create a new quest
const quest = questManager.createQuest({
  title: 'Retrieve the Ancient Artifact',
  description: 'Find and retrieve the ancient artifact from the forgotten temple.',
  status: QuestStatus.INACTIVE, // Start as inactive
  objectives: [], // We'll add objectives separately
  rewards: [
    {
      type: 'experience',
      amount: 1000
    },
    {
      type: 'currency',
      amount: 500
    }
  ],
  level: 5,
  isRepeatable: false,
  tags: ['adventure', 'exploration'],
  isHidden: false,
  isMandatory: false,
  hasTimeSensitiveObjectives: false
});

// Add objectives to the quest
const exploreObjective = questManager.addObjective(quest.id, {
  title: 'Find the Forgotten Temple',
  description: 'Locate and enter the forgotten temple in the eastern mountains.',
  type: ObjectiveType.DISCOVER,
  status: ObjectiveStatus.HIDDEN,
  isOptional: false,
  targets: [
    {
      targetId: 'temple-location-123' as UUID,
      targetType: 'location',
      targetName: 'Forgotten Temple',
      count: 1,
      current: 0
    }
  ],
  order: 0,
  requiresAllTargets: true
});

const retrieveObjective = questManager.addObjective(quest.id, {
  title: 'Retrieve the Artifact',
  description: 'Find the ancient artifact and take it from its pedestal.',
  type: ObjectiveType.COLLECT,
  status: ObjectiveStatus.HIDDEN,
  isOptional: false,
  targets: [
    {
      targetId: 'ancient-artifact-456' as UUID,
      targetType: 'item',
      targetName: 'Ancient Artifact',
      count: 1,
      current: 0
    }
  ],
  order: 1,
  requiresAllTargets: true,
  dependsOn: [exploreObjective!.id] // This objective depends on the first one
});

const returnObjective = questManager.addObjective(quest.id, {
  title: 'Return to the Village Elder',
  description: 'Bring the artifact back to the village elder.',
  type: ObjectiveType.DELIVER,
  status: ObjectiveStatus.HIDDEN,
  isOptional: false,
  targets: [
    {
      targetId: 'village-elder-789' as UUID,
      targetType: 'npc',
      targetName: 'Village Elder',
      count: 1,
      current: 0
    }
  ],
  order: 2,
  requiresAllTargets: true,
  dependsOn: [retrieveObjective!.id] // This objective depends on the second one
});
```

### Creating a Quest Using Templates

```typescript
import { questGenerator } from '../';

// Generate a fetch quest using the built-in template
const fetchQuest = questGenerator.generateQuestFromTemplate(
  'fetch',
  {
    item: 'rare herbs',
    location: 'enchanted grove',
    npc: 'local healer',
    count: '5'
  }
);

// Generate a combat quest using the built-in template
const combatQuest = questGenerator.generateQuestFromTemplate(
  'combat',
  {
    enemy: 'forest trolls',
    location: 'western woods',
    npc: 'village guard captain',
    count: '10'
  }
);
```

### Managing Quest State

```typescript
import { questManager, QuestStatus } from '../';

// Make a quest available to the player
questManager.makeQuestAvailable(quest.id);

// Player accepts the quest
questManager.activateQuest(quest.id);

// Update objective progress (e.g., when player finds the temple)
questManager.updateObjectiveProgress(
  quest.id,
  exploreObjective!.id,
  'temple-location-123' as UUID,
  1 // Increment by 1
);

// Check if this would complete the objective
// If so, the system will automatically reveal any dependent objectives

// Later, update progress for the second objective
questManager.updateObjectiveProgress(
  quest.id,
  retrieveObjective!.id,
  'ancient-artifact-456' as UUID,
  1
);

// Finally, update the last objective
questManager.updateObjectiveProgress(
  quest.id,
  returnObjective!.id,
  'village-elder-789' as UUID,
  1
);

// The quest will automatically be marked as completed
// And rewards will be granted

// If needed, you can manually change quest status
questManager.abandonQuest(quest.id); // Player abandons quest
questManager.failQuest(quest.id);    // Quest fails due to some condition
```

### Quest Queries

```typescript
import { questManager, QuestStatus } from '../';

// Get all quests
const allQuests = questManager.getAllQuests();

// Get quests by status
const activeQuests = questManager.getQuestsByStatus(QuestStatus.ACTIVE);
const completedQuests = questManager.getQuestsByStatus(QuestStatus.COMPLETED);

// Get quests by tags
const explorationQuests = questManager.getQuestsByTags(['exploration']);

// Get an individual quest
const quest = questManager.getQuest(questId);
```

## Creating and Managing Narrative Arcs

### Creating a Narrative Arc Manually

```typescript
import { arcManager, QuestStatus, ArcCompletionRequirementType } from '../';

// Create a new narrative arc
const arc = arcManager.createArc({
  title: 'The Ancient Threat',
  description: 'An ancient evil has awakened and threatens the land.',
  quests: [fetchQuest.id, combatQuest.id], // IDs of quests in this arc
  status: QuestStatus.INACTIVE,
  isActive: false,
  branchingPoints: [], // We'll add branching points later
  completionRequirements: {
    type: ArcCompletionRequirementType.ALL_QUESTS
  },
  isMainStory: true,
  tags: ['main', 'story']
});
```

### Creating a Narrative Arc with Quest Chain

```typescript
import { questGenerator } from '../';

// Generate a quest chain and arc
const storyArc = questGenerator.generateQuestChain(
  ['fetch', 'combat', 'fetch', 'combat'], // Template sequence
  'Journey to the North',
  'A perilous journey to the northern mountains to stop an impending threat.',
  true, // Is main story
  3     // Base difficulty level
);
```

### Managing Arc State

```typescript
import { arcManager } from '../';

// Activate an arc
arcManager.activateArc(arc.id);

// Add a quest to an arc
arcManager.addQuestToArc(arc.id, newQuestId);

// Remove a quest from an arc
arcManager.removeQuestFromArc(arc.id, questId);
```

### Adding Branching Points to an Arc

```typescript
import { arcManager, BranchingConditionType } from '../';

// Create branches
const peacefulBranch = {
  id: 'peaceful-branch-id' as UUID,
  name: 'Peaceful Resolution',
  description: 'Resolve the conflict through diplomacy',
  questIds: [diplomaticQuest1.id, diplomaticQuest2.id],
  isDefault: false,
  leadsToArcId: peacefulArc.id
};

const combatBranch = {
  id: 'combat-branch-id' as UUID,
  name: 'Combat Resolution',
  description: 'Resolve the conflict through force',
  questIds: [combatQuest1.id, combatQuest2.id],
  isDefault: true
};

// Add a branching point
const branchingPoint = arcManager.addBranchingPoint(
  arc.id,
  triggerQuestId, // Quest that triggers the branch
  [peacefulBranch, combatBranch],
  combatBranch.id, // Default branch
  [
    {
      type: BranchingConditionType.PLAYER_CHOICE,
      parameter: 'diplomatic_approach',
      operator: 'eq',
      value: true,
      branchId: peacefulBranch.id
    }
  ]
);

// Later, select a branch based on player choices
arcManager.selectBranch(arc.id, branchingPoint.id, peacefulBranch.id);
```

### Arc Queries

```typescript
import { arcManager } from '../';

// Get all arcs
const allArcs = arcManager.getAllArcs();

// Get active arcs
const activeArcs = arcManager.getActiveArcs();

// Get main story arcs
const mainStoryArcs = arcManager.getMainStoryArcs();

// Get arcs by tags
const sideArcs = arcManager.getArcsByTags(['side']);

// Get an individual arc
const arc = arcManager.getArc(arcId);
```

## Event Handling

```typescript
import { questManager, arcManager, QuestEvents, ArcEvents } from '../';

// Listen for quest events
questManager.on(QuestEvents.QUEST_COMPLETED, (quest) => {
  console.log(`Quest completed: ${quest.title}`);
  // Update UI, grant achievements, etc.
});

questManager.on(QuestEvents.OBJECTIVE_COMPLETED, (questId, objectiveId) => {
  console.log(`Objective completed in quest ${questId}`);
  // Play sound, show notification, etc.
});

// Listen for arc events
arcManager.on(ArcEvents.ARC_COMPLETED, (arc) => {
  console.log(`Story arc completed: ${arc.title}`);
  // Unlock achievements, trigger cutscene, etc.
});

arcManager.on(ArcEvents.BRANCH_SELECTED, (arc, branchingPoint, branch) => {
  console.log(`Branch selected in arc ${arc.title}: ${branch.name}`);
  // Update world state, character relationships, etc.
});
```

## Integration with Other Systems

### Timed Updates

```typescript
// In your game loop or time system:
function updateTimers(deltaTime: number) {
  // Update time-limited quests
  questManager.updateTimeLimitedQuests();
}
```

### Inventory System Integration

```typescript
// When player picks up an item
function onItemCollected(itemId: UUID, count: number) {
  // Find all active collection objectives for this item
  const activeQuests = questManager.getQuestsByStatus(QuestStatus.ACTIVE);
  
  for (const quest of activeQuests) {
    for (const objective of quest.objectives) {
      if (objective.type === ObjectiveType.COLLECT && 
          objective.status === ObjectiveStatus.VISIBLE) {
        for (const target of objective.targets) {
          if (target.targetId === itemId) {
            // Update the objective progress
            questManager.updateObjectiveProgress(
              quest.id,
              objective.id,
              itemId,
              count
            );
          }
        }
      }
    }
  }
} 