/**
 * Quest and Arc System Types
 * 
 * This file defines the core types used throughout the quest and narrative arc system.
 */

import { UUID } from '../../core/types';

/**
 * Quest status enum
 */
export enum QuestStatus {
  INACTIVE = 'inactive',     // Not yet available to player
  AVAILABLE = 'available',   // Available but not yet accepted
  ACTIVE = 'active',         // Accepted and in progress
  COMPLETED = 'completed',   // Successfully completed
  FAILED = 'failed',         // Failed conditions
  ABANDONED = 'abandoned',   // Abandoned by player
  EXPIRED = 'expired'        // Time limit expired
}

/**
 * Objective status enum
 */
export enum ObjectiveStatus {
  HIDDEN = 'hidden',         // Not yet visible to player
  VISIBLE = 'visible',       // Visible but not completed
  COMPLETED = 'completed',   // Successfully completed
  FAILED = 'failed',         // Failed conditions
  OPTIONAL_SKIPPED = 'optional_skipped' // Optional objective skipped
}

/**
 * Quest objective types
 */
export enum ObjectiveType {
  KILL = 'kill',             // Kill enemies
  COLLECT = 'collect',       // Collect items
  DELIVER = 'deliver',       // Deliver items
  ESCORT = 'escort',         // Escort NPCs
  DISCOVER = 'discover',     // Discover locations
  INTERACT = 'interact',     // Interact with objects
  DIALOGUE = 'dialogue',     // Complete dialogue
  CRAFT = 'craft',           // Craft items
  CUSTOM = 'custom'          // Custom objective with custom completion logic
}

/**
 * Quest reward types
 */
export enum RewardType {
  EXPERIENCE = 'experience', // Experience points
  CURRENCY = 'currency',     // Currency
  ITEM = 'item',             // Item reward
  REPUTATION = 'reputation', // Faction reputation
  SKILL = 'skill',           // Skill points or new skills
  ABILITY = 'ability',       // New abilities
  RESOURCE = 'resource'      // Game resources
}

/**
 * Quest objective target interface
 */
export interface ObjectiveTarget {
  targetId: UUID;            // ID of the target entity
  targetType: string;        // Type of the target (enemy, item, location, etc.)
  targetName: string;        // Display name of the target
  count: number;             // Number required (for counts > 1)
  current: number;           // Current progress
}

/**
 * Quest objective interface
 */
export interface QuestObjective {
  id: UUID;                  // Unique identifier
  title: string;             // Objective title
  description: string;       // Objective description
  type: ObjectiveType;       // Type of objective
  status: ObjectiveStatus;   // Current status
  isOptional: boolean;       // Whether optional for quest completion
  targets: ObjectiveTarget[]; // Targets for this objective
  order: number;             // Order in the quest (for sequential objectives)
  requiresAllTargets: boolean; // Whether all targets must be completed
  dependsOn?: UUID[];        // IDs of objectives that must be completed first
  timeLimit?: number;        // Time limit in seconds (if applicable)
  locationId?: UUID;         // Associated location (if applicable)
  data?: Record<string, any>; // Additional data for custom objectives
}

/**
 * Quest reward interface
 */
export interface QuestReward {
  type: RewardType;          // Type of reward
  amount: number;            // Amount (for numerical rewards)
  itemId?: UUID;             // Item ID (for item rewards)
  data?: Record<string, any>; // Additional data for custom rewards
}

/**
 * Quest interface
 */
