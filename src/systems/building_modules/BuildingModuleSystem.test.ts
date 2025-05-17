import { BuildingModuleSystem } from './BuildingModuleSystem';
import { FloorModule } from './FloorModule';
import { RoofModule } from './RoofModule';
import { WallModule } from './WallModule';
import { BuildingModule } from './BuildingModule';
import { Position } from '../../core/interfaces/types/common';
import { ColumnModule } from './ColumnModule';
import { BeamModule } from './BeamModule';
import { FoundationModule } from './FoundationModule';
import { StairModule } from './StairModule';
import { FurnitureModule, FurnitureType } from './FurnitureModule';
import { PartitionModule } from './PartitionModule';
import { LoadCalculationManager } from './LoadCalculationManager';
import { MaterialFatigueSystem, WeatherType } from './MaterialFatigueSystem';

describe('BuildingModuleSystem modular placement', () => {
    let system: BuildingModuleSystem;
    let grid: Map<string, BuildingModule>;

    beforeEach(() => {
        system = BuildingModuleSystem.getInstance();
        grid = new Map();
    });

    it('should place a floor module with valid support', () => {
        const supportWall = new WallModule('wall1', { x: 0, y: 0 }, 100, 'stone', 0.01, 0.05, 1, 3, true);
        const floor = new FloorModule('floor1', { x: 0, y: 1 }, 100, 'wood', 0.01, 0.05, 1, 1);
        const supportModules = [supportWall];
        const placed = system.placeFloor(floor, grid, supportModules);
        expect(placed).toBe(true);
        expect(grid.get('0,1')).toBe(floor);
    });

    it('should not place a floor module without valid support', () => {
        const floor = new FloorModule('floor2', { x: 1, y: 1 }, 100, 'wood', 0.01, 0.05, 1, 1);
        const supportModules: BuildingModule[] = [];
        const placed = system.placeFloor(floor, grid, supportModules);
        expect(placed).toBe(false);
        expect(grid.get('1,1')).toBeUndefined();
    });

    it('should connect adjacent floor modules', () => {
        const supportWall = new WallModule('wall2', { x: 0, y: 0 }, 100, 'stone', 0.01, 0.05, 1, 3, true);
        const floorA = new FloorModule('floorA', { x: 2, y: 2 }, 100, 'wood', 0.01, 0.05, 1, 1);
        const floorB = new FloorModule('floorB', { x: 2, y: 3 }, 100, 'wood', 0.01, 0.05, 1, 1);
        const supportModules = [supportWall];
        system.placeFloor(floorA, grid, supportModules);
        system.placeFloor(floorB, grid, supportModules);
        // The connection logic is a stub, but we can check both are in the grid
        expect(grid.get('2,2')).toBe(floorA);
        expect(grid.get('2,3')).toBe(floorB);
        // TODO: When connection logic is implemented, check adjacency references
    });

    it('should place a roof module with valid support', () => {
        const supportWall = new WallModule('wall3', { x: 0, y: 0 }, 100, 'stone', 0.01, 0.05, 1, 3, true);
        const roof = new RoofModule('roof1', { x: 0, y: 1 }, 100, 'wood', 0.01, 0.05, 30);
        const supportModules = [supportWall];
        const placed = system.placeRoof(roof, grid, supportModules);
        expect(placed).toBe(true);
        expect(grid.get('0,1')).toBe(roof);
    });

    it('should not place a roof module without valid support', () => {
        const roof = new RoofModule('roof2', { x: 1, y: 1 }, 100, 'wood', 0.01, 0.05, 30);
        const supportModules: BuildingModule[] = [];
        const placed = system.placeRoof(roof, grid, supportModules);
        expect(placed).toBe(false);
        expect(grid.get('1,1')).toBeUndefined();
    });

    it('should place a column module with valid support', () => {
        const foundation = new FoundationModule('foundation1', { x: 5, y: 5 }, 200, 'stone', 0.01, 0.05, 2, 2);
        const column = new ColumnModule('column1', { x: 5, y: 6 }, 100, 'stone', 0.01, 0.05, 3, 0.5, 120);
        const supportModules = [foundation];
        const placed = system.placeColumn(column, grid, supportModules);
        expect(placed).toBe(true);
        expect(grid.get('5,6')).toBe(column);
    });

    it('should not place a column module without valid support', () => {
        const column = new ColumnModule('column2', { x: 6, y: 6 }, 100, 'stone', 0.01, 0.05, 3, 0.5, 120);
        const supportModules: BuildingModule[] = [];
        const placed = system.placeColumn(column, grid, supportModules);
        expect(placed).toBe(false);
        expect(grid.get('6,6')).toBeUndefined();
    });

    it('should place a beam module with valid support', () => {
        const column = new ColumnModule('column3', { x: 7, y: 7 }, 100, 'stone', 0.01, 0.05, 3, 0.5, 120);
        const beam = new BeamModule('beam1', { x: 7, y: 8 }, 100, 'wood', 0.01, 0.05, 4, 0.3, 80);
        const supportModules = [column];
        const placed = system.placeBeam(beam, grid, supportModules);
        expect(placed).toBe(true);
        expect(grid.get('7,8')).toBe(beam);
    });

    it('should not place a beam module without valid support', () => {
        const beam = new BeamModule('beam2', { x: 8, y: 8 }, 100, 'wood', 0.01, 0.05, 4, 0.3, 80);
        const supportModules: BuildingModule[] = [];
        const placed = system.placeBeam(beam, grid, supportModules);
        expect(placed).toBe(false);
        expect(grid.get('8,8')).toBeUndefined();
    });

    it('should connect adjacent columns and beams (stub)', () => {
        const foundation = new FoundationModule('foundation2', { x: 9, y: 9 }, 200, 'stone', 0.01, 0.05, 2, 2);
        const columnA = new ColumnModule('columnA', { x: 9, y: 10 }, 100, 'stone', 0.01, 0.05, 3, 0.5, 120);
        const columnB = new ColumnModule('columnB', { x: 9, y: 11 }, 100, 'stone', 0.01, 0.05, 3, 0.5, 120);
        const supportModules = [foundation];
        system.placeColumn(columnA, grid, supportModules);
        system.placeColumn(columnB, grid, supportModules);
        expect(grid.get('9,10')).toBe(columnA);
        expect(grid.get('9,11')).toBe(columnB);
        // TODO: When connection logic is implemented, check adjacency references
    });

    it('should place a stair module with valid floor connection', () => {
        const floorA = new FloorModule('floorA', { x: 10, y: 10 }, 100, 'wood', 0.01, 0.05, 1, 1);
        const floorB = new FloorModule('floorB', { x: 10, y: 11 }, 100, 'wood', 0.01, 0.05, 1, 1);
        const stair = new StairModule('stair1', { x: 10, y: 10 }, 100, 'wood', 0.01, 0.05, 1, 1, 10, ['floorA', 'floorB']);
        // Stub always returns true for validatePlacement
        const placed = system.placeStair(stair, grid, floorA, floorB);
        expect(placed).toBe(true);
        expect(grid.get('10,10')).toBe(stair);
    });

    it('should not place a stair module with invalid floor connection', () => {
        // Override validatePlacement to return false
        const floorA = new FloorModule('floorA', { x: 11, y: 10 }, 100, 'wood', 0.01, 0.05, 1, 1);
        const floorB = new FloorModule('floorB', { x: 11, y: 11 }, 100, 'wood', 0.01, 0.05, 1, 1);
        const stair = new StairModule('stair2', { x: 11, y: 10 }, 100, 'wood', 0.01, 0.05, 1, 1, 10, ['floorA', 'floorB']);
        const originalValidate = StairModule.validatePlacement;
        StairModule.validatePlacement = () => false;
        const placed = system.placeStair(stair, grid, floorA, floorB);
        expect(placed).toBe(false);
        expect(grid.get('11,10')).toBeUndefined();
        StairModule.validatePlacement = originalValidate;
    });

    it('should connect stairs to floors (stub)', () => {
        const floorA = new FloorModule('floorA', { x: 12, y: 10 }, 100, 'wood', 0.01, 0.05, 1, 1);
        const floorB = new FloorModule('floorB', { x: 12, y: 11 }, 100, 'wood', 0.01, 0.05, 1, 1);
        const stair = new StairModule('stair3', { x: 12, y: 10 }, 100, 'wood', 0.01, 0.05, 1, 1, 10, ['floorA', 'floorB']);
        system.placeStair(stair, grid, floorA, floorB);
        expect(grid.get('12,10')).toBe(stair);
        // TODO: When connection logic is implemented, check floor references
    });

    it('should place a furniture module with valid position', () => {
        const furniture = new FurnitureModule('furn1', { x: 20, y: 20 }, 50, 'wood', 0.01, 0.05, 'chair', { width: 1, height: 1, depth: 1 }, true);
        // Stub always returns true for validatePlacement
        const placed = system.placeFurniture(furniture, grid);
        expect(placed).toBe(true);
        expect(grid.get('20,20')).toBe(furniture);
    });

    it('should not place a furniture module with invalid position', () => {
        // Override validatePlacement to return false
        const furniture = new FurnitureModule('furn2', { x: 21, y: 20 }, 50, 'wood', 0.01, 0.05, 'table', { width: 2, height: 1, depth: 2 }, true);
        const originalValidate = FurnitureModule.validatePlacement;
        FurnitureModule.validatePlacement = () => false;
        const placed = system.placeFurniture(furniture, grid);
        expect(placed).toBe(false);
        expect(grid.get('21,20')).toBeUndefined();
        FurnitureModule.validatePlacement = originalValidate;
    });

    it('should allow basic interaction with furniture (stub)', () => {
        const furniture = new FurnitureModule('furn3', { x: 22, y: 20 }, 50, 'wood', 0.01, 0.05, 'sofa', { width: 2, height: 1, depth: 1 }, true);
        expect(furniture.interact('sit')).toBe(true);
    });

    it('should place a partition module with valid position', () => {
        const partition = new PartitionModule('part1', { x: 30, y: 30 }, 80, 'wood', 0.01, 0.05, 0.2, 2.5, true, true, false);
        // Stub always returns true for validatePlacement
        const placed = system.placePartition(partition, grid);
        expect(placed).toBe(true);
        expect(grid.get('30,30')).toBe(partition);
    });

    it('should not place a partition module with invalid position', () => {
        // Override validatePlacement to return false
        const partition = new PartitionModule('part2', { x: 31, y: 30 }, 80, 'wood', 0.01, 0.05, 0.2, 2.5, true, false, true);
        const originalValidate = PartitionModule.validatePlacement;
        PartitionModule.validatePlacement = () => false;
        const placed = system.placePartition(partition, grid);
        expect(placed).toBe(false);
        expect(grid.get('31,30')).toBeUndefined();
        PartitionModule.validatePlacement = originalValidate;
    });

    it('should place a partition module with doorway and window', () => {
        const partition = new PartitionModule('part3', { x: 32, y: 30 }, 80, 'wood', 0.01, 0.05, 0.2, 2.5, true, true, true);
        const placed = system.placePartition(partition, grid);
        expect(placed).toBe(true);
        expect(grid.get('32,30')).toBe(partition);
    });
});

