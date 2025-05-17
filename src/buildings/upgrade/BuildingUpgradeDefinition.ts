export type ResourceType = string;
export type StatType = string;
export type Capability = string;
export type BuildingType = string;

export interface UpgradeCost {
    resources: Record<ResourceType, number>;
    time: number;
}

export interface UpgradeRequirements {
    techLevel: number;
    prerequisites: BuildingType[];
    otherConditions?: Condition[];
}

export interface UpgradeEffects {
    statChanges: Record<StatType, number>;
    newCapabilities: Capability[];
}

export interface UpgradeMetadata {
    description: string;
    upgradeLevel: number;
}

export interface Condition {
    type: string;
    value: any;
}

export class BuildingUpgradeDefinition {
    constructor(
        public readonly id: string,
        public readonly from: BuildingType,
        public readonly to: BuildingType,
        public readonly cost: UpgradeCost,
        public readonly requirements: UpgradeRequirements,
        public readonly effects: UpgradeEffects,
        public readonly metadata: UpgradeMetadata
    ) { }
} 