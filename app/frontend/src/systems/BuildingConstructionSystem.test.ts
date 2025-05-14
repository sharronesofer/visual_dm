import { BuildingConstructionSystem } from '../../../src/systems/BuildingConstructionSystem';
import { BuildingPhysics, BUILDING_PHYSICS_DEFAULTS, MaterialType, BuildingStructure, BuildingElement, Wall, Door, Window } from '../core/interfaces/types/building';
import { Position } from '../core/interfaces/types/common';
import { BuildingStructuralSystem } from './BuildingStructuralSystem';

describe('BuildingConstructionSystem', () => {
    let construction: BuildingConstructionSystem;
    let structure: BuildingStructure;
    let defaultPhysics: BuildingPhysics;
    let structuralSystem: BuildingStructuralSystem;

    beforeEach(() => {
        defaultPhysics = { ...BUILDING_PHYSICS_DEFAULTS };
        structuralSystem = new BuildingStructuralSystem(defaultPhysics);
        construction = new BuildingConstructionSystem(defaultPhysics, structuralSystem);
        structure = {
            id: 'test-structure',
            elements: new Map(),
            integrity: 1
        };
    });

    it('adds a wall to the structure', () => {
        const pos: Position = { x: 0, y: 0 };
        const updated = construction.addWall(structure, pos, 'stone' as MaterialType, true);
        expect(updated.elements.size).toBe(1);
        const wall = Array.from(updated.elements.values())[0] as Wall;
        expect(wall.type).toBe('wall');
        expect(wall.isLoadBearing).toBe(true);
    });

    it('adds a door to the structure', () => {
        const pos: Position = { x: 1, y: 1 };
        const updated = construction.addDoor(structure, pos, 'wood' as MaterialType);
        expect(updated.elements.size).toBe(1);
        const door = Array.from(updated.elements.values())[0] as Door;
        expect(door.type).toBe('door');
    });

    it('adds a window to the structure', () => {
        const pos: Position = { x: 2, y: 2 };
        const updated = construction.addWindow(structure, pos, 'metal' as MaterialType);
        expect(updated.elements.size).toBe(1);
        const window = Array.from(updated.elements.values())[0] as Window;
        expect(window.type).toBe('window');
    });

    it('removes an element from the structure', () => {
        const pos: Position = { x: 0, y: 0 };
        let updated = construction.addWall(structure, pos, 'stone' as MaterialType, true);
        const wallId = Array.from(updated.elements.keys())[0];
        updated = construction.removeElement(updated, wallId);
        expect(updated.elements.size).toBe(0);
    });

    // Add more tests for integrity recalculation, error cases, and edge cases as needed
}); 