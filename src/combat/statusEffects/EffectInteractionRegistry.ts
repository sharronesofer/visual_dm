import fs from 'fs';
import path from 'path';

interface Cancellation {
    canceller: string;
    cancels: string;
}
interface Combination {
    effectA: string;
    effectB: string;
    result: string;
}
interface Enhancement {
    enhancer: string;
    target: string;
    potencyMultiplier: number;
}
interface Immunity {
    immunity: string;
    blocks: string;
}
interface Priority {
    effect: string;
    priority: number;
}

interface EffectInteractionsConfig {
    cancellations: Cancellation[];
    combinations: Combination[];
    enhancements: Enhancement[];
    immunities: Immunity[];
    priorities: Priority[];
}

/**
 * Registry for effect interactions: cancellations, combinations, enhancements, immunities, priorities.
 */
export class EffectInteractionRegistry {
    private static _instance: EffectInteractionRegistry | null = null;
    private config: EffectInteractionsConfig;

    private constructor() {
        this.config = this.loadConfig();
    }

    static get instance(): EffectInteractionRegistry {
        if (!this._instance) {
            this._instance = new EffectInteractionRegistry();
        }
        return this._instance;
    }

    private loadConfig(): EffectInteractionsConfig {
        const filePath = path.join(__dirname, 'effectInteractions.json');
        if (!fs.existsSync(filePath)) {
            throw new Error(`Effect interactions file not found: ${filePath}`);
        }
        const raw = fs.readFileSync(filePath, 'utf-8');
        return JSON.parse(raw);
    }

    /**
     * Returns the effect ID that would be cancelled by the given effect, or undefined.
     */
    getCancellationTarget(cancellerId: string): string | undefined {
        const found = this.config.cancellations.find(c => c.canceller === cancellerId);
        return found?.cancels;
    }

    /**
     * Returns the result effect ID if two effects combine, or undefined.
     */
    getCombinationResult(effectA: string, effectB: string): string | undefined {
        const found = this.config.combinations.find(
            c => (c.effectA === effectA && c.effectB === effectB) || (c.effectA === effectB && c.effectB === effectA)
        );
        return found?.result;
    }

    /**
     * Returns the enhancement config if enhancer applies to target, or undefined.
     */
    getEnhancement(enhancerId: string, targetId: string): Enhancement | undefined {
        return this.config.enhancements.find(e => e.enhancer === enhancerId && e.target === targetId);
    }

    /**
     * Returns true if immunity blocks the effect.
     */
    isImmune(immunityId: string, effectId: string): boolean {
        return this.config.immunities.some(i => i.immunity === immunityId && i.blocks === effectId);
    }

    /**
     * Returns the priority for an effect, or 0 if not found.
     */
    getPriority(effectId: string): number {
        return this.config.priorities.find(p => p.effect === effectId)?.priority ?? 0;
    }
}
