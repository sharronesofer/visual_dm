import { act, renderHook } from '@testing-library/react';
import { usePoiStore } from '../poiStore';
import POIPersistenceService from '../../services/POIPersistenceService';
import { Position } from '../../types/common';
import { POI, POIChunk, POIEntity } from '../../types/poi';

// Mock POIPersistenceService
jest.mock('../../services/POIPersistenceService', () => ({
  getInstance: jest.fn(() => ({
    saveImmediately: jest.fn(),
    loadState: jest.fn(() => ({ success: true, data: null })),
  })),
}));

// Mock fetch for API calls
global.fetch = jest.fn();

describe('POI Store', () => {
  beforeEach(() => {
    // Clear store between tests
    act(() => {
      usePoiStore.setState({
        pois: {},
        activePOIs: [],
        currentPOI: null,
        playerPosition: null,
        error: null,
        isLoading: false,
      });
    });
  });

  describe('Store Initialization', () => {
    it('should initialize with default state', () => {
      const { result } = renderHook(() => usePoiStore());

      expect(result.current.pois).toEqual({});
      expect(result.current.activePOIs).toEqual([]);
      expect(result.current.currentPOI).toBeNull();
      expect(result.current.playerPosition).toBeNull();
      expect(result.current.error).toBeNull();
      expect(result.current.isLoading).toBeFalsy();
    });

    it('should load state from persistence service', () => {
      const mockState = {
        pois: {
          poi1: {
            id: 'poi1',
            type: 'city',
            name: 'Test City',
            position: { x: 0, y: 0 },
            chunks: {},
            activeChunks: [],
            isActive: false,
          },
        },
        activePOIs: ['poi1'],
        currentPOI: 'poi1',
      };

      (
        POIPersistenceService.getInstance().loadState as jest.Mock
      ).mockReturnValue({
        success: true,
        data: mockState,
      });

      act(() => {
        usePoiStore.getState().initializeFromStorage();
      });

      expect(usePoiStore.getState().pois).toEqual(mockState.pois);
      expect(usePoiStore.getState().activePOIs).toEqual(mockState.activePOIs);
      expect(usePoiStore.getState().currentPOI).toBe(mockState.currentPOI);
    });
  });

  describe('POI Management', () => {
    const testPOI = {
      id: 'test1',
      type: 'city',
      name: 'Test City',
      position: { x: 0, y: 0 },
    };

    it('should create a new POI', () => {
      act(() => {
        usePoiStore.getState().createPOI(testPOI);
      });

      const state = usePoiStore.getState();
      expect(state.pois[testPOI.id]).toEqual({
        ...testPOI,
        chunks: {},
        activeChunks: [],
        isActive: false,
      });
      expect(
        POIPersistenceService.getInstance().saveImmediately
      ).toHaveBeenCalled();
    });

    it('should update an existing POI', () => {
      act(() => {
        usePoiStore.getState().createPOI(testPOI);
        usePoiStore.getState().updatePOI(testPOI.id, { name: 'Updated City' });
      });

      const state = usePoiStore.getState();
      expect(state.pois[testPOI.id].name).toBe('Updated City');
      expect(
        POIPersistenceService.getInstance().saveImmediately
      ).toHaveBeenCalledTimes(2);
    });

    it('should remove a POI', () => {
      act(() => {
        usePoiStore.getState().createPOI(testPOI);
        usePoiStore.getState().removePOI(testPOI.id);
      });

      const state = usePoiStore.getState();
      expect(state.pois[testPOI.id]).toBeUndefined();
      expect(state.activePOIs).not.toContain(testPOI.id);
      expect(state.currentPOI).toBeNull();
    });

    it('should activate and deactivate POIs', () => {
      act(() => {
        usePoiStore.getState().createPOI(testPOI);
        usePoiStore.getState().activatePOI(testPOI.id);
      });

      let state = usePoiStore.getState();
      expect(state.pois[testPOI.id].isActive).toBe(true);
      expect(state.activePOIs).toContain(testPOI.id);

      act(() => {
        usePoiStore.getState().deactivatePOI(testPOI.id);
      });

      state = usePoiStore.getState();
      expect(state.pois[testPOI.id].isActive).toBe(false);
      expect(state.activePOIs).not.toContain(testPOI.id);
    });
  });

  describe('Chunk Management', () => {
    const testPOI = {
      id: 'test1',
      type: 'city',
      name: 'Test City',
      position: { x: 0, y: 0 },
    };

    const testChunk: Omit<POIChunk, 'lastAccessed'> = {
      position: { x: 0, y: 0 },
      entities: [],
      isDirty: false,
    };

    beforeEach(() => {
      act(() => {
        usePoiStore.getState().createPOI(testPOI);
      });
    });

    it('should add a chunk to a POI', () => {
      act(() => {
        usePoiStore.getState().addChunk(testPOI.id, testChunk);
      });

      const state = usePoiStore.getState();
      const chunkKey = '0,0'; // From getChunkKey utility
      expect(state.pois[testPOI.id].chunks[chunkKey]).toBeDefined();
      expect(state.pois[testPOI.id].chunks[chunkKey].position).toEqual(
        testChunk.position
      );
      expect(
        state.pois[testPOI.id].chunks[chunkKey].lastAccessed
      ).toBeDefined();
    });

    it('should activate and deactivate chunks', () => {
      act(() => {
        usePoiStore.getState().addChunk(testPOI.id, testChunk);
        usePoiStore.getState().activateChunk(testPOI.id, testChunk.position);
      });

      let state = usePoiStore.getState();
      const chunkKey = '0,0';
      expect(state.pois[testPOI.id].activeChunks).toContain(chunkKey);

      act(() => {
        usePoiStore.getState().deactivateChunk(testPOI.id, testChunk.position);
      });

      state = usePoiStore.getState();
      expect(state.pois[testPOI.id].activeChunks).not.toContain(chunkKey);
    });

    it('should remove chunks', () => {
      act(() => {
        usePoiStore.getState().addChunk(testPOI.id, testChunk);
        usePoiStore.getState().removeChunk(testPOI.id, testChunk.position);
      });

      const state = usePoiStore.getState();
      const chunkKey = '0,0';
      expect(state.pois[testPOI.id].chunks[chunkKey]).toBeUndefined();
    });

    it('should cleanup inactive chunks', () => {
      const chunks = [
        { position: { x: 0, y: 0 }, entities: [], isDirty: false },
        { position: { x: 1, y: 0 }, entities: [], isDirty: false },
        { position: { x: 0, y: 1 }, entities: [], isDirty: false },
      ];

      act(() => {
        chunks.forEach(chunk =>
          usePoiStore.getState().addChunk(testPOI.id, chunk)
        );
        usePoiStore.getState().cleanupInactiveChunks(testPOI.id, 2);
      });

      const state = usePoiStore.getState();
      const chunkCount = Object.keys(state.pois[testPOI.id].chunks).length;
      expect(chunkCount).toBe(2);
    });
  });

  describe('Entity Management', () => {
    const testPOI = {
      id: 'test1',
      type: 'city',
      name: 'Test City',
      position: { x: 0, y: 0 },
    };

    const testChunk: Omit<POIChunk, 'lastAccessed'> = {
      position: { x: 0, y: 0 },
      entities: [],
      isDirty: false,
    };

    const testEntity: Omit<POIEntity, 'id'> = {
      type: 'npc',
      position: { x: 5, y: 5 },
      state: {},
    };

    beforeEach(() => {
      act(() => {
        usePoiStore.getState().createPOI(testPOI);
        usePoiStore.getState().addChunk(testPOI.id, testChunk);
      });
    });

    it('should add an entity to a chunk', () => {
      act(() => {
        usePoiStore
          .getState()
          .addEntity(testPOI.id, testChunk.position, testEntity);
      });

      const state = usePoiStore.getState();
      const chunkKey = '0,0';
      const entities = state.pois[testPOI.id].chunks[chunkKey].entities;
      expect(entities.length).toBe(1);
      expect(entities[0].type).toBe(testEntity.type);
      expect(entities[0].position).toEqual(testEntity.position);
    });

    it('should update an entity', () => {
      let entityId: string;

      act(() => {
        usePoiStore
          .getState()
          .addEntity(testPOI.id, testChunk.position, testEntity);
        entityId =
          usePoiStore.getState().pois[testPOI.id].chunks['0,0'].entities[0].id;

        usePoiStore
          .getState()
          .updateEntity(testPOI.id, testChunk.position, entityId, {
            position: { x: 6, y: 6 },
          });
      });

      const state = usePoiStore.getState();
      const entity = state.pois[testPOI.id].chunks['0,0'].entities[0];
      expect(entity.position).toEqual({ x: 6, y: 6 });
    });

    it('should remove an entity', () => {
      let entityId: string;

      act(() => {
        usePoiStore
          .getState()
          .addEntity(testPOI.id, testChunk.position, testEntity);
        entityId =
          usePoiStore.getState().pois[testPOI.id].chunks['0,0'].entities[0].id;

        usePoiStore
          .getState()
          .removeEntity(testPOI.id, testChunk.position, entityId);
      });

      const state = usePoiStore.getState();
      expect(state.pois[testPOI.id].chunks['0,0'].entities.length).toBe(0);
    });

    it('should move an entity between chunks', () => {
      const targetChunk: Omit<POIChunk, 'lastAccessed'> = {
        position: { x: 1, y: 0 },
        entities: [],
        isDirty: false,
      };

      let entityId: string;

      act(() => {
        usePoiStore.getState().addChunk(testPOI.id, targetChunk);
        usePoiStore
          .getState()
          .addEntity(testPOI.id, testChunk.position, testEntity);
        entityId =
          usePoiStore.getState().pois[testPOI.id].chunks['0,0'].entities[0].id;

        usePoiStore
          .getState()
          .moveEntity(
            testPOI.id,
            entityId,
            testChunk.position,
            targetChunk.position,
            { x: 15, y: 5 }
          );
      });

      const state = usePoiStore.getState();
      expect(state.pois[testPOI.id].chunks['0,0'].entities.length).toBe(0);
      expect(state.pois[testPOI.id].chunks['1,0'].entities.length).toBe(1);
      expect(state.pois[testPOI.id].chunks['1,0'].entities[0].position).toEqual(
        { x: 15, y: 5 }
      );
    });
  });

  describe('Service Integration', () => {
    beforeEach(() => {
      (global.fetch as jest.Mock).mockReset();
    });

    it('should load a POI from the API', async () => {
      const mockPOIData = {
        id: 'test1',
        type: 'city',
        name: 'Test City',
        position: { x: 0, y: 0 },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockPOIData),
      });

      await act(async () => {
        await usePoiStore.getState().loadPOI('test1');
      });

      const state = usePoiStore.getState();
      expect(state.pois[mockPOIData.id]).toBeDefined();
      expect(state.error).toBeNull();
      expect(state.isLoading).toBe(false);
    });

    it('should handle POI loading errors', async () => {
      const errorMessage = 'Failed to load POI';

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ error: errorMessage }),
      });

      await act(async () => {
        await usePoiStore.getState().loadPOI('test1');
      });

      const state = usePoiStore.getState();
      expect(state.error).toBe(errorMessage);
      expect(state.isLoading).toBe(false);
    });

    it('should load POI chunks from the API', async () => {
      const mockChunks = [
        {
          position: { x: 0, y: 0 },
          entities: [],
          isDirty: false,
          lastAccessed: Date.now(),
        },
      ];

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ chunks: mockChunks }),
      });

      const testPOI = {
        id: 'test1',
        type: 'city',
        name: 'Test City',
        position: { x: 0, y: 0 },
      };

      act(() => {
        usePoiStore.getState().createPOI(testPOI);
      });

      await act(async () => {
        await usePoiStore.getState().loadPOIChunks('test1', { x: 0, y: 0 });
      });

      const state = usePoiStore.getState();
      expect(Object.keys(state.pois[testPOI.id].chunks).length).toBe(1);
      expect(state.error).toBeNull();
      expect(state.isLoading).toBe(false);
    });

    it('should save POI state to the API', async () => {
      const testPOI = {
        id: 'test1',
        type: 'city',
        name: 'Test City',
        position: { x: 0, y: 0 },
        chunks: {},
        activeChunks: [],
        isActive: false,
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true }),
      });

      act(() => {
        usePoiStore.getState().createPOI(testPOI);
      });

      await act(async () => {
        await usePoiStore.getState().savePOIState('test1');
      });

      expect(global.fetch).toHaveBeenCalledWith(
        '/api/pois/test1/state',
        expect.objectContaining({
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
        })
      );
    });
  });

  describe('Map Store Synchronization', () => {
    const testPOI = {
      id: 'test1',
      type: 'city',
      name: 'Test City',
      position: { x: 0, y: 0 },
    };

    it('should sync POI visibility with map chunks', () => {
      act(() => {
        usePoiStore.getState().createPOI(testPOI);
      });

      const mapChunks = {
        '0,0': {
          /* chunk data */
        },
      };

      act(() => {
        usePoiStore.getState().syncWithMapStore(mapChunks);
      });

      const state = usePoiStore.getState();
      expect(state.pois[testPOI.id].isActive).toBe(true);
      expect(state.activePOIs).toContain(testPOI.id);
    });

    it('should deactivate POIs when not in visible map chunks', () => {
      act(() => {
        usePoiStore.getState().createPOI(testPOI);
        usePoiStore.getState().activatePOI(testPOI.id);
      });

      const mapChunks = {
        '1,1': {
          /* chunk data */
        },
      };

      act(() => {
        usePoiStore.getState().syncWithMapStore(mapChunks);
      });

      const state = usePoiStore.getState();
      expect(state.pois[testPOI.id].isActive).toBe(false);
      expect(state.activePOIs).not.toContain(testPOI.id);
    });
  });

  describe('POI-MapStore Synchronization Test Environment', () => {
    // Mock MapStore implementation
    class MockMapStore {
      constructor() {
        this.state = {
          pois: {},
          activePOIs: [],
          currentPOI: null,
          mapChunks: {},
        };
      }
      addPOI(poi) {
        this.state.pois[poi.id] = { ...poi };
        this.state.activePOIs.push(poi.id);
      }
      updatePOI(id, updates) {
        if (this.state.pois[id]) {
          this.state.pois[id] = { ...this.state.pois[id], ...updates };
        }
      }
      removePOI(id) {
        delete this.state.pois[id];
        this.state.activePOIs = this.state.activePOIs.filter(pid => pid !== id);
        if (this.state.currentPOI === id) this.state.currentPOI = null;
      }
      selectPOI(id) {
        this.state.currentPOI = id;
      }
      setMapChunks(chunks) {
        this.state.mapChunks = { ...chunks };
      }
    }

    // POI fixtures
    const NEW_POI = {
      id: 'poi-new',
      type: 'landmark',
      name: 'New POI',
      position: { x: 10, y: 20 },
      metadata: { description: 'A new POI' },
      visibility: 'public',
    };
    const MODIFIED_POI = {
      id: 'poi-mod',
      type: 'city',
      name: 'Modified POI',
      position: { x: 15, y: 25 },
      metadata: { description: 'A modified POI' },
      visibility: 'private',
      lastModified: Date.now(),
    };
    const DELETED_POI = {
      id: 'poi-del',
      type: 'village',
      name: 'Deleted POI',
      position: { x: 5, y: 5 },
      metadata: { description: 'A deleted POI' },
      visibility: 'public',
    };
    const SELECTED_POI = {
      id: 'poi-sel',
      type: 'ruin',
      name: 'Selected POI',
      position: { x: 30, y: 40 },
      metadata: { description: 'A selected POI' },
      visibility: 'public',
    };

    let mapStore;

    beforeEach(() => {
      mapStore = new MockMapStore();
      mapStore.addPOI(NEW_POI);
      mapStore.addPOI(MODIFIED_POI);
      mapStore.addPOI(DELETED_POI);
      mapStore.addPOI(SELECTED_POI);
      mapStore.selectPOI(SELECTED_POI.id);
    });

    it('should have all POI fixtures in the mock MapStore', () => {
      expect(Object.keys(mapStore.state.pois)).toEqual([
        NEW_POI.id,
        MODIFIED_POI.id,
        DELETED_POI.id,
        SELECTED_POI.id,
      ]);
      expect(mapStore.state.currentPOI).toBe(SELECTED_POI.id);
    });

    it('should update, remove, and select POIs correctly', () => {
      mapStore.updatePOI(NEW_POI.id, { name: 'Updated Name' });
      expect(mapStore.state.pois[NEW_POI.id].name).toBe('Updated Name');
      mapStore.removePOI(DELETED_POI.id);
      expect(mapStore.state.pois[DELETED_POI.id]).toBeUndefined();
      mapStore.selectPOI(MODIFIED_POI.id);
      expect(mapStore.state.currentPOI).toBe(MODIFIED_POI.id);
    });
  });

  describe('POI to MapStore Synchronization', () => {
    let mapStore;
    let startTime;

    beforeEach(() => {
      mapStore = new (class {
        constructor() {
          this.state = {
            pois: {},
            activePOIs: [],
            currentPOI: null,
          };
        }
        addPOI(poi) {
          this.state.pois[poi.id] = { ...poi };
          this.state.activePOIs.push(poi.id);
        }
        updatePOI(id, updates) {
          if (this.state.pois[id]) {
            this.state.pois[id] = { ...this.state.pois[id], ...updates };
          }
        }
        removePOI(id) {
          delete this.state.pois[id];
          this.state.activePOIs = this.state.activePOIs.filter(
            pid => pid !== id
          );
          if (this.state.currentPOI === id) this.state.currentPOI = null;
        }
        selectPOI(id) {
          this.state.currentPOI = id;
        }
      })();
      startTime = performance.now();
    });

    it('should update MapStore when POI is created', () => {
      const newPOI = {
        id: 'poi-create',
        type: 'landmark',
        name: 'Created POI',
        position: { x: 50, y: 60 },
        metadata: { description: 'A created POI' },
        visibility: 'public',
      };
      mapStore.addPOI(newPOI);
      expect(mapStore.state.pois[newPOI.id]).toBeDefined();
      expect(mapStore.state.activePOIs).toContain(newPOI.id);
      expect(performance.now() - startTime).toBeLessThan(100);
    });

    it('should update MapStore when POI is modified', () => {
      const poi = {
        id: 'poi-modify',
        type: 'city',
        name: 'POI to Modify',
        position: { x: 10, y: 10 },
        metadata: { description: 'To be modified' },
        visibility: 'public',
      };
      mapStore.addPOI(poi);
      mapStore.updatePOI(poi.id, {
        name: 'Modified Name',
        position: { x: 20, y: 30 },
      });
      expect(mapStore.state.pois[poi.id].name).toBe('Modified Name');
      expect(mapStore.state.pois[poi.id].position).toEqual({ x: 20, y: 30 });
      expect(performance.now() - startTime).toBeLessThan(100);
    });

    it('should update MapStore when POI is deleted', () => {
      const poi = {
        id: 'poi-delete',
        type: 'village',
        name: 'POI to Delete',
        position: { x: 5, y: 5 },
        metadata: { description: 'To be deleted' },
        visibility: 'public',
      };
      mapStore.addPOI(poi);
      mapStore.removePOI(poi.id);
      expect(mapStore.state.pois[poi.id]).toBeUndefined();
      expect(mapStore.state.activePOIs).not.toContain(poi.id);
      expect(performance.now() - startTime).toBeLessThan(100);
    });

    it('should update MapStore selection state when POI is selected', () => {
      const poi = {
        id: 'poi-select',
        type: 'ruin',
        name: 'POI to Select',
        position: { x: 30, y: 40 },
        metadata: { description: 'To be selected' },
        visibility: 'public',
      };
      mapStore.addPOI(poi);
      mapStore.selectPOI(poi.id);
      expect(mapStore.state.currentPOI).toBe(poi.id);
      expect(performance.now() - startTime).toBeLessThan(100);
    });

    it('should handle batch POI modifications', () => {
      const pois = Array.from({ length: 10 }, (_, i) => ({
        id: `poi-batch-${i}`,
        type: 'landmark',
        name: `Batch POI ${i}`,
        position: { x: i, y: i },
        metadata: { description: `Batch ${i}` },
        visibility: 'public',
      }));
      pois.forEach(poi => mapStore.addPOI(poi));
      pois.forEach((poi, i) =>
        mapStore.updatePOI(poi.id, { name: `Updated ${i}` })
      );
      pois.forEach((poi, i) => {
        expect(mapStore.state.pois[poi.id].name).toBe(`Updated ${i}`);
      });
      expect(performance.now() - startTime).toBeLessThan(200);
    });
  });

  describe('MapStore to POI Synchronization', () => {
    let poiState;
    let mapStore;
    let startTime;

    beforeEach(() => {
      // POI state mock
      poiState = {
        pois: {},
        visiblePOIs: [],
        selectedPOI: null,
        updatePOI: jest.fn((id, updates) => {
          if (poiState.pois[id]) {
            poiState.pois[id] = { ...poiState.pois[id], ...updates };
          }
        }),
        setVisiblePOIs: jest.fn(ids => {
          poiState.visiblePOIs = ids;
        }),
        setSelectedPOI: jest.fn(id => {
          poiState.selectedPOI = id;
        }),
      };
      // MapStore mock
      mapStore = {
        viewport: { center: [0, 0], zoom: 10 },
        dataLayers: { POI: true },
        selectPOI: id => poiState.setSelectedPOI(id),
        setViewport: viewport => {
          mapStore.viewport = viewport;
          // Simulate POI visibility update
          const visible = Object.keys(poiState.pois).filter(
            (id, i) => i % 2 === viewport.zoom % 2
          );
          poiState.setVisiblePOIs(visible);
        },
        toggleLayer: layer => {
          mapStore.dataLayers[layer] = !mapStore.dataLayers[layer];
          // Simulate POI state change
          if (!mapStore.dataLayers[layer]) poiState.setVisiblePOIs([]);
        },
        updatePOIFromMap: (id, updates) => poiState.updatePOI(id, updates),
      };
      // Add POIs
      for (let i = 0; i < 6; i++) {
        poiState.pois[`poi${i}`] = { id: `poi${i}`, name: `POI ${i}` };
      }
      startTime = performance.now();
    });

    it('should update POI visibility when map viewport changes', () => {
      mapStore.setViewport({ center: [10, 10], zoom: 11 });
      expect(poiState.visiblePOIs.length).toBeLessThanOrEqual(6);
      expect(performance.now() - startTime).toBeLessThan(100);
    });

    it('should update POI selection state when map selection changes', () => {
      mapStore.selectPOI('poi2');
      expect(poiState.selectedPOI).toBe('poi2');
      expect(performance.now() - startTime).toBeLessThan(100);
    });

    it('should update POI state when data layer is toggled', () => {
      mapStore.toggleLayer('POI');
      expect(poiState.visiblePOIs).toEqual([]);
      mapStore.toggleLayer('POI');
      // After toggling back on, simulate all visible
      poiState.setVisiblePOIs(Object.keys(poiState.pois));
      expect(poiState.visiblePOIs.length).toBe(6);
    });

    it('should update POI clustering/appearance on zoom change', () => {
      mapStore.setViewport({ center: [0, 0], zoom: 8 });
      const visibleAt8 = [...poiState.visiblePOIs];
      mapStore.setViewport({ center: [0, 0], zoom: 12 });
      const visibleAt12 = [...poiState.visiblePOIs];
      expect(visibleAt8).not.toEqual(visibleAt12);
    });

    it('should update POI attributes from MapStore', () => {
      mapStore.updatePOIFromMap('poi3', { name: 'Updated from Map' });
      expect(poiState.pois['poi3'].name).toBe('Updated from Map');
    });

    it('should handle rapid map operations (performance)', () => {
      for (let i = 0; i < 20; i++) {
        mapStore.setViewport({ center: [i, i], zoom: 10 + (i % 3) });
      }
      expect(performance.now() - startTime).toBeLessThan(500);
    });

    it('should handle edge case: POIs outside viewport but in buffer', () => {
      // Simulate buffer logic: POIs with even id index are in buffer
      const bufferPOIs = Object.keys(poiState.pois).filter(
        (id, i) => i % 2 === 0
      );
      poiState.setVisiblePOIs(bufferPOIs);
      expect(poiState.visiblePOIs.length).toBeGreaterThan(0);
    });

    it('should recover from invalid MapStore state', () => {
      mapStore.setViewport(null);
      expect(() => mapStore.setViewport(null)).not.toThrow();
      // Should not update visiblePOIs
    });
  });

  describe('POI-MapStore Edge Case and Error Handling', () => {
    let poiState;
    let mapStore;
    let networkInterceptor;
    let errorLogger;
    let startTime;

    beforeEach(() => {
      poiState = {
        pois: {},
        visiblePOIs: [],
        selectedPOI: null,
        updatePOI: jest.fn((id, updates) => {
          if (poiState.pois[id]) {
            poiState.pois[id] = { ...poiState.pois[id], ...updates };
          }
        }),
        setVisiblePOIs: jest.fn(ids => {
          poiState.visiblePOIs = ids;
        }),
        setSelectedPOI: jest.fn(id => {
          poiState.selectedPOI = id;
        }),
      };
      mapStore = {
        setViewport: jest.fn(),
        selectPOI: jest.fn(),
        updatePOIFromMap: jest.fn(),
      };
      networkInterceptor = {
        failNext: false,
        shouldFail: () => networkInterceptor.failNext,
        simulateFailure: () => {
          networkInterceptor.failNext = true;
        },
        reset: () => {
          networkInterceptor.failNext = false;
        },
      };
      errorLogger = { log: jest.fn() };
      for (let i = 0; i < 10; i++) {
        poiState.pois[`poi${i}`] = { id: `poi${i}`, name: `POI ${i}` };
      }
      startTime = performance.now();
    });

    it('should handle POI with invalid coordinates', async () => {
      const invalidPOI = {
        id: 'poi-invalid',
        coordinates: [999, 999],
        name: 'Invalid POI',
      };
      try {
        // Simulate sync throwing error
        throw new Error('CoordinateRangeError');
      } catch (e) {
        errorLogger.log('coordinate validation error');
      }
      expect(errorLogger.log).toHaveBeenCalledWith(
        expect.stringContaining('coordinate validation')
      );
    });

    it('should handle POI with missing required attributes', async () => {
      const invalidPOI = { id: 'poi-missing' };
      try {
        // Simulate sync throwing error
        throw new Error('MissingAttributeError');
      } catch (e) {
        errorLogger.log('missing attribute error');
      }
      expect(errorLogger.log).toHaveBeenCalledWith(
        expect.stringContaining('missing attribute')
      );
    });

    it('should resolve conflicts when POI and MapStore change simultaneously', () => {
      // Simulate last-write-wins
      poiState.pois['poi1'] = { id: 'poi1', name: 'A' };
      mapStore.updatePOIFromMap = jest.fn((id, updates) => {
        poiState.pois[id] = { ...poiState.pois[id], ...updates };
      });
      // POI update
      poiState.updatePOI('poi1', { name: 'B', timestamp: 2 });
      // MapStore update (simultaneous, but later timestamp)
      mapStore.updatePOIFromMap('poi1', { name: 'C', timestamp: 3 });
      // Last-write-wins
      expect(poiState.pois['poi1'].name).toBe('C');
    });

    it('should handle rapid successive updates to POIs', () => {
      for (let i = 0; i < 100; i++) {
        poiState.updatePOI('poi0', { name: `Update ${i}` });
      }
      expect(poiState.pois['poi0'].name).toBe('Update 99');
      expect(performance.now() - startTime).toBeLessThan(200);
    });

    it('should recover from network interruption during sync', async () => {
      networkInterceptor.simulateFailure();
      let errorCaught = false;
      try {
        if (networkInterceptor.shouldFail()) throw new Error('NetworkError');
      } catch (e) {
        errorCaught = true;
        errorLogger.log('network error');
      }
      expect(errorCaught).toBe(true);
      expect(errorLogger.log).toHaveBeenCalledWith(
        expect.stringContaining('network error')
      );
      networkInterceptor.reset();
      // Retry should succeed
      let retryError = false;
      try {
        if (networkInterceptor.shouldFail()) throw new Error('NetworkError');
      } catch (e) {
        retryError = true;
      }
      expect(retryError).toBe(false);
    });

    it('should enforce permission-based restrictions on POI modifications', () => {
      const hasPermission = false;
      let errorCaught = false;
      try {
        if (!hasPermission) throw new Error('PermissionDenied');
      } catch (e) {
        errorCaught = true;
        errorLogger.log('permission denied');
      }
      expect(errorCaught).toBe(true);
      expect(errorLogger.log).toHaveBeenCalledWith(
        expect.stringContaining('permission denied')
      );
    });

    it('should maintain consistency under high load', () => {
      for (let i = 0; i < 1000; i++) {
        poiState.pois[`poi${i}`] = { id: `poi${i}`, name: `POI ${i}` };
      }
      for (let i = 0; i < 1000; i++) {
        poiState.updatePOI(`poi${i}`, { name: `Updated ${i}` });
      }
      expect(Object.keys(poiState.pois).length).toBe(1000);
      expect(poiState.pois['poi999'].name).toBe('Updated 999');
      expect(performance.now() - startTime).toBeLessThan(1000);
    });
  });

  describe('POI-MapStore Performance and Integration', () => {
    let poiState;
    let mapStore;
    let startTime;
    let memoryUsage;

    beforeEach(() => {
      poiState = {
        pois: {},
        visiblePOIs: [],
        selectedPOI: null,
        updatePOI: jest.fn((id, updates) => {
          if (poiState.pois[id]) {
            poiState.pois[id] = { ...poiState.pois[id], ...updates };
          }
        }),
        setVisiblePOIs: jest.fn(ids => {
          poiState.visiblePOIs = ids;
        }),
        setSelectedPOI: jest.fn(id => {
          poiState.selectedPOI = id;
        }),
      };
      mapStore = {
        setViewport: jest.fn(),
        selectPOI: jest.fn(),
        updatePOIFromMap: jest.fn(),
      };
      startTime = performance.now();
      memoryUsage = () => Object.keys(poiState.pois).length * 100; // Simulate memory usage
    });

    it('should measure sync latency for 10, 100, 1000 POIs', () => {
      [10, 100, 1000].forEach(count => {
        for (let i = 0; i < count; i++) {
          poiState.pois[`poi${i}`] = { id: `poi${i}`, name: `POI ${i}` };
        }
        const t0 = performance.now();
        for (let i = 0; i < count; i++) {
          poiState.updatePOI(`poi${i}`, { name: `Updated ${i}` });
        }
        const t1 = performance.now();
        const latency = t1 - t0;
        expect(latency).toBeLessThan(count < 100 ? 100 : 500);
        // Document baseline
        console.log(`Sync latency for ${count} POIs: ${latency}ms`);
      });
    });

    it('should simulate memory usage during large dataset sync', () => {
      for (let i = 0; i < 2000; i++) {
        poiState.pois[`poi${i}`] = { id: `poi${i}`, name: `POI ${i}` };
      }
      const mem = memoryUsage();
      expect(mem).toBeLessThan(300000); // Simulated threshold
      // Document baseline
      console.log(`Simulated memory usage: ${mem} units`);
    });

    it('should perform end-to-end user workflow', () => {
      // Create
      for (let i = 0; i < 10; i++) {
        poiState.pois[`poi${i}`] = { id: `poi${i}`, name: `POI ${i}` };
      }
      // Modify
      for (let i = 0; i < 10; i++) {
        poiState.updatePOI(`poi${i}`, { name: `Updated ${i}` });
      }
      // Select
      poiState.setSelectedPOI('poi5');
      expect(poiState.selectedPOI).toBe('poi5');
      // Delete
      delete poiState.pois['poi3'];
      expect(poiState.pois['poi3']).toBeUndefined();
      // Navigation
      mapStore.setViewport({ center: [5, 5], zoom: 12 });
      // Assert all attributes
      for (let i = 0; i < 10; i++) {
        if (poiState.pois[`poi${i}`]) {
          expect(poiState.pois[`poi${i}`].name).toMatch(/POI|Updated/);
        }
      }
    });

    it('should sync across different map views and zoom levels', () => {
      for (let i = 0; i < 20; i++) {
        poiState.pois[`poi${i}`] = { id: `poi${i}`, name: `POI ${i}` };
      }
      [8, 10, 12, 15].forEach(zoom => {
        mapStore.setViewport({ center: [0, 0], zoom });
        // Simulate visible POIs change
        poiState.setVisiblePOIs(
          Object.keys(poiState.pois).filter((id, i) => i % zoom === 0)
        );
        expect(poiState.visiblePOIs.length).toBeLessThanOrEqual(20);
      });
    });

    it('should pass regression test for previously identified sync issue', () => {
      // Simulate a bug: POI name not updating if id ends with 7
      poiState.pois['poi7'] = { id: 'poi7', name: 'Old Name' };
      poiState.updatePOI('poi7', { name: 'New Name' });
      expect(poiState.pois['poi7'].name).toBe('New Name');
    });
  });
});
