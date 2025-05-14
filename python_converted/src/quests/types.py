from typing import Any, Dict, List, Union


/**
 * Represents the current state of a quest, including player's progress
 */
class QuestState:
    inventory?: Dict[str, float>
    currentLocation?: str
    npcInteractions?: Dict[str, str[]>
    combatVictories?: Dict[str, float>
    skills?: Dict[str, float>
    completedStages?: List[str]
    currentStageId?: str
    branchHistory?: { stageId: str
    branchId: List[str]
}
/**
 * Represents a condition that must be met to progress in a quest
 */
class QuestCondition:
    type: str
    parameters: Dict[str, Any>
    description: str
    evaluate(state: QuestState): bool
/**
 * Represents a branch in the quest progression
 */
class QuestBranch:
    id: str
    condition: Dict[str, Any]
/**
 * Represents a single stage in a quest
 */
class QuestStage:
    id: str
    title: str
    description: str
    branches: List[QuestBranch]
    requirements?: List[{
    items?: str]
    skills?: List[str]
    factions?: Dict[FactionType, float>
  rewards?: {
    items?: string[]
    experience?: float
    gold?: float
    factionStanding?: Record<FactionType, number>
  }
  objectives: List[QuestObjective]
  nextStages?: string[]
  completed?: bool
}
/**
 * QuestTemplate defines the structure for all quest templates in the system.
 * See ../schemas/quest_template.schema.json for the JSON schema and ../QUEST_TEMPLATE_STRUCTURE.md for documentation.
 */
/**
 * Represents a complete quest template
 */
class QuestTemplate:
    id: str
    title: str
    description: str
    type: QuestType
    questType: QuestType
    status: Union['PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CANCELLED']
    difficulty: float
    requirements: \'QuestRequirements\'
    objectives: List[Questdictive]
    dialogue: List[QuestDialogue]
    rewards: \'QuestRewards\'
    location?: Union[str, None]
    customData?: Dict[str, Any>
ConsequenceType = Union[, 'ITEM_REWARD', 'ITEM_REMOVE', 'WORLD_STATE', 'FACTION_STANDING', 'NPC_RELATIONSHIP']
class QuestConsequence:
    type: Union['FACTION_STANDING', 'ITEM_REWARD', 'ITEM_REMOVE', 'NPC_RELATIONSHIP', 'WORLD_STATE']
    target: str
    value: Union[float, str, bool]
    description: str
class QuestRequirements:
    minimumLevel: float
    minimumReputation: float
    items?: List[str]
    abilities?: List[str]
class QuestDialogueResponse:
    text: str
    nextDialogueId?: str
    condition?: str
class QuestDialogue:
    text: str
    npcId: str
    responses: List[QuestDialogueResponse]
class DialogueVariation:
    standingThreshold?: float
    text: str
    tone?: str
class QuestObjective:
    id: str
    description: str
    type: dictiveType
    target?: str
    amount?: float
    location?: str
    customData?: Dict[str, Any>
    completed?: bool
    conditions?: List[QuestCondition]
QuestType = Union[, 'CUSTOM', 'KILL', 'COLLECT', 'EXPLORE', 'INTERACT', 'DIPLOMATIC', 'RESOURCE_GATHERING', 'TERRITORY_CONTROL']
ObjectiveType = Union[, 'CUSTOM', 'KILL', 'COLLECT', 'EXPLORE', 'INTERACT', 'DIPLOMATIC_MEETING', 'RESOURCE_EXCHANGE', 'CONTROL', 'CONTEST']
class QuestRewards:
    gold: float
    experience: float
    items: List[str]
    reputation?: float
    diplomaticInfluence?: float 