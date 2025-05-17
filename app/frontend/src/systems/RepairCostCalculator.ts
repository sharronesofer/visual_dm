// RepairCostCalculator.ts
// Utility for calculating building repair costs

import { BuildingStructure, BuildingElement } from '../core/interfaces/types/building';

export interface RepairCostConfig {
    baseCostPerDamage: number;
    typeScaling: Record<string, number>;
    materialScaling: Record<string, number>;
    vendorReputationModifier: (vendorId: string) => number;
    playerRelationshipModifier: (playerId: string) => number;
}

export const defaultRepairCostConfig: RepairCostConfig = {
    baseCostPerDamage: 100,
    typeScaling: {
        residential: 1.0,
        industrial: 1.5,
        commercial: 1.2,
        default: 1.0
    },
    materialScaling: {
        wood: 1.0,
        stone: 1.3,
        metal: 1.5,
        reinforced: 2.0,
        default: 1.0
    },
    vendorReputationModifier: (vendorId: string) => 1.0, // TODO: Implement
    playerRelationshipModifier: (playerId: string) => 1.0 // TODO: Implement
};

function hasMaterial(element: any): element is { material: string } {
    return element && typeof element.material === 'string';
}

export function calculateRepairCost(
    building: BuildingStructure,
    config: RepairCostConfig = defaultRepairCostConfig,
    vendorId?: string,
    playerId?: string
): number {
    // Calculate total damage
    const totalDamage = ((building as any).battleDamage ?? 0) + ((building as any).deterioration ?? 0);
    const type = (building as any).buildingType || 'default';
    // Find the first element with a material property
    const elementWithMaterial = Array.from(building.elements.values()).find(hasMaterial);
    const material = elementWithMaterial ? elementWithMaterial.material : 'default';

    let cost =
        totalDamage * config.baseCostPerDamage *
        (config.typeScaling[type] || config.typeScaling.default) *
        (config.materialScaling[material] || config.materialScaling.default);

    if (vendorId) cost *= config.vendorReputationModifier(vendorId);
    if (playerId) cost *= config.playerRelationshipModifier(playerId);

    return Math.round(cost);
}

export type BuildingSize = 'small' | 'medium' | 'large';
export type MaterialQuality = 'basic' | 'standard' | 'premium';
export type PlayerRelationship = 'neutral' | 'friendly' | 'allied';

export interface MaterialCost {
    type: string;
    quality: MaterialQuality;
    cost: number;
}

export class MaterialCostRegistry {
    private costs: MaterialCost[];
    constructor(costs: MaterialCost[]) {
        this.costs = costs;
    }
    getCost(type: string, quality: MaterialQuality): number {
        const entry = this.costs.find(c => c.type === type && c.quality === quality);
        return entry ? entry.cost : 100; // fallback
    }
}

export interface ExtendedRepairCostConfig extends RepairCostConfig {
    sizeScaling: Record<BuildingSize, number>;
    materialQualityScaling: Record<MaterialQuality, number>;
    specializationBonus: number; // e.g. 0.9 for 10% off
    relationshipBonus: Record<PlayerRelationship, number>; // e.g. {neutral: 1, friendly: 0.95, allied: 0.85}
    materialRegistry: MaterialCostRegistry;
}

export const defaultExtendedRepairCostConfig: ExtendedRepairCostConfig = {
    ...defaultRepairCostConfig,
    sizeScaling: {
        small: 0.8,
        medium: 1.0,
        large: 1.5
    },
    materialQualityScaling: {
        basic: 0.8,
        standard: 1.0,
        premium: 1.5
    },
    specializationBonus: 0.9,
    relationshipBonus: {
        neutral: 1.0,
        friendly: 0.95,
        allied: 0.85
    },
    materialRegistry: new MaterialCostRegistry([
        { type: 'wood', quality: 'basic', cost: 50 },
        { type: 'wood', quality: 'standard', cost: 80 },
        { type: 'wood', quality: 'premium', cost: 120 },
        { type: 'stone', quality: 'basic', cost: 70 },
        { type: 'stone', quality: 'standard', cost: 110 },
        { type: 'stone', quality: 'premium', cost: 160 },
        { type: 'metal', quality: 'basic', cost: 100 },
        { type: 'metal', quality: 'standard', cost: 150 },
        { type: 'metal', quality: 'premium', cost: 220 },
    ])
};

/**
 * Calculate the repair cost for a building, factoring in all modifiers.
 * @param building The building structure
 * @param config The cost config
 * @param vendorId The vendor's ID
 * @param vendorSpecialization The vendor's specialization (optional)
 * @param vendorReputation The vendor's reputation (1-5)
 * @param playerRelationship The player's relationship with the vendor
 * @param size The building size
 * @param materialQuality The material quality for repair
 * @returns The final repair cost
 */
export function calculateExtendedRepairCost(
    building: BuildingStructure,
    config: ExtendedRepairCostConfig,
    vendorId: string,
    vendorSpecialization: string,
    vendorReputation: number,
    playerRelationship: PlayerRelationship,
    size: BuildingSize,
    materialQuality: MaterialQuality
): number {
    // 1. Base cost: damage percentage * base value (use material cost as base)
    const damagePercent = (building.battleDamage ?? 0 + building.deterioration ?? 0) / 100;
    const baseMaterial = building.material ?? 'wood';
    const baseCost = damagePercent * config.materialRegistry.getCost(baseMaterial, materialQuality);

    // 2. Apply type, size, and material multipliers
    const typeMult = config.typeScaling[building.buildingType ?? 'default'] ?? 1.0;
    const sizeMult = config.sizeScaling[size] ?? 1.0;
    const matQualMult = config.materialQualityScaling[materialQuality] ?? 1.0;
    let adjustedCost = baseCost * typeMult * sizeMult * matQualMult;

    // 3. Vendor reputation (1-5 stars, 5-25% discount)
    const repMult = 1.0 - 0.05 * (vendorReputation ?? 1);
    adjustedCost *= repMult;

    // 4. Specialization match (10% off if vendor specializes in building type)
    if (vendorSpecialization && vendorSpecialization === (building.buildingType ?? '')) {
        adjustedCost *= config.specializationBonus;
    }

    // 5. Player relationship bonus
    adjustedCost *= config.relationshipBonus[playerRelationship] ?? 1.0;

    // 6. Minimum cost threshold
    return Math.max(Math.round(adjustedCost), 10);
} 