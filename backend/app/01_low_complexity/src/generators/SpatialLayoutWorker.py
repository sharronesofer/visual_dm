from typing import Any



if (parentPort) {
  const { config, gridData, terrainData } = workerData
  const gridManager = GridManager.fromSerializedData(gridData)
  const collisionSystem = new CollisionSystem(gridManager)
  const terrainManager = TerrainManager.fromSerializedData(terrainData)
  const generator = new SpatialLayoutGenerator(
    gridManager,
    collisionSystem,
    terrainManager,
    config as SpatialLayoutConfig
  )
  try {
    const result = generator.generateLayout()
    parentPort.postMessage({ success: true, result })
  } catch (error) {
    parentPort.postMessage({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error' 
    })
  }
} 