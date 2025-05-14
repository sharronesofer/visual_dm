import { IGeneratorRegistry, IWorldGenerator } from './IWorldGenerator';

/**
 * Implementation of a generator registry that allows registering
 * and retrieving different world generator implementations
 */
export class GeneratorRegistry<T extends IWorldGenerator<any, any>> implements IGeneratorRegistry<T> {
    private generators: Map<string, T> = new Map();

    /**
     * Register a generator with a unique ID
     * @param id The unique identifier for the generator
     * @param generator The generator instance
     * @throws Error if a generator with the given ID already exists
     */
    public register(id: string, generator: T): void {
        if (this.generators.has(id)) {
            throw new Error(`Generator with ID '${id}' already exists`);
        }

        this.generators.set(id, generator);
    }

    /**
     * Get a generator by its ID
     * @param id The ID of the generator to retrieve
     * @returns The generator instance or undefined if not found
     */
    public get(id: string): T | undefined {
        return this.generators.get(id);
    }

    /**
     * Get all registered generators
     * @returns A map of all registered generators
     */
    public getAll(): Map<string, T> {
        return new Map(this.generators);
    }

    /**
     * Check if a generator with the given ID exists
     * @param id The ID to check
     * @returns True if a generator with the given ID exists, false otherwise
     */
    public has(id: string): boolean {
        return this.generators.has(id);
    }

    /**
     * Get a generator by its ID or throw an error if not found
     * @param id The ID of the generator to retrieve
     * @returns The generator instance
     * @throws Error if no generator with the given ID exists
     */
    public getOrThrow(id: string): T {
        const generator = this.get(id);
        if (!generator) {
            throw new Error(`No generator found with ID '${id}'`);
        }
        return generator;
    }

    /**
     * Remove a generator from the registry
     * @param id The ID of the generator to remove
     * @returns True if the generator was removed, false if not found
     */
    public unregister(id: string): boolean {
        return this.generators.delete(id);
    }

    /**
     * Get the number of registered generators
     * @returns The number of registered generators
     */
    public count(): number {
        return this.generators.size;
    }

    /**
     * Get all registered generator IDs
     * @returns An array of all registered generator IDs
     */
    public getIds(): string[] {
        return Array.from(this.generators.keys());
    }

    /**
     * Clear all registered generators
     */
    public clear(): void {
        this.generators.clear();
    }
} 