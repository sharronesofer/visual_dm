import { BuildingModule } from './BuildingModule';
import { Position } from '../../core/interfaces/types/common';
import { MaterialType } from '../../core/interfaces/types/building';

export class InteriorModule extends BuildingModule {
    roomType: string;

    constructor(
        moduleId: string,
        position: Position,
        maxHealth: number,
        material: MaterialType,
        deteriorationRate: number,
        repairRate: number,
        roomType: string = 'generic'
    ) {
        super(moduleId, 'interior', position, maxHealth, material, deteriorationRate, repairRate);
        this.roomType = roomType;
    }

    getModuleType(): string {
        return 'interior';
    }
} 