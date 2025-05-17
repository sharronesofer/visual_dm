import { BuildingModule } from './BuildingModule';
import { Position } from '../../core/interfaces/types/common';
import { MaterialType } from '../../core/interfaces/types/building';

export class ColumnModule extends BuildingModule {
    height: number;
    radius: number;
    loadCapacity: number;

    constructor(
        moduleId: string,
        position: Position,
        maxHealth: number,
        material: MaterialType,
        deteriorationRate: number,
        repairRate: number,
        height: number,
        radius: number,
        loadCapacity: number
    ) {
        super(moduleId, 'column', position, maxHealth, material, deteriorationRate, repairRate);
        this.height = height;
        this.radius = radius;
        this.loadCapacity = loadCapacity;
    }

    /**
     * Calculate load capacity based on material and dimensions
     */
    static calculateLoadCapacity(material: MaterialType, radius: number, height: number): number {
        // Simple formula: base * area * material factor
        const base = 100;
        const area = Math.PI * radius * radius;
        let materialFactor = 1;
        switch (material) {
            case 'wood': materialFactor = 0.5; break;
            case 'stone': materialFactor = 1.2; break;
            case 'metal': materialFactor = 2.0; break;
            case 'reinforced': materialFactor = 2.5; break;
            default: materialFactor = 1;
        }
        return base * area * materialFactor / (height * 0.5);
    }

    /**
     * Connect this column to a floor or beam
     */
    connectTo(elementId: string) {
        // TODO: Implement connection logic (store connected element IDs)
    }

    getModuleType(): string {
        return 'column';
    }
} 