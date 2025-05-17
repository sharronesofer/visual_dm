import { RegionManager, ChunkPosition, ChunkData } from './RegionManager';
import { EventBus } from '../core/events/EventBus';
import { SceneEventType } from '../core/events/SceneEventTypes';

interface ChunkRequest {
    pos: ChunkPosition;
    priority: number;
}

export class ChunkStreamingManager {
    private regionManager: RegionManager;
    private viewDistance: number;
    private playerPos: ChunkPosition;
    private activeChunks: Set<string>;
    private loadQueue: ChunkRequest[];
    private isLoading: boolean;
    private maxConcurrentLoads: number;

    constructor(regionManager: RegionManager, viewDistance: number = 2, maxConcurrentLoads: number = 2) {
        this.regionManager = regionManager;
        this.viewDistance = viewDistance;
        this.playerPos = { x: 0, y: 0 };
        this.activeChunks = new Set();
        this.loadQueue = [];
        this.isLoading = false;
        this.maxConcurrentLoads = maxConcurrentLoads;
    }

    /**
     * Update player position and recompute active chunk set.
     */
    updatePlayerPosition(x: number, y: number) {
        this.playerPos = this.regionManager.worldToChunk(x, y);
        this.updateActiveChunks();
    }

    /**
     * Set the streaming view distance (radius in chunks).
     */
    setViewDistance(distance: number) {
        this.viewDistance = distance;
        this.updateActiveChunks();
    }

    /**
     * Get currently loaded/visible chunks.
     */
    getActiveChunks(): ChunkData[] {
        return this.regionManager.getLoadedChunks().filter(chunk =>
            this.activeChunks.has(chunk.id)
        );
    }

    /**
     * Main tick for streaming queue (call from game loop).
     */
    async tick() {
        if (this.isLoading) return;
        this.isLoading = true;
        let loads = 0;
        while (this.loadQueue.length > 0 && loads < this.maxConcurrentLoads) {
            const req = this.loadQueue.shift()!;
            await this.loadChunkAsync(req.pos);
            loads++;
        }
        this.isLoading = false;
    }

    /**
     * Internal: Update the set of active chunks and queue loads/unloads.
     */
    private updateActiveChunks() {
        const needed = new Set<string>();
        for (let dx = -this.viewDistance; dx <= this.viewDistance; dx++) {
            for (let dy = -this.viewDistance; dy <= this.viewDistance; dy++) {
                const pos = { x: this.playerPos.x + dx, y: this.playerPos.y + dy };
                const key = `${pos.x},${pos.y}`;
                needed.add(key);
                if (!this.activeChunks.has(key)) {
                    this.enqueueChunkLoad(pos, this.getPriority(pos));
                }
            }
        }
        // Unload chunks no longer needed
        for (const key of this.activeChunks) {
            if (!needed.has(key)) {
                const [x, y] = key.split(',').map(Number);
                this.regionManager.unloadChunk({ x, y });
                EventBus.getInstance().emit({
                    type: SceneEventType.REGION_EXITED,
                    source: 'ChunkStreamingManager',
                    timestamp: Date.now(),
                    data: { chunkId: key },
                });
            }
        }
        this.activeChunks = needed;
    }

    /**
     * Enqueue a chunk load request with priority.
     */
    private enqueueChunkLoad(pos: ChunkPosition, priority: number) {
        this.loadQueue.push({ pos, priority });
        // Sort queue by priority (lower = higher priority)
        this.loadQueue.sort((a, b) => a.priority - b.priority);
    }

    /**
     * Calculate priority for a chunk (distance to player).
     */
    private getPriority(pos: ChunkPosition): number {
        const dx = pos.x - this.playerPos.x;
        const dy = pos.y - this.playerPos.y;
        return dx * dx + dy * dy;
    }

    /**
     * Async load a chunk and emit events.
     */
    private async loadChunkAsync(pos: ChunkPosition) {
        const chunk = await this.regionManager.getChunk(
            pos.x * this.regionManager['chunkSize'],
            pos.y * this.regionManager['chunkSize']
        );
        EventBus.getInstance().emit({
            type: SceneEventType.REGION_ENTERED,
            source: 'ChunkStreamingManager',
            timestamp: Date.now(),
            data: { chunk },
        });
    }
} 