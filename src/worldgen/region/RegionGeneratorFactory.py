from typing import Dict, List, Optional, Any, Union

/**
 * Factory for creating and managing region generators
 */
class RegionGeneratorFactory {
    /** Registry for all registered generators */
    private registry: GeneratorRegistry<IRegionGenerator>;
    /**
     * Create a new region generator factory
     */
    constructor() {
        this.registry = new GeneratorRegistry<IRegionGenerator>();
        this.registerDefaultGenerators();
    }
    /**
     * Register the default generators
     */
    private registerDefaultGenerators(): void {
        this.registry.register('procedural', new ProceduralRegionGenerator());
        this.registry.register('handcrafted', new HandcraftedRegionGenerator());
    }
    /**
     * Get a generator by ID
     * @param id The ID of the generator
     * @returns The generator
     */
    public getGenerator(id: string): IRegionGenerator {
        return this.registry.getOrThrow(id);
    }
    /**
     * Get a generator by type
     * @param type The type of generator
     * @returns The generator
     */
    public getGeneratorByType(type: GeneratorType): IRegionGenerator {
        for (const [id, generator] of this.registry.getAll()) {
            if (generator.getGeneratorType() === type) {
                return generator;
            }
        }
        throw new Error(`No generator found for type '${type}'`);
    }
    /**
     * Register a custom generator
     * @param id The ID to register the generator with
     * @param generator The generator to register
     */
    public registerGenerator(id: string, generator: IRegionGenerator): void {
        this.registry.register(id, generator);
    }
    /**
     * Get all registered generators
     * @returns A map of all registered generators
     */
    public getGenerators(): Map<string, IRegionGenerator> {
        return this.registry.getAll();
    }
    /**
     * Create a region with a procedural generator
     * @param options Generation options
     * @returns The generated region
     */
    public createProceduralRegion(options: RegionGeneratorOptions) {
        const generator = this.getGenerator('procedural');
        return generator.generate(options);
    }
    /**
     * Create a region with a hand-crafted generator
     * @param options Generation options
     * @returns The generated region
     */
    public createHandcraftedRegion(options: HandcraftedRegionGeneratorOptions) {
        const generator = this.getGenerator('handcrafted') as HandcraftedRegionGenerator;
        return generator.generate(options);
    }
    /**
     * Get the default instance of the factory
     * This is a singleton to ensure consistent access to the same generators
     */
    private static defaultInstance: RegionGeneratorFactory;
    /**
     * Get the default factory instance
     * @returns The default factory instance
     */
    public static getDefaultInstance(): RegionGeneratorFactory {
        if (!RegionGeneratorFactory.defaultInstance) {
            RegionGeneratorFactory.defaultInstance = new RegionGeneratorFactory();
        }
        return RegionGeneratorFactory.defaultInstance;
    }
} 