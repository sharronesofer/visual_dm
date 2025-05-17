import { BuildingDamageVisualizer, VisualEffect, VisualState } from './BuildingDamageVisualizer';
import { DamageResult } from './BuildingDamageCalculator';
import { BuildingMaterial } from './BuildingDamageCalculator';

describe('BuildingDamageVisualizer', () => {
    function makeDamageResult(damage: number, newHealth: number): DamageResult {
        return { buildingId: 'b1', damage, newHealth, destroyed: newHealth === 0 };
    }

    it('maps fireball on wood to scorch_wood effect, severe', () => {
        const result = makeDamageResult(100, 50); // 100/(100+50) = 0.66 -> severe
        const effects = BuildingDamageVisualizer.determineVisualEffects(result, 'fireball', 'wood', { x: 1, y: 2 });
        expect(effects.length).toBe(1);
        expect(effects[0].type).toBe('scorch_wood');
        expect(effects[0].severity).toBe('severe');
        expect(effects[0].sound).toBe('fire_blast');
    });

    it('maps arrow on stone to splinter_stone effect, minor', () => {
        const result = makeDamageResult(5, 95); // 5/(5+95) = 0.05 -> minor
        const effects = BuildingDamageVisualizer.determineVisualEffects(result, 'arrow', 'stone', { x: 0, y: 0 });
        expect(effects[0].type).toBe('splinter_stone');
        expect(effects[0].severity).toBe('minor');
        expect(effects[0].sound).toBe('wood_hit');
    });

    it('returns empty array for zero damage', () => {
        const result = makeDamageResult(0, 100);
        const effects = BuildingDamageVisualizer.determineVisualEffects(result, 'arrow', 'wood', { x: 0, y: 0 });
        expect(effects.length).toBe(0);
    });

    it('returns correct visual state for various health ratios', () => {
        expect(BuildingDamageVisualizer.getBuildingVisualState(100, 100)).toBe('undamaged');
        expect(BuildingDamageVisualizer.getBuildingVisualState(70, 100)).toBe('damaged');
        expect(BuildingDamageVisualizer.getBuildingVisualState(20, 100)).toBe('heavilyDamaged');
        expect(BuildingDamageVisualizer.getBuildingVisualState(0, 100)).toBe('destroyed');
    });

    it('handles unknown projectile type with generic effect', () => {
        const result = makeDamageResult(20, 80);
        const effects = BuildingDamageVisualizer.determineVisualEffects(result, 'unknown', 'metal', { x: 5, y: 5 });
        expect(effects[0].type).toBe('impact_metal');
        expect(effects[0].sound).toBe('impact_generic');
    });
}); 