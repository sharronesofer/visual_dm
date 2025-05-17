import { BuildingModule } from './BuildingModule';
import { ModuleStateManager, ModuleStateObserver, ModuleStateChange } from './ModuleStateManager';
import { ModifierRegistry } from './ModifierSystem';
import { ModuleRelationshipManager } from './ModuleRelationshipManager';
import { FloorModule } from './FloorModule';
import { RoofModule } from './RoofModule';
import { WallModule } from './WallModule';
import { Column } from '../../core/interfaces/types/building';
import { ColumnModule } from './ColumnModule';
import { BeamModule } from './BeamModule';
import { StairModule } from './StairModule';
import { FurnitureModule } from './FurnitureModule';
import { PartitionModule } from './PartitionModule';

// ITickable interface for periodic updates
export interface ITickable {
    onTick(time: GameTime): void;
    getTickPriority?(): number;
}

// GameTime type for tick context
export interface GameTime {
    currentTick: number;
    currentHour: number;
    currentDay: number;
}

// Configuration system (simple JSON-based for now)
export interface ModuleConfigParams {
    [key: string]: any;
}

export class ModuleConfigSystem {
    private config: ModuleConfigParams = {};
    load(config: ModuleConfigParams) {
        this.config = { ...config };
    }
    get(key: string, defaultValue?: any) {
        return this.config[key] !== undefined ? this.config[key] : defaultValue;
    }
    set(key: string, value: any) {
        this.config[key] = value;
    }
}

// Main facade for the building module system
export class BuildingModuleSystem implements ITickable {
    private static instance: BuildingModuleSystem;
    private modules: Map<string, BuildingModule> = new Map();
    private stateManagers: Map<string, ModuleStateManager> = new Map();
    private relationshipManager: ModuleRelationshipManager = new ModuleRelationshipManager();
    private modifierRegistry: ModifierRegistry = ModifierRegistry.getInstance();
    private configSystem: ModuleConfigSystem = new ModuleConfigSystem();
    private uiObservers: Set<ModuleStateObserver> = new Set();

    private constructor() { }

    static getInstance(): BuildingModuleSystem {
        if (!BuildingModuleSystem.instance) {
            BuildingModuleSystem.instance = new BuildingModuleSystem();
        }
        return BuildingModuleSystem.instance;
    }

    registerModule(module: BuildingModule, stateManager?: ModuleStateManager) {
        this.modules.set(module.moduleId, module);
        this.relationshipManager.registerModule(module);
        const sm = stateManager || new ModuleStateManager(module);
        this.stateManagers.set(module.moduleId, sm);
        for (const observer of this.uiObservers) {
            sm.addObserver(observer);
        }
    }

    unregisterModule(moduleId: string) {
        this.modules.delete(moduleId);
        this.stateManagers.delete(moduleId);
        this.relationshipManager.unregisterModule(moduleId);
    }

    getModule(moduleId: string): BuildingModule | undefined {
        return this.modules.get(moduleId);
    }

    getStateManager(moduleId: string): ModuleStateManager | undefined {
        return this.stateManagers.get(moduleId);
    }

    getRelationshipManager(): ModuleRelationshipManager {
        return this.relationshipManager;
    }

    getModifierRegistry(): ModifierRegistry {
        return this.modifierRegistry;
    }

    getConfigSystem(): ModuleConfigSystem {
        return this.configSystem;
    }

    // UI observer registration
    addUIObserver(observer: ModuleStateObserver) {
        this.uiObservers.add(observer);
        for (const sm of this.stateManagers.values()) {
            sm.addObserver(observer);
        }
    }

    removeUIObserver(observer: ModuleStateObserver) {
        this.uiObservers.delete(observer);
        for (const sm of this.stateManagers.values()) {
            sm.removeObserver(observer);
        }
    }

    // Main tick processing (hourly by default)
    onTick(time: GameTime): void {
        for (const [id, module] of this.modules.entries()) {
            // Apply deterioration using modifiers
            const baseDeterioration = module.deteriorationRate;
            const effectiveDeterioration = this.modifierRegistry.getEffectiveRate(
                id,
                baseDeterioration,
                'deteriorationRate'
            );
            const sm = this.stateManagers.get(id);
            if (sm) {
                sm.applyDeterioration(effectiveDeterioration, 'tick');
            }
        }
        // Optionally, process relationships (e.g., cascading damage)
        // this.relationshipManager.validateIntegrity();
    }

