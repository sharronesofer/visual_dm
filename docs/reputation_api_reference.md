# Reputation System API Reference

This document provides a comprehensive API reference for all public methods, properties, events, and data structures used in the reputation system and its integration points. It is intended for use by all teams integrating with or extending the reputation system.

---

## Table of Contents
- [ReputationSystem](#reputationsystem)
- [GroupManager](#groupmanager)
- [SocialPOI](#socialpoi)
- [FactionQuestSystem](#factionquestsystem)
- [EconomicAgentSystem](#economicagentsystem)

---

## ReputationSystem

**File:** `src/systems/npc/ReputationSystem.ts`

### Data Structures

#### ReputationChange
```typescript
interface ReputationChange {
  value: number;
  reason: string;
  timestamp: number;
}
```
- **Description:** Represents a single change in reputation, with a value, reason, and timestamp.

### Public Methods

#### processInteractionReputation
```typescript
processInteractionReputation(npcId: string, targetId: string, result: InteractionResult): Promise<number>
```
- **Description:** Processes the result of an interaction and updates reputation accordingly.
- **Parameters:**
  - `npcId`: ID of the NPC
  - `targetId`: ID of the target entity
  - `result`: The result of the interaction
- **Returns:** Promise resolving to the reputation change value
- **Example:**
```typescript
await reputationSystem.processInteractionReputation('npc123', 'player456', result);
```
- **Exceptions:** Logs errors to console, returns 0 on error
- **Best Practices:** Always handle the returned promise and check for errors
- **Performance:** Event-based, minimal overhead

#### calculateBaseReputation
```typescript
private calculateBaseReputation(result: InteractionResult): number
```
- **Description:** Calculates the base reputation change from an interaction result
- **Parameters:**
  - `result`: The result of the interaction
- **Returns:** Numeric base change
- **Notes:** Used internally by `processInteractionReputation`

#### applyInteractionModifiers
```typescript
private applyInteractionModifiers(baseChange: number, result: InteractionResult): number
```
- **Description:** Applies modifiers (economic, emotional) to the base reputation change
- **Parameters:**
  - `baseChange`: The base reputation change
  - `result`: The result of the interaction
- **Returns:** Modified reputation change
- **Notes:** Used internally by `processInteractionReputation`

#### recordReputationChange
```typescript
recordReputationChange(npcId: string, targetId: string, value: number, result: InteractionResult): void
```
- **Description:** Records a reputation change in the history
- **Parameters:**
  - `npcId`: ID of the NPC
  - `targetId`: ID of the target entity
  - `value`: The reputation change value
  - `result`: The result of the interaction
- **Returns:** void
- **Example:**
```typescript
reputationSystem.recordReputationChange('npc123', 'player456', 0.1, result);
```
- **Exceptions:** None
- **Performance:** Fast, in-memory update

#### getReputationHistory
```typescript
getReputationHistory(npcId: string, targetId: string): ReputationChange[]
```
- **Description:** Retrieves the reputation change history between two entities
- **Parameters:**
  - `npcId`: ID of the NPC
  - `targetId`: ID of the target entity
- **Returns:** Array of `ReputationChange`
- **Example:**
```typescript
const history = reputationSystem.getReputationHistory('npc123', 'player456');
```
- **Exceptions:** None

#### getAggregateReputation
```typescript
getAggregateReputation(npcId: string, targetId: string): number
```
- **Description:** Computes the aggregate reputation score between two entities, weighted by recency
- **Parameters:**
  - `npcId`: ID of the NPC
  - `targetId`: ID of the target entity
- **Returns:** Numeric reputation score
- **Example:**
```typescript
const score = reputationSystem.getAggregateReputation('npc123', 'player456');
```
- **Exceptions:** None
- **Performance:** Fast, uses in-memory data

---

## GroupManager

**File:** `src/systems/npc/GroupManager.ts`

### Public Methods

#### updateGroupReputation
```typescript
updateGroupReputation(groupId: string, delta: number): boolean
```
- **Description:** Updates the reputation of a group by a delta value
- **Parameters:**
  - `groupId`: ID of the group
  - `delta`: Amount to change reputation by
- **Returns:** Boolean indicating success
- **Example:**
```typescript
groupManager.updateGroupReputation('group1', 5);
```
- **Exceptions:** Returns false if group not found
- **Performance:** Fast, event-based

---

## SocialPOI

**File:** `src/poi/models/SocialPOI.ts`

### Public Methods

#### completeQuest
```typescript
completeQuest(questId: string): boolean
```
- **Description:** Completes a quest and applies reputation changes if specified
- **Parameters:**
  - `questId`: ID of the quest
- **Returns:** Boolean indicating success
- **Example:**
```typescript
poi.completeQuest('quest42');
```
- **Exceptions:** Returns false if quest not found

#### adjustFactionReputation
```typescript
adjustFactionReputation(factionId: string, change: number): boolean
```
- **Description:** Adjusts the player's reputation with a faction at the POI
- **Parameters:**
  - `factionId`: ID of the faction
  - `change`: Amount to change reputation by
- **Returns:** Boolean indicating success
- **Example:**
```typescript
poi.adjustFactionReputation('factionA', 10);
```
- **Exceptions:** Returns false if faction not found

---

## FactionQuestSystem

**File:** `src/quests/factions/FactionQuestSystem.ts`

### Public Methods

#### updateStandings
```typescript
updateStandings(questId: string, factionId: string, outcome: 'success' | 'failure' | 'abandoned', choices: string[]): void
```
- **Description:** Updates player/faction standings and reputation based on quest outcome
- **Parameters:**
  - `questId`: ID of the quest
  - `factionId`: ID of the faction
  - `outcome`: Quest outcome
  - `choices`: Array of player choices
- **Returns:** void
- **Example:**
```typescript
factionQuestSystem.updateStandings('quest42', 'factionA', 'success', ['choice1']);
```
- **Exceptions:** None

#### adjustReputation
```typescript
adjustReputation(standing: FactionStanding, change: number): void
```
- **Description:** Adjusts the reputation value in a FactionStanding
- **Parameters:**
  - `standing`: The FactionStanding object
  - `change`: Amount to change reputation by
- **Returns:** void
- **Example:**
```typescript
factionQuestSystem.adjustReputation(standing, 10);
```
- **Exceptions:** None

---

## EconomicAgentSystem

**File:** `src/systems/economy/EconomicAgentSystem.ts`

### Public Methods

#### updateReputation
```typescript
updateReputation(agentId: string, changeAmount: number): void
```
- **Description:** Updates an economic agent's reputation based on trade outcomes
- **Parameters:**
  - `agentId`: ID of the agent
  - `changeAmount`: Amount to change reputation by
- **Returns:** void
- **Example:**
```typescript
economicAgentSystem.updateReputation('agent007', 5);
```
- **Exceptions:** None

---

# Best Practices & Common Pitfalls
- Always check for entity existence before updating reputation
- Clamp reputation values to defined min/max to avoid overflow
- Use event-based updates for performance
- Cross-reference integration points and sequence diagrams for correct usage patterns

# Performance Considerations
- Most operations are in-memory and event-based, ensuring minimal overhead
- For large-scale queries (e.g., all reputation records), consider batching or pagination

# See Also
- [Integration Mapping](./reputation_integration_mapping.csv)
- [Technical Specifications](./reputation_integration_specs.md)
- [Sequence Diagrams](./reputation_sequence_diagrams.md) 