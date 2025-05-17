import { Building, BuildingGenerationHook, BuildingCustomizationConfig, BuildingCustomizationAPI } from './RegionGeneratorInterfaces';

/**
 * Implementation of the BuildingCustomizationAPI
 */
class BuildingCustomizationAPIImpl implements BuildingCustomizationAPI {
    private hooks: Set<BuildingGenerationHook> = new Set();
    private customizations: Map<string, BuildingCustomizationConfig> = new Map();
    private generators: Map<string, (...args: any[]) => Building> = new Map();
    private modifiers: Map<string, (building: Building) => Building> = new Map();

    registerHook(hook: BuildingGenerationHook): void {
        this.hooks.add(hook);
    }
    unregisterHook(hook: BuildingGenerationHook): void {
        this.hooks.delete(hook);
    }
    getHooks(): BuildingGenerationHook[] {
        return Array.from(this.hooks);
    }
    applyCustomization(config: BuildingCustomizationConfig): void {
        this.customizations.set(config.id, config);
    }
    getCustomizations(): BuildingCustomizationConfig[] {
        return Array.from(this.customizations.values());
    }
    registerGenerator(type: string, generator: (...args: any[]) => Building): void {
        this.generators.set(type, generator);
    }
    registerModifier(type: string, modifier: (building: Building) => Building): void {
        this.modifiers.set(type, modifier);
    }
    getGenerators(): Record<string, (...args: any[]) => Building> {
        const out: Record<string, (...args: any[]) => Building> = {};
        for (const [type, gen] of this.generators.entries()) {
            out[type] = gen;
        }
        return out;
    }
    getModifiers(): Record<string, (building: Building) => Building> {
        const out: Record<string, (building: Building) => Building> = {};
        for (const [type, mod] of this.modifiers.entries()) {
            out[type] = mod;
        }
        return out;
    }
}

/**
 * Singleton instance for use throughout the system
 */
export const BuildingCustomizationAPIInstance = new BuildingCustomizationAPIImpl(); 