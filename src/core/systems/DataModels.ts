/**
 * DataModels.ts
 * 
 * Core data models and interfaces for all backend systems. This file defines the common
 * data structures used across multiple systems including motifs, relationships, memories,
 * economy, inventory, quests, party management, map generation, dialogue, combat, and
 * player memory systems.
 */

import { v4 as uuidv4 } from 'uuid';

// ------------------------------
// Base Interfaces
// ------------------------------

/**
 * Base interface for all entity types in the system
 */
export interface BaseEntity {
    id: string;
    createdAt: number;
    updatedAt: number;
}

/**
 * Interface for entities that can be tagged
 */
export interface Taggable {
    tags: string[];
}

/**
 * Interface for entities that have an importance/priority
 */
export interface Prioritizable {
    importance: number; // 0-100 scale
}

// ------------------------------
// Motif System
// ------------------------------

export enum MotifType {
    THEME = 'theme',
    SYMBOL = 'symbol',
    RECURRING_ELEMENT = 'recurring_element',
    NARRATIVE_DEVICE = 'narrative_device',
    CHARACTER_TRAIT = 'character_trait',
    ENVIRONMENTAL = 'environmental'
}

export interface Motif extends BaseEntity, Taggable, Prioritizable {
    type: MotifType;
    name: string;
    description: string;
    occurrences: MotifOccurrence[];
    relevanceScore: number; // Dynamically calculated
}

export interface MotifOccurrence {
    id: string;
    timestamp: number;
    context: string;
    strength: number; // 0-100 scale
    entityIds: string[]; // IDs of entities involved (NPCs, locations, etc.)
}

// ------------------------------
// Relationship System
// ------------------------------

export enum RelationshipType {
    FRIEND = 'friend',
    ALLY = 'ally',
    ENEMY = 'enemy',
    RIVAL = 'rival',
    FAMILY = 'family',
    ROMANTIC = 'romantic',
    PROFESSIONAL = 'professional',
    ACQUAINTANCE = 'acquaintance'
}

export interface Relationship extends BaseEntity {
    type: RelationshipType;
    entityId1: string;
    entityId2: string;
    affinity: number; // -100 to 100 scale
    trust: number; // 0-100 scale
    familiarity: number; // 0-100 scale
    history: RelationshipEvent[];
}

export interface RelationshipEvent {
    id: string;
    timestamp: number;
    description: string;
    affinityChange: number;
    trustChange: number;
    familiarityChange: number;
    memoryIds: string[]; // Associated memories
}

// ------------------------------
// Memory System
// ------------------------------

export enum MemoryType {
    INTERACTION = 'interaction',
    OBSERVATION = 'observation',
    COMBAT = 'combat',
    DISCOVERY = 'discovery',
    ACHIEVEMENT = 'achievement',
    EMOTIONAL = 'emotional',
    TRADE = 'trade',
    QUEST = 'quest'
}

export interface Memory extends BaseEntity, Taggable, Prioritizable {
    type: MemoryType;
    ownerEntityId: string;
    involvedEntityIds: string[];
    description: string;
    details: Record<string, any>;
    emotionalImpact: number; // -100 to 100 scale
    decayRate: number; // 0-100 scale (0 = no decay)
    lastRecalled: number; // Timestamp
    relatedMemoryIds: string[];
}

// ------------------------------
// Economy System
// ------------------------------

export enum CurrencyType {
    GOLD = 'gold',
    SILVER = 'silver',
    COPPER = 'copper',
    SPECIAL = 'special'
}

export interface Currency {
    type: CurrencyType;
    amount: number;
    specialType?: string; // For SPECIAL currency type
}

export interface EconomicValue {
    currencies: Currency[];
    valueModifier: number; // Multiplier for base values
}

export interface PriceFactors {
    regionalModifier: number;
    supplyModifier: number;
    demandModifier: number;
    reputationModifier: number;
    seasonalModifier: number;
}

// ------------------------------
// Inventory System
// ------------------------------

export enum ItemType {
    WEAPON = 'weapon',
    ARMOR = 'armor',
    CONSUMABLE = 'consumable',
    QUEST = 'quest',
    MATERIAL = 'material',
    VALUABLE = 'valuable',
    TOOL = 'tool',
    CONTAINER = 'container'
}

export enum ItemRarity {
    COMMON = 'common',
    UNCOMMON = 'uncommon',
    RARE = 'rare',
    EPIC = 'epic',
    LEGENDARY = 'legendary',
    UNIQUE = 'unique'
}

export interface Item extends BaseEntity, Taggable {
    name: string;
    description: string;
    type: ItemType;
    rarity: ItemRarity;
    weight: number;
    value: EconomicValue;
    stackable: boolean;
    maxStackSize: number;
    quantity: number;
    properties: Record<string, any>;
    requiredLevel?: number;
    iconId?: string;
}

export interface Inventory extends BaseEntity {
    ownerId: string;
    slots: InventorySlot[];
    maxWeight: number;
    maxSlots: number;
    currentWeight: number;
}

