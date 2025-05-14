import { Position } from '../types/common';
import { useMapStore } from '../store/mapStore';
import { deserializeChunkKey } from '../store/mapStore';

export interface Tile {
  type: string;
  walkable: boolean;
  description?: string;
  texture?: string;
}

export interface MapChunk {
  x: number;
  y: number;
  width: number;
  height: number;
  tiles: Record<string, Tile>;
  entities: Record<string, any>;
  lastAccessed: number;
}

export class MapService {
  private static instance: MapService;
  private isFetching: boolean;

  private constructor() {
    this.isFetching = false;
  }

  public static getInstance(): MapService {
    if (!MapService.instance) {
      MapService.instance = new MapService();
    }
    return MapService.instance;
  }

  private getChunkKey(x: number, y: number): { x: number; y: number } {
    const store = useMapStore.getState();
    const chunkX = Math.floor(x / store.chunkSize);
    const chunkY = Math.floor(y / store.chunkSize);
    return { x: chunkX, y: chunkY };
  }

  private async fetchChunk(x: number, y: number): Promise<Omit<MapChunk, 'lastAccessed'>> {
    const store = useMapStore.getState();
    const response = await fetch(`/api/map/chunk?x=${x}&y=${y}&size=${store.chunkSize}`);

    if (!response.ok) {
      throw new Error('Failed to fetch map chunk');
    }

    return await response.json();
  }

  private async processPrefetchQueue(): Promise<void> {
    const store = useMapStore.getState();
    if (this.isFetching || store.activeChunks.size === 0) return;

    this.isFetching = true;
    const [nextChunkKey] = store.activeChunks;
    store.activeChunks.delete(nextChunkKey);

    try {
      const key = deserializeChunkKey(nextChunkKey);
      if (!store.getChunk(key)) {
        const chunk = await this.fetchChunk(key.x * store.chunkSize, key.y * store.chunkSize);
        store.setChunk(key, { ...chunk, isLoading: false });
      }
    } catch (error) {
      console.warn('Failed to prefetch chunk:', error);
    } finally {
      this.isFetching = false;
      if (store.activeChunks.size > 0) {
        setTimeout(() => this.processPrefetchQueue(), 100);
      }
    }
  }

  private queueAdjacentChunks(centerX: number, centerY: number): void {
    const store = useMapStore.getState();
    const radius = 1; // Prefetch one chunk in each direction

    for (let dy = -radius; dy <= radius; dy++) {
      for (let dx = -radius; dx <= radius; dx++) {
        if (dx === 0 && dy === 0) continue;

        const key = this.getChunkKey(
          centerX + dx * store.chunkSize,
          centerY + dy * store.chunkSize
        );

        if (!store.getChunk(key)) {
          store.activeChunks.add(`${key.x},${key.y}`);
        }
      }
    }

    this.processPrefetchQueue();
  }

  public async getMapData(position: Position): Promise<{
    tiles: Record<string, Tile>;
    entities: Record<string, any>;
    visibleArea: Position[];
  }> {
    const store = useMapStore.getState();
    const chunkKey = this.getChunkKey(position.x, position.y);

    let chunk = store.getChunk(chunkKey);

    if (!chunk) {
      try {
        const newChunk = await this.fetchChunk(position.x, position.y);
        store.setChunk(chunkKey, { ...newChunk, isLoading: false });
        chunk = store.getChunk(chunkKey);
      } catch (error) {
        console.error('Error fetching map chunk:', error);
        store.setError(error instanceof Error ? error.message : 'Failed to fetch map chunk');
        throw error;
      }
    }

    // Queue adjacent chunks for prefetching
    this.queueAdjacentChunks(position.x, position.y);

    // Calculate visible area
    const visibleArea = this.calculateVisibleArea(position, 5);
    store.setVisibleArea(visibleArea);

    // Clean up old chunks
    store.clearInactiveChunks();

    return {
      tiles: chunk!.tiles,
      entities: chunk!.entities,
      visibleArea,
    };
  }

  private calculateVisibleArea(center: Position, radius: number): Position[] {
    const visibleArea: Position[] = [];

    for (let y = center.y - radius; y <= center.y + radius; y++) {
      for (let x = center.x - radius; x <= center.x + radius; x++) {
        if (this.isInRange(center, { x, y }, radius)) {
          visibleArea.push({ x, y });
        }
      }
    }

    return visibleArea;
  }

  private isInRange(center: Position, point: Position, radius: number): boolean {
    const dx = center.x - point.x;
    const dy = center.y - point.y;
    return Math.sqrt(dx * dx + dy * dy) <= radius;
  }

  public getChunkForPosition(position: Position): MapChunk | undefined {
    const key = this.getChunkKey(position.x, position.y);
    return useMapStore.getState().getChunk(key);
  }
}
