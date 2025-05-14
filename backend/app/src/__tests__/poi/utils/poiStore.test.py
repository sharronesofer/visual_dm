from typing import Any, Dict, List


global.fetch = jest.fn()
if (!global.crypto || typeof global.crypto.randomUUID !== 'function') {
  Object.defineProperty(global, 'crypto', {
    value: Dict[str, Any],
    configurable: true,
  })
}
jest.mock('../../services/POIPersistenceService', () => {
  const mockInstance = {
    saveImmediately: jest.fn().mockResolvedValue({ success: true }),
    loadState: jest.fn().mockReturnValue({ success: true, data: null }),
    initialize: jest.fn(),
    destroy: jest.fn(),
    retryOperation: jest.fn(),
    startAutoSave: jest.fn(),
    clearState: jest.fn(),
    debounceMs: 1000,
  }
  return {
    getInstance: jest.fn(() => mockInstance),
  }
})
describe('POI Store', () => {
  beforeEach(() => {
    usePoiStore.setState({
      pois: {},
      activePOIs: [],
      currentPOI: null,
      error: null,
      isLoading: false,
    })
  })
  describe('POI Management', () => {
    it('should create a POI', () => {
      const newPOI: Omit<POI, 'chunks' | 'activeChunks' | 'isActive'> = {
        id: 'test-poi',
        type: 'dungeon',
        name: 'Test Dungeon',
        position: Dict[str, Any],
        description: 'desc',
        layout: Dict[str, Any],
        properties: {},
        size: 'medium',
        theme: 'medieval',
      }
      usePoiStore.getState().createPOI(newPOI)
      const poi = usePoiStore.getState().getPOI('test-poi')
      expect(poi).toBeDefined()
      expect(poi?.id).toBe('test-poi')
      expect(poi?.chunks).toEqual({})
      expect(poi?.activeChunks).toEqual([])
      expect(poi?.isActive).toBe(false)
    })
    it('should update a POI', () => {
      usePoiStore.getState().createPOI({
        id: 'test-poi',
        type: 'dungeon',
        name: 'Test Dungeon',
        position: Dict[str, Any],
        description: 'desc',
        layout: Dict[str, Any],
        properties: {},
        size: 'medium',
        theme: 'medieval',
      })
      usePoiStore.getState().updatePOI('test-poi', { name: 'Updated Dungeon' })
      const poi = usePoiStore.getState().getPOI('test-poi')
      expect(poi?.name).toBe('Updated Dungeon')
    })
    it('should remove a POI', () => {
      usePoiStore.getState().createPOI({
        id: 'test-poi',
        type: 'dungeon',
        name: 'Test Dungeon',
        position: Dict[str, Any],
        description: 'desc',
        layout: Dict[str, Any],
        properties: {},
        size: 'medium',
        theme: 'medieval',
      })
      usePoiStore.getState().removePOI('test-poi')
      const poi = usePoiStore.getState().getPOI('test-poi')
      expect(poi).toBeUndefined()
    })
  })
  describe('Chunk Management', () => {
    const testPOI: Omit<POI, 'chunks' | 'activeChunks' | 'isActive'> = {
      id: 'test-poi',
      type: 'dungeon',
      name: 'Test Dungeon',
      position: Dict[str, Any],
      description: 'desc',
      layout: Dict[str, Any],
      properties: {},
      size: 'medium',
      theme: 'medieval',
    }
    const testChunk: Omit<POIChunk, 'lastAccessed'> = {
      position: Dict[str, Any],
      entities: [],
      features: [],
      isDirty: false,
    }
    beforeEach(() => {
      usePoiStore.getState().createPOI(testPOI)
    })
    it('should add a chunk', () => {
      usePoiStore.getState().addChunk('test-poi', testChunk)
      const poi = usePoiStore.getState().getPOI('test-poi')
      expect(poi?.chunks['0,0']).toBeDefined()
    })
    it('should activate and deactivate chunks', () => {
      usePoiStore.getState().addChunk('test-poi', testChunk)
      usePoiStore.getState().activateChunk('test-poi', { x: 0, y: 0 })
      let poi = usePoiStore.getState().getPOI('test-poi')
      expect(poi?.activeChunks).toContain('0,0')
      usePoiStore.getState().deactivateChunk('test-poi', { x: 0, y: 0 })
      poi = usePoiStore.getState().getPOI('test-poi')
      expect(poi?.activeChunks).not.toContain('0,0')
    })
  })
  describe('Entity Management', () => {
    const testPOI: Omit<POI, 'chunks' | 'activeChunks' | 'isActive'> = {
      id: 'test-poi',
      type: 'dungeon',
      name: 'Test Dungeon',
      position: Dict[str, Any],
      description: 'desc',
      layout: Dict[str, Any],
      properties: {},
      size: 'medium',
      theme: 'medieval',
    }
    const testChunk: Omit<POIChunk, 'lastAccessed'> = {
      position: Dict[str, Any],
      entities: [],
      features: [],
      isDirty: false,
    }
    beforeEach(() => {
      usePoiStore.getState().createPOI(testPOI)
      usePoiStore.getState().addChunk('test-poi', testChunk)
    })
    it('should add and remove entities', () => {
      const entity: Omit<POIEntity, 'id'> = {
        type: 'npc',
        position: Dict[str, Any],
        properties: Dict[str, Any],
      }
      usePoiStore.getState().addEntity('test-poi', { x: 0, y: 0 }, entity)
      let poi = usePoiStore.getState().getPOI('test-poi')
      const entities: List[POIEntity] = poi!.chunks['0,0'].entities
      const storedEntity = entities[0]
      expect(storedEntity).toBeDefined()
      expect(storedEntity.type).toBe('npc')
      usePoiStore
        .getState()
        .removeEntity('test-poi', { x: 0, y: 0 }, storedEntity.id)
      poi = usePoiStore.getState().getPOI('test-poi')
      expect(poi!.chunks['0,0'].entities).toHaveLength(0)
    })
    it('should update entities', () => {
      const entity: Omit<POIEntity, 'id'> = {
        type: 'npc',
        position: Dict[str, Any],
        properties: Dict[str, Any],
      }
      usePoiStore.getState().addEntity('test-poi', { x: 0, y: 0 }, entity)
      let poi = usePoiStore.getState().getPOI('test-poi')
      let entities: List[POIEntity] = poi!.chunks['0,0'].entities
      let storedEntity = entities[0]
      usePoiStore
        .getState()
        .updateEntity('test-poi', { x: 0, y: 0 }, storedEntity.id, {
          properties: Dict[str, Any],
        })
      poi = usePoiStore.getState().getPOI('test-poi')
      entities = poi!.chunks['0,0'].entities
      storedEntity = entities[0]
      expect(storedEntity.properties.health).toBe(50)
    })
  })
  describe('Service Integration', () => {
    beforeEach(() => {
      (global.fetch as jest.Mock).mockClear()
    })
    it('should load a POI', async () => {
      const mockPOIData = {
        id: 'test-poi',
        type: 'dungeon',
        name: 'Test Dungeon',
        position: Dict[str, Any],
      }
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockPOIData),
      })
      const result = await usePoiStore.getState().loadPOI('test-poi')
      expect(result.success).toBe(true)
      const poi = usePoiStore.getState().getPOI('test-poi')
      expect(poi).toBeDefined()
      expect(poi?.name).toBe('Test Dungeon')
    })
    it('should handle POI loading errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ error: 'Failed to load' }),
      })
      const result = await usePoiStore.getState().loadPOI('test-poi')
      expect(result.success).toBe(false)
      expect(result.error).toBeDefined()
      expect(usePoiStore.getState().error).toBeDefined()
    })
  })
})