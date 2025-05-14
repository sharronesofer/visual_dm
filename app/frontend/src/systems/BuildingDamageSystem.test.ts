import { BuildingDamageSystem } from '../../../src/systems/BuildingDamageSystem';
import { BuildingPhysics, BUILDING_PHYSICS_DEFAULTS, MaterialType, BuildingStructure, BuildingElement, Wall } from '../core/interfaces/types/building';
import { Position } from '../core/interfaces/types/common';
import { BuildingStructuralSystem } from './BuildingStructuralSystem';

describe('BuildingDamageSystem', () => {
    let damageSystem: BuildingDamageSystem;
    let structure: BuildingStructure;
    let defaultPhysics: BuildingPhysics;
    let structuralSystem: BuildingStructuralSystem;

    function makeWall(id: string, position: Position, health = 100, maxHealth = 100, isLoadBearing = true, material: MaterialType = 'stone'): Wall {
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

    beforeEach(() => {
        defaultPhysics = { ...BUILDING_PHYSICS_DEFAULTS };
        structuralSystem = new BuildingStructuralSystem(defaultPhysics);
        damageSystem = new BuildingDamageSystem(defaultPhysics, structuralSystem);
        structure = {
            id: 'test-structure',
            elements: new Map(),
            integrity: 1
        };
    });

    it('applies impact damage to a wall', () => {
        const wall = makeWall('w1', { x: 0, y: 0 });
        structure.elements.set(wall.id, wall);
        const updated = damageSystem.applyDamage(structure, 'w1', 30, 'impact');
        const damagedWall = updated.elements.get('w1') as Wall;
        expect(damagedWall.health).toBe(70);
    });

    it('does not reduce health below zero', () => {
        const wall = makeWall('w1', { x: 0, y: 0 }, 10);
        structure.elements.set(wall.id, wall);
        const updated = damageSystem.applyDamage(structure, 'w1', 50, 'impact');
        const damagedWall = updated.elements.get('w1') as Wall;
        expect(damagedWall.health).toBe(0);
    });

    it('returns unchanged structure if element does not exist', () => {
        const updated = damageSystem.applyDamage(structure, 'nonexistent', 10, 'impact');
        expect(updated).toEqual(structure);
    });

    // Add more tests for fire/explosion damage, error cases, and integration as needed
}); 