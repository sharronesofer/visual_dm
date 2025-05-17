export type DamageEffectType = 'flash' | 'crack' | 'particle';

export interface DamageEffect {
    id: string;
    type: DamageEffectType;
    x: number;
    y: number;
    width: number;
    height: number;
    startTime: number;
    duration: number;
    color?: string;
    customRender?: (ctx: CanvasRenderingContext2D, progress: number, effect: DamageEffect) => void;
}

/**
 * DamageEventManager manages temporary visual effects for building damage events.
 * Effects are queued, updated, and rendered each frame.
 */
export class DamageEventManager {
    private effects: DamageEffect[] = [];

    /**
     * Trigger a new damage effect.
     * @param effect Effect parameters (type, position, duration, etc.)
     * @returns The effect ID
     */
    public triggerEffect(effect: Omit<DamageEffect, 'id' | 'startTime'>): string {
        const id = `${effect.type}-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`;
        this.effects.push({ ...effect, id, startTime: performance.now() });
        return id;
    }

    /**
     * Update all active effects (should be called each frame).
     * @param now Current timestamp (ms)
     */
    public update(now: number) {
        this.effects = this.effects.filter(effect => now - effect.startTime < effect.duration);
    }

    /**
     * Render all active effects.
     * @param ctx Canvas context
     * @param now Current timestamp (ms)
     */
    public render(ctx: CanvasRenderingContext2D, now: number) {
        for (const effect of this.effects) {
            const progress = Math.min(1, (now - effect.startTime) / effect.duration);
            if (effect.customRender) {
                effect.customRender(ctx, progress, effect);
                continue;
            }
            switch (effect.type) {
                case 'flash':
                    ctx.save();
                    ctx.globalAlpha = 0.5 * (1 - progress);
                    ctx.fillStyle = effect.color || 'yellow';
                    ctx.fillRect(effect.x, effect.y, effect.width, effect.height);
                    ctx.restore();
                    break;
                case 'crack':
                    ctx.save();
                    ctx.globalAlpha = 1 - progress;
                    ctx.strokeStyle = effect.color || 'black';
                    ctx.lineWidth = 2 + 2 * (1 - progress);
                    ctx.beginPath();
                    ctx.moveTo(effect.x, effect.y + effect.height / 2);
                    ctx.lineTo(effect.x + effect.width, effect.y + effect.height / 2);
                    ctx.stroke();
                    ctx.restore();
                    break;
                case 'particle':
                    ctx.save();
                    ctx.globalAlpha = 1 - progress;
                    ctx.fillStyle = effect.color || 'orange';
                    const radius = (effect.width / 4) * (1 - progress);
                    ctx.beginPath();
                    ctx.arc(effect.x + effect.width / 2, effect.y + effect.height / 2, radius, 0, 2 * Math.PI);
                    ctx.fill();
                    ctx.restore();
                    break;
                default:
                    // Unknown effect type: skip
                    break;
            }
        }
    }

    /**
     * Remove an effect by ID.
     */
    public removeEffect(id: string) {
        this.effects = this.effects.filter(e => e.id !== id);
    }

    /**
     * Clear all effects (e.g., on scene reset).
     */
    public clear() {
        this.effects = [];
    }
} 