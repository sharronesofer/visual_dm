import { BuildingUpgradeDefinition, UpgradeCost, UpgradeRequirements, BuildingType } from './BuildingUpgradeDefinition';

export interface ValidationResult {
    success: boolean;
    errors?: string[];
}

export interface Resources {
    [resource: string]: number;
}

export interface Building {
    type: BuildingType;
    // Add other relevant properties as needed
}

export class BuildingUpgradeValidator {
    static validateResources(playerResources: Resources, upgradeCost: UpgradeCost): boolean {
        for (const [resource, amount] of Object.entries(upgradeCost.resources)) {
            if ((playerResources[resource] || 0) < amount) {
                return false;
            }
        }
        return true;
    }

    static validateTechRequirements(playerTechLevel: number, requiredLevel: number): boolean {
        return playerTechLevel >= requiredLevel;
    }

    static validatePrerequisites(playerBuildings: Building[], requiredBuildings: BuildingType[]): boolean {
        const playerTypes = new Set(playerBuildings.map(b => b.type));
        return requiredBuildings.every(req => playerTypes.has(req));
    }

    static canUpgrade(
        building: Building,
        targetUpgrade: BuildingUpgradeDefinition,
        playerResources: Resources,
        playerTechLevel: number,
        playerBuildings: Building[]
    ): ValidationResult {
        const errors: string[] = [];
        if (!this.validateResources(playerResources, targetUpgrade.cost)) {
            errors.push('Insufficient resources');
        }
        if (!this.validateTechRequirements(playerTechLevel, targetUpgrade.requirements.techLevel)) {
            errors.push('Tech level too low');
        }
        if (!this.validatePrerequisites(playerBuildings, targetUpgrade.requirements.prerequisites)) {
            errors.push('Missing prerequisite buildings');
        }
        // Add more checks for otherConditions if needed
        return {
            success: errors.length === 0,
            errors: errors.length > 0 ? errors : undefined
        };
    }
} 