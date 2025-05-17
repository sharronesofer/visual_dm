import { ChunkStreamingManager } from './ChunkStreamingManager';
import { RegionManager, ChunkPosition, ChunkData } from './RegionManager';
import { EventBus } from '../core/events/EventBus';
import { SceneEventType } from '../core/events/SceneEventTypes';

describe('ChunkStreamingManager', () => {
    let regionManager: RegionManager;
    let streamingManager: ChunkStreamingManager;
    let events: any[];

    beforeEach(() => {
        regionManager = new RegionManager({ chunkSize: 100, maxChunks: 4 });
        streamingManager = new ChunkStreamingManager(regionManager, 1, 2);
        events = [];
        jest.spyOn(EventBus, 'getInstance').mockReturnValue({
            emit: (event: any) => events.push(event),
        } as any);
    });

    afterEach(() => {
        jest.restoreAllMocks();
    });

    it('loads chunks around player position and emits events', async () => {
        streamingManager.updatePlayerPosition(100, 100); // player at (1,1)
        await streamingManager.tick();
        const active = streamingManager.getActiveChunks();
        expect(active.length).toBeGreaterThanOrEqual(1);
        expect(events.some(e => e.type === SceneEventType.REGION_ENTERED)).toBe(true);
    });

    it('unloads chunks when player moves away', async () => {
        streamingManager.updatePlayerPosition(0, 0);
        await streamingManager.tick();
        streamingManager.updatePlayerPosition(300, 300); // move far away
        await streamingManager.tick();
        expect(events.some(e => e.type === SceneEventType.REGION_EXITED)).toBe(true);
    });

    it('respects view distance and max concurrent loads', async () => {
        streamingManager.setViewDistance(2);
        streamingManager.updatePlayerPosition(0, 0);
        await streamingManager.tick();
        // Should have queued and loaded more chunks
        expect(streamingManager.getActiveChunks().length).toBeGreaterThanOrEqual(5);
    });

    it('prioritizes closer chunks in the load queue', async () => {
        streamingManager.setViewDistance(2);
        streamingManager.updatePlayerPosition(0, 0);
        // Enqueue a bunch of loads
        await streamingManager.tick();
        // The first loaded chunk should be closest to player
        const loadedChunks = events.filter(e => e.type === SceneEventType.REGION_ENTERED);
        expect(loadedChunks.length).toBeGreaterThanOrEqual(1);
        // The first chunk loaded should be (0,0)
        expect(loadedChunks[0].data.chunk.position).toEqual({ x: 0, y: 0 });
    });
}); 