import { act, renderHook } from '@testing-library/react';
import { usePoiStore } from '../../store/poiStore';
import POIPersistenceService from '../../services/POIPersistenceService';
import { Position } from '../../types/common';
import type {
  POI,
  POIChunk,
  POIEntity,
  POIServiceResponse,
  POISize,
  POITheme,
  POILayout,
  POIType,
} from '../../types/poi';

// Mock crypto.randomUUID
const mockUUID = '12345678-1234-1234-1234-123456789012';
Object.defineProperty(global.crypto, 'randomUUID', {
  value: jest.fn().mockReturnValue(mockUUID),
});

// Mock POIPersistenceService
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
  };

  return {
    getInstance: jest.fn(() => mockInstance),
  };
});

// Mock fetch for API calls
global.fetch = jest.fn();

// Test data
const testPOI: Omit<POI, 'chunks' | 'activeChunks' | 'isActive'> = {
  id: 'test1',
  name: 'Test POI',
  type: 'city',
  position: { x: 0, y: 0 },
  description: 'Test description',
  layout: {
    width: 100,
    height: 100,
    rooms: [],
    connections: [],
  },
  properties: {},
  size: 'medium',
  theme: 'medieval',
};

const testEntity: Omit<POIEntity, 'id'> = {
  type: 'npc',
  position: { x: 5, y: 5 },
  properties: {},
};

const testChunk: Omit<POIChunk, 'lastAccessed'> = {
  position: { x: 0, y: 0 },
  entities: [],
  features: [],
  isDirty: false,
};

const targetChunk: Omit<POIChunk, 'lastAccessed'> = {
  position: { x: 1, y: 0 },
  entities: [],
  features: [],
  isDirty: false,
};

const chunks = [
  testChunk,
  {
    position: { x: 1, y: 0 },
    entities: [],
    features: [],
    isDirty: false,
  },
  {
    position: { x: 0, y: 1 },
    entities: [],
    features: [],
    isDirty: false,
  },
];

const mockChunks: POIChunk[] = chunks.map(chunk => ({
  ...chunk,
  lastAccessed: Date.now(),
}));

