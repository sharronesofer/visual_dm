import { BuildingModule } from './BuildingModule';
import { Position } from '../../core/interfaces/types/common';
import { MaterialType } from '../../core/interfaces/types/building';

export type FurnitureType = 'chair' | 'table' | 'bed' | 'sofa' | 'cabinet' | 'shelf' | 'custom';

export class FurnitureModule extends BuildingModule {
    furnitureType: FurnitureType;
    dimensions: { width: number; height: number; depth: number };
    isMovable: boolean;

    constructor(
        moduleId: string,
        position: Position,
        maxHealth: number,
        material: MaterialType,
        deteriorationRate: number,
        repairRate: number,
        furnitureType: FurnitureType,
        dimensions: { width: number; height: number; depth: number },
        isMovable: boolean = true
    ) {
        super(moduleId, 'furniture', position, maxHealth, material, deteriorationRate, repairRate);
        this.furnitureType = furnitureType;
        this.dimensions = dimensions;
        this.isMovable = isMovable;
    }

    /**
     * Validate placement (collision detection stub)
     */
    static validatePlacement(position: Position, dimensions: { width: number; height: number; depth: number }, grid: Map<string, BuildingModule>): boolean {
        // TODO: Implement collision detection with other modules
        return true;
    }

    /**
     * Basic interaction (e.g., sit, open)
     */
    interact(action: string): boolean {
        // TODO: Implement interaction logic based on furnitureType and action
        return true;
    }

    getModuleType(): string {
        return 'furniture';
    }
} 