export interface InventorySlot {
    id: string;
    itemId: string | null;
    quantity: number;
}

// ------------------------------
// Quest/Arc System
// ------------------------------

export enum QuestType {
    MAIN = 'main',
    SIDE = 'side',
    REPEATABLE = 'repeatable',
    DYNAMIC = 'dynamic',
    TUTORIAL = 'tutorial'
}

export enum QuestStatus {
    UNAVAILABLE = 'unavailable',
    AVAILABLE = 'available',
    ACTIVE = 'active',
    COMPLETED = 'completed',
    FAILED = 'failed'
}

export enum ObjectiveType {
    KILL = 'kill',
    COLLECT = 'collect',
    TALK = 'talk',
    REACH_LOCATION = 'reach_location',
    ESCORT = 'escort',
    DEFEND = 'defend',
    INVESTIGATE = 'investigate',
    CRAFT = 'craft',
    MULTI = 'multi'
}

export interface Quest extends BaseEntity, Taggable {
    title: string;
    description: string;
    type: QuestType;
    status: QuestStatus;
    giverEntityId: string;
    targetEntityIds: string[];
    objectives: QuestObjective[];
    rewards: QuestReward[];
    parentQuestId?: string;
    childQuestIds: string[];
    requiredLevel?: number;
    timeLimit?: number; // Time in milliseconds, undefined = no limit
    startTime?: number; // When quest was accepted
    associatedMotifIds: string[];
    summary: string; // Brief description for UI
}

export interface QuestObjective {
    id: string;
    type: ObjectiveType;
    description: string;
    targetId?: string;
    targetCount?: number;
    currentCount: number;
    completed: boolean;
    locationId?: string;
    parameters: Record<string, any>;
}

export interface QuestReward {
    type: 'item' | 'currency' | 'experience' | 'reputation' | 'skill';
    amount: number;
    targetId?: string; // Item ID, faction ID, skill ID, etc.
    delivered: boolean;
}

// ------------------------------
// Party System
// ------------------------------

export enum PartyRole {
    LEADER = 'leader',
    MEMBER = 'member',
    TEMPORARY = 'temporary',
    QUEST = 'quest'
}

export interface Party extends BaseEntity {
    name: string;
    leaderEntityId: string;
    members: PartyMember[];
    maxSize: number;
    formationPositions: Record<string, { x: number, y: number }>;
    activeQuests: string[];
}

export interface PartyMember {
    entityId: string;
    role: PartyRole;
    joinedAt: number;
    contribution: number; // 0-100 rating of participation
    loyaltyScore: number; // 0-100 rating of loyalty
}

// ------------------------------
// Map/POI System
// ------------------------------

export enum POIType {
    SETTLEMENT = 'settlement',
    DUNGEON = 'dungeon',
    LANDMARK = 'landmark',
    RESOURCE = 'resource',
    ENCOUNTER = 'encounter',
    QUEST = 'quest',
    SECRET = 'secret'
}

export enum POISize {
    TINY = 'tiny',
    SMALL = 'small',
    MEDIUM = 'medium',
    LARGE = 'large',
    HUGE = 'huge'
}

export enum POIStatus {
    UNDISCOVERED = 'undiscovered',
    VISIBLE = 'visible',
    VISITED = 'visited',
    CLEARED = 'cleared'
}

export interface POI extends BaseEntity, Taggable {
    name: string;
    description: string;
    type: POIType;
    size: POISize;
    status: POIStatus;
    position: { x: number, y: number };
    region: string;
    difficulty: number; // 1-100 scale
    inhabitants: string[]; // Entity IDs
    loot: Item[];
    associatedQuestIds: string[];
    discoveryRequirements?: Record<string, any>;
    entrances: { position: { x: number, y: number }, description: string }[];
    interiorMapId?: string;
    discoveredBy?: string[];
    visitedBy?: string[];
}

// ------------------------------
// Dialogue System
// ------------------------------

export enum DialogueType {
    GREETING = 'greeting',
    QUERY = 'query',
    RESPONSE = 'response',
    OFFER = 'offer',
    DEMAND = 'demand',
    FAREWELL = 'farewell'
}

export enum DialogueTone {
    FRIENDLY = 'friendly',
    NEUTRAL = 'neutral',
    HOSTILE = 'hostile',
    FORMAL = 'formal',
    INFORMAL = 'informal',
    URGENT = 'urgent',
    MYSTERIOUS = 'mysterious'
}

export interface DialogueContext {
    speakerId: string;
    listenerId: string;
    relationship?: Relationship;
    recentMemories: Memory[];
    relevantMotifs: Motif[];
    activeQuests: Quest[];
    environmentDescription: string;
    timeOfDay: string;
    previousDialogues: Dialogue[];
    emotionalState: Record<string, number>; // Emotion -> intensity (0-100)
}

