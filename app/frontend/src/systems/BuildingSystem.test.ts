import { BuildingSystem } from './../../../src/systems/BuildingSystem';
import { BuildingPhysics, BUILDING_PHYSICS_DEFAULTS, MaterialType, BuildingStructure, BuildingElement } from '../core/interfaces/types/building';
import { Position } from '../core/interfaces/types/common';
import { BuildingDamageSystem } from '../../../src/systems/BuildingDamageSystem';
import { BuildingConstructionSystem } from '../../../src/systems/BuildingConstructionSystem';
import { BuildingStructuralSystem } from './BuildingStructuralSystem';

describe('BuildingSystem', () => {
    let system: BuildingSystem;
    let defaultPhysics: BuildingPhysics;

    beforeEach(() => {
        defaultPhysics = { ...BUILDING_PHYSICS_DEFAULTS };
        system = new BuildingSystem(defaultPhysics);
    });

    it('creates a new structure and retrieves it', () => {
        const id = system.createStructure();
        const structure = system.getStructure(id);
        expect(structure).toBeDefined();
        expect(structure?.id).toBe(id);
    });

    it('deletes a structure', () => {
        const id = system.createStructure();
        expect(system.deleteStructure(id)).toBe(true);
        expect(system.getStructure(id)).toBeUndefined();
    });

    it('returns false when deleting a non-existent structure', () => {
        expect(system.deleteStructure('non-existent')).toBe(false);
    });

    it('adds a wall to a structure', () => {
        const id = system.createStructure();
        const pos: Position = { x: 0, y: 0 };
        const result = system.addWall(id, pos, 'stone' as MaterialType, true);
        expect(result).toBe(true);
        const structure = system.getStructure(id);
        expect(structure?.elements.size).toBe(1);
    });

    it('fails to add a wall to a non-existent structure', () => {
        const pos: Position = { x: 0, y: 0 };
        expect(system.addWall('bad-id', pos, 'stone' as MaterialType, true)).toBe(false);
    });

    it('adds a door to a structure', () => {
        const id = system.createStructure();
        const pos: Position = { x: 1, y: 1 };
        const result = system.addDoor(id, pos, 'wood' as MaterialType);
        expect(result).toBe(true);
        const structure = system.getStructure(id);
        expect(structure?.elements.size).toBe(1);
    });

    it('fails to add a door to a non-existent structure', () => {
        const pos: Position = { x: 1, y: 1 };
        expect(system.addDoor('bad-id', pos, 'wood' as MaterialType)).toBe(false);
    });

    // Add more tests for construction, damage, and integration as needed
});

describe('BuildingSystem Integration', () => {
    let system: BuildingSystem;
    let construction: BuildingConstructionSystem;
    let damage: BuildingDamageSystem;
    let structural: BuildingStructuralSystem;
    let defaultPhysics: BuildingPhysics;

    beforeEach(() => {
        defaultPhysics = { ...BUILDING_PHYSICS_DEFAULTS };
        structural = new BuildingStructuralSystem(defaultPhysics);
        construction = new BuildingConstructionSystem(defaultPhysics, structural);
        damage = new BuildingDamageSystem(defaultPhysics, structural);
        system = new BuildingSystem(defaultPhysics);
    });

    it('constructs, damages, and checks integrity of a structure', () => {
        const id = system.createStructure();
        const pos: Position = { x: 0, y: 0 };
        // Add two load-bearing walls
        system.addWall(id, pos, 'stone', true);
        system.addWall(id, { x: 1, y: 0 }, 'stone', true);
        let structure = system.getStructure(id)!;
        // Simulate damage
        const wallId = Array.from(structure.elements.keys())[0];
        structure = damage.applyDamage(structure, wallId, 50, 'impact');
        // Recalculate integrity
        const integrity = structural.calculateIntegrity(structure);
        expect(integrity).toBeLessThan(defaultPhysics.maxIntegrity);
        expect(integrity).toBeGreaterThan(0);
    });

    it('handles full destruction of a wall and integrity drops to zero', () => {
        const id = system.createStructure();
        system.addWall(id, { x: 0, y: 0 }, 'stone', true);
        system.addWall(id, { x: 1, y: 0 }, 'stone', true);
        let structure = system.getStructure(id)!;
        const wallId = Array.from(structure.elements.keys())[0];
        structure = damage.applyDamage(structure, wallId, 1000, 'impact');
        // Remove wall if health is zero
        if ((structure.elements.get(wallId) as any)?.health === 0) {
            structure.elements.delete(wallId);
        }
        const integrity = structural.calculateIntegrity(structure);
        expect(integrity).toBe(0);
    });
});

describe('BuildingSystem Performance and Regression', () => {
    let system: BuildingSystem;
    let construction: BuildingConstructionSystem;
    let damage: BuildingDamageSystem;
    let structural: BuildingStructuralSystem;
    let defaultPhysics: BuildingPhysics;

    beforeEach(() => {
        defaultPhysics = { ...BUILDING_PHYSICS_DEFAULTS };
        structural = new BuildingStructuralSystem(defaultPhysics);
        construction = new BuildingConstructionSystem(defaultPhysics, structural);
        damage = new BuildingDamageSystem(defaultPhysics, structural);
        system = new BuildingSystem(defaultPhysics);
    });

    it('handles a large structure efficiently', () => {
        const id = system.createStructure();
        // Add 1000 walls
        for (let i = 0; i < 1000; i++) {
            system.addWall(id, { x: i, y: 0 }, 'stone', true);
        }
        const structure = system.getStructure(id)!;
        const start = Date.now();
        const integrity = structural.calculateIntegrity(structure);
        const duration = Date.now() - start;
        expect(integrity).toBeGreaterThanOrEqual(0);
        expect(duration).toBeLessThan(1000); // Should complete in under 1s
    });

    it('regression: deleting a wall updates integrity correctly', () => {
        const id = system.createStructure();
        system.addWall(id, { x: 0, y: 0 }, 'stone', true);
        system.addWall(id, { x: 1, y: 0 }, 'stone', true);
        let structure = system.getStructure(id)!;
        // Remove one wall
        const wallId = Array.from(structure.elements.keys())[0];
        structure.elements.delete(wallId);
        const integrity = structural.calculateIntegrity(structure);
        // Should be zero if not enough load-bearing walls
        expect(integrity).toBe(0);
    });
}); 