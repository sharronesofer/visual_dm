import { BuildingModule } from './BuildingModule';
import { Position } from '../../core/interfaces/types/common';
import { MaterialType } from '../../core/interfaces/types/building';

export class WallModule extends BuildingModule {
    thickness: number;
    height: number;
    isLoadBearing: boolean;

    constructor(
        moduleId: string,
        position: Position,
        maxHealth: number,
        material: MaterialType,
        deteriorationRate: number,
        repairRate: number,
        thickness: number,
        height: number,
        isLoadBearing: boolean = false
    ) {
        super(moduleId, 'wall', position, maxHealth, material, deteriorationRate, repairRate);
        this.thickness = thickness;
        this.height = height;
        this.isLoadBearing = isLoadBearing;
    }

    getModuleType(): string {
        return 'wall';
    }
} 