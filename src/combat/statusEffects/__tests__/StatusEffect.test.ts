import { StatusEffect, StatusEffectParams } from '../StatusEffect';

describe('StatusEffect', () => {
    const baseParams: StatusEffectParams = {
        id: 'burn',
        name: 'Burn',
        description: 'Deals fire damage over time.',
        type: 'damage',
        category: 'magical',
        durationType: 'turns',
        baseDuration: 3,
        maxStacks: 5,
        source: 'attacker1',
        target: 'target1',
        visualAssets: { icon: 'burn_icon.png', animation: 'burn_anim' },
    };

    it('constructs with correct defaults', () => {
        const effect = new StatusEffect(baseParams);
        expect(effect.id).toBe('burn');
        expect(effect.currentDuration).toBe(3);
        expect(effect.stackCount).toBe(1);
        expect(effect.maxStacks).toBe(5);
        expect(effect.source).toBe('attacker1');
        expect(effect.target).toBe('target1');
    });

    it('ticks duration and expires correctly', () => {
        const effect = new StatusEffect(baseParams);
        expect(effect.isExpired()).toBe(false);
        effect.tickDuration();
        expect(effect.currentDuration).toBe(2);
        effect.tickDuration();
        expect(effect.currentDuration).toBe(1);
        effect.tickDuration();
        expect(effect.currentDuration).toBe(0);
        expect(effect.isExpired()).toBe(true);
    });

    it('never expires if durationType is permanent', () => {
        const effect = new StatusEffect({ ...baseParams, durationType: 'permanent' });
        for (let i = 0; i < 10; i++) {
            effect.tickDuration();
        }
        expect(effect.isExpired()).toBe(false);
    });

    it('serializes and deserializes via JSON', () => {
        const effect = new StatusEffect(baseParams);
        const json = effect.toJSON();
        const restored = StatusEffect.fromJSON(json);
        expect(restored).toBeInstanceOf(StatusEffect);
        expect(restored.id).toBe(effect.id);
        expect(restored.currentDuration).toBe(effect.currentDuration);
        expect(restored.stackCount).toBe(effect.stackCount);
    });
});
