import { Position } from '../../core/interfaces/types/common';
import { MaterialType } from '../../core/interfaces/types/building';

// Enum for module state
export enum ModuleState {
    INTACT = 'INTACT',
    DAMAGED = 'DAMAGED',
    SEVERELY_DAMAGED = 'SEVERELY_DAMAGED',
    DESTROYED = 'DESTROYED',
}

// Interfaces for module behaviors
export interface IRepairable {
    repair(amount: number): void;
    canRepair(): boolean;
}

export interface IDamageable {
    applyDamage(amount: number): void;
}

export interface IDeterioration {
    deteriorate(amount: number): void;
}

// Abstract base class for all building modules
export abstract class BuildingModule implements IRepairable, IDamageable, IDeterioration {
    readonly moduleId: string;
    readonly type: string;
    position: Position;
    health: number;
    maxHealth: number;
    deteriorationRate: number;
    repairRate: number;
    material: MaterialType;
    currentState: ModuleState;

    constructor(
        moduleId: string,
        type: string,
        position: Position,
        maxHealth: number,
        material: MaterialType,
        deteriorationRate: number,
        repairRate: number
    ) {
        this.moduleId = moduleId;
        this.type = type;
        this.position = position;
        this.maxHealth = maxHealth;
        this.health = maxHealth;
        this.material = material;
        this.deteriorationRate = deteriorationRate;
        this.repairRate = repairRate;
        this.currentState = ModuleState.INTACT;
    }

    abstract getModuleType(): string;

    applyDamage(amount: number): void {
        this.health = Math.max(0, this.health - amount);
        this.updateState();
    }

    repair(amount: number): void {
        if (!this.canRepair()) return;
        this.health = Math.min(this.maxHealth, this.health + amount);
        this.updateState();
    }

    canRepair(): boolean {
        return this.health < this.maxHealth && this.currentState !== ModuleState.DESTROYED;
    }

    deteriorate(amount: number): void {
        this.applyDamage(amount * this.deteriorationRate);
    }

    protected updateState(): void {
        const healthRatio = this.health / this.maxHealth;
        if (this.health <= 0) {
            this.currentState = ModuleState.DESTROYED;
        } else if (healthRatio < 0.25) {
            this.currentState = ModuleState.SEVERELY_DAMAGED;
        } else if (healthRatio < 0.75) {
            this.currentState = ModuleState.DAMAGED;
        } else {
            this.currentState = ModuleState.INTACT;
        }
    }

    // Serialization for save/load
    serialize(): any {
        return {
            moduleId: this.moduleId,
            type: this.type,
            position: this.position,
            health: this.health,
            maxHealth: this.maxHealth,
            deteriorationRate: this.deteriorationRate,
            repairRate: this.repairRate,
            material: this.material,
            currentState: this.currentState,
        };
    }

    static deserialize(data: any): BuildingModule {
        throw new Error('Use ModuleFactory to deserialize specific module types.');
    }

    // --- Advanced Material System Hooks ---
    /**
     * Apply weathering to this module based on material properties and environment
     * TODO: Integrate with weather system and MaterialRegistry
     */
    applyWeathering(amount: number, reason?: string): void {
        // Example: degrade health based on weatheringRate
        // TODO: Use real weather/environment data
        // Optionally log to weatheringHistory
        this.applyDamage(amount * (this.deteriorationRate || 1));
        // TODO: Update visual degradation state
    }

    /**
     * Upgrade this module's material if possible
     * TODO: Integrate with MaterialRegistry and resource system
     */
    upgradeMaterial(newMaterial: MaterialType): void {
        // TODO: Validate upgrade path and resource requirements
        this.material = newMaterial;
        // Optionally update maxHealth, repairRate, etc.
        // TODO: Update visual state and notify systems
    }

    /**
     * Update visual state based on material degradation
     * TODO: Integrate with visual system and MaterialProperties.visualDegradationStates
     */
    updateVisualDegradationState(): void {
        // TODO: Set current visual state based on health/maxHealth and material
    }
    // --- End Advanced Material System Hooks ---
} 