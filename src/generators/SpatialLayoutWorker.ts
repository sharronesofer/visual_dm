import { parentPort, workerData } from 'worker_threads';
import { SpatialLayoutGenerator } from './SpatialLayoutGenerator';
import { GridManager } from '../utils/grid';
import { CollisionSystem } from '../utils/collision';
import { TerrainManager } from '../utils/terrain';
import { SpatialLayoutConfig } from '../types/spatial';

// Worker thread entry point
if (parentPort) {
  const { config, gridData, terrainData } = workerData;

  // Reconstruct required instances from serialized data
  const gridManager = GridManager.fromSerializedData(gridData);
  const collisionSystem = new CollisionSystem(gridManager);
  const terrainManager = TerrainManager.fromSerializedData(terrainData);

  // Create generator instance
  const generator = new SpatialLayoutGenerator(
    gridManager,
    collisionSystem,
    terrainManager,
    config as SpatialLayoutConfig
  );

  try {
    // Generate layout
    const result = generator.generateLayout();
    parentPort.postMessage({ success: true, result });
  } catch (error) {
    parentPort.postMessage({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error' 
    });
  }
} 