    // Extension point: add new module types
    static registerCustomModuleType(type: string, factory: (config: any) => BuildingModule) {
        // Implementation: store in a registry for dynamic instantiation
        // (Not shown here, but can be added for plugin support)
    }

    // Logging (simple console-based for now)
    log(level: 'debug' | 'info' | 'warn' | 'error', message: string, ...args: any[]) {
        if (level === 'debug' && !this.configSystem.get('debug', false)) return;
        console[level](`[BuildingModuleSystem][${level}] ${message}`, ...args);
    }

    /**
     * Place a modular floor segment at a grid position.
     * Checks for valid support (columns, walls, or beams).
     */
    placeFloor(
        floor: FloorModule,
        grid: Map<string, BuildingModule>,
        supportModules: BuildingModule[]
    ): boolean {
        // Check for support: must have at least one supporting column, wall, or beam below
        const hasSupport = supportModules.some(
            m => m.getModuleType() === 'column' || m.getModuleType() === 'wall' || m.getModuleType() === 'beam'
        );
        if (!hasSupport) return false;
        // Place floor in grid
        const key = `${floor.position.x},${floor.position.y}`;
        grid.set(key, floor);
        // Connect to adjacent floors for modularity
        this.connectAdjacentModules(floor, grid, 'floor');
        // TODO: Trigger visual/physics integration
        return true;
    }

    /**
     * Place a modular roof segment at a grid position.
     * Checks for valid support (beams or walls).
     */
    placeRoof(
        roof: RoofModule,
        grid: Map<string, BuildingModule>,
        supportModules: BuildingModule[]
    ): boolean {
        // Check for support: must have at least one supporting beam or wall below
        const hasSupport = supportModules.some(
            m => m.getModuleType() === 'beam' || m.getModuleType() === 'wall'
        );
        if (!hasSupport) return false;
        // Place roof in grid
        const key = `${roof.position.x},${roof.position.y}`;
        grid.set(key, roof);
        // Connect to adjacent roofs for modularity
        this.connectAdjacentModules(roof, grid, 'roof');
        // TODO: Trigger visual/physics integration
        return true;
    }

    /**
     * Connect adjacent modules of the same type for seamless modularity.
     */
    connectAdjacentModules(
        module: BuildingModule,
        grid: Map<string, BuildingModule>,
        type: string
    ) {
        const { x, y } = module.position;
        const adjacentKeys = [
            `${x - 1},${y}`,
            `${x + 1},${y}`,
            `${x},${y - 1}`,
            `${x},${y + 1}`
        ];
        for (const key of adjacentKeys) {
            const neighbor = grid.get(key);
            if (neighbor && neighbor.getModuleType() === type) {
                // TODO: Implement connection logic (e.g., update references, merge seams, etc.)
            }
        }
    }

    /**
     * Validate structural integrity after placement.
     * (Stub: to be expanded with full integrity logic)
     */
    validateIntegrity(grid: Map<string, BuildingModule>): boolean {
        // TODO: Implement full structural integrity validation
        return true;
    }

    /**
     * Place and register a modular floor segment, enforcing placement rules and system registration.
     */
    placeAndRegisterFloor(
        floor: FloorModule,
        grid: Map<string, BuildingModule>,
        supportModules: BuildingModule[],
        stateManager?: ModuleStateManager
    ): boolean {
        if (!this.placeFloor(floor, grid, supportModules)) return false;
        this.registerModule(floor, stateManager);
        return true;
    }

    /**
     * Place and register a modular roof segment, enforcing placement rules and system registration.
     */
    placeAndRegisterRoof(
        roof: RoofModule,
        grid: Map<string, BuildingModule>,
        supportModules: BuildingModule[],
        stateManager?: ModuleStateManager
    ): boolean {
        if (!this.placeRoof(roof, grid, supportModules)) return false;
        this.registerModule(roof, stateManager);
        return true;
    }

    /**
     * Place a modular column at a grid position. Checks for valid support (foundation).
     */
    placeColumn(
        column: ColumnModule,
        grid: Map<string, BuildingModule>,
        supportModules: BuildingModule[]
    ): boolean {
        // Check for support: must have at least one supporting foundation below
        const hasSupport = supportModules.some(
            m => m.getModuleType() === 'foundation'
        );
        if (!hasSupport) return false;
        const key = `${column.position.x},${column.position.y}`;
        grid.set(key, column);
        // TODO: Connect to adjacent beams/floors
        // TODO: Trigger visual/physics integration
        return true;
    }

