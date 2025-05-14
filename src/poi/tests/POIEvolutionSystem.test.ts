import { POIEvolutionSystem } from '../systems/POIEvolutionSystem';
import { POIManager } from '../managers/POIManager';
import { POIFactory } from '../factories/POIFactory';
import { POIType, POISubtype } from '../types/POITypes';
import { BasePOI } from '../models/BasePOI';

describe('POIEvolutionSystem', () => {
    let evolutionSystem: POIEvolutionSystem;
    let poiManager: POIManager;
    let factory: POIFactory;

    beforeEach(() => {
        evolutionSystem = POIEvolutionSystem.getInstance();
        poiManager = POIManager.getInstance();
        factory = POIFactory.getInstance();
    });

    test('singleton instance works correctly', () => {
        const instance1 = POIEvolutionSystem.getInstance();
        const instance2 = POIEvolutionSystem.getInstance();
        expect(instance1).toBe(instance2);
    });

    test('evolution rules are applied correctly', () => {
        // Create a test dungeon POI
        const dungeonPOI = factory.createPOI({
            type: POIType.DUNGEON,
            subType: POISubtype.DUNGEON_RUINS,
            name: 'Test Dungeon',
            coordinates: { x: 0, y: 0, z: 0 },
            thematicElements: {
                themes: ['ancient', 'mysterious'],
                difficulty: 1
            }
        });

        // Register test rule
        evolutionSystem.addEvolutionRule(POIType.DUNGEON, {
            condition: () => true, // Always trigger for test
            transform: (poi) => ({
                thematicElements: {
                    ...poi.thematicElements,
                    difficulty: 2
                }
            }),
            priority: 1
        });

        // Trigger evolution
        evolutionSystem.processPOIEvolution(dungeonPOI.id, {
            type: 'time',
            data: { elapsed: 3600 }
        });

        // Verify changes
        expect(dungeonPOI.thematicElements.difficulty).toBe(2);
    });

    test('thematic consistency validation works', () => {
        // Create two connected POIs
        const poi1 = factory.createPOI({
            type: POIType.DUNGEON,
            subType: POISubtype.DUNGEON_RUINS,
            name: 'Dungeon 1',
            coordinates: { x: 0, y: 0, z: 0 },
            thematicElements: {
                themes: ['ancient', 'mysterious']
            }
        });

        const poi2 = factory.createPOI({
            type: POIType.DUNGEON,
            subType: POISubtype.DUNGEON_RUINS,
            name: 'Dungeon 2',
            coordinates: { x: 10, y: 0, z: 0 },
            thematicElements: {
                themes: ['mysterious', 'cursed']
            }
        });

        // Connect POIs
        poi1.addConnection(poi2.id);
        poi2.addConnection(poi1.id);

        // Add evolution rule that would break thematic consistency
        evolutionSystem.addEvolutionRule(POIType.DUNGEON, {
            condition: () => true,
            transform: () => ({
                thematicElements: {
                    themes: ['futuristic', 'tech'] // Incompatible themes
                }
            }),
            priority: 1
        });

        // Try to evolve POI1
        evolutionSystem.processPOIEvolution(poi1.id, {
            type: 'event',
            data: { event: 'test' }
        });

        // Verify changes were rejected
        expect(poi1.thematicElements.themes).toContain('ancient');
        expect(poi1.thematicElements.themes).not.toContain('futuristic');
    });

    test('evolution events are emitted', (done) => {
        const poi = factory.createPOI({
            type: POIType.SOCIAL,
            subType: POISubtype.SOCIAL_SETTLEMENT,
            name: 'Test Village',
            coordinates: { x: 0, y: 0, z: 0 },
            thematicElements: {
                themes: ['peaceful', 'rural'],
                population: 1
            }
        });

        // Listen for modification event
        poiManager.once('poiModified', (data) => {
            expect(data.poiId).toBe(poi.id);
            expect(data.poi.thematicElements.population).toBe(2);
            done();
        });

        // Add and trigger evolution rule
        evolutionSystem.addEvolutionRule(POIType.SOCIAL, {
            condition: () => true,
            transform: (poi) => ({
                thematicElements: {
                    ...poi.thematicElements,
                    population: 2
                }
            }),
            priority: 1
        });

        evolutionSystem.processPOIEvolution(poi.id, {
            type: 'interaction',
            data: { type: 'visit' }
        });
    });
});

describe('IPOI/BasePOI Data Structure', () => {
    test('BasePOI implements IPOI and exposes all required properties', () => {
        const poi = new BasePOI(
            'test-id',
            'Test POI',
            POIType.SETTLEMENT,
            POISubtype.VILLAGE,
            { x: 1, y: 2, z: 3, level: 0 },
            {
                biome: 'forest',
                climate: 'temperate',
                era: 'medieval',
                culture: 'elven',
                dangerLevel: 2,
                lighting: 'bright',
                themes: ['peaceful'],
            }
        );
        expect(poi.id).toBe('test-id');
        expect(poi.name).toBe('Test POI');
        expect(poi.type).toBe(POIType.SETTLEMENT);
        expect(poi.subtype).toBe(POISubtype.VILLAGE);
        expect(poi.coordinates).toEqual({ x: 1, y: 2, z: 3, level: 0 });
        expect(poi.thematicElements.biome).toBe('forest');
        expect(typeof poi.serialize).toBe('function');
        expect(typeof poi.deserialize).toBe('function');
        expect(typeof poi.validate).toBe('function');
    });

    test('BasePOI serialization and deserialization preserves data', () => {
        const poi = new BasePOI(
            'test-id',
            'Test POI',
            POIType.LANDMARK,
            POISubtype.MONUMENT,
            { x: 5, y: 6, z: 7, level: 1 },
            {
                biome: 'mountain',
                climate: 'arid',
                era: 'ancient',
                culture: 'dwarven',
                dangerLevel: 5,
                lighting: 'dim',
                themes: ['historic'],
            }
        );
        poi.description = 'A mysterious monument.';
        poi.isActive = true;
        poi.isDiscovered = true;
        poi.isExplored = false;
        poi.canExpand = false;
        const serialized = poi.serialize();
        const newPOI = new BasePOI(
            '', '', POIType.LANDMARK, POISubtype.MONUMENT,
            { x: 0, y: 0, z: 0, level: 0 },
            {
                biome: '', climate: '', era: '', culture: '', dangerLevel: 0, lighting: 'dim', themes: []
            }
        );
        newPOI.deserialize(serialized);
        expect(newPOI.id).toBe('test-id');
        expect(newPOI.name).toBe('Test POI');
        expect(newPOI.type).toBe(POIType.LANDMARK);
        expect(newPOI.subtype).toBe(POISubtype.MONUMENT);
        expect(newPOI.coordinates).toEqual({ x: 5, y: 6, z: 7, level: 1 });
        expect(newPOI.thematicElements.biome).toBe('mountain');
        expect(newPOI.description).toBe('A mysterious monument.');
        expect(newPOI.isActive).toBe(true);
        expect(newPOI.isDiscovered).toBe(true);
        expect(newPOI.isExplored).toBe(false);
        expect(newPOI.canExpand).toBe(false);
    });
}); 