import { BuildingModule } from './BuildingModule';
import { Position } from '../../core/interfaces/types/common';
import { MaterialType } from '../../core/interfaces/types/building';
import { BuildingElement } from '../../core/interfaces/types/building';

declare module '../../core/interfaces/types/building' {
    interface BuildingElementTypeMap {
        foundation: 'foundation';
    }
}

export class FoundationModule extends BuildingModule implements BuildingElement {
    id: string;
    type: 'foundation';
    depth: number;
    materialStrength: number;

    constructor(
        moduleId: string,
        position: Position,
        maxHealth: number,
        material: MaterialType,
        deteriorationRate: number,
        repairRate: number,
        depth: number,
        materialStrength: number
    ) {
        super(moduleId, 'foundation', position, maxHealth, material, deteriorationRate, repairRate);
        this.id = moduleId;
        this.type = 'foundation';
        this.depth = depth;
        this.materialStrength = materialStrength;
    }

    getModuleType(): string {
        return 'foundation';
    }

    /**
     * Factory method to create a foundation adapted to terrain/building params
     * @param moduleId Unique module ID
     * @param position Position of the foundation
     * @param material Material type
     * @param foundationType Foundation type (standard, stilted, anchored, etc.)
     * @param depth Foundation depth
     * @param materialStrength Material strength
     * @param slope Slope at the build site (0-1)
     * @param terrainType Terrain type (e.g., 'plains', 'mountain', 'water')
     */
    static createAdaptive(
        moduleId: string,
        position: Position,
        material: MaterialType,
        foundationType: string,
        depth: number,
        materialStrength: number,
        slope: number = 0,
        terrainType: string = 'plains'
    ): FoundationModule {
        // Adjust depth and materialStrength based on slope and terrain
        let adjustedDepth = depth;
        let adjustedStrength = materialStrength;
        if (slope > 0.15) {
            adjustedDepth += 1;
            adjustedStrength *= 0.9;
        }
        if (foundationType === 'stilted') {
            adjustedDepth += 2;
            adjustedStrength *= 0.8;
        } else if (foundationType === 'anchored') {
            adjustedStrength *= 1.2;
        }
        if (terrainType === 'mountain') {
            adjustedStrength *= 1.1;
        } else if (terrainType === 'water') {
            adjustedStrength *= 0.7;
        }
        // Set deterioration/repair rates based on foundation type
        let deteriorationRate = 0.01;
        let repairRate = 0.05;
        if (foundationType === 'stilted') {
            deteriorationRate = 0.02;
            repairRate = 0.04;
        } else if (foundationType === 'anchored') {
            deteriorationRate = 0.008;
            repairRate = 0.06;
        }
        // Max health can be a function of materialStrength and depth
        const maxHealth = Math.round(100 * adjustedStrength * adjustedDepth);
        const foundation = new FoundationModule(
            moduleId,
            position,
            maxHealth,
            material,
            deteriorationRate,
            repairRate,
            adjustedDepth,
            adjustedStrength
        );
        foundation.id = moduleId;
        return foundation;
    }
} 