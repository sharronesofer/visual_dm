import { Position } from '../types/common';
import { POIEntity, POIChunk } from '../types/poi';
import { TypedEventEmitter } from '../utils/TypedEventEmitter';
import { ServiceConfig, ServiceResponse, ServiceError } from './base/types';
import { ServiceResponseType, SuccessResponse, ErrorResponse, createErrorResponse } from './adapters/types';

/**
 * Events emitted by the POIChunkManager
 */
interface POIChunkEvents {
  'chunkLoaded': { poiId: string; position: Position; chunk: POIChunk };
  'chunkUnloaded': { poiId: string; position: Position };
  'chunkUpdated': { poiId: string; position: Position; chunk: POIChunk };
  'chunkSaved': { poiId: string; position: Position };
  'chunkError': { poiId: string; position: Position; error: string };
  'cacheCleared': { count: number };
  'queueProcessed': { processed: number; remaining: number };
  'chunkEvicted': { poiId: string; position: Position };
}

interface ChunkManagerConfig {
  chunkSize: number;
  maxCachedChunks: number;
  preloadRadius: number;
  unloadThreshold: number;
  saveInterval: number;
  priorityLevels: number;
  loadingBatchSize: number;
  loadingDelay: number;
}

interface ChunkCacheEntry {
  chunk: POIChunk;
  lastAccessed: number;
  isDirty: boolean;
  priority: number;
}

const DEFAULT_CONFIG: ChunkManagerConfig = {
  chunkSize: 16,
  maxCachedChunks: 64,
  preloadRadius: 2,
  unloadThreshold: 300000, // 5 minutes
  saveInterval: 60000, // 1 minute
  priorityLevels: 3,
  loadingBatchSize: 4,
  loadingDelay: 1000,
};

type POIServiceResponse<T = POIChunk> = ServiceResponseType<T>;

/**
 * Manages loading, caching, and unloading of POI chunks with optimized memory management
 */
export class POIChunkManager extends TypedEventEmitter<POIChunkEvents> {
  private config: ChunkManagerConfig;
  private chunkCache: Map<string, ChunkCacheEntry>;
  private loadQueue: Set<string>;
  private isLoading: boolean;
  private saveTimer?: NodeJS.Timeout;
  private resourceFetcher: (endpoint: string, options?: ServiceConfig) => Promise<ServiceResponse<POIChunk>>;
  private chunks: Map<string, POIChunk> = new Map();

  constructor(
    resourceFetcher: (endpoint: string, options?: ServiceConfig) => Promise<ServiceResponse<POIChunk>>,
    config: Partial<ChunkManagerConfig> = {}
  ) {
    super();
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.chunkCache = new Map();
    this.loadQueue = new Set();
    this.isLoading = false;
    this.resourceFetcher = resourceFetcher;
    this.startAutoSave();
  }

  /**
   * Add a chunk to the cache with specified priority
   * @private
   */
  private addToCache(
    poiId: string,
    chunk: POIChunk,
    priority: number = this.config.priorityLevels - 1
  ): void {
    const key = this.getChunkKey(poiId, chunk.position);
    this.chunkCache.set(key, {
      chunk,
      lastAccessed: Date.now(),
      isDirty: false,
      priority,
    });

    if (this.chunkCache.size > this.config.maxCachedChunks) {
      this.cleanupCache();
    }

    this.emit('chunkLoaded', { poiId, position: chunk.position, chunk });
  }

  /**
   * Clean up the cache by removing old or low-priority chunks
   * @private
   */
  private cleanupCache(): void {
    const now = Date.now();
    const entries = Array.from(this.chunkCache.entries());

    // Sort by priority first, then by last accessed time
    entries.sort(([, a], [, b]) => {
      if (a.priority !== b.priority) {
        return b.priority - a.priority; // Higher priority = keep in cache
      }
      return a.lastAccessed - b.lastAccessed;
    });

    // Save and remove old chunks until we're under the limit
    let removedCount = 0;
    while (entries.length > this.config.maxCachedChunks) {
      const [key, entry] = entries.shift()!;
      const [poiId, coords] = key.split(':');
      const [x, y] = coords.split(',').map(Number);
      const position = { x, y };

      if (entry.isDirty) {
        this.saveChunk(poiId, position);
      }

      this.chunkCache.delete(key);
      removedCount++;
      this.emit('chunkUnloaded', { poiId, position });
    }

    if (removedCount > 0) {
      this.emit('cacheCleared', { count: removedCount });
    }
  }

