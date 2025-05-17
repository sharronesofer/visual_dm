import { BuildingModule } from './BuildingModule';
import { Position } from '../../core/interfaces/types/common';
import { MaterialType } from '../../core/interfaces/types/building';

export class PartitionModule extends BuildingModule {
    thickness: number;
    height: number;
    isMovable: boolean;
    hasDoorway: boolean;
    hasWindow: boolean;

    constructor(
        moduleId: string,
        position: Position,
        maxHealth: number,
        material: MaterialType,
        deteriorationRate: number,
        repairRate: number,
        thickness: number,
        height: number,
        isMovable: boolean = true,
        hasDoorway: boolean = false,
        hasWindow: boolean = false
    ) {
        super(moduleId, 'partition', position, maxHealth, material, deteriorationRate, repairRate);
        this.thickness = thickness;
        this.height = height;
        this.isMovable = isMovable;
        this.hasDoorway = hasDoorway;
        this.hasWindow = hasWindow;
    }

    /**
     * Validate placement (collision detection stub)
     */
    static validatePlacement(position: Position, thickness: number, height: number, grid: Map<string, BuildingModule>): boolean {
        // TODO: Implement collision detection with other modules
        return true;
    }

    getModuleType(): string {
        return 'partition';
    }
} 