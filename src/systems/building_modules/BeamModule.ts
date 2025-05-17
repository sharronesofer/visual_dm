import { BuildingModule } from './BuildingModule';
import { Position } from '../../core/interfaces/types/common';
import { MaterialType } from '../../core/interfaces/types/building';

export class BeamModule extends BuildingModule {
    length: number;
    crossSection: number;
    loadCapacity: number;

    constructor(
        moduleId: string,
        position: Position,
        maxHealth: number,
        material: MaterialType,
        deteriorationRate: number,
        repairRate: number,
        length: number,
        crossSection: number,
        loadCapacity: number
    ) {
        super(moduleId, 'beam', position, maxHealth, material, deteriorationRate, repairRate);
        this.length = length;
        this.crossSection = crossSection;
        this.loadCapacity = loadCapacity;
    }

    /**
     * Calculate load capacity based on material and cross-section
     */
    static calculateLoadCapacity(material: MaterialType, crossSection: number, length: number): number {
        // Simple formula: base * crossSection * material factor / length
        const base = 80;
        let materialFactor = 1;
        switch (material) {
            case 'wood': materialFactor = 0.4; break;
            case 'stone': materialFactor = 1.0; break;
            case 'metal': materialFactor = 2.2; break;
            case 'reinforced': materialFactor = 2.8; break;
            default: materialFactor = 1;
        }
        return base * crossSection * materialFactor / (length * 0.7);
    }

    /**
     * Connect this beam to columns, floors, or roofs
     */
    connectTo(elementId: string) {
        // TODO: Implement connection logic (store connected element IDs)
    }

    getModuleType(): string {
        return 'beam';
    }
} 