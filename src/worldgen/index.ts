/**
 * World Generation System
 * 
 * A deterministic, extensible architecture for procedural and hand-crafted world generation
 * with built-in validation and a clear separation of concerns.
 */

// Core interfaces and types
export * from './core/IWorldGenerator';
export * from './core/DeterministicRNG';
export * from './core/GeneratorRegistry';
export * from './core/GenerationPipeline';

// Region generation
export * from './region/RegionGeneratorInterfaces';
export * from './region/BaseRegionGenerator';
export * from './region/ProceduralRegionGenerator';
export * from './region/HandcraftedRegionGenerator';
export * from './region/RegionGeneratorFactory';

// Validation
export * from './validation/RegionValidationRules';
export * from './validation/RegionValidator';

// Import for helper functions
import { RegionGeneratorFactory } from './region/RegionGeneratorFactory';
import { GeneratorType } from './core/IWorldGenerator';
import { RegionValidator } from './validation/RegionValidator';

/**
 * Create a procedural region using the default factory
 * @param width Region width
 * @param height Region height
 * @param seed Optional seed value
 * @returns The generated region
 */
export function createProceduralRegion(width: number, height: number, seed?: number) {
    const factory = RegionGeneratorFactory.getDefaultInstance();

    return factory.createProceduralRegion({
        width,
        height,
        generatorType: GeneratorType.PROCEDURAL,
        seedConfig: seed ? { seed } : undefined
    });
}

/**
 * Create a hand-crafted region using a template
 * @param templateId The template ID to use
 * @param width Optional width (uses template width if not provided)
 * @param height Optional height (uses template height if not provided)
 * @param seed Optional seed value
 * @returns The generated region
 */
export function createTemplateRegion(templateId: string, width?: number, height?: number, seed?: number) {
    const factory = RegionGeneratorFactory.getDefaultInstance();

    return factory.createHandcraftedRegion({
        templateId,
        width,
        height,
        generatorType: GeneratorType.HAND_CRAFTED,
        seedConfig: seed ? { seed } : undefined
    });
}

/**
 * Validate a region with the default validator
 * @param region The region to validate
 * @returns Validation result
 */
export function validateRegion(region: any) {
    const validator = RegionValidator.getDefaultInstance();
    return validator.validate(region);
} 