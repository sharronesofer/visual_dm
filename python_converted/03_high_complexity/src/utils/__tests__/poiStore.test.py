from typing import Any, Dict, List



  POI,
  POIChunk,
  POIEntity,
  POIServiceResponse,
  POISize,
  POITheme,
  POILayout,
  POIType,
} from '../../types/poi'
const mockUUID = '12345678-1234-1234-1234-123456789012'
Object.defineProperty(global.crypto, 'randomUUID', {
  value: jest.fn().mockReturnValue(mockUUID),
})
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
global.fetch = jest.fn()
const testPOI: Omit<POI, 'chunks' | 'activeChunks' | 'isActive'> = {
  id: 'test1',
  name: 'Test POI',
  type: 'city',
  position: Dict[str, Any],
  description: 'Test description',
  layout: Dict[str, Any],
  properties: {},
  size: 'medium',
  theme: 'medieval',
}
const testEntity: Omit<POIEntity, 'id'> = {
  type: 'npc',
  position: Dict[str, Any],
  properties: {},
}
const testChunk: Omit<POIChunk, 'lastAccessed'> = {
  position: Dict[str, Any],
  entities: [],
  features: [],
  isDirty: false,
}
const targetChunk: Omit<POIChunk, 'lastAccessed'> = {
  position: Dict[str, Any],
  entities: [],
  features: [],
  isDirty: false,
}
const chunks = [
  testChunk,
  {
    position: Dict[str, Any],
    entities: [],
    features: [],
    isDirty: false,
  },
  {
    position: Dict[str, Any],
    entities: [],
    features: [],
    isDirty: false,
  },
]
const mockChunks: List[POIChunk] = chunks.map(chunk => ({
  ...chunk,
  lastAccessed: Date.now(),
}))
describe('POI Store', () => {
  beforeEach(() => {
    act(() => {
      usePoiStore.setState({
        pois: {},
        activePOIs: [],
        currentPOI: null,
      })
    })
  })
  describe('POI Management', () => {
  })
  describe('Store Initialization', () => {
    it('should initialize with empty state', () => {
      const { result } = renderHook(() => usePoiStore())
      expect(result.current.pois).toEqual({})
      expect(result.current.activePOIs).toEqual([])
      expect(result.current.currentPOI).toBeNull()
      expect(result.current.isLoading).toBeFalsy()
      expect(result.current.error).toBeNull()
    })
    it('should initialize from storage', () => {
      const mockState = {
        pois: Dict[str, Any],
            activeChunks: [],
            isActive: false,
          },
        },
        activePOIs: ['test1'],
        currentPOI: 'test1',
      }
      const mockPersistenceService = POIPersistenceService.getInstance()
      (mockPersistenceService.loadState as jest.Mock).mockReturnValue({
        success: true,
        data: mockState,
      })
      const { result } = renderHook(() => usePoiStore())
      act(() => {
        result.current.initializeFromStorage()
      })
      expect(result.current.pois.test1).toEqual(mockState.pois.test1)
      expect(result.current.activePOIs).toEqual(['test1'])
      expect(result.current.currentPOI).toBe('test1')
    })
    it('should handle storage initialization errors', () => {
      const mockPersistenceService = POIPersistenceService.getInstance()
      (mockPersistenceService.loadState as jest.Mock).mockReturnValue({
        success: false,
        error: 'Failed to load state',
      })
      const { result } = renderHook(() => usePoiStore())
      act(() => {
        result.current.initializeFromStorage()
      })
      expect(result.current.error).toBe('Failed to load state')
      expect(result.current.isLoading).toBe(false)
    })
    it('should handle empty storage state', () => {
      const mockPersistenceService = POIPersistenceService.getInstance()
      (mockPersistenceService.loadState as jest.Mock).mockReturnValue({
        success: true,
        data: null,
      })
      const { result } = renderHook(() => usePoiStore())
      act(() => {
        result.current.initializeFromStorage()
      })
      expect(result.current.pois).toEqual({})
      expect(result.current.activePOIs).toEqual([])
      expect(result.current.currentPOI).toBeNull()
      expect(result.current.error).toBe('Failed to load state')
    })
  })
  describe('Chunk Management', () => {
    it('should add a new chunk', () => {
      const { result } = renderHook(() => usePoiStore())
      act(() => {
        result.current.createPOI(testPOI)
        result.current.addChunk('test1', testChunk)
      })
      const poi = result.current.getPOI('test1')
      expect(poi?.chunks['0,0']).toBeDefined()
      expect(poi?.chunks['0,0'].entities).toEqual([])
      expect(poi?.chunks['0,0'].features).toEqual([])
    })
    it('should activate and deactivate chunks', () => {
      const { result } = renderHook(() => usePoiStore())
      act(() => {
        result.current.createPOI(testPOI)
        result.current.addChunk('test1', testChunk)
        result.current.activateChunk('test1', { x: 0, y: 0 })
      })
      const poi = result.current.getPOI('test1')
      expect(poi?.activeChunks).toContain('0,0')
      act(() => {
        result.current.deactivateChunk('test1', { x: 0, y: 0 })
      })
      const updatedPoi = result.current.getPOI('test1')
      expect(updatedPoi?.activeChunks).not.toContain('0,0')
    })
    it('should cleanup inactive chunks', () => {
      const { result } = renderHook(() => usePoiStore())
      act(() => {
        result.current.createPOI(testPOI)
        chunks.forEach(chunk => result.current.addChunk('test1', chunk))
        result.current.activateChunk('test1', { x: 0, y: 0 })
      })
      const poi = result.current.getPOI('test1')
      expect(Object.keys(poi?.chunks || {})).toHaveLength(3)
      act(() => {
        result.current.cleanupInactiveChunks('test1', 1)
      })
      const updatedPoi = result.current.getPOI('test1')
      expect(Object.keys(updatedPoi?.chunks || {})).toHaveLength(1)
      expect(updatedPoi?.chunks['0,0']).toBeDefined()
    })
    it('should load chunks from API', async () => {
      const mockChunkData = {
        position: Dict[str, Any],
        entities: [],
        features: [],
        isDirty: false,
        lastAccessed: Date.now(),
      }
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ chunks: [mockChunkData] }),
      })
      const { result } = renderHook(() => usePoiStore())
      act(() => {
        result.current.createPOI(testPOI)
      })
      await act(async () => {
        await result.current.loadPOIChunks('test1', { x: 0, y: 0 }, 1)
      })
      const poi = result.current.getPOI('test1')
      console.log('POI after chunk load:', poi)
      expect(poi?.chunks['0,0']).toBeDefined()
      expect(poi?.chunks['0,0'].entities).toEqual([])
      expect(poi?.chunks['0,0'].features).toEqual([])
    })
    it('should handle chunk load errors', async () => {
      global.fetch = jest.fn().mockRejectedValue(new Error('Network error'))
      const { result } = renderHook(() => usePoiStore())
      act(() => {
        result.current.createPOI(testPOI)
      })
      await act(async () => {
        await result.current.loadPOIChunks('test1', { x: 0, y: 0 }, 1)
      })
      expect(result.current.error).toBe(
        'Failed to load POI chunks: Network error'
      )
    })
    it('should retry failed chunk loads', async () => {
      const mockChunkData = {
        position: Dict[str, Any],
        entities: [],
        features: [],
        isDirty: false,
        lastAccessed: Date.now(),
      }
      let attempts = 0
      global.fetch = jest.fn().mockImplementation(() => {
        attempts++
        if (attempts < 3) {
          return Promise.reject(new Error('Network error'))
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ chunks: [mockChunkData] }),
        })
      })
      const { result } = renderHook(() => usePoiStore())
      act(() => {
        result.current.createPOI(testPOI)
      })
      await act(async () => {
        await result.current.loadPOIChunks('test1', { x: 0, y: 0 }, 1)
      })
      expect(attempts).toBe(3)
      const poi = result.current.getPOI('test1')
      console.log('POI after retry chunk load:', poi)
      expect(poi?.chunks['0,0']).toBeDefined()
    })
  })
  describe('Entity Management', () => {
    it('should add an entity to a chunk', () => {
      const { result } = renderHook(() => usePoiStore())
      act(() => {
        result.current.createPOI(testPOI)
        result.current.addChunk('test1', testChunk)
        result.current.addEntity('test1', { x: 0, y: 0 }, testEntity)
      })
      const poi = result.current.getPOI('test1')
      const entities = Object.values(
        poi?.chunks['0,0'].entities || {}
      ) as POIEntity[]
      expect(entities).toHaveLength(1)
      expect(entities[0].type).toBe('npc')
      expect(entities[0].id).toBeDefined()
    })
    it('should update an entity', () => {
      const { result } = renderHook(() => usePoiStore())
      act(() => {
        result.current.createPOI(testPOI)
        result.current.addChunk('test1', testChunk)
        result.current.addEntity('test1', { x: 0, y: 0 }, testEntity)
      })
      const poi = result.current.getPOI('test1')
      const entityId = poi?.chunks['0,0'].entities[0]?.id
      expect(entityId).toBeDefined()
      if (typeof entityId === 'string') {
        act(() => {
          result.current.updateEntity('test1', { x: 0, y: 0 }, entityId, {
            position: Dict[str, Any],
          })
        })
      }
      const updatedPoi = result.current.getPOI('test1')
      console.log('POI after updateEntity:', updatedPoi)
      const entity = updatedPoi?.chunks['0,0'].entities.find(
        e => e.id === entityId
      )
      expect(entity).toBeDefined()
      expect(entity!.position).toEqual({ x: 10, y: 10 })
    })
    it('should move an entity between chunks', () => {
      const { result } = renderHook(() => usePoiStore())
      act(() => {
        result.current.createPOI(testPOI)
        result.current.addChunk('test1', testChunk)
        result.current.addChunk('test1', targetChunk)
        result.current.addEntity('test1', { x: 0, y: 0 }, testEntity)
      })
      const poi = result.current.getPOI('test1')
      const entityId = poi?.chunks['0,0'].entities[0]?.id
      expect(entityId).toBeDefined()
      if (typeof entityId === 'string') {
        act(() => {
          result.current.moveEntity(
            'test1',
            entityId,
            { x: 0, y: 0 },
            { x: 1, y: 0 },
            { x: 15, y: 5 }
          )
        })
      }
      const updatedPoi = result.current.getPOI('test1')
      console.log('POI after moveEntity:', updatedPoi)
      expect(updatedPoi?.chunks['0,0'].entities.length).toBe(0)
      expect(updatedPoi?.chunks['1,0'].entities.length).toBe(1)
      const movedEntity = updatedPoi?.chunks['1,0'].entities.find(
        e => e.id === entityId
      )
      expect(movedEntity).toBeDefined()
      expect(movedEntity!.position).toEqual({ x: 15, y: 5 })
    })
    it('should maintain entity state consistency during updates', () => {
      const { result } = renderHook(() => usePoiStore())
      act(() => {
        result.current.createPOI(testPOI)
        result.current.addChunk('test1', testChunk)
        result.current.addEntity(
          'test1',
          { x: 0, y: 0 },
          {
            ...testEntity,
            properties: Dict[str, Any],
          }
        )
      })
      const poi = result.current.getPOI('test1')
      const entityId = poi?.chunks['0,0'].entities[0]?.id
      expect(entityId).toBeDefined()
      if (typeof entityId === 'string') {
        act(() => {
          result.current.updateEntity('test1', { x: 0, y: 0 }, entityId, {
            properties: Dict[str, Any],
          })
          result.current.updateEntity('test1', { x: 0, y: 0 }, entityId, {
            properties: Dict[str, Any],
          })
        })
      }
      const updatedPoi = result.current.getPOI('test1')
      console.log('POI after maintainEntity:', updatedPoi)
      const entity = updatedPoi?.chunks['0,0'].entities.find(
        e => e.id === entityId
      )
      expect(entity).toBeDefined()
      expect(entity!.properties.health).toBe(90)
      expect(entity!.properties.status).toEqual(['active', 'wounded'])
    })
    it('should handle entity removal', () => {
      const { result } = renderHook(() => usePoiStore())
      act(() => {
        result.current.createPOI(testPOI)
        result.current.addChunk('test1', testChunk)
        result.current.addEntity('test1', { x: 0, y: 0 }, testEntity)
      })
      const poi = result.current.getPOI('test1')
      const entityId = poi?.chunks['0,0'].entities[0]?.id
      expect(entityId).toBeDefined()
      if (typeof entityId === 'string') {
        act(() => {
          result.current.removeEntity('test1', { x: 0, y: 0 }, entityId)
        })
      }
      const updatedPoi = result.current.getPOI('test1')
      console.log('POI after removeEntity:', updatedPoi)
      expect(updatedPoi?.chunks['0,0'].entities.length).toBe(0)
    })
    it('should retry failed chunk loads', async () => {
      const { result } = renderHook(() => usePoiStore())
      let callCount = 0
      global.fetch = jest.fn().mockImplementation(() => {
        callCount++
        if (callCount === 1) {
          return Promise.reject(new Error('Network error'))
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ chunks: mockChunks }),
        })
      })
      await act(async () => {
        await result.current.loadPOIChunks('test1', { x: 0, y: 0 }, 1)
      })
      expect(callCount).toBe(2)
      expect(result.current.error).toBeNull()
    })
  })
  describe('Service Integration', () => {
    it('should load a POI from the API', async () => {
      const mockPOIData: Omit<POI, 'chunks' | 'activeChunks' | 'isActive'> = {
        id: 'test1',
        type: 'city' as POIType,
        name: 'Test City',
        position: Dict[str, Any],
        properties: {},
        size: 'medium' as POISize,
        theme: 'medieval' as POITheme,
        description: 'Test city description',
        layout: Dict[str, Any] as POILayout,
      }
    })
    it('should load POI chunks from the API', async () => {
      const mockChunks: List[POIChunk] = [
        {
          position: Dict[str, Any],
          entities: [],
          isDirty: false,
          features: [],
          lastAccessed: Date.now(),
        },
      ]
      const testPOI: Omit<POI, 'chunks' | 'activeChunks' | 'isActive'> = {
        id: 'test1',
        type: 'city' as POIType,
        name: 'Test City',
        position: Dict[str, Any],
        properties: {},
        size: 'medium' as POISize,
        theme: 'medieval' as POITheme,
        description: 'Test city description',
        layout: Dict[str, Any] as POILayout,
      }
    })
    it('should save POI state to the API', async () => {
      const testPOI: POI = {
        id: 'test1',
        type: 'city' as POIType,
        name: 'Test City',
        position: Dict[str, Any],
        properties: {},
        size: 'medium' as POISize,
        theme: 'medieval' as POITheme,
        description: 'Test city description',
        layout: Dict[str, Any] as POILayout,
        chunks: {},
        activeChunks: [],
        isActive: false,
      }
    })
    it('should handle API errors gracefully', async () => {
      const { result } = renderHook(() => usePoiStore())
      global.fetch = jest.fn().mockRejectedValue(new Error('Network error'))
      await act(async () => {
        await result.current.loadPOI('test1')
      })
      expect(result.current.error).toBe('Failed to load POI: Network error')
      expect(result.current.isLoading).toBe(false)
    })
    it('should retry failed chunk loads', async () => {
      const { result } = renderHook(() => usePoiStore())
      let callCount = 0
      global.fetch = jest.fn().mockImplementation(() => {
        callCount++
        if (callCount === 1) {
          return Promise.reject(new Error('Network error'))
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ chunks: mockChunks }),
        })
      })
      await act(async () => {
        await result.current.loadPOIChunks('test1', { x: 0, y: 0 }, 1)
      })
      expect(callCount).toBe(2)
      expect(result.current.error).toBeNull()
    })
  })
  describe('Map Store Synchronization', () => {
    const testPOI: Omit<POI, 'chunks' | 'activeChunks' | 'isActive'> = {
      id: 'test1',
      type: 'city' as POIType,
      name: 'Test City',
      position: Dict[str, Any],
      properties: {},
      size: 'medium' as POISize,
      theme: 'medieval' as POITheme,
      description: 'Test city description',
      layout: Dict[str, Any] as POILayout,
    }
  })
})