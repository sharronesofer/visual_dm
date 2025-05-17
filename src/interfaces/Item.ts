import { BaseEntity } from './BaseEntity';

/**
 * Item rarity enum
 */
export enum ItemRarity {
    COMMON = 'common',
    UNCOMMON = 'uncommon',
    RARE = 'rare',
    EPIC = 'epic',
    LEGENDARY = 'legendary',
    ARTIFACT = 'artifact',
    UNIQUE = 'unique'
}

/**
 * Item type enum
 */
export enum ItemType {
    WEAPON = 'weapon',
    ARMOR = 'armor',
    ACCESSORY = 'accessory',
    CONSUMABLE = 'consumable',
    MATERIAL = 'material',
    QUEST_ITEM = 'quest_item',
    KEY_ITEM = 'key_item',
    CONTAINER = 'container',
    CURRENCY = 'currency',
    TOOL = 'tool',
    BOOK = 'book',
    MISCELLANEOUS = 'miscellaneous'
}

/**
 * Item property that affects its behavior or stats
 */
export interface ItemProperty {
    id: string;
    name: string;
    description: string;
    type: string; // Type of property (e.g., "damage", "defense", "healing", etc.)
    value: number | string | boolean | Record<string, any>; // Property value
    isHidden: boolean; // Whether this property is initially hidden to the player
    conditions?: Record<string, any>; // Conditions for when this property is active
}

/**
 * Historical event for an item
 */
export interface ItemHistoryEntry {
    date: Date;
    type: string; // Type of event (e.g., "created", "acquired", "upgraded", etc.)
    description: string;
    locationId?: string | number; // Where this event happened
    characterId?: string | number; // Who was involved
    data?: Record<string, any>; // Additional event data
}

/**
 * Item usage record
 */
export interface ItemUsage {
    id: string;
    date: Date;
    characterId: string | number; // Who used the item
    locationId?: string | number; // Where the item was used
    result: string; // Result of the usage
    effectiveness?: number; // How effective the usage was (0-100)
    cooldownExpires?: Date; // When the item can be used again if cooldown applies
}

/**
 * Item enhancement/upgrade definition
 */
export interface ItemEnhancement {
    id: string;
    name: string;
    description: string;
    level: number; // Current enhancement level
    maxLevel: number; // Maximum enhancement level
    properties: ItemProperty[]; // Properties granted by this enhancement
    requirements: { // Requirements for further enhancement
        materials?: { id: string | number, quantity: number }[];
        gold?: number;
        skillRequirements?: { skill: string, level: number }[];
        characterRequirements?: Record<string, any>;
    };
}

/**
 * Item interface representing an in-game item
 */
export interface Item extends BaseEntity {
    name: string;
    description: string;

    // Basic properties
    type: ItemType;
    subtype?: string; // More specific classification
    rarity: ItemRarity;
    levelRequirement?: number; // Minimum level to use
    value: number; // Base gold value
    weight: number; // Weight in appropriate units
    stackable: boolean; // Whether items of this type can stack
    stackSize: number; // Current stack size (1 for non-stackable)
    maxStackSize: number; // Maximum stack size

    // Visual attributes
    icon?: string; // Icon reference
    model?: string; // 3D model reference if applicable
    appearance?: Record<string, any>; // Additional visual properties

    // Dynamic properties
    properties: ItemProperty[];

    // History tracking
    history: ItemHistoryEntry[];

    // Usage tracking
    usageCount: number; // How many times the item has been used
    lastUsed?: Date; // When the item was last used
    usageHistory?: ItemUsage[]; // Detailed usage history
    usageLimit?: number; // Maximum number of uses if limited

    // Durability
    durability?: {
        current: number;
        max: number;
        repairCost: number; // Base cost to repair
        degradationRate: number; // How quickly it loses durability
    };

    // Enhancement
    enhancements?: ItemEnhancement[];

    // Container contents (if container type)
    contents?: (string | number)[]; // IDs of contained items
    capacity?: number; // Maximum number of items that can be contained

    // Equipment data (if equippable)
    equippable?: boolean;
    equipSlot?: string | string[]; // Where this item can be equipped
    equippedBy?: string | number; // ID of character who has this equipped

    // Additional data
    customData?: Record<string, any>; // Any additional custom properties
} 