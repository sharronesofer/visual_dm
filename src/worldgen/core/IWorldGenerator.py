from enum import Enum
from typing import Dict, List, Optional, Any, Union

/**
 * Core interfaces for the world generation system.
 * This file defines the base interfaces and types that all world generators must implement.
 */
/**
 * Configuration for random number generation to ensure determinism
 */
class ISeedConfig:
    /** The primary seed value for the generator */
    seed: float
    /** Optional name/identifier for the seed's purpose (useful for debugging) */
    name?: str
    /** Optional parent seed this was derived from (for hierarchical seeding) */
    parent?: ISeedConfig
/**
 * Common options interface for all generators
 */
class IGeneratorOptions:
    /** Seed configuration to ensure deterministic generation */
    seedConfig: ISeedConfig
    /** Optional debug mode flag to enable additional logging */
    debug?: bool
/**
 * A deterministic random number generator interface
 */
class IRandomGenerator:
    /** Get the seed configuration */
    getSeedConfig(): ISeedConfig
    /** Get a random number between 0 and 1 */
    random(): float
    /** Get a random integer between min (inclusive) and max (inclusive) */
    randomInt(min: float, max: float): float
    /** Get a random element from an array */
    randomElement<T>(array: T[]): T
    /** Get a random weighted element from an array with weights */
    randomWeightedElement<T>(elements: T[], weights: float[]): T
    /** Create a child random generator with a derived seed */
    createChild(name: str): IRandomGenerator
    /** Get the current state of the RNG (for debugging/logging) */
    getState(): Any
/**
 * Generic output type for world generators
 */
interface IGenerationResult<T> {
    /** The generated output */
    result: T;
    /** Metadata about the generation process */
    metadata: {
        /** The seed configuration used */
        seedConfig: ISeedConfig;
        /** Generation timestamp */
        timestamp: number;
        /** Performance metrics */
        performance?: {
            /** Time taken in milliseconds */
            timeMs: number;
        };
        /** Debug information if debug mode was enabled */
        debug?: any;
    };
}
/**
 * Base interface that all world generators must implement
 */
interface IWorldGenerator<TOptions extends IGeneratorOptions, TOutput> {
    /** Generate output using the provided options */
    generate(options: TOptions): IGenerationResult<TOutput>;
}
/**
 * Registry for storing and retrieving generator implementations
 */
interface IGeneratorRegistry<T extends IWorldGenerator<any, any>> {
    /** Register a generator with a unique ID */
    register(id: string, generator: T): void;
    /** Get a generator by its ID */
    get(id: string): T | undefined;
    /** Get all registered generators */
    getAll(): Map<string, T>;
    /** Check if a generator with the given ID exists */
    has(id: string): boolean;
}
/**
 * Defines the interface for a pipeline step in the generation process
 */
interface IPipelineStep<TInput, TOutput> {
    /** Process the input and return the transformed output */
    process(input: TInput, random: IRandomGenerator): TOutput;
}
/**
 * Defines the interface for a generation pipeline that consists of multiple steps
 */
interface IGenerationPipeline<TInput, TOutput> {
    /** Add a step to the pipeline */
    addStep<TIntermediate>(step: IPipelineStep<TInput, TIntermediate>): IGenerationPipeline<TIntermediate, TOutput>;
    /** Execute the pipeline with the given input */
    execute(input: TInput, random: IRandomGenerator): TOutput;
}
/**
 * Types of world generators
 */
class GeneratorType(Enum):
    /** Procedural generators use algorithms and random number generation */
    PROCEDURAL = 'procedural'
    /** Hand-crafted generators use pre-defined templates */
    HAND_CRAFTED = 'hand_crafted'
    /** Hybrid generators combine procedural and hand-crafted approaches */
    HYBRID = 'hybrid'
/**
 * Base interface for validation rules that can be applied to generation results
 */
interface IValidationRule<T> {
    /** Validate the generated output */
    validate(output: T): boolean;
    /** Get an error message if validation fails */
    getErrorMessage(): string;
} 