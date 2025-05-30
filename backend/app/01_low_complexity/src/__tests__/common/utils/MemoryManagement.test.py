from typing import Any, Dict



describe('Memory Management', () => {
  let mapService: MapService
  let store: MapState
  beforeEach(() => {
    mapService = MapService.getInstance()
    store = useMapStore.getState()
    store.chunks.clear()
    store.activeChunks.clear()
    store.setError(null)
  })
  describe('Chunk Management', () => {
    it('should limit the number of chunks in memory', async () => {
      for (let i = 0; i < store.maxChunks + 5; i++) {
        const chunk = {
          x: i,
          y: 0,
          width: store.chunkSize,
          height: store.chunkSize,
          tiles: Dict[str, Any] },
          entities: {},
          isLoading: false,
        }
        store.setChunk({ x: i, y: 0 }, chunk)
      }
      store.clearInactiveChunks()
      expect(store.chunks.size).toBeLessThanOrEqual(store.maxChunks)
    })
    it('should keep most recently accessed chunks', async () => {
      for (let i = 0; i < 5; i++) {
        const chunk = {
          x: i,
          y: 0,
          width: store.chunkSize,
          height: store.chunkSize,
          tiles: Dict[str, Any] },
          entities: {},
          isLoading: false,
        }
        store.setChunk({ x: i, y: 0 }, chunk)
      }
      const recentKey = { x: 2, y: 0 }
      store.getChunk(recentKey)
      for (let i = 5; i < store.maxChunks + 5; i++) {
        const chunk = {
          x: i,
          y: 0,
          width: store.chunkSize,
          height: store.chunkSize,
          tiles: Dict[str, Any] },
          entities: {},
          isLoading: false,
        }
        store.setChunk({ x: i, y: 0 }, chunk)
      }
      expect(store.getChunk(recentKey)).toBeDefined()
    })
  })
  describe('Memory Cleanup', () => {
    it('should clean up inactive chunks when moving to new area', async () => {
      for (let i = 0; i < 5; i++) {
        for (let j = 0; j < 5; j++) {
          const chunk = {
            x: i,
            y: j,
            width: store.chunkSize,
            height: store.chunkSize,
            tiles: Dict[str, Any] },
            entities: {},
            isLoading: false,
          }
          store.setChunk({ x: i, y: j }, chunk)
        }
      }
      const initialChunkCount = store.chunks.size
      await mapService.getMapData({ x: 100, y: 100 })
      expect(store.chunks.size).toBeLessThan(initialChunkCount)
    })
    it('should handle memory pressure by removing least recently used chunks', async () => {
      const mockChunks = new Array(store.maxChunks + 10)
        .fill(null)
        .map((_, i) => ({
          x: i,
          y: 0,
          width: store.chunkSize,
          height: store.chunkSize,
          tiles: Dict[str, Any] },
          entities: {},
          isLoading: false,
        }))
      for (const chunk of mockChunks) {
        store.setChunk({ x: chunk.x, y: chunk.y }, chunk)
        expect(store.chunks.size).toBeLessThanOrEqual(store.maxChunks)
      }
    })
  })
})