from typing import Any, Dict, List



  POICategory,
  POIPlacementRules,
  SpatialLayoutConfig
} from '../src/types/spatial'
class BenchmarkConfig:
    gridSize: float
    iterations: float
    concurrent: float
    warmup: float
class BenchmarkResult:
    config: \'BenchmarkConfig\'
    original: Dict[str, Any]
  improvement: Dict[str, Any]
}
async function runBenchmark(config: BenchmarkConfig): Promise<BenchmarkResult> {
  const dimensions: GridDimensions = { 
    width: config.gridSize, 
    height: config.gridSize 
  }
  const gridManager = new GridManager(dimensions)
  const collisionSystem = new CollisionSystem(gridManager)
  const terrainData: TerrainData = {
    heightMap: Array(dimensions.height).fill(Array(dimensions.width).fill(0)),
    features: Array(dimensions.height).fill(Array(dimensions.width).fill([])),
    buildableAreas: Array(dimensions.height).fill(Array(dimensions.width).fill(true))
  }
  const terrainManager = new TerrainManager(terrainData)
  const layoutConfig: SpatialLayoutConfig = createTestConfig(dimensions)
  const original = new SpatialLayoutGenerator(
    gridManager,
    collisionSystem,
    terrainManager,
    layoutConfig
  )
  const optimized = new OptimizedSpatialLayoutGenerator(
    gridManager,
    collisionSystem,
    terrainManager,
    layoutConfig
  )
  for (let i = 0; i < config.warmup; i++) {
    await optimized.generateLayout()
  }
  optimized.clearCache()
  const originalTimes: List[number] = []
  const originalMemory: List[number] = []
  for (let i = 0; i < config.iterations; i++) {
    const startMemory = process.memoryUsage().heapUsed
    const startTime = performance.now()
    if (config.concurrent > 1) {
      await Promise.all(
        Array(config.concurrent)
          .fill(null)
          .map(() => original.generateLayout())
      )
    } else {
      await original.generateLayout()
    }
    const endTime = performance.now()
    const endMemory = process.memoryUsage().heapUsed
    originalTimes.push(endTime - startTime)
    originalMemory.push((endMemory - startMemory) / 1024 / 1024) 
  }
  const optimizedTimes: List[number] = []
  const optimizedMemory: List[number] = []
  let cacheHits = 0
  let totalGenerations = 0
  for (let i = 0; i < config.iterations; i++) {
    const startMemory = process.memoryUsage().heapUsed
    const startTime = performance.now()
    const cacheSize = (optimized as any).cache.size
    if (config.concurrent > 1) {
      await Promise.all(
        Array(config.concurrent)
          .fill(null)
          .map(() => optimized.generateLayout())
      )
      totalGenerations += config.concurrent
    } else {
      await optimized.generateLayout()
      totalGenerations++
    }
    const endTime = performance.now()
    const endMemory = process.memoryUsage().heapUsed
    const newCacheSize = (optimized as any).cache.size
    optimizedTimes.push(endTime - startTime)
    optimizedMemory.push((endMemory - startMemory) / 1024 / 1024)
    if (newCacheSize === cacheSize) {
      cacheHits += config.concurrent > 1 ? config.concurrent : 1
    }
  }
  const result: \'BenchmarkResult\' = {
    config,
    original: Dict[str, Any],
    optimized: Dict[str, Any],
    improvement: Dict[str, Any]
  }
  return result
}
function createTestConfig(dimensions: GridDimensions): SpatialLayoutConfig {
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
  return {
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
}
function average(numbers: List[number]): float {
  return numbers.reduce((a, b) => a + b, 0) / numbers.length
}
async function main() {
  const testCases: List[BenchmarkConfig] = [
    { gridSize: 50, iterations: 5, concurrent: 1, warmup: 2 },
    { gridSize: 100, iterations: 5, concurrent: 1, warmup: 2 },
    { gridSize: 200, iterations: 5, concurrent: 1, warmup: 2 },
    { gridSize: 100, iterations: 5, concurrent: 5, warmup: 2 }
  ]
  const results: List[BenchmarkResult] = []
  for (const testCase of testCases) {
    console.log(`Running benchmark with grid size ${testCase.gridSize}x${testCase.gridSize}`)
    console.log(`Iterations: ${testCase.iterations}, Concurrent: ${testCase.concurrent}`)
    const result = await runBenchmark(testCase)
    results.push(result)
    console.log('\nResults:')
    console.log('Original Implementation:')
    console.log(`  Avg Time: ${result.original.avgTimeMs.toFixed(2)}ms`)
    console.log(`  Avg Memory: ${result.original.avgMemoryMB.toFixed(2)}MB`)
    console.log('\nOptimized Implementation:')
    console.log(`  Avg Time: ${result.optimized.avgTimeMs.toFixed(2)}ms`)
    console.log(`  Avg Memory: ${result.optimized.avgMemoryMB.toFixed(2)}MB`)
    console.log(`  Cache Hit Ratio: ${(result.optimized.cacheHitRatio * 100).toFixed(1)}%`)
    console.log('\nImprovements:')
    console.log(`  Time: ${result.improvement.timePercent.toFixed(1)}%`)
    console.log(`  Memory: ${result.improvement.memoryPercent.toFixed(1)}%`)
    console.log('\n---\n')
  }
  const outputPath = path.join(process.cwd(), 'benchmark-results.json')
  fs.writeFileSync(outputPath, JSON.stringify(results, null, 2))
  console.log(`Full results saved to ${outputPath}`)
}
if (require.main === module) {
  main().catch(console.error)
} 