// ChunkManager.ts
// Manages chunked building generation, prioritization, and lifecycle for large-scale worldgen

export type ChunkCoord = { x: number; y: number };

export enum ChunkState {
    Unloaded = 'unloaded',
    Loading = 'loading',
    Loaded = 'loaded',
    Unloading = 'unloading',
}

export interface Chunk {
    coord: ChunkCoord;
    state: ChunkState;
    buildings: any[]; // Replace with actual Building[] type as needed
    lastAccess: number;
    priority: number;
}

export interface ChunkManagerOptions {
    chunkSize: number;
    getPlayerPosition: () => { x: number; y: number };
    maxActiveChunks?: number;
}

/**
 * ChunkManager: Handles chunk lifecycle, prioritization, and state for building generation
 */
export class ChunkManager {
    private chunks: Map<string, Chunk> = new Map();
    private options: ChunkManagerOptions;

    constructor(options: ChunkManagerOptions) {
        this.options = options;
    }

    /**
     * Get chunk key from coordinates
     */
    private chunkKey(coord: ChunkCoord): string {
        return `${coord.x},${coord.y}`;
    }

    /**
     * Get or create a chunk at the given coordinates
     */
    getChunk(coord: ChunkCoord): Chunk {
        const key = this.chunkKey(coord);
        let chunk = this.chunks.get(key);
        if (!chunk) {
            chunk = {
                coord,
                state: ChunkState.Unloaded,
                buildings: [],
                lastAccess: Date.now(),
                priority: 0,
            };
            this.chunks.set(key, chunk);
        }
        return chunk;
    }

    /**
     * Update chunk priorities based on player/camera position
     */
    updateChunkPriorities() {
        const player = this.options.getPlayerPosition();
        for (const chunk of this.chunks.values()) {
            const dx = chunk.coord.x - Math.floor(player.x / this.options.chunkSize);
            const dy = chunk.coord.y - Math.floor(player.y / this.options.chunkSize);
            chunk.priority = 1 / (1 + Math.sqrt(dx * dx + dy * dy));
        }
    }

    /**
     * Get a prioritized list of chunks to load/generate
     */
    getChunksToLoad(): Chunk[] {
        this.updateChunkPriorities();
        const sorted = Array.from(this.chunks.values())
            .filter(c => c.state === ChunkState.Unloaded)
            .sort((a, b) => b.priority - a.priority);
        if (this.options.maxActiveChunks) {
            return sorted.slice(0, this.options.maxActiveChunks);
        }
        return sorted;
    }

    /**
     * Mark a chunk as loaded
     */
    markChunkLoaded(coord: ChunkCoord, buildings: any[]) {
        const chunk = this.getChunk(coord);
        chunk.state = ChunkState.Loaded;
        chunk.buildings = buildings;
        chunk.lastAccess = Date.now();
    }

    /**
     * Mark a chunk as unloaded
     */
    markChunkUnloaded(coord: ChunkCoord) {
        const chunk = this.getChunk(coord);
        chunk.state = ChunkState.Unloaded;
        chunk.buildings = [];
        chunk.lastAccess = Date.now();
    }

    /**
     * Unload least recently used chunks if over maxActiveChunks
     */
    enforceChunkLimit() {
        if (!this.options.maxActiveChunks) return;
        const loaded = Array.from(this.chunks.values()).filter(c => c.state === ChunkState.Loaded);
        if (loaded.length > this.options.maxActiveChunks) {
            loaded.sort((a, b) => a.lastAccess - b.lastAccess);
            for (let i = 0; i < loaded.length - this.options.maxActiveChunks; i++) {
                this.markChunkUnloaded(loaded[i].coord);
            }
        }
    }
} 