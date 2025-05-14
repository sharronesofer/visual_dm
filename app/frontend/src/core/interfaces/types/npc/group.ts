import { MemoryEvent } from './memory';
import { FactionType } from '../factions/faction';
import { Faction } from '../factions/faction';
import { Position } from '../world/position';
import { NPCData, NPCGoal } from './npc';

export enum GroupRole {
  LEADER = 'LEADER',
  DEPUTY = 'DEPUTY',
  ADVISOR = 'ADVISOR',
  MEMBER = 'MEMBER',
  RECRUIT = 'recruit',
  GUEST = 'guest'
}

export enum GroupType {
  ADVENTURING = 'ADVENTURING',
  TRADING = 'TRADING',
  CRAFTING = 'CRAFTING',
  MERCENARY = 'MERCENARY',
  SOCIAL = 'SOCIAL',
  FACTION = 'FACTION',
  TASK = 'TASK',
  ECONOMIC = 'ECONOMIC',
  COMBAT = 'COMBAT'
}

export enum GroupDecisionType {
  LEADERSHIP_CHANGE = 'leadership_change',
  MEMBER_ADMISSION = 'member_admission',
  MEMBER_EXPULSION = 'member_expulsion',
  GOAL_SETTING = 'goal_setting',
  RESOURCE_ALLOCATION = 'resource_allocation',
  ALLIANCE_FORMATION = 'alliance_formation',
  CONFLICT_RESOLUTION = 'conflict_resolution'
}

export interface GroupMember extends NPCData {
  role: GroupRole;
  joinedAt: number;
  contributionScore: number;
  relationshipScores: Map<string, number>;
}

export interface GroupDecision {
  id: string;
  type: GroupDecisionType;
  proposerId: string;
  timestamp: number;
  description: string;
  options: {
    id: string;
    description: string;
    supporters: string[];
    opposition: string[];
    weight: number;
  }[];
  status: 'pending' | 'approved' | 'rejected' | 'implemented';
  outcome?: string;
  votingDeadline?: number;
  requiredInfluence: number;
  affectedMembers: string[];
  relatedDecisions?: string[];
}

export interface GroupMeetingSchedule {
  frequency: 'daily' | 'weekly' | 'monthly';
  nextMeeting: number;
  location: string;
}

export interface GroupSubgroup {
  leaderId: string;
  members: string[];
  specialization: string;
}

export interface GroupHierarchy {
  leaderId: string;
  deputyIds: string[];
  advisorIds: string[];
  subgroups: GroupSubgroup[];
}

export interface GroupResources {
  wealth: number;
  territory: string[];
  assets: Map<string, number>;
  sharedInventory: Map<string, number>;
  accessPermissions: Map<string, Set<string>>;
}

export interface Group {
  id: string;
  name: string;
  type: GroupType;
  description: string;
  leaderId: string;
  members: Map<string, GroupMember>;
  createdAt: number;
  lastActive: number;
  reputation: number;
  hierarchy: GroupHierarchy;
  resources: GroupResources;
  goals: NPCGoal[];
  relationships: Map<string, {
    groupId: string;
    type: 'ally' | 'rival' | 'neutral';
    strength: number; // -10 to 10
    lastInteraction: number;
  }>;
  factionAffiliation?: FactionType;
  activeDecisions: GroupDecision[];
  decisionHistory: GroupDecision[];
  meetingSchedule?: GroupMeetingSchedule;
  disbandConditions?: {
    minMembers: number;
    minInfluence: number;
    maxInactivityPeriod: number;
  };
  decisions: GroupDecision[];
  formationTime: number;
  dissolutionConditions: GroupDissolutionCondition[];
}

export interface PersonalityCompatibility {
  traitWeights: Map<string, number>;  // trait -> importance weight
  complementaryTraits: Map<string, string[]>;  // trait -> complementary traits
  minCompatibilityScore: number;  // minimum score required for compatibility
}

export interface InteractionHistory {
  npcId: string;
  interactions: {
    timestamp: number;
    type: string;
    outcome: 'positive' | 'neutral' | 'negative';
    context: string;
    impact: number;  // -1 to 1
  }[];
  successRate: number;  // 0 to 1
  lastInteraction: number;
}

export interface GroupFormationTrigger {
  type: 'emergency' | 'resource' | 'goal' | 'periodic' | 'social';
  condition: {
    type: string;
    threshold: number;
    timeWindow?: number;
  };
  priority: number;  // 0 to 100
  minGroupSize: number;
  maxGroupSize: number;
  requiredRoles?: string[];
}