    /**
     * Place a modular beam at a grid position. Checks for valid support (columns or walls).
     */
    placeBeam(
        beam: BeamModule,
        grid: Map<string, BuildingModule>,
        supportModules: BuildingModule[]
    ): boolean {
        // Check for support: must have at least one supporting column or wall
        const hasSupport = supportModules.some(
            m => m.getModuleType() === 'column' || m.getModuleType() === 'wall'
        );
        if (!hasSupport) return false;
        const key = `${beam.position.x},${beam.position.y}`;
        grid.set(key, beam);
        // TODO: Connect to adjacent columns/floors/roofs
        // TODO: Trigger visual/physics integration
        return true;
    }

    /**
     * Place and register a modular column, enforcing placement rules and system registration.
     */
    placeAndRegisterColumn(
        column: ColumnModule,
        grid: Map<string, BuildingModule>,
        supportModules: BuildingModule[],
        stateManager?: ModuleStateManager
    ): boolean {
        if (!this.placeColumn(column, grid, supportModules)) return false;
        this.registerModule(column, stateManager);
        return true;
    }

    /**
     * Place and register a modular beam, enforcing placement rules and system registration.
     */
    placeAndRegisterBeam(
        beam: BeamModule,
        grid: Map<string, BuildingModule>,
        supportModules: BuildingModule[],
        stateManager?: ModuleStateManager
    ): boolean {
        if (!this.placeBeam(beam, grid, supportModules)) return false;
        this.registerModule(beam, stateManager);
        return true;
    }

    /**
     * Place a modular stair at a grid position. Checks for valid connection between two floors at different heights.
     */
    placeStair(
        stair: StairModule,
        grid: Map<string, BuildingModule>,
        floorA: BuildingModule,
        floorB: BuildingModule
    ): boolean {
        // Validate placement between two floors
        if (!StairModule.validatePlacement(floorA, floorB)) return false;
        const key = `${stair.position.x},${stair.position.y}`;
        grid.set(key, stair);
        // TODO: Connect to floors
        // TODO: Trigger navmesh/player integration
        return true;
    }

    /**
     * Place and register a modular stair, enforcing placement rules and system registration.
     */
    placeAndRegisterStair(
        stair: StairModule,
        grid: Map<string, BuildingModule>,
        floorA: BuildingModule,
        floorB: BuildingModule,
        stateManager?: ModuleStateManager
    ): boolean {
        if (!this.placeStair(stair, grid, floorA, floorB)) return false;
        this.registerModule(stair, stateManager);
        return true;
    }

    /**
     * Place a modular furniture item at a grid position. Checks for valid placement (collision detection stub).
     */
    placeFurniture(
        furniture: FurnitureModule,
        grid: Map<string, BuildingModule>
    ): boolean {
        if (!FurnitureModule.validatePlacement(furniture.position, furniture.dimensions, grid)) return false;
        const key = `${furniture.position.x},${furniture.position.y}`;
        grid.set(key, furniture);
        // TODO: Trigger interaction/visual integration
        return true;
    }

    /**
     * Place and register a modular furniture item, enforcing placement rules and system registration.
     */
    placeAndRegisterFurniture(
        furniture: FurnitureModule,
        grid: Map<string, BuildingModule>,
        stateManager?: ModuleStateManager
    ): boolean {
        if (!this.placeFurniture(furniture, grid)) return false;
        this.registerModule(furniture, stateManager);
        return true;
    }

    /**
     * Place a modular partition at a grid position. Checks for valid placement (collision detection stub).
     */
    placePartition(
        partition: PartitionModule,
        grid: Map<string, BuildingModule>
    ): boolean {
        if (!PartitionModule.validatePlacement(partition.position, partition.thickness, partition.height, grid)) return false;
        const key = `${partition.position.x},${partition.position.y}`;
        grid.set(key, partition);
        // TODO: Trigger visual integration
        return true;
    }

    /**
     * Place and register a modular partition, enforcing placement rules and system registration.
     */
    placeAndRegisterPartition(
        partition: PartitionModule,
        grid: Map<string, BuildingModule>,
        stateManager?: ModuleStateManager
    ): boolean {
        if (!this.placePartition(partition, grid)) return false;
        this.registerModule(partition, stateManager);
        return true;
    }

    // TODO: Add stubs for visual/physics integration
} 