describe('LoadCalculationManager', () => {
    let manager: LoadCalculationManager;
    let dummyElement: any;

    beforeEach(() => {
        manager = new LoadCalculationManager();
        dummyElement = { moduleId: 'dummy1', getModuleType: () => 'column' };
    });

    it('should register and unregister elements', () => {
        manager.registerElement(dummyElement);
        expect(manager['elements'].has('dummy1')).toBe(true);
        manager.unregisterElement('dummy1');
        expect(manager['elements'].has('dummy1')).toBe(false);
    });

    it('should calculate load distribution for registered elements', () => {
        manager.registerElement(dummyElement);
        const distribution = manager.calculateLoadDistribution();
        expect(distribution.has('dummy1')).toBe(true);
        const data = distribution.get('dummy1');
        expect(typeof data?.load).toBe('number');
        expect(typeof data?.stress).toBe('number');
        expect(typeof data?.redundancy).toBe('boolean');
    });

    it('should emit redundancy event', () => {
        manager.registerElement(dummyElement);
        let eventFired = false;
        manager.addEventListener(event => {
            if (event.type === 'redundancy-activated' && event.elementId === 'dummy1') {
                eventFired = true;
            }
        });
        // Force redundancy event by monkey-patching Math.random
        const originalRandom = Math.random;
        Math.random = () => 0.01;
        manager.checkRedundancyAndNotify();
        Math.random = originalRandom;
        expect(eventFired).toBe(true);
    });

    it('should get stress levels for visualization', () => {
        manager.registerElement(dummyElement);
        const stressMap = manager.getStressLevels();
        expect(stressMap.has('dummy1')).toBe(true);
        expect(typeof stressMap.get('dummy1')).toBe('number');
    });
});