export interface GroupDissolutionCondition {
  type: 'conflict' | 'goalCompletion' | 'resourceDepletion' | 'inactivity' | 'ineffectiveness';
  threshold: number;
  evaluationPeriod: number;  // in milliseconds
  gracePeriod?: number;  // in milliseconds
  warningThreshold?: number;
}

export interface GroupFormationScore {
  npcId: string;
  score: number;
  affinityScore: number;
  proximityScore: number;
  goalAlignmentScore: number;
  personalityScore: number;
  interactionScore: number;
}

export interface GroupSizeRecommendation {
  min: number;
  optimal: number;
  max: number;
  overhead: number;
  resourceRequirements: {
    type: string;
    amountPerMember: number;
  }[];
  effectivenessMultiplier: number;
}

// Configuration constants
export const GROUP_CONSTANTS = {
  MIN_MEMBERS: 2,
  MAX_MEMBERS: 10,
  MIN_REPUTATION: -100,
  MAX_REPUTATION: 100,
  CONTRIBUTION_DECAY_RATE: 0.1,
  INACTIVITY_THRESHOLD: 7 * 24 * 60 * 60 * 1000, // 7 days in milliseconds
  DEFAULT_REPUTATION: 0,
  MIN_MEMBERS_FOR_SUBGROUP: 3,
  MAX_ADVISORS: 5,
  MAX_DEPUTIES: 2,
  MIN_INFLUENCE_FOR_LEADERSHIP: 75,
  MIN_CONTRIBUTION_FOR_PROMOTION: 80,
  RELATIONSHIP_DECAY_RATE: 0.1,
  INFLUENCE_DECAY_RATE: 0.05,
  MAX_DECISION_DURATION: 7 * 24 * 60 * 60 * 1000, // 7 days in ms
  MIN_VOTING_PERIOD: 24 * 60 * 60 * 1000, // 1 day in ms
  INACTIVITY_WARNING_THRESHOLD: 30 * 24 * 60 * 60 * 1000, // 30 days in ms
  MIN_RELATIONSHIP_SCORE: -100,
  MAX_RELATIONSHIP_SCORE: 100,
  MIN_INFLUENCE: 0,
  MAX_INFLUENCE: 100,
  MAX_SUBGROUPS_PER_GROUP: 5,
  MAX_WEALTH: 1000000,
  MAX_TERRITORY_SIZE: 100,
  MAX_ASSET_TYPES: 50,
  MAX_INVENTORY_TYPES: 100,
  MIN_MEETING_INTERVAL: 24 * 60 * 60 * 1000, // 1 day in milliseconds
  MAX_MEETING_INTERVAL: 30 * 24 * 60 * 60 * 1000, // 30 days in milliseconds
  // Personality compatibility constants
  TRAIT_MATCH_WEIGHT: 0.4,
  TRAIT_COMPLEMENT_WEIGHT: 0.6,
  MIN_PERSONALITY_COMPATIBILITY: 0.5,
  // Interaction history constants
  RECENT_INTERACTION_WINDOW: 7 * 24 * 60 * 60 * 1000, // 7 days
  INTERACTION_DECAY_RATE: 0.1,
  MIN_INTERACTIONS_FOR_HISTORY: 3,
  // Group formation trigger constants
  EMERGENCY_PRIORITY: 90,
  RESOURCE_PRIORITY: 70,
  GOAL_PRIORITY: 60,
  PERIODIC_PRIORITY: 30,
  SOCIAL_PRIORITY: 20,
  // Group dissolution constants
  CONFLICT_THRESHOLD: 0.7,
  EFFECTIVENESS_THRESHOLD: 0.4,
  MIN_ACTIVITY_PERIOD: 3 * 24 * 60 * 60 * 1000, // 3 days
  DISSOLUTION_GRACE_PERIOD: 24 * 60 * 60 * 1000, // 1 day
  // Group size optimization
  MAX_COMMUNICATION_OVERHEAD: 0.5,
  RESOURCE_SCALING_FACTOR: 1.2,
  EFFECTIVENESS_DECAY_RATE: 0.1,
  // Formation weights
  AFFINITY_WEIGHT: 2.0,
  PROXIMITY_WEIGHT: 1.0,
  GOAL_ALIGNMENT_WEIGHT: 2.5,
  PERSONALITY_WEIGHT: 1.5,
  INTERACTION_WEIGHT: 1.0
} as const; 