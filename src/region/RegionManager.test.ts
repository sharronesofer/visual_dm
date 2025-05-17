import { RegionManager, ChunkPosition } from './RegionManager';
import { EventBus } from '../core/events/EventBus';
import { SceneEventType } from '../core/events/SceneEventTypes';

describe('RegionManager', () => {
    let regionManager: RegionManager;
    let events: any[];

    beforeEach(() => {
        regionManager = new RegionManager({ chunkSize: 100, maxChunks: 2 });
        events = [];
        jest.spyOn(EventBus, 'getInstance').mockReturnValue({
            emit: (event: any) => events.push(event),
        } as any);
    });

    afterEach(() => {
        jest.restoreAllMocks();
    });

    it('converts world coordinates to chunk coordinates', () => {
        expect(regionManager.worldToChunk(150, 250)).toEqual({ x: 1, y: 2 });
        expect(regionManager.worldToChunk(99, 99)).toEqual({ x: 0, y: 0 });
    });

    it('loads and retrieves chunks, emitting events', async () => {
        const chunk = await regionManager.getChunk(150, 250);
        expect(chunk.position).toEqual({ x: 1, y: 2 });
        expect(events[0].type).toBe(SceneEventType.REGION_ENTERED);
        // Should retrieve from cache on second call
        const chunk2 = await regionManager.getChunk(150, 250);
        expect(chunk2).toBe(chunk);
        expect(events.length).toBe(1); // No new event
    });

    it('evicts least recently used chunk when over maxChunks', async () => {
        const chunkA = await regionManager.getChunk(0, 0); // (0,0)
        const chunkB = await regionManager.getChunk(100, 0); // (1,0)
        expect(regionManager.getLoadedChunks().length).toBe(2);
        // Access chunkA to make chunkB oldest
        await regionManager.getChunk(0, 0);
        // Add a third chunk, should evict chunkB
        const chunkC = await regionManager.getChunk(0, 100); // (0,1)
        expect(regionManager.getLoadedChunks().length).toBe(2);
        // chunkB should be evicted
        expect(regionManager.getLoadedChunks().find(c => c.id === '1,0')).toBe(undefined);
        // Should emit REGION_EXITED event
        expect(events.some(e => e.type === SceneEventType.REGION_EXITED)).toBe(true);
    });

    it('rebases origin and updates chunk coordinates', () => {
        regionManager.rebaseOrigin({ x: 1000, y: 1000 });
        expect(regionManager.worldToChunk(1100, 1200)).toEqual({ x: 1, y: 2 });
    });

    it('unloads chunk and emits event', async () => {
        const chunk = await regionManager.getChunk(0, 0);
        regionManager.unloadChunk(chunk.position);
        expect(regionManager.getLoadedChunks().length).toBe(0);
        expect(events.some(e => e.type === SceneEventType.REGION_EXITED)).toBe(true);
    });
}); 