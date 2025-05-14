from typing import Any, Dict, List, Union
from enum import Enum


class GroupRole(Enum):
    LEADER = 'LEADER'
    DEPUTY = 'DEPUTY'
    ADVISOR = 'ADVISOR'
    MEMBER = 'MEMBER'
    RECRUIT = 'recruit'
    GUEST = 'guest'
class GroupType(Enum):
    ADVENTURING = 'ADVENTURING'
    TRADING = 'TRADING'
    CRAFTING = 'CRAFTING'
    MERCENARY = 'MERCENARY'
    SOCIAL = 'SOCIAL'
    FACTION = 'FACTION'
    TASK = 'TASK'
    ECONOMIC = 'ECONOMIC'
    COMBAT = 'COMBAT'
class GroupDecisionType(Enum):
    LEADERSHIP_CHANGE = 'leadership_change'
    MEMBER_ADMISSION = 'member_admission'
    MEMBER_EXPULSION = 'member_expulsion'
    GOAL_SETTING = 'goal_setting'
    RESOURCE_ALLOCATION = 'resource_allocation'
    ALLIANCE_FORMATION = 'alliance_formation'
    CONFLICT_RESOLUTION = 'conflict_resolution'
class GroupMember:
    role: \'GroupRole\'
    joinedAt: float
    contributionScore: float
    relationshipScores: Dict[str, float>
class GroupDecision:
    id: str
    type: \'GroupDecisionType\'
    proposerId: str
    timestamp: float
    description: str
    options: Dict[str, Any]
class GroupMeetingSchedule:
    frequency: Union['daily', 'weekly', 'monthly']
    nextMeeting: float
    location: str
class GroupSubgroup:
    leaderId: str
    members: List[str]
    specialization: str
class GroupHierarchy:
    leaderId: str
    deputyIds: List[str]
    advisorIds: List[str]
    subgroups: List[GroupSubgroup]
class GroupResources:
    wealth: float
    territory: List[str]
    assets: Dict[str, float>
    sharedInventory: Dict[str, float>
    accessPermissions: Dict[str, Set[str>>
class Group:
    id: str
    name: str
    type: \'GroupType\'
    description: str
    leaderId: str
    members: Dict[str, GroupMember>
    createdAt: float
    lastActive: float
    reputation: float
    hierarchy: \'GroupHierarchy\'
    resources: \'GroupResources\'
    goals: List[NPCGoal]
    relationships: Dict[str, {
    groupId: str
    type: Union['ally', 'rival', 'neutral']
    strength: float
    lastInteraction: float>
  factionAffiliation?: FactionType
  activeDecisions: List[GroupDecision]
  decisionHistory: List[GroupDecision]
  meetingSchedule?: \'GroupMeetingSchedule\'
  disbandConditions?: {
    minMembers: float
    minInfluence: float
    maxInactivityPeriod: float
  }
  decisions: List[GroupDecision]
  formationTime: float
  dissolutionConditions: List[GroupDissolutionCondition]
}
class PersonalityCompatibility:
    traitWeights: Dict[str, float>
    complementaryTraits: Dict[str, str[]>
    minCompatibilityScore: float
class InteractionHistory:
    npcId: str
    interactions: Dict[str, Any]
class GroupFormationTrigger:
    type: Union['emergency', 'resource', 'goal', 'periodic', 'social']
    condition: Dict[str, Any]
class GroupDissolutionCondition:
    type: Union['conflict', 'goalCompletion', 'resourceDepletion', 'inactivity', 'ineffectiveness']
    threshold: float
    evaluationPeriod: float
    gracePeriod?: float
    warningThreshold?: float
class GroupFormationScore:
    npcId: str
    score: float
    affinityScore: float
    proximityScore: float
    goalAlignmentScore: float
    personalityScore: float
    interactionScore: float
class GroupSizeRecommendation:
    min: float
    optimal: float
    max: float
    overhead: float
    resourceRequirements: Dict[str, Any]
const GROUP_CONSTANTS = {
  MIN_MEMBERS: 2,
  MAX_MEMBERS: 10,
  MIN_REPUTATION: -100,
  MAX_REPUTATION: 100,
  CONTRIBUTION_DECAY_RATE: 0.1,
  INACTIVITY_THRESHOLD: 7 * 24 * 60 * 60 * 1000, 
  DEFAULT_REPUTATION: 0,
  MIN_MEMBERS_FOR_SUBGROUP: 3,
  MAX_ADVISORS: 5,
  MAX_DEPUTIES: 2,
  MIN_INFLUENCE_FOR_LEADERSHIP: 75,
  MIN_CONTRIBUTION_FOR_PROMOTION: 80,
  RELATIONSHIP_DECAY_RATE: 0.1,
  INFLUENCE_DECAY_RATE: 0.05,
  MAX_DECISION_DURATION: 7 * 24 * 60 * 60 * 1000, 
  MIN_VOTING_PERIOD: 24 * 60 * 60 * 1000, 
  INACTIVITY_WARNING_THRESHOLD: 30 * 24 * 60 * 60 * 1000, 
  MIN_RELATIONSHIP_SCORE: -100,
  MAX_RELATIONSHIP_SCORE: 100,
  MIN_INFLUENCE: 0,
  MAX_INFLUENCE: 100,
  MAX_SUBGROUPS_PER_GROUP: 5,
  MAX_WEALTH: 1000000,
  MAX_TERRITORY_SIZE: 100,
  MAX_ASSET_TYPES: 50,
  MAX_INVENTORY_TYPES: 100,
  MIN_MEETING_INTERVAL: 24 * 60 * 60 * 1000, 
  MAX_MEETING_INTERVAL: 30 * 24 * 60 * 60 * 1000, 
  TRAIT_MATCH_WEIGHT: 0.4,
  TRAIT_COMPLEMENT_WEIGHT: 0.6,
  MIN_PERSONALITY_COMPATIBILITY: 0.5,
  RECENT_INTERACTION_WINDOW: 7 * 24 * 60 * 60 * 1000, 
  INTERACTION_DECAY_RATE: 0.1,
  MIN_INTERACTIONS_FOR_HISTORY: 3,
  EMERGENCY_PRIORITY: 90,
  RESOURCE_PRIORITY: 70,
  GOAL_PRIORITY: 60,
  PERIODIC_PRIORITY: 30,
  SOCIAL_PRIORITY: 20,
  CONFLICT_THRESHOLD: 0.7,
  EFFECTIVENESS_THRESHOLD: 0.4,
  MIN_ACTIVITY_PERIOD: 3 * 24 * 60 * 60 * 1000, 
  DISSOLUTION_GRACE_PERIOD: 24 * 60 * 60 * 1000, 
  MAX_COMMUNICATION_OVERHEAD: 0.5,
  RESOURCE_SCALING_FACTOR: 1.2,
  EFFECTIVENESS_DECAY_RATE: 0.1,
  AFFINITY_WEIGHT: 2.0,
  PROXIMITY_WEIGHT: 1.0,
  GOAL_ALIGNMENT_WEIGHT: 2.5,
  PERSONALITY_WEIGHT: 1.5,
  INTERACTION_WEIGHT: 1.0
} as const 