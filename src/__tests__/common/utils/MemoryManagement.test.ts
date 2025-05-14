import { useMapStore } from '../../store/mapStore';
import { MapService } from '../../services/MapService';
import { MapState } from '../../store/mapStore';

describe('Memory Management', () => {
  let mapService: MapService;
  let store: MapState;

  beforeEach(() => {
    mapService = MapService.getInstance();
    store = useMapStore.getState();

    // Clear the store before each test
    store.chunks.clear();
    store.activeChunks.clear();
    store.setError(null);
  });

  describe('Chunk Management', () => {
    it('should limit the number of chunks in memory', async () => {
      // Add more chunks than the maximum limit
      for (let i = 0; i < store.maxChunks + 5; i++) {
        const chunk = {
          x: i,
          y: 0,
          width: store.chunkSize,
          height: store.chunkSize,
          tiles: { '0,0': { type: 'grass', walkable: true } },
          entities: {},
          isLoading: false,
        };

        store.setChunk({ x: i, y: 0 }, chunk);
      }

      // Trigger cleanup
      store.clearInactiveChunks();

      // Verify chunk count
      expect(store.chunks.size).toBeLessThanOrEqual(store.maxChunks);
    });

    it('should keep most recently accessed chunks', async () => {
      // Add chunks
      for (let i = 0; i < 5; i++) {
        const chunk = {
          x: i,
          y: 0,
          width: store.chunkSize,
          height: store.chunkSize,
          tiles: { '0,0': { type: 'grass', walkable: true } },
          entities: {},
          isLoading: false,
        };

        store.setChunk({ x: i, y: 0 }, chunk);
      }

      // Access specific chunks
      const recentKey = { x: 2, y: 0 };
      store.getChunk(recentKey);

      // Add more chunks to trigger cleanup
      for (let i = 5; i < store.maxChunks + 5; i++) {
        const chunk = {
          x: i,
          y: 0,
          width: store.chunkSize,
          height: store.chunkSize,
          tiles: { '0,0': { type: 'grass', walkable: true } },
          entities: {},
          isLoading: false,
        };

        store.setChunk({ x: i, y: 0 }, chunk);
      }

      // Verify recently accessed chunk is still present
      expect(store.getChunk(recentKey)).toBeDefined();
    });
  });

  describe('Memory Cleanup', () => {
    it('should clean up inactive chunks when moving to new area', async () => {
      // Add chunks in initial area
      for (let i = 0; i < 5; i++) {
        for (let j = 0; j < 5; j++) {
          const chunk = {
            x: i,
            y: j,
            width: store.chunkSize,
            height: store.chunkSize,
            tiles: { '0,0': { type: 'grass', walkable: true } },
            entities: {},
            isLoading: false,
          };

          store.setChunk({ x: i, y: j }, chunk);
        }
      }

      const initialChunkCount = store.chunks.size;

      // Move to new area
      await mapService.getMapData({ x: 100, y: 100 });

      // Verify old chunks were cleaned up
      expect(store.chunks.size).toBeLessThan(initialChunkCount);
    });

    it('should handle memory pressure by removing least recently used chunks', async () => {
      const mockChunks = new Array(store.maxChunks + 10)
        .fill(null)
        .map((_, i) => ({
          x: i,
          y: 0,
          width: store.chunkSize,
          height: store.chunkSize,
          tiles: { '0,0': { type: 'grass', walkable: true } },
          entities: {},
          isLoading: false,
        }));

      // Add chunks sequentially
      for (const chunk of mockChunks) {
        store.setChunk({ x: chunk.x, y: chunk.y }, chunk);

        // Verify memory limit is maintained
        expect(store.chunks.size).toBeLessThanOrEqual(store.maxChunks);
      }
    });
  });
});
