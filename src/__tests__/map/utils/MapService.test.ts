import { MapService } from '../../services/MapService';
import { Position } from '../../types/common';

describe('MapService', () => {
  let mapService: MapService;

  beforeEach(() => {
    mapService = MapService.getInstance();
    mapService.setChunkSize(16);
    // Clear the cache before each test
    mapService.clearCache();
  });

  describe('getMapData', () => {
    beforeEach(() => {
      global.fetch = jest.fn();
    });

    it('should fetch and cache map chunk data', async () => {
      const mockChunk = {
        x: 0,
        y: 0,
        width: 16,
        height: 16,
        tiles: {
          '0,0': { type: 'grass', walkable: true },
        },
        entities: {},
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockChunk,
      });

      const position: Position = { x: 0, y: 0 };
      const result = await mapService.getMapData(position);

      expect(result.tiles).toEqual(mockChunk.tiles);
      expect(result.entities).toEqual(mockChunk.entities);
      expect(result.visibleArea.length).toBeGreaterThan(0);

      // Should use cached data on second call
      await mapService.getMapData(position);
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('should handle fetch errors gracefully', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(
        new Error('Network error')
      );

      const position: Position = { x: 0, y: 0 };

      await expect(mapService.getMapData(position)).rejects.toThrow(
        'Network error'
      );
    });

    it('should calculate visible area correctly', async () => {
      const mockChunk = {
        x: 0,
        y: 0,
        width: 16,
        height: 16,
        tiles: {},
        entities: {},
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockChunk,
      });

      const position: Position = { x: 5, y: 5 };
      const result = await mapService.getMapData(position);

      // Check that visible area contains the center position
      expect(result.visibleArea).toContainEqual(position);

      // Check that visible area doesn't contain points too far away
      expect(result.visibleArea).not.toContainEqual({ x: 20, y: 20 });
    });
  });

  describe('chunk management', () => {
    it('should handle chunk boundaries correctly', async () => {
      const mockChunk1 = {
        x: 0,
        y: 0,
        width: 16,
        height: 16,
        tiles: { '0,0': { type: 'grass', walkable: true } },
        entities: {},
      };

      const mockChunk2 = {
        x: 16,
        y: 0,
        width: 16,
        height: 16,
        tiles: { '16,0': { type: 'grass', walkable: true } },
        entities: {},
      };

      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockChunk1,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockChunk2,
        });

      // Test first chunk
      await mapService.getMapData({ x: 0, y: 0 });
      expect(global.fetch).toHaveBeenCalledTimes(1);

      // Test second chunk
      await mapService.getMapData({ x: 16, y: 0 });
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });
  });
});