export interface Dialogue extends BaseEntity {
    speakerId: string;
    listenerId: string;
    type: DialogueType;
    tone: DialogueTone;
    content: string;
    options?: DialogueOption[];
    contextSnapshot: DialogueContext;
    responseToId?: string;
    memoryId?: string; // Memory created from this dialogue
}

export interface DialogueOption {
    id: string;
    content: string;
    requirements?: Record<string, any>;
    consequences?: Record<string, any>;
}

// ------------------------------
// Combat System
// ------------------------------

export enum CombatActionType {
    ATTACK = 'attack',
    DEFEND = 'defend',
    ABILITY = 'ability',
    MOVE = 'move',
    ITEM = 'item',
    RETREAT = 'retreat',
    INTERACT = 'interact'
}

export enum DamageType {
    PHYSICAL = 'physical',
    MAGICAL = 'magical',
    FIRE = 'fire',
    ICE = 'ice',
    LIGHTNING = 'lightning',
    POISON = 'poison',
    PSYCHIC = 'psychic',
    HOLY = 'holy',
    UNHOLY = 'unholy',
    TRUE = 'true' // Ignores resistances
}

export enum StatusEffectType {
    BUFF = 'buff',
    DEBUFF = 'debuff',
    CONTROL = 'control',
    DAMAGE_OVER_TIME = 'damage_over_time',
    HEAL_OVER_TIME = 'heal_over_time'
}

export interface CombatAction {
    id: string;
    type: CombatActionType;
    actorId: string;
    targetIds: string[];
    timestamp: number;
    parameters: Record<string, any>;
    result?: CombatActionResult;
}

export interface CombatActionResult {
    success: boolean;
    damageDealt?: { [targetId: string]: { type: DamageType, amount: number }[] };
    healingDone?: { [targetId: string]: number };
    statusEffectsApplied?: { [targetId: string]: StatusEffect[] };
    statusEffectsRemoved?: { [targetId: string]: string[] }; // Status effect IDs
    positionChanges?: { [entityId: string]: { x: number, y: number } };
    interactionResults?: Record<string, any>;
}

export interface StatusEffect extends BaseEntity {
    name: string;
    type: StatusEffectType;
    description: string;
    duration: number; // In turns or milliseconds
    strength: number; // 0-100 scale
    sourceEntityId: string;
    targetEntityId: string;
    effects: Record<string, any>;
    stackable: boolean;
    maxStacks: number;
    currentStacks: number;
    periodic: boolean;
    interval?: number; // Time between periodic effects
    lastApplied: number; // Timestamp or turn number
}

// ------------------------------
// Movement System
// ------------------------------

export enum MovementType {
    WALK = 'walk',
    RUN = 'run',
    SWIM = 'swim',
    FLY = 'fly',
    TELEPORT = 'teleport',
    CLIMB = 'climb'
}

export enum TerrainType {
    PLAIN = 'plain',
    FOREST = 'forest',
    MOUNTAIN = 'mountain',
    WATER = 'water',
    SWAMP = 'swamp',
    DESERT = 'desert',
    SNOW = 'snow',
    URBAN = 'urban'
}

export interface MovementCapabilities {
    types: MovementType[];
    speeds: Record<MovementType, number>;
    terrainPenalties: Record<TerrainType, number>; // Multipliers, 1 = normal speed
    maxStamina: number;
    currentStamina: number;
    staminaRegenRate: number;
    staminaCosts: Record<MovementType, number>;
}

// ------------------------------
// Player Memory System
// ------------------------------

export enum PlayerMemoryCategory {
    QUEST = 'quest',
    INTERACTION = 'interaction',
    DISCOVERY = 'discovery',
    COMBAT = 'combat',
    DECISION = 'decision',
    ACHIEVEMENT = 'achievement'
}

export interface PlayerMemory extends BaseEntity, Taggable, Prioritizable {
    category: PlayerMemoryCategory;
    title: string;
    description: string;
    context: string;
    involvedEntityIds: string[];
    location: { regionId: string, position: { x: number, y: number } };
    consequences: string[];
    callbacks: PlayerMemoryCallback[];
    lastReferencedAt?: number;
    referenceCount: number;
}

export interface PlayerMemoryCallback {
    id: string;
    triggerCondition: Record<string, any>;
    narrativeText: string;
    hasTriggered: boolean;
    triggeredAt?: number;
    cooldown: number; // Time before can trigger again
}

// ------------------------------
// Utility/Helper Functions
// ------------------------------

export function createBaseEntity(): BaseEntity {
    const now = Date.now();
    return {
        id: uuidv4(),
        createdAt: now,
        updatedAt: now
    };
}

export function createTaggable(tags: string[] = []): Taggable {
    return { tags };
}

export function createPrioritizable(importance: number = 50): Prioritizable {
    return { importance };
}

export function updateEntityTimestamp(entity: BaseEntity): BaseEntity {
    return {
        ...entity,
        updatedAt: Date.now()
    };
}

export function mergeTags(existingTags: string[], newTags: string[]): string[] {
    return [...new Set([...existingTags, ...newTags])];
} 