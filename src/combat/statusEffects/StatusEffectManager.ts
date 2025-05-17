import { StatusEffect, StatusEffectParams, StackingBehavior } from './StatusEffect';
import { EffectInteractionRegistry } from './EffectInteractionRegistry';

/**
 * Manages status effects for multiple entities in combat.
 */
export class StatusEffectManager {
    /**
     * Maps entityId to an array of active StatusEffect instances.
     */
    private activeEffects: Map<string, StatusEffect[]> = new Map();

    /**
     * Applies a status effect to an entity, handling stacking logic.
     * @param entityId The target entity's ID.
     * @param effectParams The parameters for the new status effect.
     */
    applyEffect(entityId: string, effectParams: StatusEffectParams): StatusEffect | undefined {
        const effect = new StatusEffect(effectParams);
        if (!this.activeEffects.has(entityId)) {
            this.activeEffects.set(entityId, []);
        }
        const effects = this.activeEffects.get(entityId)!;
        const registry = EffectInteractionRegistry.instance;

        // Immunity: block if present
        for (const e of effects) {
            if (registry.isImmune(e.id, effect.id)) {
                return undefined; // Blocked by immunity
            }
        }

        // Cancellation: remove cancelled effect
        const cancels = registry.getCancellationTarget(effect.id);
        if (cancels) {
            const idx = effects.findIndex(e => e.id === cancels);
            if (idx !== -1) {
                effects.splice(idx, 1);
            }
        }

        // Combination: replace both with result
        for (const e of effects) {
            const combo = registry.getCombinationResult(effect.id, e.id);
            if (combo) {
                // Remove both, add result
                const idx = effects.findIndex(x => x.id === e.id);
                if (idx !== -1) effects.splice(idx, 1);
                const comboParams = { ...effectParams, id: combo, name: combo, stackCount: 1 };
                const comboEffect = new StatusEffect(comboParams);
                effects.push(comboEffect);
                return comboEffect;
            }
        }

        // Stacking logic (as before)
        const existingIdx = effects.findIndex(e => e.id === effect.id);
        let resultEffect: StatusEffect;
        if (existingIdx !== -1) {
            const existing = effects[existingIdx];
            switch (effect.stackingBehavior) {
                case 'additive':
                    if (existing.stackCount < existing.maxStacks) {
                        existing.addStack();
                    } else if (existing.refreshDuration) {
                        existing.currentDuration = existing.baseDuration;
                    }
                    resultEffect = effects[existingIdx];
                    break;
                case 'highest':
                    if (effect.isHigherPotencyThan(existing)) {
                        effects[existingIdx] = effect;
                        resultEffect = effects[existingIdx];
                    } else {
                        resultEffect = effects[existingIdx];
                    }
                    break;
                case 'newest':
                    effects[existingIdx] = effect;
                    resultEffect = effects[existingIdx];
                    break;
            }
        } else {
            effects.push(effect);
            resultEffect = effects[effects.length - 1];
        }

        // Enhancement: boost potency/duration (both directions)
        // 1. Existing effect enhances new effect
        for (const e of effects) {
            const enh = registry.getEnhancement(e.id, resultEffect.id);
            if (enh) {
                resultEffect.potency = (resultEffect.potency ?? 1) * enh.potencyMultiplier;
                resultEffect.currentDuration = resultEffect.baseDuration * enh.potencyMultiplier;
            }
        }
        // 2. New effect enhances existing effect(s)
        for (const e of effects) {
            const enh = registry.getEnhancement(resultEffect.id, e.id);
            if (enh) {
                e.potency = (e.potency ?? 1) * enh.potencyMultiplier;
                e.currentDuration = e.baseDuration * enh.potencyMultiplier;
            }
        }
        return resultEffect;
    }

    /**
     * Removes a status effect from an entity by effect ID.
     * @param entityId The target entity's ID.
     * @param effectId The ID of the effect to remove.
     * @returns True if removed, false if not found.
     */
    removeEffect(entityId: string, effectId: string): boolean {
        const effects = this.activeEffects.get(entityId);
        if (!effects) return false;
        const initialLength = effects.length;
        const filtered = effects.filter(effect => effect.id !== effectId);
        this.activeEffects.set(entityId, filtered);
        return filtered.length !== initialLength;
    }

    /**
     * Modifies the stack count of an effect by a given amount.
     * Removes the effect if stack count drops to zero.
     */
    modifyStack(entityId: string, effectId: string, amount: number): void {
        const effects = this.activeEffects.get(entityId);
        if (!effects) return;
        const idx = effects.findIndex(e => e.id === effectId);
        if (idx === -1) return;
        const effect = effects[idx];
        if (amount > 0) {
            for (let i = 0; i < amount; i++) effect.addStack();
        } else if (amount < 0) {
            for (let i = 0; i < Math.abs(amount); i++) {
                if (effect.removeStack()) {
                    effects.splice(idx, 1);
                    break;
                }
            }
        }
    }

    /**
     * Resets stacks for an effect.
     */
    resetStacks(entityId: string, effectId: string): void {
        const effects = this.activeEffects.get(entityId);
        if (!effects) return;
        const effect = effects.find(e => e.id === effectId);
        if (effect) effect.resetStacks();
    }

    /**
     * Gets the stack count for a given effect on an entity.
     */
    getStackCount(entityId: string, effectId: string): number {
        const effects = this.activeEffects.get(entityId);
        if (!effects) return 0;
        const effect = effects.find(e => e.id === effectId);
        return effect ? effect.stackCount : 0;
    }

    /**
     * Updates all effects for all entities (e.g., at the end of a turn or time tick).
     * Expired effects are removed automatically.
     */
    updateEffects(): void {
        for (const [entityId, effects] of this.activeEffects.entries()) {
            for (const effect of effects) {
                effect.tickDuration();
            }
            // Remove expired effects
            this.activeEffects.set(
                entityId,
                effects.filter(effect => !effect.isExpired())
            );
        }
    }

    /**
     * Gets all active effects for a given entity.
     * @param entityId The entity's ID.
     */
    getActiveEffects(entityId: string): StatusEffect[] {
        return this.activeEffects.get(entityId) || [];
    }

    /**
     * Removes all effects from an entity.
     * @param entityId The entity's ID.
     */
    clearEffects(entityId: string): void {
        this.activeEffects.delete(entityId);
    }

    /**
     * Serializes all active effects for persistence.
     */
    toJSON(): object {
        const result: Record<string, object[]> = {};
        for (const [entityId, effects] of this.activeEffects.entries()) {
            result[entityId] = effects.map(e => e.toJSON());
        }
        return result;
    }

    /**
     * Loads effects from a serialized object.
     */
    static fromJSON(json: any): StatusEffectManager {
        const manager = new StatusEffectManager();
        for (const entityId in json) {
            manager.activeEffects.set(
                entityId,
                (json[entityId] as any[]).map(StatusEffect.fromJSON)
            );
        }
        return manager;
    }

    /**
     * Returns an array of visual feedback objects for all active effects on an entity.
     * Each object contains icon, animation, and stackCount (if >1).
     */
    getVisualFeedback(entityId: string): { icon: string; animation?: string; stackCount?: number }[] {
        const effects = this.getActiveEffects(entityId);
        return effects
            .filter(e => e.visualAssets && e.visualAssets.icon)
            .map(e => ({
                icon: e.visualAssets!.icon!,
                animation: e.visualAssets!.animation,
                stackCount: e.stackCount > 1 ? e.stackCount : undefined
            }));
    }
}
