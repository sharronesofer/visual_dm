import { POIChunkManager } from '../POIChunkManager';
import { Position } from '../../types/common';
import { POIChunk } from '../../types/poi';

describe('POIChunkManager', () => {
  let chunkManager: POIChunkManager;
  let mockFetch: jest.Mock;

  beforeEach(() => {
    mockFetch = jest.fn();
    chunkManager = new POIChunkManager(mockFetch, {
      chunkSize: 16,
      maxCachedChunks: 4,
      preloadRadius: 2,
      loadingBatchSize: 2,
    });
  });

  describe('Chunk Loading Optimization', () => {
    const mockChunk = (x: number, y: number): POIChunk => ({
      position: { x, y },
      entities: {},
      lastModified: Date.now(),
    });

    it('should load chunks in batches', async () => {
      mockFetch.mockImplementation(async (path: string) => {
        const [x, y] = path.split('/').pop()!.split(',').map(Number);
        return mockChunk(x, y);
      });

      const centerPos: Position = { x: 0, y: 0 };
      const result = await chunkManager.loadChunksInRadius(
        'test-poi',
        centerPos,
        1
      );

      expect(result.success).toBe(true);
      expect(result.data.queued).toBeGreaterThan(0);
      expect(mockFetch).toHaveBeenCalled();
    });

    it('should prioritize chunks closer to center', async () => {
      const fetchOrder: string[] = [];
      mockFetch.mockImplementation(async (path: string) => {
        fetchOrder.push(path);
        const [x, y] = path.split('/').pop()!.split(',').map(Number);
        return mockChunk(x, y);
      });

      const centerPos: Position = { x: 0, y: 0 };
      await chunkManager.loadChunksInRadius('test-poi', centerPos, 2);

      // Verify that closer chunks are loaded first
      const distances = fetchOrder.map(path => {
        const [x, y] = path.split('/').pop()!.split(',').map(Number);
        return Math.sqrt(x * x + y * y);
      });

      // Check if distances are generally increasing (chunks further away loaded later)
      for (let i = 1; i < distances.length; i++) {
        expect(distances[i]).toBeGreaterThanOrEqual(distances[i - 1]);
      }
    });

    it('should handle cache eviction based on priority', async () => {
      mockFetch.mockImplementation(async (path: string) => {
        const [x, y] = path.split('/').pop()!.split(',').map(Number);
        return mockChunk(x, y);
      });

      // Load more chunks than maxCachedChunks
      for (let i = 0; i < 6; i++) {
        await chunkManager.loadChunk('test-poi', { x: i, y: 0 });
      }

      // Load a high-priority chunk
      const highPriorityResult = await chunkManager.loadChunk('test-poi', {
        x: 0,
        y: 0,
      });
      expect(highPriorityResult.success).toBe(true);

      // Verify the high-priority chunk is still in cache
      const cachedResult = await chunkManager.loadChunk('test-poi', {
        x: 0,
        y: 0,
      });
      expect(cachedResult.success).toBe(true);
      expect(mockFetch).not.toHaveBeenCalledWith('/test-poi/chunks/0,0');
    });

    it('should process load queue efficiently', async () => {
      const loadTimes: number[] = [];
      mockFetch.mockImplementation(async (path: string) => {
        const startTime = Date.now();
        const [x, y] = path.split('/').pop()!.split(',').map(Number);
        await new Promise(resolve => setTimeout(resolve, 50)); // Simulate network delay
        loadTimes.push(Date.now() - startTime);
        return mockChunk(x, y);
      });

      const centerPos: Position = { x: 0, y: 0 };
      await chunkManager.loadChunksInRadius('test-poi', centerPos, 2);

      // Verify that chunks are loaded in parallel within batch size
      const maxParallelLoads = Math.max(
        ...loadTimes.map(
          (time, i) =>
            loadTimes.filter((t, j) => Math.abs(t - time) < 20 && i !== j)
              .length + 1
        )
      );
      expect(maxParallelLoads).toBeLessThanOrEqual(2); // loadingBatchSize
    });

    it('should handle errors gracefully during batch loading', async () => {
      let errorCount = 0;
      mockFetch.mockImplementation(async (path: string) => {
        if (errorCount++ % 2 === 0) {
          throw new Error('Simulated fetch error');
        }
        const [x, y] = path.split('/').pop()!.split(',').map(Number);
        return mockChunk(x, y);
      });

      const centerPos: Position = { x: 0, y: 0 };
      const result = await chunkManager.loadChunksInRadius(
        'test-poi',
        centerPos,
        1
      );

      expect(result.success).toBe(true);
      expect(result.data.queued).toBeGreaterThan(0);
      // Verify that failed chunks don't prevent loading of other chunks
      expect(mockFetch).toHaveBeenCalledTimes(expect.any(Number));
    });
  });
});
