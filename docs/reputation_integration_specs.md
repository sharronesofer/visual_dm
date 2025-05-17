# Reputation System Integration Technical Specifications

This document details the technical specifications for all integration points between the reputation system and other major game systems. Each section includes data structures, method signatures, event patterns, error handling, performance considerations, edge cases, and code references.

---

## Dialogue System

### 1. InteractionSystem (src/systems/npc/InteractionSystem.ts)
- **Nature of Interaction:** Reads and updates reputation based on dialogue outcomes.
- **Data Structures:**
  - `InteractionResult` (imported from './InteractionSystem')
  - `ReputationChange` (see `src/systems/npc/ReputationSystem.ts`)
- **Key Methods:**
  - `processInteractionReputation(npcId: string, targetId: string, result: InteractionResult): Promise<number>`
  - `recordReputationChange(npcId: string, targetId: string, value: number, result: InteractionResult): void`
- **Event Patterns:** Direct API calls, invoked after dialogue events.
- **Error Handling:** Try/catch blocks around reputation processing; logs errors to console.
- **Performance:** Event-based, minimal overhead per interaction.
- **Edge Cases:**
  - No reputation record exists for the pair (creates new entry).
  - Extreme reputation values are clamped.
- **Code Reference:**
  - `src/systems/npc/InteractionSystem.ts` (lines 3, 42, 94, 121)
  - `src/systems/npc/ReputationSystem.ts` (lines 9-164)

---

## Quest System

### 1. SocialPOI (src/poi/models/SocialPOI.ts)
- **Nature of Interaction:** Adjusts faction reputation as quest reward.
- **Data Structures:**
  - `quest.properties.rewards.reputation` (number)
- **Key Methods:**
  - `completeQuest(questId: string): boolean`
  - `adjustFactionReputation(factionId: string, change: number): boolean`
- **Event Patterns:** Direct API call on quest completion.
- **Error Handling:** Checks for quest/faction existence; returns false if not found.
- **Performance:** Event-based, only on quest completion.
- **Edge Cases:**
  - No primary faction found.
  - Reputation clamped between -100 and 100.
- **Code Reference:**
  - `src/poi/models/SocialPOI.ts` (lines 177-195)

### 2. QuestBranchingSystem (src/quests/QuestBranchingSystem.ts)
- **Nature of Interaction:** Calculates branch weights and requirements using player reputation.
- **Data Structures:**
  - `MemoryEventType.FACTION_EVENT`
- **Key Methods:**
  - `getPlayerReputation(playerId: string): Promise<number>`
  - `calculateBranchWeight(...)`
- **Event Patterns:** Direct API call during quest branching.
- **Error Handling:** Handles missing memories gracefully.
- **Performance:** May be called frequently during quest evaluation.
- **Edge Cases:**
  - No reputation memories found (returns 0).
- **Code Reference:**
  - `src/quests/QuestBranchingSystem.ts` (lines 63-80, 141-162)

### 3. FactionQuestSystem (src/quests/factions/FactionQuestSystem.ts)
- **Nature of Interaction:** Updates player/faction reputation on quest completion.
- **Data Structures:**
  - `FactionStanding` (with `reputation: number`)
- **Key Methods:**
  - `updateStandings(questId, factionId, outcome, choices)`
  - `adjustReputation(standing, change)`
- **Event Patterns:** Direct API call after quest outcome.
- **Error Handling:** Checks for standing/faction existence.
- **Performance:** Event-based, per quest.
- **Edge Cases:**
  - Reputation clamped between -100 and 100.
- **Code Reference:**
  - `src/quests/factions/FactionQuestSystem.ts` (lines 158-204, 409-427)

---

## Combat System

- **Nature of Interaction:** Modifies reputation for combat actions (kill, assist, property damage).
- **Data Structures:**
  - See audit template in `docs/reputation_audit_template.md`.
- **Key Methods:** Planned, not yet implemented.
- **Event Patterns:** Event-based, to be triggered by combat events.
- **Error Handling:** N/A (planned).
- **Performance:** N/A (planned).
- **Edge Cases:** N/A (planned).
- **Code Reference:**
  - `docs/reputation_audit_template.md`

---

## AI System

### 1. ReputationSystem (src/systems/npc/ReputationSystem.ts)
- **Nature of Interaction:** AI uses reputation to modify NPC behavior.
- **Data Structures:**
  - `ReputationChange`, `ReputationSystem`
- **Key Methods:**
  - `getAggregateReputation(npcId: string, targetId: string): number`
