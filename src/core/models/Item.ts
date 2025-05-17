import { v4 as uuidv4 } from 'uuid';
import { BaseItem, BaseStats, ItemType, RarityTier } from '../interfaces/types/loot';

/**
 * Item Property interface represents dynamic properties that can be applied to items
 */
export interface ItemProperty {
    id: string;
    name: string;
    description: string;
    modifier: any;
    condition?: (context: any) => boolean;
}

/**
 * Item History Event interface for tracking significant events in an item's history
 */
export interface ItemHistoryEvent {
    id: string;
    timestamp: Date;
    eventType: string;
    description: string;
    actorId?: string;
    location?: string;
    metadata?: Record<string, any>;
}

/**
 * Enhanced Item class with full functionality for the item system
 */
export class Item implements BaseItem {
    id: string;
    name: string;
    description: string;
    type: ItemType;
    weight: number;
    value: number;
    baseStats: BaseStats;
    createdAt: Date;
    updatedAt: Date;

    // Extended properties for enhanced item system
    rarity?: RarityTier;
    properties: ItemProperty[] = [];
    historyEvents: ItemHistoryEvent[] = [];
    maxDurability: number = 100;
    currentDurability: number = 100;
    maxCharges?: number;
    currentCharges?: number;
    cooldownTime?: number;
    lastUsedTime?: Date;
    usageCount: number = 0;
    maxUsageCount?: number;
    enhancementLevel: number = 0;

    constructor(item: Partial<BaseItem>) {
        this.id = item.id || uuidv4();
        this.name = item.name || 'Unknown Item';
        this.description = item.description || '';
        this.type = item.type || ItemType.MISC;
        this.weight = item.weight || 0;
        this.value = item.value || 0;
        this.baseStats = item.baseStats || {};
        this.createdAt = item.createdAt || new Date();
        this.updatedAt = item.updatedAt || new Date();

        // Add creation to history
        this.addHistoryEvent({
            eventType: 'CREATED',
            description: `Item created: ${this.name}`
        });
    }

    /**
     * Add a property to the item
     */
    addProperty(property: Omit<ItemProperty, 'id'>): void {
        const newProperty: ItemProperty = {
            id: uuidv4(),
            ...property
        };
        this.properties.push(newProperty);
        this.updatedAt = new Date();
    }

    /**
     * Remove a property from the item
     */
    removeProperty(propertyId: string): boolean {
        const initialLength = this.properties.length;
        this.properties = this.properties.filter(p => p.id !== propertyId);
        this.updatedAt = new Date();
        return this.properties.length !== initialLength;
    }

    /**
     * Add a history event to the item
     */
    addHistoryEvent(event: Omit<ItemHistoryEvent, 'id' | 'timestamp'>): void {
        const newEvent: ItemHistoryEvent = {
            id: uuidv4(),
            timestamp: new Date(),
            ...event
        };
        this.historyEvents.push(newEvent);
        this.updatedAt = new Date();
    }

    /**
     * Set item rarity and update stats accordingly
     */
    setRarity(rarity: RarityTier): void {
        this.rarity = rarity;
        // Apply the value multiplier
        this.value = Math.round(this.value * rarity.valueMultiplier);

        this.addHistoryEvent({
            eventType: 'RARITY_CHANGE',
            description: `Item rarity set to ${rarity.name}`
        });

        this.updatedAt = new Date();
    }

    /**
     * Use the item, updating charges/durability/cooldown as needed
     */
    use(context: any = {}): boolean {
        // Check if item is on cooldown
        if (this.cooldownTime && this.lastUsedTime) {
            const currentTime = new Date();
            const cooldownEndTime = new Date(this.lastUsedTime.getTime() + this.cooldownTime);
            if (currentTime < cooldownEndTime) {
                return false; // Still on cooldown
            }
        }

        // Check if max usage count is reached
        if (this.maxUsageCount !== undefined && this.usageCount >= this.maxUsageCount) {
            return false; // Max usage reached
        }

        // Check charges
        if (this.maxCharges !== undefined) {
            if (this.currentCharges === undefined || this.currentCharges <= 0) {
                return false; // No charges left
            }
            this.currentCharges--;
        }

        // Reduce durability (if applicable)
        if (this.currentDurability > 0) {
            this.currentDurability = Math.max(0, this.currentDurability - 1);

            // Check if item broke
            if (this.currentDurability === 0) {
                this.addHistoryEvent({
                    eventType: 'BROKEN',
                    description: 'Item broken due to durability loss'
                });
            }
        }

        // Update usage tracking
        this.usageCount++;
        this.lastUsedTime = new Date();

        // Add history event
        this.addHistoryEvent({
            eventType: 'USED',
            description: `Item used${context.actorId ? ` by ${context.actorId}` : ''}${context.location ? ` at ${context.location}` : ''}`,
            actorId: context.actorId,
            location: context.location,
            metadata: context
        });

        this.updatedAt = new Date();
        return true;
    }

