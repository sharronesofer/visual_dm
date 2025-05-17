import { EventBus } from '../core/events/EventBus';
import { SceneEventType } from '../core/events/SceneEventTypes';

export type ChunkState = 'unloaded' | 'loading' | 'loaded' | 'unloading';

interface ChunkInfo {
    id: string;
    state: ChunkState;
    priority: number;
    dependencies: Set<string>;
}

export class ChunkPartitioningManager {
    private chunks: Map<string, ChunkInfo>;

    constructor() {
        this.chunks = new Map();
    }

    /**
     * Set the state of a chunk and emit event if changed.
     */
    setChunkState(chunkId: string, state: ChunkState) {
        let info = this.chunks.get(chunkId);
        if (!info) {
            info = { id: chunkId, state, priority: 0, dependencies: new Set() };
            this.chunks.set(chunkId, info);
        } else if (info.state !== state) {
            info.state = state;
            EventBus.getInstance().emit({
                type: SceneEventType.SCENE_OBJECT_ADDED, // Use a more specific event if available
                source: 'ChunkPartitioningManager',
                timestamp: Date.now(),
                data: { chunkId, state },
            });
        }
    }

    getChunkState(chunkId: string): ChunkState | undefined {
        return this.chunks.get(chunkId)?.state;
    }

    setChunkPriority(chunkId: string, priority: number) {
        let info = this.chunks.get(chunkId);
        if (!info) {
            info = { id: chunkId, state: 'unloaded', priority, dependencies: new Set() };
            this.chunks.set(chunkId, info);
        } else if (info.priority !== priority) {
            info.priority = priority;
            EventBus.getInstance().emit({
                type: SceneEventType.SCENE_OBJECT_ADDED, // Use a more specific event if available
                source: 'ChunkPartitioningManager',
                timestamp: Date.now(),
                data: { chunkId, priority },
            });
        }
    }

    getChunkPriority(chunkId: string): number | undefined {
        return this.chunks.get(chunkId)?.priority;
    }

    addDependency(chunkId: string, dependsOnId: string) {
        let info = this.chunks.get(chunkId);
        if (!info) {
            info = { id: chunkId, state: 'unloaded', priority: 0, dependencies: new Set() };
            this.chunks.set(chunkId, info);
        }
        info.dependencies.add(dependsOnId);
    }

    removeDependency(chunkId: string, dependsOnId: string) {
        const info = this.chunks.get(chunkId);
        if (info) {
            info.dependencies.delete(dependsOnId);
        }
    }

    canUnload(chunkId: string): boolean {
        const info = this.chunks.get(chunkId);
        if (!info) return true;
        return info.dependencies.size === 0;
    }

    /**
     * Get all chunk info (for debugging or integration).
     */
    getAllChunks(): ChunkInfo[] {
        return Array.from(this.chunks.values());
    }
} 