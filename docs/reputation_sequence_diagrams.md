# Reputation System Complex Interaction Sequence Diagrams

This document contains Mermaid sequence diagrams illustrating the flow of reputation data across multiple game systems for key complex scenarios.

---

## 1. Reputation Change Propagation Through Factions

```mermaid
sequenceDiagram
    participant Player
    participant QuestSystem
    participant FactionSystem
    participant FactionA
    participant FactionB
    Player->>QuestSystem: completeQuest(questId)
    QuestSystem->>FactionSystem: updateStandings(questId, factionId, outcome)
    FactionSystem->>FactionA: adjustReputation(standing, +10)
    FactionSystem->>FactionB: applyInterFactionConsequences(factionId, outcome)
    FactionSystem->>FactionB: adjustReputation(standing, -5)
    FactionA-->>FactionSystem: updated reputation
    FactionB-->>FactionSystem: updated reputation
    FactionSystem-->>QuestSystem: updated standings
    QuestSystem-->>Player: quest completion result
```

---

## 2. Reputation-Based Quest Unlocking

```mermaid
sequenceDiagram
    participant Player
    participant QuestBranchingSystem
    participant MemoryManager
    participant FactionSystem
    Player->>QuestBranchingSystem: requestAvailableQuests()
    QuestBranchingSystem->>MemoryManager: queryMemories(playerId, FACTION_EVENT)
    MemoryManager-->>QuestBranchingSystem: reputationMemories
    QuestBranchingSystem->>FactionSystem: getFactionStanding(playerId, factionId)
    FactionSystem-->>QuestBranchingSystem: standing
    QuestBranchingSystem->>QuestBranchingSystem: calculateBranchWeight(...)
    QuestBranchingSystem-->>Player: available quest branches
```

---

## 3. Reputation Effects on Dialogue and Merchant Pricing

```mermaid
sequenceDiagram
    participant Player
    participant DialogueSystem
    participant NPC
    participant ReputationSystem
    participant EconomySystem
    Player->>DialogueSystem: initiateDialogue(npcId)
    DialogueSystem->>ReputationSystem: getAggregateReputation(npcId, playerId)
    ReputationSystem-->>DialogueSystem: reputationScore
    DialogueSystem->>NPC: determineDialogueOptions(reputationScore)
    Player->>EconomySystem: requestPrice(npcId, itemId)
    EconomySystem->>ReputationSystem: getAggregateReputation(npcId, playerId)
    ReputationSystem-->>EconomySystem: reputationScore
    EconomySystem->>NPC: calculatePrice(reputationScore)
    NPC-->>Player: dialogue/price options
```

---

## 4. Group Reputation Affecting AI Behavior

```mermaid
sequenceDiagram
    participant GroupManager
    participant Group
    participant ReputationSystem
    participant AIManager
    GroupManager->>Group: updateGroupReputation(groupId, delta)
    Group->>ReputationSystem: recordReputationChange(...)
    AIManager->>ReputationSystem: getAggregateReputation(groupId, npcId)
    ReputationSystem-->>AIManager: groupReputationScore
    AIManager->>Group: adjustBehavior(groupReputationScore)
```

---

## 5. POI Reputation Influencing Quest and Economy Systems

```mermaid
sequenceDiagram
    participant Player
    participant POISystem
    participant QuestSystem
    participant EconomySystem
    participant ReputationSystem
    Player->>POISystem: interactWithPOI(poiId)
    POISystem->>ReputationSystem: getReputation(playerId, poiId)
    ReputationSystem-->>POISystem: poiReputation
    POISystem->>QuestSystem: unlockQuests(poiReputation)
    POISystem->>EconomySystem: adjustPrices(poiReputation)
    QuestSystem-->>Player: available quests
    EconomySystem-->>Player: updated prices
```

---

# End of Diagrams 