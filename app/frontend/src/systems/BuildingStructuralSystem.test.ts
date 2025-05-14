import { BuildingStructuralSystem } from './BuildingStructuralSystem';
import {
    BuildingStructure,
    BuildingElement,
    Wall,
    BuildingPhysics,
    BUILDING_PHYSICS_DEFAULTS
} from '../../core/interfaces/types/building';
import { Position } from '../../core/interfaces/types/common';

describe('BuildingStructuralSystem', () => {
    let system: BuildingStructuralSystem;
    let defaultPhysics: BuildingPhysics & { maxIntegrity: number; minSupportPoints: number };

    beforeEach(() => {
        defaultPhysics = {
            ...BUILDING_PHYSICS_DEFAULTS,
            maxIntegrity: 100,
            minSupportPoints: 2
        };
        system = new BuildingStructuralSystem(defaultPhysics);
    });

    function makeWall(id: string, position: Position, isLoadBearing = true, health = 100, maxHealth = 100, material: 'wood' | 'stone' | 'metal' | 'reinforced' = 'stone'): Wall {
        return {
            id,
            type: 'wall',
            position,
            isLoadBearing,
            health,
            maxHealth,
            material,
            thickness: 1,
            height: 3
        };
    }

    function makeStructure(elements: BuildingElement[], supportPoints: Position[] = [{ x: 0, y: 0 }]): BuildingStructure & { supportPoints: Position[] } {
        const map = new Map(elements.map(e => [e.id, e]));
        return {
            id: 'structure-1',
            elements: map,
            supportPoints,
            integrity: 1
        };
    }

    it('returns 0 integrity if not enough load-bearing walls', () => {
        const structure = makeStructure([
            makeWall('w1', { x: 0, y: 0 }, false)
        ]);
        expect(system.calculateIntegrity(structure)).toBe(0);
    });

    it('calculates integrity with sufficient support points and healthy elements', () => {
        const wall1 = makeWall('w1', { x: 0, y: 0 });
        const wall2 = makeWall('w2', { x: 1, y: 0 });
        const structure = makeStructure([wall1, wall2], [{ x: 0, y: 0 }, { x: 1, y: 0 }]);
        const integrity = system.calculateIntegrity(structure);
        expect(integrity).toBeGreaterThan(0);
        expect(integrity).toBeLessThanOrEqual(defaultPhysics.maxIntegrity);
    });

    it('reduces integrity if element health is low', () => {
        const wall1 = makeWall('w1', { x: 0, y: 0 }, true, 50, 100);
        const wall2 = makeWall('w2', { x: 1, y: 0 }, true, 100, 100);
        const structure = makeStructure([wall1, wall2], [{ x: 0, y: 0 }, { x: 1, y: 0 }]);
        const integrity = system.calculateIntegrity(structure);
        expect(integrity).toBeLessThan(defaultPhysics.maxIntegrity);
    });

    it('reduces integrity if weight distribution is poor', () => {
        const wall1 = makeWall('w1', { x: 0, y: 0 });
        const wall2 = makeWall('w2', { x: 100, y: 100 });
        const structure = makeStructure([wall1, wall2], [{ x: 0, y: 0 }]);
        const integrity = system.calculateIntegrity(structure);
        expect(integrity).toBeLessThan(defaultPhysics.maxIntegrity);
    });

    it('returns maxIntegrity if all factors are optimal', () => {
        const wall1 = makeWall('w1', { x: 0, y: 0 });
        const wall2 = makeWall('w2', { x: 1, y: 0 });
        const structure = makeStructure([wall1, wall2], [{ x: 0, y: 0 }, { x: 1, y: 0 }]);
        // Patch system to always return 1 for health and weight factors
        jest.spyOn<any, any>(system, 'calculateElementsHealthFactor').mockReturnValue(1);
        jest.spyOn<any, any>(system, 'calculateWeightDistribution').mockReturnValue(1);
        const integrity = system.calculateIntegrity(structure);
        expect(integrity).toBe(defaultPhysics.maxIntegrity);
    });

    it('predicts modification impact correctly', () => {
        const wall1 = makeWall('w1', { x: 0, y: 0 });
        const wall2 = makeWall('w2', { x: 1, y: 0 });
        const structure = makeStructure([wall1, wall2], [{ x: 0, y: 0 }, { x: 1, y: 0 }]);
        const newHealth = 50;
        const predicted = system.predictModificationImpact(structure, wall1, newHealth);
        expect(predicted).toBeLessThan(system.calculateIntegrity(structure));
    });

    it('handles empty structure gracefully', () => {
        const structure = makeStructure([], []);
        expect(system.calculateIntegrity(structure)).toBe(0);
    });

    it('handles edge case: all elements at zero health', () => {
        const wall1 = makeWall('w1', { x: 0, y: 0 }, true, 0, 100);
        const wall2 = makeWall('w2', { x: 1, y: 0 }, true, 0, 100);
        const structure = makeStructure([wall1, wall2], [{ x: 0, y: 0 }, { x: 1, y: 0 }]);
        expect(system.calculateIntegrity(structure)).toBe(0);
    });

    it('handles edge case: support points far from center of mass', () => {
        const wall1 = makeWall('w1', { x: 0, y: 0 });
        const wall2 = makeWall('w2', { x: 100, y: 100 });
        const structure = makeStructure([wall1, wall2], [{ x: 0, y: 0 }]);
        const integrity = system.calculateIntegrity(structure);
        expect(integrity).toBeLessThan(defaultPhysics.maxIntegrity);
    });

    it('performs under large model (performance test)', () => {
        const elements: BuildingElement[] = [];
        for (let i = 0; i < 10000; i++) {
            elements.push(makeWall(`w${i}`, { x: i % 100, y: Math.floor(i / 100) }));
        }
        const supportPoints = Array.from({ length: 100 }, (_, i) => ({ x: i, y: 0 }));
        const structure = makeStructure(elements, supportPoints);
        const start = Date.now();
        const integrity = system.calculateIntegrity(structure);
        const duration = Date.now() - start;
        expect(integrity).toBeGreaterThanOrEqual(0);
        expect(duration).toBeLessThan(1000); // Should complete in under 1s
    });

    // Add more integration tests as needed for partial scene loading, streaming, and system interactions
}); 