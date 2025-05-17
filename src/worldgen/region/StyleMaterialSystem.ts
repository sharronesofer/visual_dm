import { RegionCell, Resource, BuildingMaterialStyle } from './RegionGeneratorInterfaces';

export interface EnvironmentFactors {
    temperature: number; // 0-1
    humidity: number;    // 0-1
    altitude: number;    // 0-1
    [key: string]: any;
}

// Plugin registry for extensibility
const styleMaterialPlugins: ((context: {
    cell: RegionCell;
    resources: Resource[];
    environment: EnvironmentFactors;
    current: { material: string; style: string; textureVariant?: string; modelVariant?: string };
}) => Partial<{ material: string; style: string; textureVariant: string; modelVariant: string }>)[] = [];

/**
 * Register a plugin for the style/material system (for modding/extensibility)
 */
export function registerStyleMaterialPlugin(plugin: typeof styleMaterialPlugins[0]) {
    styleMaterialPlugins.push(plugin);
}

/**
 * Registry for runtime registration of new materials and styles (modding/extensibility)
 */
const styleMaterialRegistry: BuildingMaterialStyle[] = [];

/**
 * Register a new material/style definition at runtime
 * @param entry BuildingMaterialStyle to register
 */
export function registerStyleMaterial(entry: BuildingMaterialStyle) {
    styleMaterialRegistry.push(entry);
}

/**
 * Clear all registered materials/styles (for testing or reload)
 */
export function clearStyleMaterialRegistry() {
    styleMaterialRegistry.length = 0;
}

/**
 * Main function to select material and style for a building
 * Extensible: applies all registered plugins for modding/customization.
 * @param cell The region cell where the building is placed
 * @param resources Array of available resources in the region
 * @param environment Environmental factors (temperature, humidity, altitude, etc.)
 * @returns Selected material, style, and optional variants
 */
export function selectMaterialAndStyle(
    cell: RegionCell,
    resources: Resource[],
    environment: EnvironmentFactors
): {
    material: string;
    style: string;
    textureVariant?: string;
    modelVariant?: string;
} {
    // Biome-to-material mapping
    const biomeMaterialMap: Record<string, string[]> = {
        forest: ['wood', 'thatch'],
        mountain: ['stone', 'slate'],
        desert: ['clay', 'adobe'],
        plains: ['wood', 'brick'],
        urban: ['brick', 'concrete'],
        water: ['wood', 'stone']
    };
    // Biome-to-style mapping
    const biomeStyleMap: Record<string, string[]> = {
        forest: ['cabin', 'timber'],
        mountain: ['chalet', 'fortress'],
        desert: ['adobe', 'tent'],
        plains: ['farmhouse', 'cottage'],
        urban: ['rowhouse', 'villa'],
        water: ['stilted', 'dockhouse']
    };
    // Resource availability check
    const resourceTypes = new Set(resources.map(r => r.templateId));
    let material = 'wood';
    let style = 'default';
    const biome = cell.terrain;
    // Use registry if populated, otherwise fallback to built-in mappings
    let candidates: string[];
    if (styleMaterialRegistry.length > 0) {
        candidates = styleMaterialRegistry
            .filter(ms => !ms.biome || ms.biome === biome)
            .map(ms => ms.material);
        if (candidates.length === 0) {
            candidates = ['wood'];
        }
    } else {
        candidates = biomeMaterialMap[biome] || ['wood'];
    }
    material = candidates.find(m => resourceTypes.has(m)) || candidates[0];
    // Material substitution if none available
    if (!resourceTypes.has(material)) {
        // Fallback to any available resource
        material = Array.from(resourceTypes)[0] || candidates[0];
    }
    // Style selection
    let styleCandidates: string[];
    if (styleMaterialRegistry.length > 0) {
        styleCandidates = styleMaterialRegistry
            .filter(ms => !ms.biome || ms.biome === biome)
            .map(ms => ms.style);
        if (styleCandidates.length === 0) {
            styleCandidates = ['default'];
        }
    } else {
        styleCandidates = biomeStyleMap[biome] || ['default'];
    }
    style = styleCandidates[Math.floor(environment.temperature * styleCandidates.length) % styleCandidates.length];
    // Environmental adaptation (texture/model variants)
    let textureVariant: string | undefined;
    let modelVariant: string | undefined;
    if (environment.humidity > 0.7) {
        textureVariant = 'mossy';
    } else if (environment.temperature > 0.8) {
        textureVariant = 'sunbleached';
    }
    if (environment.altitude > 0.7) {
        modelVariant = 'high-altitude';
    }
    // Procedural variation
    if (Math.random() < 0.2) {
        style += '-alt';
    }
    // --- Plugin extensibility: allow mods to override/extend logic ---
    let result = { material, style, textureVariant, modelVariant };
    for (const plugin of styleMaterialPlugins) {
        const pluginResult = plugin({ cell, resources, environment, current: result });
        if (pluginResult) {
            result = { ...result, ...pluginResult };
        }
    }
    return result;
}

/**
 * StyleMaterialSystem: Extensible system for selecting building materials and styles
 *
 * Extension points:
 * - registerStyleMaterialPlugin(plugin): Add custom logic for style/material selection (modding)
 * - registerStyleMaterial(entry): Add new material/style definitions at runtime
 * - clearStyleMaterialRegistry(): Clear registry (for reload/testing)
 *
 * Usage:
 *   import { selectMaterialAndStyle, registerStyleMaterial, registerStyleMaterialPlugin } from './StyleMaterialSystem';
 *
 *   // Register a new material/style
 *   registerStyleMaterial({ material: 'bamboo', style: 'pagoda', biome: 'forest' });
 *
 *   // Register a plugin to override style selection
 *   registerStyleMaterialPlugin(({ cell, current }) => {
 *     if (cell.terrain === 'desert') return { style: 'pyramid' };
 *   });
 *
 *   // Use in region generation
 *   const result = selectMaterialAndStyle(cell, resources, environment);
 */

/**
 * System is designed for extensibility: modders can override or extend mappings and logic.
 * Use registerStyleMaterialPlugin() to add new logic at runtime.
 */ 