import { describe, it, expect, vi } from 'vitest';
import {
    createProceduralRegion,
    createTemplateRegion,
    validateRegion,
    GeneratorType,
    RegionGeneratorFactory,
    DeterministicRNG,
    Region,
    RegionTemplate
} from '../../src/worldgen';

describe('Region Generation System', () => {
    // Test deterministic behavior
    describe('Deterministic Behavior', () => {
        it('should generate identical regions with the same seed', () => {
            // Generate two regions with the same seed
            const seed = 12345;
            const region1 = createProceduralRegion(10, 10, seed);
            const region2 = createProceduralRegion(10, 10, seed);

            // Check that the regions exist
            expect(region1).toBeDefined();
            expect(region2).toBeDefined();
            expect(region1.result).toBeDefined();
            expect(region2.result).toBeDefined();

            // They should be identical
            expect(region1.result.width).toEqual(region2.result.width);
            expect(region1.result.height).toEqual(region2.result.height);
            // Deep compare the cells array
            expect(JSON.stringify(region1.result.cells)).toEqual(JSON.stringify(region2.result.cells));
        });

        it('should generate different regions with different seeds', () => {
            // Generate two regions with different seeds
            const region1 = createProceduralRegion(10, 10, 12345);
            const region2 = createProceduralRegion(10, 10, 67890);

            // Check that the regions exist
            expect(region1).toBeDefined();
            expect(region2).toBeDefined();
            expect(region1.result).toBeDefined();
            expect(region2.result).toBeDefined();

            // They should be different
            expect(JSON.stringify(region1.result.cells)).not.toEqual(JSON.stringify(region2.result.cells));
        });

        it('should produce repeatable results with child RNGs', () => {
            const seed1 = 54321;
            const seed2 = 54321;

            const rng1 = new DeterministicRNG({ seed: seed1 });
            const rng2 = new DeterministicRNG({ seed: seed2 });

            // Generate a sequence of random numbers with both RNGs
            const nums1 = Array.from({ length: 100 }, () => rng1.random());
            const nums2 = Array.from({ length: 100 }, () => rng2.random());

            // They should be identical
            expect(nums1).toEqual(nums2);

            // Create child RNGs and test them
            const child1 = rng1.createChild('test');
            const child2 = rng2.createChild('test');

            const childNums1 = Array.from({ length: 100 }, () => child1.random());
            const childNums2 = Array.from({ length: 100 }, () => child2.random());

            // They should also be identical
            expect(childNums1).toEqual(childNums2);
        });
    });

    // Test extensibility
    describe('Extensibility', () => {
        it('should support custom templates for hand-crafted regions', () => {
            // Create a factory
            const factory = RegionGeneratorFactory.getDefaultInstance();

            // Create a hand-crafted generator
            const handcraftedGenerator = factory.getGenerator('handcrafted');

            // Create a template
            const template: RegionTemplate = {
                id: 'test-template',
                name: 'Test Template',
                description: 'A test template',
                width: 5,
                height: 5,
                cells: [
                    { x: 0, y: 0, terrain: 'water' },
                    { x: 1, y: 1, terrain: 'forest' },
                    { x: 2, y: 2, terrain: 'mountain' },
                    { x: 3, y: 3, terrain: 'desert' },
                    { x: 4, y: 4, terrain: 'urban' }
                ],
                pointsOfInterest: [
                    { templateId: 'poi1', x: 2, y: 2 }
                ],
                resources: [
                    { templateId: 'resource1', x: 1, y: 1, amount: 0.5 }
                ]
            };

            // Register the template
            (handcraftedGenerator as any).registerTemplate(template);

            // Create a region with the template
            const regionResult = createTemplateRegion('test-template');
            const region = regionResult.result;

            // Check that the template was used
            expect(region.name).toBe('Test Template');
            expect(region.width).toBe(5);
            expect(region.height).toBe(5);

            // Check that the cells were created correctly
            expect(region.cells.find(c => c.x === 0 && c.y === 0)?.terrain).toBe('water');
            expect(region.cells.find(c => c.x === 1 && c.y === 1)?.terrain).toBe('forest');
            expect(region.cells.find(c => c.x === 2 && c.y === 2)?.terrain).toBe('mountain');

            // Check POIs and resources
            expect(region.pointsOfInterest.length).toBe(1);
            expect(region.pointsOfInterest[0].templateId).toBe('poi1');
            expect(region.resources.length).toBe(1);
            expect(region.resources[0].templateId).toBe('resource1');
        });

        it('should support custom generators', () => {
            // Create a factory
            const factory = RegionGeneratorFactory.getDefaultInstance();

            // Define a mock implementation of a custom generator
            const mockGenerator = {
                generate: vi.fn().mockReturnValue({
                    result: {
                        id: 'mock-region',
                        name: 'Mock Region',
                        description: 'A mock region',
                        width: 10,
                        height: 10,
                        cells: [],
                        pointsOfInterest: [],
                        resources: [],
                        metadata: {
                            seed: 42,
                            generatorType: GeneratorType.HYBRID,
                            parameters: {}
                        }
                    },
                    metadata: {
                        seedConfig: { seed: 42 },
                        timestamp: Date.now()
                    }
                }),
                getGeneratorType: vi.fn().mockReturnValue(GeneratorType.HYBRID)
            };

            // Register the mock generator
            factory.registerGenerator('mock', mockGenerator);

            // Get the generator and use it
            const generator = factory.getGenerator('mock');
            const result = generator.generate({
                width: 10,
                height: 10,
                generatorType: GeneratorType.HYBRID,
                seedConfig: { seed: 42 }
            });

            // Check that the mock was called
            expect(mockGenerator.generate).toHaveBeenCalled();
            expect(result.result.name).toBe('Mock Region');
        });
    });

    // Test validation
    describe('Validation', () => {
        it('should validate valid regions', () => {
            // Create a valid region
            const regionResult = createProceduralRegion(10, 10, 12345);

            // Check that the region exists
            expect(regionResult).toBeDefined();
            expect(regionResult.result).toBeDefined();

            const region = regionResult.result;

            // Validate it
            const validation = validateRegion(region);

            // It should be valid
            expect(validation.isValid).toBe(true);
        });

        it('should detect invalid regions', () => {
            // Create an invalid region (missing cells)
            const invalidRegion: any = {
                id: 'invalid-region',
                name: 'Invalid Region',
                description: 'An invalid region',
                width: 10,
                height: 10,
                // Missing cells array
                pointsOfInterest: [],
                resources: [],
                metadata: {
                    seed: 42,
                    generatorType: GeneratorType.PROCEDURAL,
                    parameters: {}
                }
            };

            // Validate it
            const validation = validateRegion(invalidRegion);

            // It should be invalid
            expect(validation.isValid).toBe(false);
            // The error should contain details
            expect(validation.errorMessage).toBeDefined();
        });
    });
}); 