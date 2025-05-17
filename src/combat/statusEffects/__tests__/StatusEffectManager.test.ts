import { StatusEffectManager } from '../StatusEffectManager';
import { StatusEffectParams } from '../StatusEffect';

describe('StatusEffectManager', () => {
    const burnParams: StatusEffectParams = {
        id: 'burn',
        name: 'Burn',
        description: 'Deals fire damage over time.',
        type: 'damage',
        category: 'magical',
        durationType: 'turns',
        baseDuration: 2,
        maxStacks: 5,
        stackingBehavior: 'additive',
        source: 'attacker1',
        target: 'target1',
        visualAssets: { icon: 'burn_icon.png', animation: 'burn_anim' },
    };
    const regenParams: StatusEffectParams = {
        id: 'regen',
        name: 'Regeneration',
        description: 'Restores health each turn.',
        type: 'buff',
        category: 'physical',
        durationType: 'turns',
        baseDuration: 3,
        maxStacks: 1,
        stackingBehavior: 'additive',
        source: 'attacker2',
        target: 'target1',
        visualAssets: { icon: 'regen_icon.png', animation: 'regen_anim' },
    };
    const stunParams: StatusEffectParams = {
        id: 'stun',
        name: 'Stun',
        description: 'Disables actions for a turn.',
        type: 'debuff',
        category: 'magical',
        durationType: 'turns',
        baseDuration: 1,
        maxStacks: 1,
        stackingBehavior: 'newest',
        source: 'attacker3',
        target: 'target1',
        visualAssets: { icon: 'stun_icon.png', animation: 'stun_anim' },
    };

    let manager: StatusEffectManager;
    beforeEach(() => {
        manager = new StatusEffectManager();
    });

    it('applies and retrieves effects for an entity', () => {
        manager.applyEffect('target1', burnParams);
        manager.applyEffect('target1', regenParams);
        const effects = manager.getActiveEffects('target1');
        expect(effects.length).toBe(2);
        expect(effects.some(e => e.id === 'burn')).toBe(true);
        expect(effects.some(e => e.id === 'regen')).toBe(true);
    });

    it('removes effects by ID', () => {
        manager.applyEffect('target1', burnParams);
        manager.applyEffect('target1', regenParams);
        const removed = manager.removeEffect('target1', 'burn');
        expect(removed).toBe(true);
        const effects = manager.getActiveEffects('target1');
        expect(effects.length).toBe(1);
        expect(effects[0].id).toBe('regen');
    });

    it('updates effects and removes expired ones', () => {
        manager.applyEffect('target1', { ...burnParams, baseDuration: 1 });
        manager.applyEffect('target1', regenParams);
        manager.updateEffects(); // burn: 0 (should be removed), regen: 2
        let effects = manager.getActiveEffects('target1');
        expect(effects.length).toBe(1);
        expect(effects[0].id).toBe('regen');
        manager.updateEffects(); // regen: 1
        effects = manager.getActiveEffects('target1');
        expect(effects.length).toBe(1);
        expect(effects[0].id).toBe('regen');
    });

    it('clears all effects from an entity', () => {
        manager.applyEffect('target1', burnParams);
        manager.applyEffect('target1', regenParams);
        manager.clearEffects('target1');
        expect(manager.getActiveEffects('target1').length).toBe(0);
    });

    it('serializes and deserializes manager state', () => {
        manager.applyEffect('target1', burnParams);
        manager.applyEffect('target2', regenParams);
        const json = manager.toJSON();
        const restored = StatusEffectManager.fromJSON(json);
        expect(restored.getActiveEffects('target1').length).toBe(1);
        expect(restored.getActiveEffects('target2').length).toBe(1);
        expect(restored.getActiveEffects('target1')[0].id).toBe('burn');
        expect(restored.getActiveEffects('target2')[0].id).toBe('regen');
    });

    it('handles additive stacking: increments stacks and enforces max', () => {
        const params = { ...burnParams, maxStacks: 2, stackingBehavior: 'additive', refreshDuration: true };
        manager.applyEffect('target1', params);
        manager.applyEffect('target1', params); // Should stack
        let effects = manager.getActiveEffects('target1');
        expect(effects.length).toBe(1);
        expect(effects[0].stackCount).toBe(2);
        // Exceed maxStacks
        manager.applyEffect('target1', params);
        effects = manager.getActiveEffects('target1');
        expect(effects[0].stackCount).toBe(2); // Still max
        // Duration refreshes
        effects[0].currentDuration = 1;
        manager.applyEffect('target1', params);
        expect(effects[0].currentDuration).toBe(params.baseDuration);
    });

    it('handles highest stacking: keeps effect with highest potency', () => {
        const high = { ...burnParams, id: 'high', stackingBehavior: 'highest', potency: 10 };
        const low = { ...burnParams, id: 'high', stackingBehavior: 'highest', potency: 5 };
        manager.applyEffect('target1', low);
        let effects = manager.getActiveEffects('target1');
        expect(effects.length).toBe(1);
        expect(effects[0].potency).toBe(5);
        // Apply higher potency
        manager.applyEffect('target1', high);
        effects = manager.getActiveEffects('target1');
        expect(effects.length).toBe(1);
        expect(effects[0].potency).toBe(10);
        // Apply lower potency again (should not replace)
        manager.applyEffect('target1', low);
        effects = manager.getActiveEffects('target1');
        expect(effects[0].potency).toBe(10);
    });

    it('handles newest stacking: always replaces with new effect', () => {
        const params = { ...stunParams, stackingBehavior: 'newest', baseDuration: 1 };
        manager.applyEffect('target1', params);
        let effects = manager.getActiveEffects('target1');
        expect(effects.length).toBe(1);
        expect(effects[0].currentDuration).toBe(1);
        // Apply again with different duration
        const params2 = { ...params, baseDuration: 3 };
        manager.applyEffect('target1', params2);
        effects = manager.getActiveEffects('target1');
        expect(effects.length).toBe(1);
        expect(effects[0].currentDuration).toBe(3);
    });

    it('cancels effects: burn cancels freeze', () => {
        const freeze = { ...burnParams, id: 'freeze', name: 'Freeze', stackingBehavior: 'newest' };
        manager.applyEffect('target1', freeze);
        expect(manager.getActiveEffects('target1').some(e => e.id === 'freeze')).toBe(true);
        const burn = { ...burnParams, id: 'burn', stackingBehavior: 'additive' };
        manager.applyEffect('target1', burn);
        expect(manager.getActiveEffects('target1').some(e => e.id === 'freeze')).toBe(false);
        expect(manager.getActiveEffects('target1').some(e => e.id === 'burn')).toBe(true);
    });

    it('combines effects: burn + oil = explosion', () => {
        const oil = { ...burnParams, id: 'oil', name: 'Oil', stackingBehavior: 'newest' };
        manager.applyEffect('target1', oil);
        expect(manager.getActiveEffects('target1').some(e => e.id === 'oil')).toBe(true);
        const burn = { ...burnParams, id: 'burn', stackingBehavior: 'additive' };
        manager.applyEffect('target1', burn);
        const effects = manager.getActiveEffects('target1');
        expect(effects.some(e => e.id === 'explosion')).toBe(true);
        expect(effects.some(e => e.id === 'oil')).toBe(false);
        expect(effects.some(e => e.id === 'burn')).toBe(false);
    });

    it('enhances effects: oil2 enhances burn2', () => {
        const oil2 = { ...burnParams, id: 'oil2', name: 'Oil2', stackingBehavior: 'newest' };
        manager.applyEffect('target1', oil2);
        const burn2 = { ...burnParams, id: 'burn2', name: 'Burn2', stackingBehavior: 'additive', potency: 2, baseDuration: 2 };
        manager.applyEffect('target1', burn2);
        const burnEffect = manager.getActiveEffects('target1').find(e => e.id === 'burn2');
        expect(burnEffect?.potency).toBe(4); // 2 * 2
        expect(burnEffect?.currentDuration).toBe(4); // 2 * 2
    });

    it('blocks effects with immunity: shield blocks stun', () => {
        const shield = { ...burnParams, id: 'shield', name: 'Shield', stackingBehavior: 'newest' };
        manager.applyEffect('target1', shield);
        const stun = { ...burnParams, id: 'stun', name: 'Stun', stackingBehavior: 'newest' };
        const result = manager.applyEffect('target1', stun);
        expect(result).toBeUndefined();
        expect(manager.getActiveEffects('target1').some(e => e.id === 'stun')).toBe(false);
    });

    it('getVisualFeedback returns correct visual assets and stack counts', () => {
        const burn = { ...burnParams, id: 'burn', stackingBehavior: 'additive', visualAssets: { icon: 'burn_icon.png', animation: 'burn_anim' } };
        const regen = { ...regenParams, id: 'regen', stackingBehavior: 'additive', visualAssets: { icon: 'regen_icon.png' } };
        manager.applyEffect('target1', burn);
        manager.applyEffect('target1', regen);
        // Stack burn
        manager.applyEffect('target1', burn);
        const visuals = manager.getVisualFeedback('target1');
        expect(visuals.length).toBe(2);
        const burnVisual = visuals.find(v => v.icon === 'burn_icon.png');
        expect(burnVisual).toBeDefined();
        expect(burnVisual?.animation).toBe('burn_anim');
        expect(burnVisual?.stackCount).toBe(2);
        const regenVisual = visuals.find(v => v.icon === 'regen_icon.png');
        expect(regenVisual).toBeDefined();
        expect(regenVisual?.animation).toBeUndefined();
        expect(regenVisual?.stackCount).toBeUndefined();
    });

    it('getVisualFeedback returns empty array if no effects', () => {
        const visuals = manager.getVisualFeedback('target1');
        expect(visuals).toEqual([]);
    });
});