describe('MaterialFatigueSystem', () => {
    let system: MaterialFatigueSystem;
    let dummyElement: any;

    beforeEach(() => {
        system = new MaterialFatigueSystem();
        dummyElement = {
            moduleId: 'mat1',
            material: 'wood',
            health: 100,
            maxHealth: 100,
            deteriorate: function (amount: number) { this.health -= amount; },
            repair: function (amount: number) { this.health += amount; if (this.health > this.maxHealth) this.health = this.maxHealth; }
        };
    });

    it('should register and unregister elements', () => {
        system.registerElement(dummyElement);
        expect(system['elements'].has('mat1')).toBe(true);
        system.unregisterElement('mat1');
        expect(system['elements'].has('mat1')).toBe(false);
    });

    it('should degrade wood faster than stone over time', () => {
        const wood = { ...dummyElement, moduleId: 'wood', material: 'wood', health: 100, maxHealth: 100 };
        const stone = { ...dummyElement, moduleId: 'stone', material: 'stone', health: 100, maxHealth: 100 };
        system.registerElement(wood);
        system.registerElement(stone);
        system.tick(10);
        expect(wood.health).toBeLessThan(stone.health);
    });

    it('should apply weather effects to degradation', () => {
        const metal = { ...dummyElement, moduleId: 'metal', material: 'metal', health: 100, maxHealth: 100 };
        system.registerElement(metal);
        system.setWeather('rain');
        system.tick(10);
        expect(metal.health).toBeLessThan(100);
    });

    it('should allow repair of damaged elements', () => {
        system.registerElement(dummyElement);
        system.tick(10);
        const damaged = dummyElement.health;
        system.repairElement('mat1', 20);
        expect(dummyElement.health).toBeGreaterThan(damaged);
    });

    it('should provide degradation state for visual feedback', () => {
        system.registerElement(dummyElement);
        system.tick(10);
        const states = system.getDegradationStates();
        expect(states.has('mat1')).toBe(true);
        expect(typeof states.get('mat1')).toBe('number');
    });
}); 