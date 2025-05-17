import { EventBus } from '../core/events/EventBus';
import { SceneEventType } from '../core/events/SceneEventTypes';

// Type for chunk position
export interface ChunkPosition {
    x: number;
    y: number;
}

// Type for chunk data
export interface ChunkData {
    id: string;
    position: ChunkPosition;
    data: any; // Replace with actual chunk data type
    lastAccessed: number;
}

interface RegionManagerConfig {
    chunkSize?: number;
    maxChunks?: number;
}

/**
 * RegionManager: Handles chunk-based world division, LRU caching, and floating origin support.
 */
export class RegionManager {
    private chunkSize: number;
    private maxChunks: number;
    private chunks: Map<string, ChunkData>;
    private origin: ChunkPosition;

    constructor(config: RegionManagerConfig = {}) {
        this.chunkSize = config.chunkSize ?? 256;
        this.maxChunks = config.maxChunks ?? 128;
        this.chunks = new Map();
        this.origin = { x: 0, y: 0 };
    }

    /**
     * Convert world coordinates to chunk coordinates.
     */
    worldToChunk(x: number, y: number): ChunkPosition {
        return {
            x: Math.floor((x - this.origin.x) / this.chunkSize),
            y: Math.floor((y - this.origin.y) / this.chunkSize),
        };
    }

    /**
     * Get chunk key for map storage.
     */
    private getChunkKey(pos: ChunkPosition): string {
        return `${pos.x},${pos.y}`;
    }

    /**
     * Get chunk data for given world coordinates (loads if not present).
     */
    async getChunk(x: number, y: number): Promise<ChunkData> {
        const pos = this.worldToChunk(x, y);
        const key = this.getChunkKey(pos);
        let chunk = this.chunks.get(key);
        if (!chunk) {
            chunk = await this.loadChunk(pos);
        } else {
            chunk.lastAccessed = Date.now();
        }
        this.touchChunk(key);
        return chunk;
    }

    /**
     * Load chunk data asynchronously.
     */
    async loadChunk(pos: ChunkPosition): Promise<ChunkData> {
        const key = this.getChunkKey(pos);
        // Simulate async loading (replace with real loading logic)
        const chunk: ChunkData = {
            id: key,
            position: pos,
            data: {},
            lastAccessed: Date.now(),
        };
        this.chunks.set(key, chunk);
        this.evictIfNeeded();
        // Emit event
        EventBus.getInstance().emit({
            type: SceneEventType.REGION_ENTERED,
            source: 'RegionManager',
            timestamp: Date.now(),
            data: { chunk },
        });
        return chunk;
    }

    /**
     * Unload chunk data.
     */
    unloadChunk(pos: ChunkPosition): void {
        const key = this.getChunkKey(pos);
        if (this.chunks.has(key)) {
            const chunk = this.chunks.get(key);
            this.chunks.delete(key);
            // Emit event
            EventBus.getInstance().emit({
                type: SceneEventType.REGION_EXITED,
                source: 'RegionManager',
                timestamp: Date.now(),
                data: { chunk },
            });
        }
    }

    /**
     * Update chunk access order for LRU.
     */
    private touchChunk(key: string): void {
        const chunk = this.chunks.get(key);
        if (!chunk) return;
        this.chunks.delete(key);
        this.chunks.set(key, chunk);
    }

    /**
     * Evict least recently used chunks if over memory budget.
     */
    private evictIfNeeded(): void {
        while (this.chunks.size > this.maxChunks) {
            // Oldest chunk is first in insertion order
            const oldestKey = this.chunks.keys().next().value;
            this.unloadChunk(this.chunks.get(oldestKey)!.position);
        }
    }

    /**
     * Rebase world origin for floating origin support.
     */
    rebaseOrigin(newOrigin: ChunkPosition): void {
        this.origin = { ...newOrigin };
        // Optionally update all loaded chunk positions
        // (Implementation depends on how chunk data is structured)
    }

    /**
     * Get all currently loaded chunks.
     */
    getLoadedChunks(): ChunkData[] {
        return Array.from(this.chunks.values());
    }
} 