  /**
   * Process the queue of chunks to be loaded
   * @private
   */
  private async processLoadQueue(): Promise<void> {
    if (this.loadQueue.size === 0) return;

    const batch = Array.from(this.loadQueue).slice(0, this.config.loadingBatchSize);
    for (const key of batch) {
      try {
        const [poiId, x, y] = key.split(':');
        const position = { x: parseInt(x), y: parseInt(y) };
        await this.loadChunk(poiId, position);
        this.loadQueue.delete(key);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to process load queue';
        this.emit('chunkError', {
          poiId: key.split(':')[0],
          position: { x: 0, y: 0 }, // Default position for error case
          error: errorMessage
        });
      }
    }

    if (this.loadQueue.size > 0) {
      setTimeout(() => this.processLoadQueue(), this.config.loadingDelay);
    }
  }

  /**
   * Load a specific chunk for a POI
   * @param poiId - ID of the POI
   * @param position - Position of the chunk
   */
  public async loadChunk(poiId: string, position: Position): Promise<POIServiceResponse> {
    try {
      const key = this.getChunkKey(poiId, position);

      // Return cached chunk if available
      if (this.chunkCache.has(key)) {
        this.touchChunk(key);
        const entry = this.chunkCache.get(key)!;
        return { success: true, data: entry.chunk } as SuccessResponse<POIChunk>;
      }

      // Add to load queue if not already loading
      if (this.loadQueue.has(key)) {
        const error = new ServiceError('CHUNK_LOADING', 'Chunk is already being loaded');
        return createErrorResponse(error);
      }

      this.loadQueue.add(key);

      // Fetch chunk from server
      const response = await this.resourceFetcher(`/api/poi/${poiId}/chunks/${position.x}/${position.y}`, {
        ...this.config,
        method: 'GET',
      });

      if (!response.success) {
        return response as ErrorResponse;
      }

      const chunk = response.data as POIChunk;
      const priority = this.calculateChunkPriority(position);
      this.cacheChunk(key, chunk, false, priority);
      this.emit('chunkLoaded', { poiId, position, chunk });

      return { success: true, data: chunk } as SuccessResponse<POIChunk>;

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error loading chunk';
      this.emit('chunkError', { poiId, position, error: errorMessage });
      const serviceError = new ServiceError('CHUNK_LOAD_ERROR', errorMessage);
      return createErrorResponse(serviceError);

    } finally {
      this.loadQueue.delete(this.getChunkKey(poiId, position));
    }
  }

  /**
   * Load all chunks within a radius of a center position
   * @param poiId - ID of the POI
   * @param centerPosition - Center position to load chunks around
   * @param radius - Radius in chunks to load (default: config.preloadRadius)
   */
  public async loadChunksInRadius(
    poiId: string,
    centerPosition: Position,
    radius: number = this.config.preloadRadius
  ): Promise<POIServiceResponse<{ queued: number; cached: number }>> {
    try {
      const centerChunkPos = this.getChunkPosition(centerPosition);
      this.loadQueue.clear();

      // Calculate chunk positions and priorities
      for (let dx = -radius; dx <= radius; dx++) {
        for (let dy = -radius; dy <= radius; dy++) {
          const chunkPos = {
            x: centerChunkPos.x + dx,
            y: centerChunkPos.y + dy,
          };

          if (this.isChunkInRadius(centerChunkPos, chunkPos, radius)) {
            const key = this.getChunkKey(poiId, chunkPos);
            if (!this.chunkCache.has(key)) {
              this.loadQueue.add(key);
            }
          }
        }
      }

      // Start processing the load queue
      void this.processLoadQueue();

      return {
        success: true,
        data: {
          queued: this.loadQueue.size,
          cached: this.chunkCache.size,
        }
      };
    } catch (error) {
      const serviceError = new ServiceError(
        'LOAD_CHUNKS_ERROR',
        error instanceof Error ? error.message : 'Failed to load chunks in radius'
      );
      return createErrorResponse(serviceError);
    }
  }

