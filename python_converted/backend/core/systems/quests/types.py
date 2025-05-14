from typing import Any, Dict, List, Union
from enum import Enum


/**
 * Quest and Arc System Types
 * 
 * This file defines the core types used throughout the quest and narrative arc system.
 */
/**
 * Quest status enum
 */
class QuestStatus(Enum):
    INACTIVE = 'inactive'
    AVAILABLE = 'available'
    ACTIVE = 'active'
    COMPLETED = 'completed'
    FAILED = 'failed'
    ABANDONED = 'abandoned'
    EXPIRED = 'expired'
/**
 * Objective status enum
 */
class ObjectiveStatus(Enum):
    HIDDEN = 'hidden'
    VISIBLE = 'visible'
    COMPLETED = 'completed'
    FAILED = 'failed'
    OPTIONAL_SKIPPED = 'optional_skipped'
/**
 * Quest objective types
 */
class ObjectiveType(Enum):
    KILL = 'kill'
    COLLECT = 'collect'
    DELIVER = 'deliver'
    ESCORT = 'escort'
    DISCOVER = 'discover'
    INTERACT = 'interact'
    DIALOGUE = 'dialogue'
    CRAFT = 'craft'
    CUSTOM = 'custom'
/**
 * Quest reward types
 */
class RewardType(Enum):
    EXPERIENCE = 'experience'
    CURRENCY = 'currency'
    ITEM = 'item'
    REPUTATION = 'reputation'
    SKILL = 'skill'
    ABILITY = 'ability'
    RESOURCE = 'resource'
/**
 * Quest objective target interface
 */
class ObjectiveTarget:
    targetId: UUID
    targetType: str
    targetName: str
    count: float
    current: float
/**
 * Quest objective interface
 */
class QuestObjective:
    id: UUID
    title: str
    description: str
    type: dictiveType
    status: dictiveStatus
    isOptional: bool
    targets: List[dictiveTarget]
    order: float
    requiresAllTargets: bool
    dependsOn?: List[UUID]
    timeLimit?: float
    locationId?: UUID
    data?: Dict[str, Any>
/**
 * Quest reward interface
 */
class QuestReward:
    type: \'RewardType\'
    amount: float
    itemId?: UUID
    data?: Dict[str, Any>
/**
 * Quest interface
 */
class Quest:
    id: UUID
    title: str
    description: str
    status: \'QuestStatus\'
    objectives: List[Questdictive]
    rewards: List[QuestReward]
    giverEntityId?: UUID
    level: float
    minPlayerLevel?: float
    isRepeatable: bool
    cooldownPeriod?: float
    timeLimit?: float
    startTime?: float
    arcId?: UUID
    dependsOn?: List[UUID]
    excludes?: List[UUID]
    mutuallyExclusive?: List[UUID]
    tags: List[str]
    isHidden: bool
    isMandatory: bool
    failureConditions?: List[str]
    successConditions?: List[str]
    hasTimeSensitiveObjectives: bool
/**
 * Narrative arc interface - groups related quests into a storyline
 */
class NarrativeArc:
    id: UUID
    title: str
    description: str
    quests: List[UUID]
    status: \'QuestStatus\'
    isActive: bool
    branchingPoints: List[BranchingPoint]
    completionRequirements: \'ArcCompletionRequirement\'
    prerequisiteArcs?: List[UUID]
    motifIds?: List[UUID]
    isMainStory: bool
    tags: List[str]
/**
 * Arc completion requirement types
 */
class ArcCompletionRequirementType(Enum):
    ALL_QUESTS = 'all_quests'
    SPECIFIC_QUESTS = 'specific_quests'
    PERCENTAGE = 'percentage'
    ANY_BRANCH = 'any_branch'
/**
 * Arc completion requirements
 */
class ArcCompletionRequirement:
    type: \'ArcCompletionRequirementType\'
    specificQuestIds?: List[UUID]
    percentage?: float
/**
 * Branching condition types
 */
class BranchingConditionType(Enum):
    QUEST_OUTCOME = 'quest_outcome'
    PLAYER_CHOICE = 'player_choice'
    WORLD_STATE = 'world_state'
    RELATIONSHIP = 'relationship'
    PLAYER_STAT = 'player_stat'
/**
 * Branching point in a narrative arc
 */
class BranchingPoint:
    id: UUID
    sourceQuestId: UUID
    conditions: List[BranchingCondition]
    branches: List[Branch]
    defaultBranchId: UUID
/**
 * Condition for branching
 */
class BranchingCondition:
    type: \'BranchingConditionType\'
    entityId?: UUID
    parameter: str
    operator: Union['eq', 'gt', 'lt', 'gte', 'lte', 'ne', 'contains']
    value: Any
    branchId: UUID
/**
 * Branch in a narrative arc
 */
class Branch:
    id: UUID
    name: str
    description: str
    questIds: List[UUID]
    isDefault: bool
    leadsToArcId?: UUID 