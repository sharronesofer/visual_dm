from typing import Any, Dict, List, Union


WorldStateChangeType = Union[, 'QUEST_COMPLETION', 'QUEST_FAILURE', 'QUEST_CANCELLED', 'FACTION_TENSION_CHANGE', 'TENSION_DECREASE', 'DIPLOMATIC_OPPORTUNITY', 'RESOURCE_CHANGE', 'TERRITORY_CHANGE', 'FACTION_ALLIANCE_BENEFIT', 'FACTION_ALLIANCE_OPPORTUNITY', 'DIPLOMATIC_MEETING', 'DIPLOMATIC_AGREEMENT', 'DIPLOMATIC_FAILURE', 'RESOURCE_EXCHANGE']
WorldStateChangeEventType = Union[, 'QUEST_COMPLETION', 'QUEST_FAILURE', 'QUEST_CANCELLATION', 'TENSION_DECAY', 'TENSION_STATE_CHANGE', 'DIPLOMATIC_EVENT', 'ALLIANCE_VICTORY_BENEFIT', 'ALLIANCE_OPPORTUNITY', 'DIPLOMATIC_MEETING', 'DIPLOMATIC_AGREEMENT', 'DIPLOMATIC_FAILURE', 'RESOURCE_EXCHANGE']
class WorldStateChangeCustomData:
    type: WorldStateChangeEventType
    questId?: str
    groupId?: str
    winningFaction?: FactionType
    factions?: List[FactionType]
    timestamp: float
    oldState?: Union['HIGH_TENSION', 'LOW_TENSION', 'NEUTRAL', 'ALLIED']
    newState?: Union['HIGH_TENSION', 'LOW_TENSION', 'NEUTRAL', 'ALLIED']
    eventType?: Union['OPPORTUNITY', 'CONFLICT', 'AGREEMENT', 'MEETING']
    allyFaction?: FactionType
    questGroupId?: str
    tensionLevel?: float
    diplomaticOutcome?: Union['SUCCESS', 'FAILURE', 'PARTIAL']
    resourceExchange?: {
    offeredResources: Dict[str, Any][]
  }
  meetingDetails?: {
    location: str
    participants: List[FactionType]
    agenda: List[string]
    outcome: str
  }
}
class WorldStateChange:
    type: WorldStateChangeType
    description: str
    value: float
    affectedFactions: List[FactionType]
    location: Union[str, None]
    customData?: \'WorldStateChangeCustomData\'
class WorldState:
    factionInfluence: Dict[FactionType, float>
    factionTensions: Dict[str, float>
    resources: Dict[str, float>
    territories: Dict[FactionType, str[]>
    customStates: Dict[str, Any>
    economyFactors: Dict[str, float>
/**
 * Types of player actions that can trigger consequences
 */
PlayerActionType = Union[, 'QUEST_COMPLETION', 'QUEST_FAILURE', 'QUEST_BRANCH_CHOICE', 'DIALOGUE_CHOICE', 'RESOURCE_EXCHANGE', 'FACTION_INTERACTION', 'WORLD_EVENT']
/**
 * Represents a single player action with context for consequence tracking
 */
class PlayerAction:
    playerId: str
    actionType: PlayerActionType
    timestamp: float
    questId?: str
    factionId?: FactionType
    targetFactionId?: FactionType
    choiceId?: str
    outcome?: str
    details?: Dict[str, Any>
/**
 * Tracks the history of player actions for consequence and world state tracking
 */
class PlayerActionHistory:
    playerId: str
    actions: List[PlayerAction] 