export interface Quest {
  id: UUID;                  // Unique identifier
  title: string;             // Quest title
  description: string;       // Quest description
  status: QuestStatus;       // Current status
  objectives: QuestObjective[]; // List of objectives
  rewards: QuestReward[];    // List of rewards
  giverEntityId?: UUID;      // Entity that gave the quest
  level: number;             // Quest difficulty level
  minPlayerLevel?: number;   // Minimum player level required
  isRepeatable: boolean;     // Whether can be repeated
  cooldownPeriod?: number;   // Cooldown before repeatable (in seconds)
  timeLimit?: number;        // Overall time limit (in seconds)
  startTime?: number;        // When the quest was started (timestamp)
  arcId?: UUID;              // ID of the arc this quest belongs to
  dependsOn?: UUID[];        // IDs of quests that must be completed first
  excludes?: UUID[];         // IDs of quests that become unavailable after this
  mutuallyExclusive?: UUID[]; // IDs of quests that cannot be active simultaneously
  tags: string[];            // Tags for categorization and filtering
  isHidden: boolean;         // Whether hidden from quest log
  isMandatory: boolean;      // Whether required for game progression
  failureConditions?: string[]; // Conditions that will cause quest failure
  successConditions?: string[]; // Additional success conditions beyond objectives
  hasTimeSensitiveObjectives: boolean; // Whether contains time-sensitive objectives
}

/**
 * Narrative arc interface - groups related quests into a storyline
 */
export interface NarrativeArc {
  id: UUID;                  // Unique identifier
  title: string;             // Arc title
  description: string;       // Arc description
  quests: UUID[];            // Ordered list of quest IDs in this arc
  status: QuestStatus;       // Overall arc status
  isActive: boolean;         // Whether currently active
  branchingPoints: BranchingPoint[]; // Points where the arc can branch
  completionRequirements: ArcCompletionRequirement; // Requirements to complete arc
  prerequisiteArcs?: UUID[]; // Arcs that must be completed first
  motifIds?: UUID[];         // Associated motifs/themes
  isMainStory: boolean;      // Whether part of main story
  tags: string[];            // Tags for categorization and filtering
}

/**
 * Arc completion requirement types
 */
export enum ArcCompletionRequirementType {
  ALL_QUESTS = 'all_quests',             // All quests must be completed
  SPECIFIC_QUESTS = 'specific_quests',   // Specific quests must be completed
  PERCENTAGE = 'percentage',             // Percentage of quests must be completed
  ANY_BRANCH = 'any_branch'              // Any complete branch satisfies completion
}

/**
 * Arc completion requirements
 */
export interface ArcCompletionRequirement {
  type: ArcCompletionRequirementType;    // Type of requirement
  specificQuestIds?: UUID[];             // Required quest IDs (for SPECIFIC_QUESTS)
  percentage?: number;                   // Required percentage (for PERCENTAGE)
}

/**
 * Branching condition types
 */
export enum BranchingConditionType {
  QUEST_OUTCOME = 'quest_outcome',       // Based on how a quest was completed
  PLAYER_CHOICE = 'player_choice',       // Based on explicit player choice
  WORLD_STATE = 'world_state',           // Based on world state variables
  RELATIONSHIP = 'relationship',         // Based on NPC relationships
  PLAYER_STAT = 'player_stat'            // Based on player stats/attributes
}

/**
 * Branching point in a narrative arc
 */
export interface BranchingPoint {
  id: UUID;                              // Unique identifier
  sourceQuestId: UUID;                   // Quest where branching occurs
  conditions: BranchingCondition[];      // Conditions that determine branching
  branches: Branch[];                    // Possible branches
  defaultBranchId: UUID;                 // Default branch if no conditions met
}

/**
 * Condition for branching
 */
export interface BranchingCondition {
  type: BranchingConditionType;          // Type of condition
  entityId?: UUID;                       // Related entity (NPC, item, etc.)
  parameter: string;                     // Specific parameter to check
  operator: 'eq' | 'gt' | 'lt' | 'gte' | 'lte' | 'ne' | 'contains'; // Comparison operator
  value: any;                            // Value to compare against
  branchId: UUID;                        // Branch to take if condition is met
}

/**
 * Branch in a narrative arc
 */
export interface Branch {
  id: UUID;                              // Unique identifier
  name: string;                          // Branch name
  description: string;                   // Branch description
  questIds: UUID[];                      // Ordered list of quest IDs in this branch
  isDefault: boolean;                    // Whether this is the default branch
  leadsToArcId?: UUID;                   // Arc this branch leads to (if any)
} 