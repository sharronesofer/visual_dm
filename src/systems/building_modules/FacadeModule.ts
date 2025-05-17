import { BuildingModule } from './BuildingModule';
import { Position } from '../../core/interfaces/types/common';
import { MaterialType } from '../../core/interfaces/types/building';

export class FacadeModule extends BuildingModule {
    // Example: Facade-specific property
    style: string;

    constructor(
        moduleId: string,
        position: Position,
        maxHealth: number,
        material: MaterialType,
        deteriorationRate: number,
        repairRate: number,
        style: string = 'default'
    ) {
        super(moduleId, 'facade', position, maxHealth, material, deteriorationRate, repairRate);
        this.style = style;
    }

    getModuleType(): string {
        return 'facade';
    }
} 