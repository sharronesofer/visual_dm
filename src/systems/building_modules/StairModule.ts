import { BuildingModule } from './BuildingModule';
import { Position } from '../../core/interfaces/types/common';
import { MaterialType } from '../../core/interfaces/types/building';

export class StairModule extends BuildingModule {
    width: number;
    height: number;
    steps: number;
    connects: [string, string]; // IDs of connected floors

    constructor(
        moduleId: string,
        position: Position,
        maxHealth: number,
        material: MaterialType,
        deteriorationRate: number,
        repairRate: number,
        width: number,
        height: number,
        steps: number,
        connects: [string, string]
    ) {
        super(moduleId, 'stair', position, maxHealth, material, deteriorationRate, repairRate);
        this.width = width;
        this.height = height;
        this.steps = steps;
        this.connects = connects;
    }

    /**
     * Validate placement between two floors at different heights
     */
    static validatePlacement(floorA: BuildingModule, floorB: BuildingModule): boolean {
        // TODO: Implement logic to check if floors are at different heights and can be connected by stairs
        return true;
    }

    /**
     * Stub for navmesh integration
     */
    integrateWithNavMesh() {
        // TODO: Implement navmesh update for AI pathfinding
    }

    /**
     * Stub for player movement/collision integration
     */
    integrateWithPlayerMovement() {
        // TODO: Implement player movement/collision logic for stairs
    }

    getModuleType(): string {
        return 'stair';
    }
} 