    /**
     * Repair the item, restoring durability
     */
    repair(amount: number): number {
        const oldDurability = this.currentDurability;
        this.currentDurability = Math.min(this.maxDurability, this.currentDurability + amount);

        const amountRepaired = this.currentDurability - oldDurability;

        if (amountRepaired > 0) {
            this.addHistoryEvent({
                eventType: 'REPAIRED',
                description: `Item repaired for ${amountRepaired} durability points`
            });
        }

        this.updatedAt = new Date();
        return amountRepaired;
    }

    /**
     * Recharge the item
     */
    recharge(amount: number): number {
        if (this.maxCharges === undefined || this.currentCharges === undefined) {
            return 0;
        }

        const oldCharges = this.currentCharges;
        this.currentCharges = Math.min(this.maxCharges, this.currentCharges + amount);

        const amountRecharged = this.currentCharges - oldCharges;

        if (amountRecharged > 0) {
            this.addHistoryEvent({
                eventType: 'RECHARGED',
                description: `Item recharged for ${amountRecharged} charges`
            });
        }

        this.updatedAt = new Date();
        return amountRecharged;
    }

    /**
     * Enhance the item, improving its stats
     */
    enhance(materials: any[] = []): boolean {
        // Calculate success probability based on current enhancement level
        // The higher the level, the lower the chance of success
        const baseSuccessRate = 0.9;
        const successRateReduction = 0.1 * this.enhancementLevel;
        const successRate = Math.max(0.1, baseSuccessRate - successRateReduction);

        // Check if enhancement succeeds
        const success = Math.random() < successRate;

        if (success) {
            this.enhancementLevel++;

            // Boost item stats based on enhancement level
            this.value = Math.round(this.value * 1.2);

            // Improve base stats
            Object.keys(this.baseStats).forEach(key => {
                if (this.baseStats[key] !== undefined) {
                    this.baseStats[key] = (this.baseStats[key] as number) * 1.1;
                }
            });

            this.addHistoryEvent({
                eventType: 'ENHANCED',
                description: `Item enhanced to level ${this.enhancementLevel}`,
                metadata: { materials }
            });
        } else {
            this.addHistoryEvent({
                eventType: 'ENHANCEMENT_FAILED',
                description: `Item enhancement failed at level ${this.enhancementLevel}`,
                metadata: { materials }
            });
        }

        this.updatedAt = new Date();
        return success;
    }

    /**
     * Check if item can be used
     */
    canUse(): boolean {
        // Check durability
        if (this.currentDurability <= 0) {
            return false;
        }

        // Check charges
        if (this.maxCharges !== undefined &&
            (this.currentCharges === undefined || this.currentCharges <= 0)) {
            return false;
        }

        // Check cooldown
        if (this.cooldownTime && this.lastUsedTime) {
            const currentTime = new Date();
            const cooldownEndTime = new Date(this.lastUsedTime.getTime() + this.cooldownTime);
            if (currentTime < cooldownEndTime) {
                return false;
            }
        }

        // Check usage limits
        if (this.maxUsageCount !== undefined && this.usageCount >= this.maxUsageCount) {
            return false;
        }

        return true;
    }

    /**
     * Serialize item to JSON
     */
    toJSON(): any {
        return {
            id: this.id,
            name: this.name,
            description: this.description,
            type: this.type,
            weight: this.weight,
            value: this.value,
            baseStats: this.baseStats,
            createdAt: this.createdAt,
            updatedAt: this.updatedAt,
            rarity: this.rarity,
            properties: this.properties,
            historyEvents: this.historyEvents,
            maxDurability: this.maxDurability,
            currentDurability: this.currentDurability,
            maxCharges: this.maxCharges,
            currentCharges: this.currentCharges,
            cooldownTime: this.cooldownTime,
            lastUsedTime: this.lastUsedTime,
            usageCount: this.usageCount,
            maxUsageCount: this.maxUsageCount,
            enhancementLevel: this.enhancementLevel
        };
    }

    /**
     * Create an item from JSON
     */
    static fromJSON(json: any): Item {
        const item = new Item({
            id: json.id,
            name: json.name,
            description: json.description,
            type: json.type,
            weight: json.weight,
            value: json.value,
            baseStats: json.baseStats,
            createdAt: new Date(json.createdAt),
            updatedAt: new Date(json.updatedAt)
        });

        item.rarity = json.rarity;
        item.properties = json.properties || [];
        item.historyEvents = json.historyEvents || [];
        item.maxDurability = json.maxDurability || 100;
        item.currentDurability = json.currentDurability || 100;
        item.maxCharges = json.maxCharges;
        item.currentCharges = json.currentCharges;
        item.cooldownTime = json.cooldownTime;
        item.lastUsedTime = json.lastUsedTime ? new Date(json.lastUsedTime) : undefined;
        item.usageCount = json.usageCount || 0;
        item.maxUsageCount = json.maxUsageCount;
        item.enhancementLevel = json.enhancementLevel || 0;

        return item;
    }
} 