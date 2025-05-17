import { ValidationRule, ValidationSeverity, ValidationContext } from './ValidationService';
import { ConsistencyChecker } from './ValidationService';

/**
 * Economic System Validation Rules
 */
export class NoNegativeBalanceRule implements ValidationRule {
    severity = ValidationSeverity.ERROR;
    validate(data: any, context?: ValidationContext): boolean {
        if (data.fromAgent && data.fromAgent.currency < 0) {
            return false;
        }
        if (data.toAgent && data.toAgent.currency < 0) {
            return false;
        }
        return true;
    }
    getErrorMessage() {
        return 'Agent balance cannot be negative.';
    }
}

export class SufficientFundsRule implements ValidationRule {
    severity = ValidationSeverity.ERROR;
    validate(data: any, context?: ValidationContext): boolean {
        if (data.fromAgent && typeof data.amount === 'number') {
            return data.fromAgent.currency >= data.amount;
        }
        return false;
    }
    getErrorMessage() {
        return 'Insufficient funds for transfer.';
    }
}

/**
 * Reputation System Validation Rules
 */
export class ReputationBoundsRule implements ValidationRule {
    severity = ValidationSeverity.ERROR;
    validate(data: any, context?: ValidationContext): boolean {
        if (typeof data.delta === 'number' && data.agent) {
            const newRep = (data.agent.reputation ?? 0) + data.delta;
            return newRep >= 0 && newRep <= 100;
        }
        return true;
    }
    getErrorMessage() {
        return 'Reputation must remain between 0 and 100.';
    }
}

/**
 * Inventory System Validation Rules
 */
export class InventorySlotLimitRule implements ValidationRule {
    severity = ValidationSeverity.ERROR;
    validate(data: any, context?: ValidationContext): boolean {
        if (data.inventory && data.inventory.slots) {
            return data.inventory.slots.some((slot: any) => slot.itemId === null);
        }
        return true;
    }
    getErrorMessage() {
        return 'No available inventory slots.';
    }
}

export class InventoryWeightLimitRule implements ValidationRule {
    severity = ValidationSeverity.ERROR;
    validate(data: any, context?: ValidationContext): boolean {
        if (data.inventory && data.item && typeof data.quantity === 'number') {
            const weightImpact = (data.item.weight ?? 0) * data.quantity;
            return (data.inventory.currentWeight + weightImpact) <= (data.inventory.maxWeight ?? Infinity);
        }
        return true;
    }
    getErrorMessage() {
        return 'Adding this item would exceed inventory weight limit.';
    }
}

export class ValidItemRule implements ValidationRule {
    severity = ValidationSeverity.ERROR;
    validate(data: any, context?: ValidationContext): boolean {
        return !!data.item;
    }
    getErrorMessage() {
        return 'Item does not exist.';
    }
}

/**
 * Cross-System Consistency Validation Rules
 */
export class EconomicInventoryConsistencyRule implements ValidationRule {
    severity = ValidationSeverity.ERROR;
    async validate(data: any, context?: ValidationContext): Promise<boolean> {
        if (data.economicData && data.inventoryData) {
            return await ConsistencyChecker.checkEconomicInventory(data.economicData, data.inventoryData);
        }
        return true;
    }
    getErrorMessage() {
        return 'Economic items must exist in inventory.';
    }
}

export class ReputationEconomicConsistencyRule implements ValidationRule {
    severity = ValidationSeverity.ERROR;
    async validate(data: any, context?: ValidationContext): Promise<boolean> {
        if (data.reputationData && data.economicData) {
            return await ConsistencyChecker.checkReputationEconomic(data.reputationData, data.economicData);
        }
        return true;
    }
    getErrorMessage() {
        return 'Reputation changes must be reflected in economic privileges.';
    }
}

export class InventoryReputationConsistencyRule implements ValidationRule {
    severity = ValidationSeverity.ERROR;
    async validate(data: any, context?: ValidationContext): Promise<boolean> {
        if (data.inventoryData && data.reputationData) {
            return await ConsistencyChecker.checkInventoryReputation(data.inventoryData, data.reputationData);
        }
        return true;
    }
    getErrorMessage() {
        return 'Inventory access must match reputation requirements.';
    }
} 