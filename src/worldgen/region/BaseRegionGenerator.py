from typing import Dict, List, Optional, Any, Union

/**
 * Abstract base class for region generators that implements common functionality
 */
abstract class BaseRegionGenerator implements IRegionGenerator {
    /** The type of generator */
    protected readonly generatorType: GeneratorType;
    /**
     * Create a new base region generator
     * @param generatorType The type of this generator
     */
    constructor(generatorType: GeneratorType) {
        this.generatorType = generatorType;
    }
    /**
     * Get the type of this generator
     * @returns The generator type
     */
    public getGeneratorType(): GeneratorType {
        return this.generatorType;
    }
    /**
     * Generate a region with the given options
     * @param options The generation options
     * @returns The generation result containing the region
     */
    public generate(options: RegionGeneratorOptions): IGenerationResult<Region> {
        const seedConfig = this.ensureSeedConfig(options);
        const random = new DeterministicRNG(seedConfig);
        const startTime = performance.now();
        const region = this.generateRegion(options, random);
        const endTime = performance.now();
        const timeMs = endTime - startTime;
        return {
            result: region,
            metadata: {
                seedConfig,
                timestamp: Date.now(),
                performance: {
                    timeMs
                },
                debug: options.debug ? this.generateDebugInfo(options, random) : undefined
            }
        };
    }
    /**
     * Ensure that a seed configuration is available
     * @param options The generation options
     * @returns The seed configuration
     */
    protected ensureSeedConfig(options: RegionGeneratorOptions): ISeedConfig {
        if (options.seedConfig) {
            return options.seedConfig;
        }
        const seed = Math.floor(Math.random() * 1000000);
        return {
            seed,
            name: 'auto-generated'
        };
    }
    /**
     * Generate debug information if debug mode is enabled
     * @param options The generation options
     * @param random The random number generator
     * @returns Debug information
     */
    protected generateDebugInfo(options: RegionGeneratorOptions, random: IRandomGenerator): any {
        return {
            options,
            randomState: random.getState(),
            generatorType: this.generatorType
        };
    }
    /**
     * Abstract method to generate a region
     * This is where the implementation-specific logic goes
     * @param options The generation options
     * @param random The random number generator
     * @returns The generated region
     */
    protected abstract generateRegion(options: RegionGeneratorOptions, random: IRandomGenerator): Region;
    /**
     * Generate a unique ID for a region
     * @param options The generation options
     * @param random The random number generator
     * @returns A unique region ID
     */
    protected generateRegionId(options: RegionGeneratorOptions, random: IRandomGenerator): string {
        if (options.id) {
            return options.id;
        }
        const randomPart = Math.floor(random.random() * 1000000).toString(16);
        return `region-${Date.now().toString(36)}-${randomPart}`;
    }
    /**
     * Generate a name for a region if not provided
     * @param options The generation options
     * @param random The random number generator
     * @returns A region name
     */
    protected generateRegionName(options: RegionGeneratorOptions, random: IRandomGenerator): string {
        if (options.name) {
            return options.name;
        }
        const prefixes = ['North', 'South', 'East', 'West', 'Upper', 'Lower', 'Old', 'New'];
        const suffixes = ['Lands', 'Hills', 'Plains', 'Peaks', 'Valley', 'Ridge', 'Forest', 'Shores'];
        const prefix = random.randomElement(prefixes);
        const suffix = random.randomElement(suffixes);
        return `${prefix} ${suffix}`;
    }
} 