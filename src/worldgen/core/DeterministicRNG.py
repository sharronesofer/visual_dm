from typing import Dict, List, Optional, Any, Union

/**
 * Implementation of a deterministic random number generator
 * This uses a xorshift algorithm to ensure consistent results across platforms
 */
class DeterministicRNG implements IRandomGenerator {
    private seedConfig: ISeedConfig;
    private state: number;
    private initialState: number;
    /**
     * Create a new deterministic random number generator
     * @param seedConfig The seed configuration
     */
    constructor(seedConfig: ISeedConfig) {
        this.seedConfig = seedConfig;
        this.state = this.initialState = this.initState(seedConfig.seed);
    }
    /**
     * Initialize the state from a seed value
     * @param seed The seed value
     * @returns The initial state
     */
    private initState(seed: number): number {
        return seed !== 0 ? Math.abs(seed) : 1;
    }
    /**
     * Implements the xorshift algorithm for random number generation
     * This provides better statistical properties than naive PRNGs
     * @returns A random integer
     */
    private next(): number {
        let x = this.state;
        x ^= x << 13;
        x ^= x >> 17;
        x ^= x << 5;
        this.state = x;
        return x;
    }
    /**
     * Get the seed configuration
     * @returns The seed configuration
     */
    public getSeedConfig(): ISeedConfig {
        return this.seedConfig;
    }
    /**
     * Get a random number between 0 and 1
     * @returns A random number in [0, 1)
     */
    public random(): number {
        return Math.abs(this.next()) / 0x7FFFFFFF;
    }
    /**
     * Get a random integer between min (inclusive) and max (inclusive)
     * @param min The minimum value (inclusive)
     * @param max The maximum value (inclusive)
     * @returns A random integer in [min, max]
     */
    public randomInt(min: number, max: number): number {
        return Math.floor(this.random() * (max - min + 1)) + min;
    }
    /**
     * Get a random element from an array
     * @param array The array to select from
     * @returns A random element
     */
    public randomElement<T>(array: T[]): T {
        if (array.length === 0) {
            throw new Error('Cannot select from an empty array');
        }
        return array[this.randomInt(0, array.length - 1)];
    }
    /**
     * Get a random weighted element from an array with weights
     * @param elements The elements array
     * @param weights The corresponding weights
     * @returns A randomly selected element based on weights
     */
    public randomWeightedElement<T>(elements: T[], weights: number[]): T {
        if (elements.length === 0) {
            throw new Error('Cannot select from an empty array');
        }
        if (elements.length !== weights.length) {
            throw new Error('Elements and weights arrays must have the same length');
        }
        const totalWeight = weights.reduce((sum, weight) => sum + weight, 0);
        let randomValue = this.random() * totalWeight;
        for (let i = 0; i < elements.length; i++) {
            randomValue -= weights[i];
            if (randomValue <= 0) {
                return elements[i];
            }
        }
        return elements[elements.length - 1];
    }
    /**
     * Create a child random generator with a derived seed
     * @param name The name for the child generator
     * @returns A new random generator with a derived seed
     */
    public createChild(name: string): IRandomGenerator {
        let childSeed = this.seedConfig.seed;
        for (let i = 0; i < name.length; i++) {
            childSeed = (childSeed * 31 + name.charCodeAt(i)) | 0;
        }
        const childSeedConfig: ISeedConfig = {
            seed: childSeed,
            name: name,
            parent: this.seedConfig
        };
        return new DeterministicRNG(childSeedConfig);
    }
    /**
     * Get the current state of the RNG (for debugging/logging)
     * @returns The current state
     */
    public getState(): any {
        return {
            state: this.state,
            initialState: this.initialState,
            seedConfig: this.seedConfig
        };
    }
    /**
     * Reset the RNG to its initial state
     */
    public reset(): void {
        this.state = this.initialState;
    }
} 