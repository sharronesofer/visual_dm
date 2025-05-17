import { BuildingDamageCalculator, BuildingIntegrity, BuildingMaterial } from './BuildingDamageCalculator';
import { ImpactLog } from './BuildingImpactDetector';

describe('BuildingDamageCalculator', () => {
    function makeIntegrity(material: BuildingMaterial, health = 100): BuildingIntegrity {
        return { id: 'b1', health, maxHealth: health, material };
    }

    it('applies fireball to wood (high damage)', () => {
        const impact: ImpactLog = { buildingId: 'b1', point: { x: 0, y: 0 }, angle: 0, projectileType: 'fireball' };
        const integrity = makeIntegrity('wood', 200);
        const result = BuildingDamageCalculator.applyDamage(impact, integrity, 20);
        expect(result.damage).toBeGreaterThan(30); // fireball + wood bonus
        expect(result.newHealth).toBeLessThan(200);
        expect(result.destroyed).toBe(false);
    });

    it('applies arrow to stone (low damage)', () => {
        const impact: ImpactLog = { buildingId: 'b1', point: { x: 0, y: 0 }, angle: 0, projectileType: 'arrow' };
        const integrity = makeIntegrity('stone');
        const result = BuildingDamageCalculator.applyDamage(impact, integrity, 10);
        expect(result.damage).toBeLessThan(10);
        expect(result.newHealth).toBeGreaterThan(90);
    });

    it('handles overkill (health cannot go below zero)', () => {
        const impact: ImpactLog = { buildingId: 'b1', point: { x: 0, y: 0 }, angle: 0, projectileType: 'fireball' };
        const integrity = makeIntegrity('wood', 5);
        const result = BuildingDamageCalculator.applyDamage(impact, integrity, 50);
        expect(result.newHealth).toBe(0);
        expect(result.destroyed).toBe(true);
    });

    it('applies angle effect (glancing hit does less damage)', () => {
        const impact: ImpactLog = { buildingId: 'b1', point: { x: 0, y: 0 }, angle: 80, projectileType: 'arrow' };
        const integrity = makeIntegrity('wood');
        const result = BuildingDamageCalculator.applyDamage(impact, integrity, 10);
        expect(result.damage).toBeLessThan(10);
    });

    it('applies velocity effect (higher velocity = more damage)', () => {
        const impact: ImpactLog = { buildingId: 'b1', point: { x: 0, y: 0 }, angle: 0, projectileType: 'arrow' };
        const integrity = makeIntegrity('wood');
        const low = BuildingDamageCalculator.applyDamage(impact, makeIntegrity('wood'), 5);
        const high = BuildingDamageCalculator.applyDamage(impact, makeIntegrity('wood'), 50);
        expect(high.damage).toBeGreaterThan(low.damage);
    });

    it('simulates persistence (serialize/deserialize)', () => {
        const integrity = makeIntegrity('stone', 80);
        const persisted = BuildingDamageCalculator.persistIntegrity(integrity);
        expect(persisted).toEqual(integrity);
        expect(persisted).not.toBe(integrity); // Should be a copy
    });
}); 