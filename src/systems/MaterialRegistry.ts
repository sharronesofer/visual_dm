// MaterialRegistry.ts
// Central registry for advanced material system: properties, upgrades, combinations, synergy bonuses
import { MaterialType, MaterialProperties, BUILDING_PHYSICS_DEFAULTS } from '../core/interfaces/types/building';

export interface MaterialCombination {
    materials: [MaterialType, MaterialType];
    result: MaterialType;
    synergyBonus?: number;
}

export class MaterialRegistry {
    private static instance: MaterialRegistry;
    private materialProperties: Record<MaterialType, MaterialProperties>;
    private combinations: MaterialCombination[];

    private constructor() {
        this.materialProperties = { ...BUILDING_PHYSICS_DEFAULTS.materialProperties };
        this.combinations = [
            // Example: combining wood + metal yields composite
            { materials: ['wood', 'metal'], result: 'composite', synergyBonus: 0.1 },
            // Example: combining stone + metal yields reinforced
            { materials: ['stone', 'metal'], result: 'reinforced', synergyBonus: 0.05 },
            // TODO: Add more combinations as needed
        ];
    }

    public static getInstance(): MaterialRegistry {
        if (!MaterialRegistry.instance) {
            MaterialRegistry.instance = new MaterialRegistry();
        }
        return MaterialRegistry.instance;
    }

    public getProperties(type: MaterialType): MaterialProperties | undefined {
        return this.materialProperties[type];
    }

    public getUpgradePath(type: MaterialType): string[] {
        return this.materialProperties[type]?.upgradePath || [];
    }

    public getCombinationResult(a: MaterialType, b: MaterialType): MaterialCombination | undefined {
        return this.combinations.find(
            (combo) =>
                (combo.materials[0] === a && combo.materials[1] === b) ||
                (combo.materials[0] === b && combo.materials[1] === a)
        );
    }

    public addMaterial(type: MaterialType, properties: MaterialProperties) {
        this.materialProperties[type] = properties;
    }

    public addCombination(combination: MaterialCombination) {
        this.combinations.push(combination);
    }

    // TODO: Add methods for serialization, migration, and advanced queries
} 