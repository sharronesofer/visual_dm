import { BuildingModule } from './BuildingModule';
import { MaterialType } from '../../core/interfaces/types/building';

export type WeatherType = 'clear' | 'rain' | 'snow' | 'wind';

export class MaterialFatigueSystem {
    private elements: Map<string, BuildingModule> = new Map();
    private weather: WeatherType = 'clear';
    private time: number = 0;

    // Example degradation rates by material
    private static degradationRates: Record<MaterialType, number> = {
        wood: 0.02,
        stone: 0.005,
        metal: 0.01,
        reinforced: 0.003,
        composite: 0.008,
        upgraded: 0.006
    };

    registerElement(element: BuildingModule) {
        this.elements.set(element.moduleId, element);
    }

    unregisterElement(moduleId: string) {
        this.elements.delete(moduleId);
    }

    setWeather(weather: WeatherType) {
        this.weather = weather;
    }

    /**
     * Advance time and apply degradation to all elements
     */
    tick(hours: number = 1) {
        this.time += hours;
        for (const element of this.elements.values()) {
            const baseRate = MaterialFatigueSystem.degradationRates[element.material] || 0.01;
            let rate = baseRate * hours;
            // Apply weather effects
            switch (this.weather) {
                case 'rain':
                    if (element.material === 'wood') rate *= 2;
                    if (element.material === 'metal') rate *= 1.5;
                    break;
                case 'snow':
                    if (element.material === 'wood') rate *= 1.5;
                    if (element.material === 'stone') rate *= 1.2;
                    break;
                case 'wind':
                    rate *= 1.1;
                    break;
            }
            element.deteriorate(rate);
            // TODO: Visual feedback (e.g., rust, cracks)
        }
    }

    /**
     * Repair mechanic stub
     */
    repairElement(moduleId: string, amount: number) {
        const element = this.elements.get(moduleId);
        if (element) {
            element.repair(amount);
        }
    }

    /**
     * Get current degradation state for visual feedback
     */
    getDegradationStates(): Map<string, number> {
        const states = new Map<string, number>();
        for (const [id, element] of this.elements.entries()) {
            states.set(id, 1 - element.health / element.maxHealth);
        }
        return states;
    }
} 