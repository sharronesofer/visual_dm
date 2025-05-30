from typing import Any, Dict



describe('POIEvolutionSystem', () => {
    let evolutionSystem: POIEvolutionSystem
    let poiManager: POIManager
    let factory: POIFactory
    beforeEach(() => {
        evolutionSystem = POIEvolutionSystem.getInstance()
        poiManager = POIManager.getInstance()
        factory = POIFactory.getInstance()
    })
    test('singleton instance works correctly', () => {
        const instance1 = POIEvolutionSystem.getInstance()
        const instance2 = POIEvolutionSystem.getInstance()
        expect(instance1).toBe(instance2)
    })
    test('evolution rules are applied correctly', () => {
        const dungeonPOI = factory.createPOI({
            type: POIType.DUNGEON,
            subType: POISubtype.DUNGEON_RUINS,
            name: 'Test Dungeon',
            coordinates: Dict[str, Any],
            thematicElements: Dict[str, Any]
        })
        evolutionSystem.addEvolutionRule(POIType.DUNGEON, {
            condition: () => true, 
            transform: (poi) => ({
                thematicElements: Dict[str, Any]
            }),
            priority: 1
        })
        evolutionSystem.processPOIEvolution(dungeonPOI.id, {
            type: 'time',
            data: Dict[str, Any]
        })
        expect(dungeonPOI.thematicElements.difficulty).toBe(2)
    })
    test('thematic consistency validation works', () => {
        const poi1 = factory.createPOI({
            type: POIType.DUNGEON,
            subType: POISubtype.DUNGEON_RUINS,
            name: 'Dungeon 1',
            coordinates: Dict[str, Any],
            thematicElements: Dict[str, Any]
        })
        const poi2 = factory.createPOI({
            type: POIType.DUNGEON,
            subType: POISubtype.DUNGEON_RUINS,
            name: 'Dungeon 2',
            coordinates: Dict[str, Any],
            thematicElements: Dict[str, Any]
        })
        poi1.addConnection(poi2.id)
        poi2.addConnection(poi1.id)
        evolutionSystem.addEvolutionRule(POIType.DUNGEON, {
            condition: () => true,
            transform: () => ({
                thematicElements: Dict[str, Any]
            }),
            priority: 1
        })
        evolutionSystem.processPOIEvolution(poi1.id, {
            type: 'event',
            data: Dict[str, Any]
        })
        expect(poi1.thematicElements.themes).toContain('ancient')
        expect(poi1.thematicElements.themes).not.toContain('futuristic')
    })
    test('evolution events are emitted', (done) => {
        const poi = factory.createPOI({
            type: POIType.SOCIAL,
            subType: POISubtype.SOCIAL_SETTLEMENT,
            name: 'Test Village',
            coordinates: Dict[str, Any],
            thematicElements: Dict[str, Any]
        })
        poiManager.once('poiModified', (data) => {
            expect(data.poiId).toBe(poi.id)
            expect(data.poi.thematicElements.population).toBe(2)
            done()
        })
        evolutionSystem.addEvolutionRule(POIType.SOCIAL, {
            condition: () => true,
            transform: (poi) => ({
                thematicElements: Dict[str, Any]
            }),
            priority: 1
        })
        evolutionSystem.processPOIEvolution(poi.id, {
            type: 'interaction',
            data: Dict[str, Any]
        })
    })
})
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
        )
        expect(poi.id).toBe('test-id')
        expect(poi.name).toBe('Test POI')
        expect(poi.type).toBe(POIType.SETTLEMENT)
        expect(poi.subtype).toBe(POISubtype.VILLAGE)
        expect(poi.coordinates).toEqual({ x: 1, y: 2, z: 3, level: 0 })
        expect(poi.thematicElements.biome).toBe('forest')
        expect(typeof poi.serialize).toBe('function')
        expect(typeof poi.deserialize).toBe('function')
        expect(typeof poi.validate).toBe('function')
    })
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
        )
        poi.description = 'A mysterious monument.'
        poi.isActive = true
        poi.isDiscovered = true
        poi.isExplored = false
        poi.canExpand = false
        const serialized = poi.serialize()
        const newPOI = new BasePOI(
            '', '', POIType.LANDMARK, POISubtype.MONUMENT,
            { x: 0, y: 0, z: 0, level: 0 },
            {
                biome: '', climate: '', era: '', culture: '', dangerLevel: 0, lighting: 'dim', themes: []
            }
        )
        newPOI.deserialize(serialized)
        expect(newPOI.id).toBe('test-id')
        expect(newPOI.name).toBe('Test POI')
        expect(newPOI.type).toBe(POIType.LANDMARK)
        expect(newPOI.subtype).toBe(POISubtype.MONUMENT)
        expect(newPOI.coordinates).toEqual({ x: 5, y: 6, z: 7, level: 1 })
        expect(newPOI.thematicElements.biome).toBe('mountain')
        expect(newPOI.description).toBe('A mysterious monument.')
        expect(newPOI.isActive).toBe(true)
        expect(newPOI.isDiscovered).toBe(true)
        expect(newPOI.isExplored).toBe(false)
        expect(newPOI.canExpand).toBe(false)
    })
}) 