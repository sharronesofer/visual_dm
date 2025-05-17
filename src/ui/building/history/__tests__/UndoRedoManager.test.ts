import { describe, it, expect, beforeEach } from 'vitest';
import { UndoRedoManager } from '../UndoRedoManager';
import { PlaceBuildingCommand } from '../PlaceBuildingCommand';
import { RemoveBuildingCommand } from '../RemoveBuildingCommand';
import { ModifyBuildingCommand } from '../ModifyBuildingCommand';
import { BuildingState, Building } from '../types';

describe('UndoRedoManager', () => {
    let state: BuildingState;
    let manager: UndoRedoManager;
    let buildingA: Building;
    let buildingB: Building;

    beforeEach(() => {
        state = { buildings: [] };
        manager = new UndoRedoManager(10);
        buildingA = { id: 'a', type: 'house', position: { x: 0, y: 0, z: 0 }, rotation: { x: 0, y: 0, z: 0, w: 1 } };
        buildingB = { id: 'b', type: 'tower', position: { x: 1, y: 1, z: 0 }, rotation: { x: 0, y: 0, z: 0, w: 1 } };
    });

    it('can place and undo/redo a building', () => {
        manager.executeCommand(new PlaceBuildingCommand(state, { building: buildingA }));
        expect(state.buildings.length).toBe(1);
        manager.undo();
        expect(state.buildings.length).toBe(0);
        manager.redo();
        expect(state.buildings.length).toBe(1);
    });

    it('can remove and undo/redo a building', () => {
        state.buildings.push(buildingA);
        manager.executeCommand(new RemoveBuildingCommand(state, { buildingId: 'a' }));
        expect(state.buildings.length).toBe(0);
        manager.undo();
        expect(state.buildings.length).toBe(1);
        manager.redo();
        expect(state.buildings.length).toBe(0);
    });

    it('can modify and undo/redo a building', () => {
        state.buildings.push(buildingA);
        manager.executeCommand(new ModifyBuildingCommand(state, { buildingId: 'a', newData: { type: 'castle' } }));
        expect(state.buildings[0].type).toBe('castle');
        manager.undo();
        expect(state.buildings[0].type).toBe('house');
        manager.redo();
        expect(state.buildings[0].type).toBe('castle');
    });

    it('clears redo stack on new action after undo', () => {
        manager.executeCommand(new PlaceBuildingCommand(state, { building: buildingA }));
        manager.undo();
        manager.executeCommand(new PlaceBuildingCommand(state, { building: buildingB }));
        expect(manager.canRedo()).toBe(false);
        expect(state.buildings.length).toBe(1);
        expect(state.buildings[0].id).toBe('b');
    });

    it('does not throw when undo/redo with empty stacks', () => {
        expect(() => manager.undo()).not.toThrow();
        expect(() => manager.redo()).not.toThrow();
    });
}); 