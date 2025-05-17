# Data Structures and API Methods for Progression Checks

**Document ID:** PROG-API-001
**Last Updated:** 2025-05-16

---

## 1. Data Structure Definitions

### 1.1 CharacterProgression
```typescript
interface CharacterProgression {
  characterId: string;
  skills: Map<SkillType, number>; // Skill type to level mapping
  reputation: Map<FactionId, number>; // Faction to reputation level
  achievements: Set<AchievementId>; // Completed achievements
  questProgress: Map<QuestId, QuestState>; // Quest progression tracking
  specialFlags: Set<string>; // Special condition flags
  lastUpdated: Timestamp; // For caching purposes
}
```

### 1.2 InteractionRequirement
```typescript
interface InteractionRequirement {
  id: string;
  requirementType: 'SKILL' | 'REPUTATION' | 'ACHIEVEMENT' | 'QUEST' | 'FLAG' | 'COMPOSITE';
  target?: string; // SkillType, FactionId, etc. depending on type
  threshold?: number; // Minimum value required (for skills, reputation)
  state?: string; // For quest states
  operator?: 'AND' | 'OR' | 'NOT'; // For composite requirements
  children?: InteractionRequirement[]; // For composite requirements
}
```

### 1.3 InteractionDefinition
```typescript
interface InteractionDefinition {
  id: string;
  poiId?: string; // Link to POI system (Task #472)
  buildingId?: string; // Link to Building system (Task #473)
  requirements: InteractionRequirement[];
  fallbackInteraction?: string; // Alternative interaction if requirements not met
  uiNotificationId?: string; // Link to UI notification from subtask 474.3
}
```

---

## 2. API Methods

### 2.1 Core Methods
```typescript
// Main method to check if an interaction is available
function checkInteractionAvailability(
  characterId: string, 
  interactionId: string
): Promise<{
  available: boolean;
  missingRequirements?: InteractionRequirement[];
  fallbackInteraction?: string;
  uiNotification?: string;
}>

// Batch check multiple interactions for a character
function batchCheckInteractions(
  characterId: string,
  interactionIds: string[]
): Promise<Map<string, {available: boolean, fallbackInteraction?: string}>>

// Get all available interactions for a character at a POI
function getAvailableInteractionsAtPOI(
  characterId: string,
  poiId: string
): Promise<InteractionDefinition[]>

// Get all available interactions for a character with a building
function getAvailableInteractionsWithBuilding(
  characterId: string,
  buildingId: string
): Promise<InteractionDefinition[]>
```

### 2.2 Helper Methods
```typescript
// Evaluate a single requirement
function evaluateRequirement(
  characterProgression: CharacterProgression,
  requirement: InteractionRequirement
): boolean

// Get character progression (with caching)
function getCharacterProgression(
  characterId: string
): Promise<CharacterProgression>
```

---

## 3. Pseudocode for Key Functions

```
function checkInteractionAvailability(characterId, interactionId):
  // Get data with potential caching
  let interaction = await InteractionRepository.findById(interactionId)
  let progression = await getCharacterProgression(characterId)
  
  // Track missing requirements for UI feedback
  let missingRequirements = []
  
  // Check each requirement
  let available = true
  for each requirement in interaction.requirements:
    if not evaluateRequirement(progression, requirement):
      available = false
      missingRequirements.push(requirement)
  
  return {
    available: available,
    missingRequirements: available ? null : missingRequirements,
    fallbackInteraction: available ? null : interaction.fallbackInteraction,
    uiNotification: available ? null : interaction.uiNotificationId
  }

function evaluateRequirement(progression, requirement):
  switch requirement.requirementType:
    case 'SKILL':
      return progression.skills.get(requirement.target) >= requirement.threshold
    case 'REPUTATION':
      return progression.reputation.get(requirement.target) >= requirement.threshold
    case 'ACHIEVEMENT':
      return progression.achievements.has(requirement.target)
    case 'QUEST':
      return progression.questProgress.get(requirement.target) == requirement.state
    case 'FLAG':
      return progression.specialFlags.has(requirement.target)
    case 'COMPOSITE':
      if requirement.operator == 'AND':
        return requirement.children.every(child => evaluateRequirement(progression, child))
      else if requirement.operator == 'OR':
        return requirement.children.some(child => evaluateRequirement(progression, child))
      else if requirement.operator == 'NOT':
        return !evaluateRequirement(progression, requirement.children[0])
```

---

## 4. Performance Considerations

### 4.1 Caching Strategy
- Cache CharacterProgression objects with TTL based on game activity
- Invalidate cache on relevant progression updates
- Consider Redis or similar in-memory store for fast access

### 4.2 Batch Processing
- Use batchCheckInteractions for UI elements showing multiple interaction options
- Prefetch likely interactions based on character location and history

### 4.3 Indexing
- Index interactions by POI and building IDs
- Create composite indexes for common query patterns

### 4.4 Computation Optimization
- Pre-compute common requirement checks
- Use bitfields for achievement and flag checks
- Short-circuit composite requirements evaluation

---

## 5. Integration Points

### 5.1 POI Evolution System (Task #472)
- POI state changes trigger interaction availability updates
- POIs reference available interactions by ID

### 5.2 Building Modification System (Task #473)
- Building upgrades modify available interactions
- Building state affects interaction requirements

### 5.3 UI Communication (Subtask 474.3)
- Interaction availability checks return UI notification IDs
- UI system consumes missing requirements for player feedback 