from typing import Any, Dict


  POICategory,
  POIPlacementRules,
  PlacementPattern,
  SpatialLayoutConfig
} from '../../../types/spatial'
describe('POI Layout System - Integration Tests', () => {
  let poiManager: POIManager
  let gridManager: GridManager
  let collisionSystem: CollisionSystem
  let terrainManager: TerrainManager
  let layoutGenerator: SpatialLayoutGenerator
  let config: SpatialLayoutConfig
  beforeEach(() => {
    const dimensions: GridDimensions = { width: 20, height: 20 }
    gridManager = new GridManager(dimensions)
    const terrainData: TerrainData = {
      heightMap: Array(dimensions.height).fill(null).map(() => Array(dimensions.width).fill(0)),
      features: [
        {
          type: TerrainFeatureType.WATER,
          position: Dict[str, Any],
          size: Dict[str, Any],
          elevation: -1
        },
        {
          type: TerrainFeatureType.MOUNTAIN,
          position: Dict[str, Any],
          size: Dict[str, Any],
          elevation: 5
        }
      ],
      buildableAreas: [
        {
          position: Dict[str, Any],
          size: Dict[str, Any],
          slope: 0,
          preferredCategories: ['SOCIAL']
        }
      ]
    }
    terrainManager = new TerrainManager(terrainData)
    collisionSystem = new CollisionSystem(gridManager)
    poiManager = POIManager.getInstance()
    config = {
      minDistance: 2,
      maxDistance: 5,
      placementRules: new Map<POICategory, POIPlacementRules>([
        ['SOCIAL', {
          pattern: PlacementPattern.CLUSTER,
          minElevation: -1,
          maxElevation: 3,
          terrainPreferences: [TerrainFeatureType.WATER],
          avoidFeatures: [TerrainFeatureType.MOUNTAIN]
        }]
      ])
    }
    layoutGenerator = new SpatialLayoutGenerator(
      gridManager,
      collisionSystem,
      terrainManager,
      config
    )
  })
  afterEach(() => {
    for (const poi of poiManager.getAllPOIs()) {
      poiManager.deregisterPOI(poi.id)
    }
  })
  describe('POI Placement', () => {
    test('places POIs according to terrain constraints', async () => {
      const poi = poiManager.createPOI(
        POIType.TAVERN,
        POISubtype.COMMON,
        { name: 'Test Tavern' }
      )
      const placement = await layoutGenerator.placePOI(poi, 'SOCIAL')
      expect(placement).toBeDefined()
      expect(placement?.success).toBe(true)
      if (placement?.success) {
        const coords = placement.coordinates
        const terrain = terrainManager.analyzeTerrain(coords)
        expect(terrain.elevation).toBeGreaterThanOrEqual(config.placementRules.get('SOCIAL')!.minElevation)
        expect(terrain.elevation).toBeLessThanOrEqual(config.placementRules.get('SOCIAL')!.maxElevation)
        const cell = gridManager.getCellAt(coords)
        expect(cell?.isOccupied).toBe(true)
        expect(cell?.cellType).toBe(CellType.BUILDING)
      }
    })
    test('respects minimum distance between POIs', async () => {
      const poi1 = poiManager.createPOI(
        POIType.TAVERN,
        POISubtype.COMMON,
        { name: 'Tavern 1' }
      )
      const poi2 = poiManager.createPOI(
        POIType.TAVERN,
        POISubtype.COMMON,
        { name: 'Tavern 2' }
      )
      const placement1 = await layoutGenerator.placePOI(poi1, 'SOCIAL')
      expect(placement1?.success).toBe(true)
      const placement2 = await layoutGenerator.placePOI(poi2, 'SOCIAL')
      expect(placement2?.success).toBe(true)
      if (placement1?.success && placement2?.success) {
        const distance = Math.sqrt(
          Math.pow(placement2.coordinates.x - placement1.coordinates.x, 2) +
          Math.pow(placement2.coordinates.y - placement1.coordinates.y, 2)
        )
        expect(distance).toBeGreaterThanOrEqual(config.minDistance)
      }
    })
    test('avoids placing POIs in invalid terrain', async () => {
      const poi = poiManager.createPOI(
        POIType.TAVERN,
        POISubtype.COMMON,
        { name: 'Mountain Tavern' }
      )
      const placement = await layoutGenerator.placePOI(poi, 'SOCIAL', {
        preferredPosition: Dict[str, Any] 
      })
      expect(placement?.success).toBe(true)
      if (placement?.success) {
        const terrain = terrainManager.analyzeTerrain(placement.coordinates)
        expect(terrain.nearbyFeatures).not.toContain(TerrainFeatureType.MOUNTAIN)
      }
    })
  })
  describe('Path Generation', () => {
    test('generates valid paths between POIs', async () => {
      const poi1 = poiManager.createPOI(
        POIType.TAVERN,
        POISubtype.COMMON,
        { name: 'Start Tavern' }
      )
      const poi2 = poiManager.createPOI(
        POIType.TAVERN,
        POISubtype.COMMON,
        { name: 'End Tavern' }
      )
      const placement1 = await layoutGenerator.placePOI(poi1, 'SOCIAL')
      const placement2 = await layoutGenerator.placePOI(poi2, 'SOCIAL')
      expect(placement1?.success).toBe(true)
      expect(placement2?.success).toBe(true)
      if (placement1?.success && placement2?.success) {
        const path = await layoutGenerator.generatePath(
          placement1.coordinates,
          placement2.coordinates
        )
        expect(path).toBeDefined()
        expect(path.length).toBeGreaterThan(0)
        for (let i = 0; i < path.length - 1; i++) {
          const dx = Math.abs(path[i + 1].x - path[i].x)
          const dy = Math.abs(path[i + 1].y - path[i].y)
          expect(dx + dy).toBeLessThanOrEqual(2) 
          const cell = gridManager.getCellAt(path[i])
          expect(cell?.walkable).toBe(true)
        }
      }
    })
    test('paths avoid obstacles and terrain features', async () => {
      const poi1 = poiManager.createPOI(
        POIType.TAVERN,
        POISubtype.COMMON,
        { name: 'West Tavern' }
      )
      const poi2 = poiManager.createPOI(
        POIType.TAVERN,
        POISubtype.COMMON,
        { name: 'East Tavern' }
      )
      const placement1 = await layoutGenerator.placePOI(poi1, 'SOCIAL', {
        preferredPosition: Dict[str, Any] 
      })
      const placement2 = await layoutGenerator.placePOI(poi2, 'SOCIAL', {
        preferredPosition: Dict[str, Any] 
      })
      expect(placement1?.success).toBe(true)
      expect(placement2?.success).toBe(true)
      if (placement1?.success && placement2?.success) {
        const path = await layoutGenerator.generatePath(
          placement1.coordinates,
          placement2.coordinates
        )
        expect(path).toBeDefined()
        expect(path.length).toBeGreaterThan(0)
        for (const point of path) {
          const terrain = terrainManager.analyzeTerrain(point)
          expect(terrain.nearbyFeatures).not.toContain(TerrainFeatureType.WATER)
        }
      }
    })
  })
})