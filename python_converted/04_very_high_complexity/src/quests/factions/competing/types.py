from typing import Any, Dict, List, Union



class QuestResource:
    id: str
    amount: float
class QuestCondition:
    type: str
    value: Any
class CompletedQuest:
    questId: str
    factionId: FactionType
    completionTime: float
/**
 * Configuration for the competing quest system
 */
class CompetingQuestConfig:
    maxActiveGroups: float
    maxQuestsPerGroup: float
    questExpirationTime: float
    tensionDecayInterval: float
    tensionDecayAmount: float
    allianceThreshold: float
    highTensionThreshold: float
    lowTensionThreshold: float
    baseTensionDecayRate: float
    questLockoutThreshold: float
    hostilityThreshold: float
    questCooldownPeriod: float
    questCancellationPenalty: float
    questCompletionTensionIncrease: float
    tensionThreshold: float
    diplomaticSettings: Dict[str, Any]
/**
 * Extended FactionQuestTemplate interface
 */
class CompetingFactionQuestTemplate:
    location?: Union[str, None]
    requiredResources?: List[QuestResource]
    requiredConditions?: List[QuestCondition]
/**
 * Represents a group of competing quests
 */
class CompetingQuestGroup:
    id: str
    originalQuest: \'CompetingFactionQuestTemplate\'
    competingQuests: List[CompetingFactionQuestTemplate]
    activeQuests: List[CompetingFactionQuestTemplate]
    completedQuests: List[CompletedQuest]
    winningFaction: Union[FactionType, None]
    tensionLevel: float
    status: Union['active', 'completed', 'failed', 'expired']
    quests: Dict[str, CompetingFactionQuestTemplate>
    diplomaticState?: {
    meetingScheduled?: bool
    meetingLocation?: str
    resourceExchangeProposed?: bool
    proposedResources?: List[{
      offered: QuestResource]
    requested: List[QuestResource]
    agreementDraft?: {
      terms: List[string]
      acceptedBy: List[FactionType]
      status: 'DRAFTING' | 'PROPOSED' | 'ACCEPTED' | 'REJECTED'
    }
  }
}
/**
 * Metrics for tracking tension between factions
 */
class FactionTensionMetrics:
    currentTension: float
    historicalPeak: float
    lastConflictTime: float
    lastUpdateTimestamp: float
    involvedFactions: List[FactionType]
    conflictHistory: List[ConflictHistoryEntry]
    updates: List[TensionUpdate]
/**
 * Represents a tension update event
 */
class TensionUpdate:
    timestamp: float
    factionA: FactionType
    factionB: FactionType
    oldTension: float
    newTension: float
    tensionChange: float
    type: Union['QUEST_COMPLETION', 'NATURAL_DECAY']
    reason: str
    decayAmount?: float
/**
 * Represents a conflict history entry
 */
class ConflictHistoryEntry:
    timestamp: float
    type: Union['QUEST_COMPLETION', 'NATURAL_DECAY']
    tensionChange: float
/**
 * Represents a conflict between factions
 */
class FactionConflict:
    questGroupId: str
    timestamp: float
    winningFaction: Union[FactionType, None]
    worldStateChanges: List[WorldStateChange]
    affectedFactions: List[FactionType]
/**
 * State of conflict resolution
 */
ConflictResolutionState = FactionConflict