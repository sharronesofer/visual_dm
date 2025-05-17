import { BuildingStructure, MaterialType, BuildingElement } from '../core/interfaces/types/building';

export type DestructionType = 'deconstruction' | 'environmental' | 'other';

export interface MaterialRefundConfig {
    baseRefundPercentages: { [key in MaterialType]: number };
    conditionMultipliers: { [key: string]: number };
    buildingTypeModifiers: { [key: string]: number };
}

export class MaterialRefundCalculator {
    private config: MaterialRefundConfig;

    constructor(config: MaterialRefundConfig) {
        this.config = config;
    }

    static defaultConfig(): MaterialRefundConfig {
        return {
            baseRefundPercentages: {
                wood: 0.5,
                stone: 0.6,
                metal: 0.7,
                reinforced: 0.8,
                composite: 0.75,
                upgraded: 0.85
            },
            conditionMultipliers: {
                '0-25': 0.25,
                '26-50': 0.5,
                '51-75': 0.75,
                '76-100': 1.0
            },
            buildingTypeModifiers: {
                residential: 1.0,
                industrial: 0.9,
                commercial: 0.95,
                default: 1.0
            }
        };
    }

    getConditionMultiplier(condition: number): number {
        if (condition <= 0.25) return this.config.conditionMultipliers['0-25'];
        if (condition <= 0.5) return this.config.conditionMultipliers['26-50'];
        if (condition <= 0.75) return this.config.conditionMultipliers['51-75'];
        return this.config.conditionMultipliers['76-100'];
    }

    getBuildingTypeModifier(type: string): number {
        return this.config.buildingTypeModifiers[type] ?? this.config.buildingTypeModifiers['default'];
    }

    calculateRefund(
        structure: BuildingStructure,
        buildingType: string,
        destructionType: DestructionType
    ): { [key in MaterialType]?: number } {
        // Assume structure has a way to track original materials used (to be added)
        // For now, sum by element
        const materialTotals: { [key in MaterialType]?: number } = {};
        let totalHealth = 0;
        let maxTotalHealth = 0;
        for (const element of structure.elements.values()) {
            const mat = element.material;
            const healthRatio = element.health / element.maxHealth;
            materialTotals[mat] = (materialTotals[mat] || 0) + 1; // Placeholder: 1 unit per element
            totalHealth += element.health;
            maxTotalHealth += element.maxHealth;
        }
        const condition = maxTotalHealth > 0 ? totalHealth / maxTotalHealth : 1;
        const condMultiplier = this.getConditionMultiplier(condition);
        const typeModifier = this.getBuildingTypeModifier(buildingType);
        const result: { [key in MaterialType]?: number } = {};
        for (const mat in materialTotals) {
            const base = this.config.baseRefundPercentages[mat as MaterialType] || 0.5;
            result[mat as MaterialType] =
                materialTotals[mat as MaterialType]! * base * condMultiplier * typeModifier;
        }
        return result;
    }
} 