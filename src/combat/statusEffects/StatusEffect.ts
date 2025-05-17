// StatusEffect.ts
// Core class for individual status effect instances

export type StatusEffectDurationType = 'turns' | 'time' | 'permanent';
export type StackingBehavior = 'additive' | 'highest' | 'newest';

export interface StatusEffectParams {
    id: string;
    name: string;
    description: string;
    type: string; // e.g., 'buff', 'debuff', 'damage', etc.
    category: string; // e.g., 'physical', 'magical', etc.
    durationType: StatusEffectDurationType;
    baseDuration: number;
    currentDuration?: number;
    stackCount?: number;
    maxStacks: number;
    source: string; // entityId or reference
    target: string; // entityId or reference
    visualAssets?: {
        icon?: string;
        animation?: string;
    };
    stackingBehavior: StackingBehavior;
    refreshDuration?: boolean; // Whether duration refreshes on stack
    potency?: number; // For 'highest' stacking
}

/**
 * Represents a single status effect instance applied to an entity.
 */
export class StatusEffect {
    id: string;
    name: string;
    description: string;
    type: string;
    category: string;
    durationType: StatusEffectDurationType;
    baseDuration: number;
    currentDuration: number;
    stackCount: number;
    maxStacks: number;
    source: string;
    target: string;
    visualAssets?: {
        icon?: string;
        animation?: string;
    };
    stackingBehavior: StackingBehavior;
    refreshDuration: boolean;
    potency?: number;

    constructor(params: StatusEffectParams) {
        this.id = params.id;
        this.name = params.name;
        this.description = params.description;
        this.type = params.type;
        this.category = params.category;
        this.durationType = params.durationType;
        this.baseDuration = params.baseDuration;
        this.currentDuration =
            params.currentDuration !== undefined ? params.currentDuration : params.baseDuration;
        this.stackCount = params.stackCount !== undefined ? params.stackCount : 1;
        this.maxStacks = params.maxStacks;
        this.source = params.source;
        this.target = params.target;
        this.visualAssets = params.visualAssets;
        this.stackingBehavior = params.stackingBehavior;
        this.refreshDuration = params.refreshDuration ?? true;
        this.potency = params.potency;
    }

    /**
     * Reduces the duration by one tick (turn or time unit).
     */
    tickDuration(): void {
        if (this.durationType !== 'permanent' && this.currentDuration > 0) {
            this.currentDuration -= 1;
        }
    }

    /**
     * Returns true if the effect has expired and should be removed.
     */
    isExpired(): boolean {
        if (this.durationType === 'permanent') return false;
        return this.currentDuration <= 0;
    }

    /**
     * Serializes the effect to JSON.
     */
    toJSON(): object {
        return {
            id: this.id,
            name: this.name,
            description: this.description,
            type: this.type,
            category: this.category,
            durationType: this.durationType,
            baseDuration: this.baseDuration,
            currentDuration: this.currentDuration,
            stackCount: this.stackCount,
            maxStacks: this.maxStacks,
            source: this.source,
            target: this.target,
            visualAssets: this.visualAssets,
            stackingBehavior: this.stackingBehavior,
            refreshDuration: this.refreshDuration,
            potency: this.potency,
        };
    }

    /**
     * Creates a StatusEffect from a JSON object.
     */
    static fromJSON(json: any): StatusEffect {
        return new StatusEffect(json);
    }

    /**
     * Determines if this effect can stack with another effect instance.
     */
    canStackWith(other: StatusEffect): boolean {
        return (
            this.id === other.id &&
            this.stackingBehavior === 'additive' &&
            this.stackCount < this.maxStacks
        );
    }

    /**
     * Adds a stack, enforcing maxStacks. Optionally refreshes duration.
     */
    addStack(): void {
        if (this.stackingBehavior === 'additive' && this.stackCount < this.maxStacks) {
            this.stackCount++;
            if (this.refreshDuration) {
                this.currentDuration = this.baseDuration;
            }
        }
    }

    /**
     * Removes a stack. Returns true if effect should be removed.
     */
    removeStack(): boolean {
        if (this.stackingBehavior === 'additive' && this.stackCount > 1) {
            this.stackCount--;
            return false;
        }
        return true; // Remove effect if no stacks left
    }

    /**
     * Resets stack count to 1 and duration to base.
     */
    resetStacks(): void {
        this.stackCount = 1;
        this.currentDuration = this.baseDuration;
    }

    /**
     * For 'highest' stacking: returns true if this effect is higher potency than other.
     */
    isHigherPotencyThan(other: StatusEffect): boolean {
        if (this.potency !== undefined && other.potency !== undefined) {
            return this.potency > other.potency;
        }
        return false;
    }
}
