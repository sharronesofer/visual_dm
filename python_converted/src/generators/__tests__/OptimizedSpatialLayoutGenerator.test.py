from typing import Any, Dict


  POICategory,
  POIPlacementRules,
  PlacementPattern,
  SpatialLayoutConfig
} from '../../types/spatial'
describe('OptimizedSpatialLayoutGenerator', () => {
  let gridManager: GridManager
  let collisionSystem: CollisionSystem
  let terrainManager: TerrainManager
  let generator: OptimizedSpatialLayoutGenerator
  let config: SpatialLayoutConfig
  beforeEach(() => {
    const dimensions: GridDimensions = { width: 100, height: 100 }
    gridManager = new GridManager(dimensions)
    collisionSystem = new CollisionSystem(gridManager)
    const terrainData: TerrainData = {
      heightMap: Array(dimensions.height).fill(Array(dimensions.width).fill(0)),
      features: Array(dimensions.height).fill(Array(dimensions.width).fill([])),
      buildableAreas: Array(dimensions.height).fill(Array(dimensions.width).fill(true))
    }
    terrainManager = new TerrainManager(terrainData)
    const socialRules: POIPlacementRules = {
      category: POICategory.SOCIAL,
      minSpacing: 2,
      maxSpacing: 8,
      preferredTerrainTypes: [CellType.EMPTY],
      avoidTerrainTypes: [CellType.WALL, CellType.BLOCKED],
      minGroupSize: 3,
      maxGroupSize: 6
    }
    const dungeonRules: POIPlacementRules = {
      category: POICategory.DUNGEON,
      minSpacing: 4,
      maxSpacing: 12,
      preferredTerrainTypes: [CellType.EMPTY],
      avoidTerrainTypes: [CellType.WALL, CellType.BLOCKED],
      minGroupSize: 1,
      maxGroupSize: 3
    }
    const explorationRules: POIPlacementRules = {
      category: POICategory.EXPLORATION,
      minSpacing: 3,
      maxSpacing: 10,
      preferredTerrainTypes: [CellType.EMPTY],
      avoidTerrainTypes: [CellType.WALL, CellType.BLOCKED],
      minGroupSize: 2,
      maxGroupSize: 4
    }
    config = {
      gridDimensions: dimensions,
      poiRules: [socialRules, dungeonRules, explorationRules],
      patterns: Dict[str, Any]
        },
        [POICategory.DUNGEON]: {
          type: 'SCATTERED',
          density: 0.4
        },
        [POICategory.EXPLORATION]: {
          type: 'LINEAR',
          density: 0.5,
          orientation: 45
        }
      },
      pathfindingWeight: 0.6,
      aestheticWeight: 0.4
    }
    generator = new OptimizedSpatialLayoutGenerator(
      gridManager,
      collisionSystem,
      terrainManager,
      config
    )
  })
  describe('Performance Tests', () => {
    test('generates layout within performance threshold', async () => {
      const startTime = performance.now()
      const result = await generator.generateLayout()
      const duration = performance.now() - startTime
      expect(duration).toBeLessThan(1000) 
      expect(result.placements.length).toBeGreaterThan(0)
      expect(result.paths.length).toBeGreaterThan(0)
    })
    test('caches and reuses layouts effectively', async () => {
      const startTime1 = performance.now()
      const result1 = await generator.generateLayout()
      const duration1 = performance.now() - startTime1
      const startTime2 = performance.now()
      const result2 = await generator.generateLayout()
      const duration2 = performance.now() - startTime2
      expect(duration2).toBeLessThan(duration1 * 0.5) 
      expect(result2).toEqual(result1) 
    })
    test('handles concurrent layout generation efficiently', async () => {
      const numConcurrent = 5
      const startTime = performance.now()
      const promises = Array(numConcurrent).fill(null).map(() => 
        generator.generateLayout()
      )
      const results = await Promise.all(promises)
      const duration = performance.now() - startTime
      expect(duration).toBeLessThan(2000) 
      results.forEach(result => {
        expect(result.placements.length).toBeGreaterThan(0)
        expect(result.paths.length).toBeGreaterThan(0)
      })
    })
    test('maintains reasonable memory usage', async () => {
      const initialMemory = process.memoryUsage().heapUsed
      for (let i = 0; i < 10; i++) {
        await generator.generateLayout()
      }
      const finalMemory = process.memoryUsage().heapUsed
      const memoryIncrease = finalMemory - initialMemory
      expect(memoryIncrease).toBeLessThan(50 * 1024 * 1024)
    })
    test('handles cache eviction properly', async () => {
      const iterations = OptimizedSpatialLayoutGenerator['MAX_CACHE_SIZE'] + 5
      for (let i = 0; i < iterations; i++) {
        config.patterns[POICategory.SOCIAL].density = 0.5 + (i * 0.01)
        await generator.generateLayout()
      }
      const cacheSize = (generator as any).cache.size
      expect(cacheSize).toBeLessThanOrEqual(OptimizedSpatialLayoutGenerator['MAX_CACHE_SIZE'])
    })
  })
  describe('Worker Thread Tests', () => {
    test('falls back to synchronous generation on worker failure', async () => {
      jest.mock('worker_threads', () => ({
        Worker: jest.fn().mockImplementation(() => {
          throw new Error('Worker creation failed')
        })
      }))
      const result = await generator.generateLayout()
      expect(result.placements.length).toBeGreaterThan(0)
      expect(result.paths.length).toBeGreaterThan(0)
    })
  })
}) 