import { BuildingModule } from './BuildingModule';
import { Position } from '../../core/interfaces/types/common';
import { MaterialType } from '../../core/interfaces/types/building';

export class FloorModule extends BuildingModule {
    thickness: number;
    area: number;
    supportColumns?: string[];

    constructor(
        moduleId: string,
        position: Position,
        maxHealth: number,
        material: MaterialType,
        deteriorationRate: number,
        repairRate: number,
        thickness: number = 1,
        area: number = 1,
        supportColumns?: string[]
    ) {
        super(moduleId, 'floor', position, maxHealth, material, deteriorationRate, repairRate);
        this.thickness = thickness;
        this.area = area;
        this.supportColumns = supportColumns;
    }

    getModuleType(): string {
        return 'floor';
    }
} 