describe('POI Store', () => {
  beforeEach(() => {
    // Clear store between tests
    act(() => {
      usePoiStore.setState({
        pois: {},
        activePOIs: [],
        currentPOI: null,
      });
    });
  });

  describe('POI Management', () => {
    // ... existing code ...
  });

  describe('Store Initialization', () => {
    it('should initialize with empty state', () => {
      const { result } = renderHook(() => usePoiStore());
      expect(result.current.pois).toEqual({});
      expect(result.current.activePOIs).toEqual([]);
      expect(result.current.currentPOI).toBeNull();
      expect(result.current.isLoading).toBeFalsy();
      expect(result.current.error).toBeNull();
    });

    it('should initialize from storage', () => {
      const mockState = {
        pois: {
          test1: {
            ...testPOI,
            chunks: {},
            activeChunks: [],
            isActive: false,
          },
        },
        activePOIs: ['test1'],
        currentPOI: 'test1',
      };

      // Mock loadState to return our test data
      const mockPersistenceService = POIPersistenceService.getInstance();
      (mockPersistenceService.loadState as jest.Mock).mockReturnValue({
        success: true,
        data: mockState,
      });

      const { result } = renderHook(() => usePoiStore());
      act(() => {
        result.current.initializeFromStorage();
      });

      expect(result.current.pois.test1).toEqual(mockState.pois.test1);
      expect(result.current.activePOIs).toEqual(['test1']);
      expect(result.current.currentPOI).toBe('test1');
    });

    it('should handle storage initialization errors', () => {
      const mockPersistenceService = POIPersistenceService.getInstance();
      (mockPersistenceService.loadState as jest.Mock).mockReturnValue({
        success: false,
        error: 'Failed to load state',
      });

      const { result } = renderHook(() => usePoiStore());
      act(() => {
        result.current.initializeFromStorage();
      });

      expect(result.current.error).toBe('Failed to load state');
      expect(result.current.isLoading).toBe(false);
    });

    it('should handle empty storage state', () => {
      const mockPersistenceService = POIPersistenceService.getInstance();
      (mockPersistenceService.loadState as jest.Mock).mockReturnValue({
        success: true,
        data: null,
      });

      const { result } = renderHook(() => usePoiStore());
      act(() => {
        result.current.initializeFromStorage();
      });

      expect(result.current.pois).toEqual({});
      expect(result.current.activePOIs).toEqual([]);
      expect(result.current.currentPOI).toBeNull();
      expect(result.current.error).toBe('Failed to load state');
    });
  });

  describe('Chunk Management', () => {
    it('should add a new chunk', () => {
      const { result } = renderHook(() => usePoiStore());

      act(() => {
        result.current.createPOI(testPOI);
        result.current.addChunk('test1', testChunk);
      });

      const poi = result.current.getPOI('test1');
      expect(poi?.chunks['0,0']).toBeDefined();
      expect(poi?.chunks['0,0'].entities).toEqual([]);
      expect(poi?.chunks['0,0'].features).toEqual([]);
    });

    it('should activate and deactivate chunks', () => {
      const { result } = renderHook(() => usePoiStore());

      act(() => {
        result.current.createPOI(testPOI);
        result.current.addChunk('test1', testChunk);
        result.current.activateChunk('test1', { x: 0, y: 0 });
      });

      const poi = result.current.getPOI('test1');
      expect(poi?.activeChunks).toContain('0,0');

      act(() => {
        result.current.deactivateChunk('test1', { x: 0, y: 0 });
      });

      const updatedPoi = result.current.getPOI('test1');
      expect(updatedPoi?.activeChunks).not.toContain('0,0');
    });

    it('should cleanup inactive chunks', () => {
      const { result } = renderHook(() => usePoiStore());

      act(() => {
        result.current.createPOI(testPOI);
        chunks.forEach(chunk => result.current.addChunk('test1', chunk));
        result.current.activateChunk('test1', { x: 0, y: 0 });
      });

      const poi = result.current.getPOI('test1');
      expect(Object.keys(poi?.chunks || {})).toHaveLength(3);

      act(() => {
        result.current.cleanupInactiveChunks('test1', 1);
      });

      const updatedPoi = result.current.getPOI('test1');
      expect(Object.keys(updatedPoi?.chunks || {})).toHaveLength(1);
      expect(updatedPoi?.chunks['0,0']).toBeDefined();
    });

    it('should load chunks from API', async () => {
      const mockChunkData = {
        position: { x: 0, y: 0 },
        entities: [],
        features: [],
        isDirty: false,
        lastAccessed: Date.now(),
      };

      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ chunks: [mockChunkData] }),
      });

      const { result } = renderHook(() => usePoiStore());

      act(() => {
        result.current.createPOI(testPOI);
      });

      await act(async () => {
        await result.current.loadPOIChunks('test1', { x: 0, y: 0 }, 1);
      });

      const poi = result.current.getPOI('test1');
      console.log('POI after chunk load:', poi);
      expect(poi?.chunks['0,0']).toBeDefined();
      expect(poi?.chunks['0,0'].entities).toEqual([]);
      expect(poi?.chunks['0,0'].features).toEqual([]);
    });

    it('should handle chunk load errors', async () => {
      global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => usePoiStore());

      act(() => {
        result.current.createPOI(testPOI);
      });

      await act(async () => {
        await result.current.loadPOIChunks('test1', { x: 0, y: 0 }, 1);
      });

      expect(result.current.error).toBe(
        'Failed to load POI chunks: Network error'
      );
    });

    it('should retry failed chunk loads', async () => {
      const mockChunkData = {
        position: { x: 0, y: 0 },
        entities: [],
        features: [],
        isDirty: false,
        lastAccessed: Date.now(),
      };

      let attempts = 0;
      global.fetch = jest.fn().mockImplementation(() => {
        attempts++;
        if (attempts < 3) {
          return Promise.reject(new Error('Network error'));
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ chunks: [mockChunkData] }),
        });
      });

      const { result } = renderHook(() => usePoiStore());

      act(() => {
        result.current.createPOI(testPOI);
      });

      await act(async () => {
        await result.current.loadPOIChunks('test1', { x: 0, y: 0 }, 1);
      });

      expect(attempts).toBe(3);
      const poi = result.current.getPOI('test1');
      console.log('POI after retry chunk load:', poi);
      expect(poi?.chunks['0,0']).toBeDefined();
    });
  });

  describe('Entity Management', () => {
    it('should add an entity to a chunk', () => {
      const { result } = renderHook(() => usePoiStore());

      act(() => {
        result.current.createPOI(testPOI);
        result.current.addChunk('test1', testChunk);
        result.current.addEntity('test1', { x: 0, y: 0 }, testEntity);
      });

      const poi = result.current.getPOI('test1');
      const entities = Object.values(
        poi?.chunks['0,0'].entities || {}
      ) as POIEntity[];
      expect(entities).toHaveLength(1);
      expect(entities[0].type).toBe('npc');
      expect(entities[0].id).toBeDefined();
    });

    it('should update an entity', () => {
      const { result } = renderHook(() => usePoiStore());

      // Add entity first
      act(() => {
        result.current.createPOI(testPOI);
        result.current.addChunk('test1', testChunk);
        result.current.addEntity('test1', { x: 0, y: 0 }, testEntity);
      });

      // Get actual entity ID
      const poi = result.current.getPOI('test1');
      const entityId = poi?.chunks['0,0'].entities[0]?.id;
      expect(entityId).toBeDefined();

      // Update entity
      if (typeof entityId === 'string') {
        act(() => {
          result.current.updateEntity('test1', { x: 0, y: 0 }, entityId, {
            position: { x: 10, y: 10 },
          });
        });
      }

      const updatedPoi = result.current.getPOI('test1');
      console.log('POI after updateEntity:', updatedPoi);
      const entity = updatedPoi?.chunks['0,0'].entities.find(
        e => e.id === entityId
      );
      expect(entity).toBeDefined();
      expect(entity!.position).toEqual({ x: 10, y: 10 });
    });

    it('should move an entity between chunks', () => {
      const { result } = renderHook(() => usePoiStore());

      // Add entity first
      act(() => {
        result.current.createPOI(testPOI);
        result.current.addChunk('test1', testChunk);
        result.current.addChunk('test1', targetChunk);
        result.current.addEntity('test1', { x: 0, y: 0 }, testEntity);
      });

      // Get actual entity ID
      const poi = result.current.getPOI('test1');
      const entityId = poi?.chunks['0,0'].entities[0]?.id;
      expect(entityId).toBeDefined();

      // Move entity
      if (typeof entityId === 'string') {
        act(() => {
          result.current.moveEntity(
            'test1',
            entityId,
            { x: 0, y: 0 },
            { x: 1, y: 0 },
            { x: 15, y: 5 }
          );
        });
      }

      const updatedPoi = result.current.getPOI('test1');
      console.log('POI after moveEntity:', updatedPoi);
      expect(updatedPoi?.chunks['0,0'].entities.length).toBe(0);
      expect(updatedPoi?.chunks['1,0'].entities.length).toBe(1);
      const movedEntity = updatedPoi?.chunks['1,0'].entities.find(
        e => e.id === entityId
      );
      expect(movedEntity).toBeDefined();
      expect(movedEntity!.position).toEqual({ x: 15, y: 5 });
    });

    it('should maintain entity state consistency during updates', () => {
      const { result } = renderHook(() => usePoiStore());

      // Add entity first
      act(() => {
        result.current.createPOI(testPOI);
        result.current.addChunk('test1', testChunk);
        result.current.addEntity(
          'test1',
          { x: 0, y: 0 },
          {
            ...testEntity,
            properties: { health: 100, status: ['active'] },
          }
        );
      });

      // Get actual entity ID
      const poi = result.current.getPOI('test1');
      const entityId = poi?.chunks['0,0'].entities[0]?.id;
      expect(entityId).toBeDefined();

      // Multiple concurrent updates
      if (typeof entityId === 'string') {
        act(() => {
          result.current.updateEntity('test1', { x: 0, y: 0 }, entityId, {
            properties: { health: 90 },
          });
          result.current.updateEntity('test1', { x: 0, y: 0 }, entityId, {
            properties: { status: ['active', 'wounded'] },
          });
        });
      }

      const updatedPoi = result.current.getPOI('test1');
      console.log('POI after maintainEntity:', updatedPoi);
      const entity = updatedPoi?.chunks['0,0'].entities.find(
        e => e.id === entityId
      );
      expect(entity).toBeDefined();
      expect(entity!.properties.health).toBe(90);
      expect(entity!.properties.status).toEqual(['active', 'wounded']);
    });

    it('should handle entity removal', () => {
      const { result } = renderHook(() => usePoiStore());

      // Add entity first
      act(() => {
        result.current.createPOI(testPOI);
        result.current.addChunk('test1', testChunk);
        result.current.addEntity('test1', { x: 0, y: 0 }, testEntity);
      });

      // Get actual entity ID
      const poi = result.current.getPOI('test1');
      const entityId = poi?.chunks['0,0'].entities[0]?.id;
      expect(entityId).toBeDefined();

      // Remove entity
      if (typeof entityId === 'string') {
        act(() => {
          result.current.removeEntity('test1', { x: 0, y: 0 }, entityId);
        });
      }

      const updatedPoi = result.current.getPOI('test1');
      console.log('POI after removeEntity:', updatedPoi);
      expect(updatedPoi?.chunks['0,0'].entities.length).toBe(0);
    });

    it('should retry failed chunk loads', async () => {
      const { result } = renderHook(() => usePoiStore());
      let callCount = 0;

      // Mock API with failure then success
      global.fetch = jest.fn().mockImplementation(() => {
        callCount++;
        if (callCount === 1) {
          return Promise.reject(new Error('Network error'));
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ chunks: mockChunks }),
        });
      });

      await act(async () => {
        await result.current.loadPOIChunks('test1', { x: 0, y: 0 }, 1);
      });

      expect(callCount).toBe(2);
      expect(result.current.error).toBeNull();
    });
  });

  describe('Service Integration', () => {
    it('should load a POI from the API', async () => {
      const mockPOIData: Omit<POI, 'chunks' | 'activeChunks' | 'isActive'> = {
        id: 'test1',
        type: 'city' as POIType,
        name: 'Test City',
        position: { x: 0, y: 0 },
        properties: {},
        size: 'medium' as POISize,
        theme: 'medieval' as POITheme,
        description: 'Test city description',
        layout: {
          width: 100,
          height: 100,
          rooms: [],
          connections: [],
        } as POILayout,
      };

      // ... existing code ...
    });

    it('should load POI chunks from the API', async () => {
      const mockChunks: POIChunk[] = [
        {
          position: { x: 0, y: 0 },
          entities: [],
          isDirty: false,
          features: [],
          lastAccessed: Date.now(),
        },
      ];

      // ... existing code ...

      const testPOI: Omit<POI, 'chunks' | 'activeChunks' | 'isActive'> = {
        id: 'test1',
        type: 'city' as POIType,
        name: 'Test City',
        position: { x: 0, y: 0 },
        properties: {},
        size: 'medium' as POISize,
        theme: 'medieval' as POITheme,
        description: 'Test city description',
        layout: {
          width: 100,
          height: 100,
          rooms: [],
          connections: [],
        } as POILayout,
      };

      // ... existing code ...
    });

    it('should save POI state to the API', async () => {
      const testPOI: POI = {
        id: 'test1',
        type: 'city' as POIType,
        name: 'Test City',
        position: { x: 0, y: 0 },
        properties: {},
        size: 'medium' as POISize,
        theme: 'medieval' as POITheme,
        description: 'Test city description',
        layout: {
          width: 100,
          height: 100,
          rooms: [],
          connections: [],
        } as POILayout,
        chunks: {},
        activeChunks: [],
        isActive: false,
      };

      // ... existing code ...
    });

    it('should handle API errors gracefully', async () => {
      const { result } = renderHook(() => usePoiStore());

      // Mock API error
      global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));

      await act(async () => {
        await result.current.loadPOI('test1');
      });

      expect(result.current.error).toBe('Failed to load POI: Network error');
      expect(result.current.isLoading).toBe(false);
    });

    it('should retry failed chunk loads', async () => {
      const { result } = renderHook(() => usePoiStore());
      let callCount = 0;

      // Mock API with failure then success
      global.fetch = jest.fn().mockImplementation(() => {
        callCount++;
        if (callCount === 1) {
          return Promise.reject(new Error('Network error'));
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ chunks: mockChunks }),
        });
      });

      await act(async () => {
        await result.current.loadPOIChunks('test1', { x: 0, y: 0 }, 1);
      });

      expect(callCount).toBe(2);
      expect(result.current.error).toBeNull();
    });
  });

  describe('Map Store Synchronization', () => {
    const testPOI: Omit<POI, 'chunks' | 'activeChunks' | 'isActive'> = {
      id: 'test1',
      type: 'city' as POIType,
      name: 'Test City',
      position: { x: 0, y: 0 },
      properties: {},
      size: 'medium' as POISize,
      theme: 'medieval' as POITheme,
      description: 'Test city description',
      layout: {
        width: 100,
        height: 100,
        rooms: [],
        connections: [],
      } as POILayout,
    };

    // ... existing code ...
  });

  // ... existing code ...
});