  /**
   * Calculate chunk priority based on distance from center
   * @private
   */
  private calculateChunkPriority(position: Position): number {
    const distance = Math.sqrt(position.x * position.x + position.y * position.y);
    const normalizedDistance = Math.min(distance / this.config.preloadRadius, 1);
    return Math.floor(normalizedDistance * (this.config.priorityLevels - 1));
  }

  /**
   * Get the cache key for a chunk
   * @private
   */
  private getChunkKey(poiId: string, position: Position): string {
    return `${poiId}:${position.x}:${position.y}`;
  }

  /**
   * Update the last accessed time for a chunk
   * @private
   */
  private touchChunk(key: string): void {
    const entry = this.chunkCache.get(key);
    if (entry) {
      entry.lastAccessed = Date.now();
    }
  }

  /**
   * Convert a world position to a chunk position
   * @private
   */
  private getChunkPosition(position: Position): Position {
    return {
      x: Math.floor(position.x / this.config.chunkSize),
      y: Math.floor(position.y / this.config.chunkSize),
    };
  }

  /**
   * Check if a chunk position is within a radius of a center position
   * @private
   */
  private isChunkInRadius(center: Position, chunk: Position, radius: number): boolean {
    const dx = Math.abs(center.x - chunk.x);
    const dy = Math.abs(center.y - chunk.y);
    return dx <= radius && dy <= radius;
  }

  /**
   * Save a specific chunk
   * @param poiId - ID of the POI
   * @param position - Position of the chunk to save
   */
  public async saveChunk(poiId: string, position: Position): Promise<POIServiceResponse> {
    const chunkKey = this.getChunkKey(poiId, position);
    const chunk = this.chunkCache.get(chunkKey)?.chunk;

    if (!chunk) {
      return createErrorResponse(new ServiceError('CHUNK_NOT_FOUND', `Chunk not found: ${chunkKey}`));
    }

    try {
      const response = await this.resourceFetcher(`/api/poi/${poiId}/chunks/${position.x}/${position.y}`, {
        ...this.config,
        method: 'PUT',
        data: chunk,
      });

      if (!response.success) {
        return response as ErrorResponse;
      }

      this.cacheChunk(chunkKey, chunk, false);
      return { success: true, data: chunk } as SuccessResponse<POIChunk>;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save chunk';
      const serviceError = new ServiceError('SAVE_CHUNK_ERROR', errorMessage);
      return createErrorResponse(serviceError);
    }
  }

  public async saveAllChunks(): Promise<POIServiceResponse[]> {
    const savePromises: Promise<POIServiceResponse>[] = [];

    for (const [key, entry] of this.chunkCache.entries()) {
      if (entry.isDirty) {
        const [poiId, x, y] = key.split(':');
        const position = { x: parseInt(x), y: parseInt(y) };
        savePromises.push(this.saveChunk(poiId, position));
      }
    }

    return Promise.all(savePromises);
  }

  private startAutoSave(): void {
    // Implementation of startAutoSave method
  }

  private cacheChunk(key: string, chunk: POIChunk, isDirty = false, priority = 0): void {
    // Evict oldest chunks if cache is full
    while (this.chunkCache.size >= this.config.maxCachedChunks!) {
      let oldestKey = '';
      let oldestTime = Infinity;
      let lowestPriority = Infinity;

      for (const [k, entry] of this.chunkCache.entries()) {
        // Prefer evicting lower priority chunks
        if (entry.priority < lowestPriority || 
           (entry.priority === lowestPriority && entry.lastAccessed < oldestTime)) {
          if (!entry.isDirty) {
            oldestKey = k;
            oldestTime = entry.lastAccessed;
            lowestPriority = entry.priority;
          }
        }
      }

      if (oldestKey) {
        const [poiId, x, y] = oldestKey.split(':');
        this.emit('chunkEvicted', {
          poiId,
          position: { x: parseInt(x), y: parseInt(y) },
        });
        this.chunkCache.delete(oldestKey);
      } else {
        // All chunks are dirty, can't evict
        throw new Error('Cache full and all chunks are dirty');
      }
    }

    this.chunkCache.set(key, {
      chunk,
      lastAccessed: Date.now(),
      isDirty,
      priority,
    });
  }
}