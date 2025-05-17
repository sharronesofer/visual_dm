import { BuildingModule } from './BuildingModule';
import { Position } from '../../core/interfaces/types/common';
import { MaterialType } from '../../core/interfaces/types/building';

export class RoofModule extends BuildingModule {
    // Example: Roof-specific property
    slope: number;

    constructor(
        moduleId: string,
        position: Position,
        maxHealth: number,
        material: MaterialType,
        deteriorationRate: number,
        repairRate: number,
        slope: number = 30 // degrees
    ) {
        super(moduleId, 'roof', position, maxHealth, material, deteriorationRate, repairRate);
        this.slope = slope;
    }

    getModuleType(): string {
        return 'roof';
    }
} 