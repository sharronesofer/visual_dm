import { BuildingModule } from './BuildingModule';
import { ColumnModule } from './ColumnModule';
import { BeamModule } from './BeamModule';
import { FloorModule } from './FloorModule';
import { RoofModule } from './RoofModule';
import { WallModule } from './WallModule';
import { Position } from '../../core/interfaces/types/common';

export type LoadEvent = {
    type: 'integrity-compromised' | 'redundancy-activated';
    elementId: string;
    details?: any;
};

export class LoadCalculationManager {
    private elements: Map<string, BuildingModule> = new Map();
    private eventListeners: ((event: LoadEvent) => void)[] = [];

    registerElement(element: BuildingModule) {
        this.elements.set(element.moduleId, element);
    }

    unregisterElement(moduleId: string) {
        this.elements.delete(moduleId);
    }

    /**
     * Calculate and distribute loads from top to bottom of the structure
     * Returns a map of elementId to calculated load and stress
     */
    calculateLoadDistribution(): Map<string, { load: number; stress: number; redundancy: boolean }> {
        // For simplicity, assume vertical load path: roof -> floor -> beam/column -> foundation
        // This is a stub; real implementation would traverse the structure graph
        const result = new Map<string, { load: number; stress: number; redundancy: boolean }>();
        for (const [id, element] of this.elements.entries()) {
            // Example: assign arbitrary load and stress values
            let load = 100;
            let stress = Math.random();
            let redundancy = false;
            // TODO: Implement real load calculation based on connections and material
            result.set(id, { load, stress, redundancy });
        }
        return result;
    }

    /**
     * Redundancy logic: activate secondary support if primary fails
     */
    checkRedundancyAndNotify() {
        // TODO: Implement redundancy check and event notification
        // Example: if a primary element is overloaded, activate secondary and notify
        for (const [id, element] of this.elements.entries()) {
            // Stub: randomly trigger redundancy
            if (Math.random() < 0.05) {
                this.emitEvent({ type: 'redundancy-activated', elementId: id });
            }
        }
    }

    /**
     * Integrate with Core Building Damage System (stub)
     */
    integrateWithDamageSystem() {
        // TODO: Call into BuildingDamageSystem to apply damage based on overload
    }

    /**
     * Add event listener for load events
     */
    addEventListener(listener: (event: LoadEvent) => void) {
        this.eventListeners.push(listener);
    }

    private emitEvent(event: LoadEvent) {
        for (const listener of this.eventListeners) {
            listener(event);
        }
    }

    /**
     * Get stress levels for visualization
     */
    getStressLevels(): Map<string, number> {
        const distribution = this.calculateLoadDistribution();
        const stressMap = new Map<string, number>();
        for (const [id, data] of distribution.entries()) {
            stressMap.set(id, data.stress);
        }
        return stressMap;
    }
} 