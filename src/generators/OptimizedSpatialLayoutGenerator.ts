import { Worker } from 'worker_threads';
import path from 'path';
import { 
  SpatialLayoutConfig, 
  SpatialLayoutResult,
  POICategory,
  POIPlacementRules
} from '../types/spatial';
import { GridManager } from '../utils/grid';
import { CollisionSystem } from '../utils/collision';
import { TerrainManager } from '../utils/terrain';

interface LayoutCache {
  config: SpatialLayoutConfig;
  result: SpatialLayoutResult;
  timestamp: number;
}

export class OptimizedSpatialLayoutGenerator {
  private static readonly CACHE_TTL = 5 * 60 * 1000; // 5 minutes
  private static readonly MAX_CACHE_SIZE = 50;
  private cache: Map<string, LayoutCache>;
  private gridManager: GridManager;
  private collisionSystem: CollisionSystem;
  private terrainManager: TerrainManager;
  private config: SpatialLayoutConfig;

  constructor(
    gridManager: GridManager,
    collisionSystem: CollisionSystem,
    terrainManager: TerrainManager,
    config: SpatialLayoutConfig
  ) {
    this.gridManager = gridManager;
    this.collisionSystem = collisionSystem;
    this.terrainManager = terrainManager;
    this.config = config;
    this.cache = new Map();
  }

  public async generateLayout(): Promise<SpatialLayoutResult> {
    const cacheKey = this.generateCacheKey();
    const cached = this.getCachedLayout(cacheKey);
    if (cached) {
      return cached;
    }

    try {
      const result = await this.generateLayoutInWorker();
      this.cacheLayout(cacheKey, result);
      return result;
    } catch (error) {
      console.error('Worker thread error:', error);
      // Fallback to synchronous generation
      const result = this.generateLayoutSync();
      this.cacheLayout(cacheKey, result);
      return result;
    }
  }

  private generateLayoutSync(): SpatialLayoutResult {
    // Import the original generator for fallback
    const { SpatialLayoutGenerator } = require('./SpatialLayoutGenerator');
    const generator = new SpatialLayoutGenerator(
      this.gridManager,
      this.collisionSystem,
      this.terrainManager,
      this.config
    );
    return generator.generateLayout();
  }

  private async generateLayoutInWorker(): Promise<SpatialLayoutResult> {
    return new Promise((resolve, reject) => {
      const worker = new Worker(path.join(__dirname, 'SpatialLayoutWorker.js'), {
        workerData: {
          config: this.config,
          gridData: this.gridManager.toSerializedData(),
          terrainData: this.terrainManager.toSerializedData()
        }
      });

      worker.on('message', (message: { success: boolean; result?: SpatialLayoutResult; error?: string }) => {
        if (message.success && message.result) {
          resolve(message.result);
        } else {
          reject(new Error(message.error || 'Worker failed'));
        }
      });

      worker.on('error', reject);
      worker.on('exit', (code) => {
        if (code !== 0) {
          reject(new Error(`Worker stopped with exit code ${code}`));
        }
      });
    });
  }

  private generateCacheKey(): string {
    // Create a deterministic key based on config and grid state
    const configKey = JSON.stringify({
      dimensions: this.config.gridDimensions,
      rules: this.config.poiRules.map(rule => ({
        category: rule.category,
        minSpacing: rule.minSpacing,
        maxSpacing: rule.maxSpacing
      })),
      patterns: Object.entries(this.config.patterns).map(([category, pattern]) => ({
        category,
        type: pattern.type,
        density: pattern.density
      }))
    });

    const gridKey = JSON.stringify({
      dimensions: this.gridManager.getWidth() + 'x' + this.gridManager.getHeight(),
      timestamp: Math.floor(Date.now() / OptimizedSpatialLayoutGenerator.CACHE_TTL) // Round to cache TTL
    });

    return `${configKey}-${gridKey}`;
  }

  private getCachedLayout(key: string): SpatialLayoutResult | null {
    const cached = this.cache.get(key);
    if (!cached) return null;

    const age = Date.now() - cached.timestamp;
    if (age > OptimizedSpatialLayoutGenerator.CACHE_TTL) {
      this.cache.delete(key);
      return null;
    }

    return cached.result;
  }

  private cacheLayout(key: string, result: SpatialLayoutResult): void {
    // Implement LRU cache eviction if needed
    if (this.cache.size >= OptimizedSpatialLayoutGenerator.MAX_CACHE_SIZE) {
      const oldestKey = Array.from(this.cache.entries())
        .sort(([, a], [, b]) => a.timestamp - b.timestamp)[0][0];
      this.cache.delete(oldestKey);
    }

    this.cache.set(key, {
      config: this.config,
      result,
      timestamp: Date.now()
    });
  }

  public clearCache(): void {
    this.cache.clear();
  }
} 