- **Event Patterns:** Direct API call during AI decision-making.
- **Error Handling:** Handles missing history gracefully.
- **Performance:** Real-time, may be called frequently.
- **Edge Cases:**
  - No reputation history (returns 0).
- **Code Reference:**
  - `src/systems/npc/ReputationSystem.ts` (lines 141-164)

---

## Economy System

### 1. EconomicAgentSystem (src/systems/economy/EconomicAgentSystem.ts)
- **Nature of Interaction:** Updates agent reputation based on trades.
- **Data Structures:**
  - `agent.reputation: number`
- **Key Methods:**
  - `updateReputation(agentId: string, changeAmount: number): void`
- **Event Patterns:** Direct API call after trade.
- **Error Handling:** Checks for agent existence.
- **Performance:** Event-based, per trade.
- **Edge Cases:**
  - Reputation clamped between 0 and 100.
- **Code Reference:**
  - `src/systems/economy/EconomicAgentSystem.ts` (lines 48, 190-196)

### 2. EconomicTypes (src/systems/economy/EconomicTypes.ts)
- **Nature of Interaction:** Stores reputation as part of agent state.
- **Data Structures:**
  - `reputation: number` in agent types.
- **Key Methods:** N/A (data structure only).
- **Event Patterns:** N/A.
- **Error Handling:** N/A.
- **Performance:** Real-time.
- **Edge Cases:** N/A.
- **Code Reference:**
  - `src/systems/economy/EconomicTypes.ts` (lines 52, 112)

---

## Faction System

### 1. FactionQuestSystem (src/quests/factions/FactionQuestSystem.ts)
- **Nature of Interaction:** Tracks and updates faction reputation.
- **Data Structures:**
  - `FactionStanding`, `FactionProfile`
- **Key Methods:**
  - `initializePlayerStanding`, `adjustReputation`, `getPlayerStandings`
- **Event Patterns:** Direct API call/event-based.
- **Error Handling:** Checks for existence of player/faction.
- **Performance:** Event-based.
- **Edge Cases:**
  - Reputation clamped between -100 and 100.
- **Code Reference:**
  - `src/quests/factions/FactionQuestSystem.ts` (lines 63-78, 409-427, 878-910)

### 2. SocialPOI (src/poi/models/SocialPOI.ts)
- **Nature of Interaction:** Adjusts player reputation with factions at POIs.
- **Data Structures:**
  - `faction.properties.playerReputation`
- **Key Methods:**
  - `adjustFactionReputation(factionId: string, change: number): boolean`
- **Event Patterns:** Direct API call.
- **Error Handling:** Checks for faction existence.
- **Performance:** Event-based.
- **Edge Cases:**
  - Reputation clamped between -100 and 100.
- **Code Reference:**
  - `src/poi/models/SocialPOI.ts` (lines 177-195)

---

## POI System

### 1. SocialPOI (src/poi/models/SocialPOI.ts)
- **Nature of Interaction:** Stores and updates player reputation for POIs.
- **Data Structures:**
  - `playerReputation: number`
- **Key Methods:**
  - `adjustFactionReputation`, `completeQuest`
- **Event Patterns:** Direct API call.
- **Error Handling:** Checks for POI/faction existence.
- **Performance:** Event-based.
- **Edge Cases:**
  - Reputation clamped between -100 and 100.
- **Code Reference:**
  - `src/poi/models/SocialPOI.ts` (lines 46, 177-195)

---

## Group System

### 1. GroupManager (src/systems/npc/GroupManager.ts)
- **Nature of Interaction:** Updates group reputation.
- **Data Structures:**
  - `group.reputation: number`
- **Key Methods:**
  - `updateGroupReputation(groupId: string, delta: number): boolean`
- **Event Patterns:** Direct API call.
- **Error Handling:** Checks for group existence.
- **Performance:** Event-based.
- **Edge Cases:**
  - Reputation clamped between min and max.
- **Code Reference:**
  - `src/systems/npc/GroupManager.ts` (lines 260-271)

---

## Region System

- **Nature of Interaction:** Planned support for region reputation.
- **Data Structures:**
  - To be defined.
- **Key Methods:**
  - To be defined.
- **Event Patterns:**
  - Planned.
- **Error Handling:**
  - Planned.
- **Performance:**
  - Planned.
- **Edge Cases:**
  - Planned.
- **Code Reference:**
  - `docs/interaction_system/source_materials/tasks_478-482.json`

---

# End of Document 