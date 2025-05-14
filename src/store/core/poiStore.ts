import { create } from 'zustand';
import { Position } from '../../types/common';
import type {
  POI,
  POIState,
  POIServiceResponse,
  POIEntity,
  POIChunk,
} from '../../types/poi';
import { getChunkKey } from '../../utils/poiUtils';
import { createPersistence } from '../utils/persistence';
import { createValidator } from '../utils/validation';

// Create persistence handler
const persistence = createPersistence({
  prefix: 'vdm_poi_',
  debounceTime: 1000,
  version: 1,
});

// Create validator
const validator = createValidator<POI>();

// Add validation rules
validator.addFieldValidation({
  field: 'name',
  rules: [
    validator.rules.required('POI name is required'),
    validator.rules.minLength(2, 'Name must be at least 2 characters'),
    validator.rules.maxLength(50, 'Name must be at most 50 characters'),
  ],
});

validator.addFieldValidation({
  field: 'type',
  rules: [validator.rules.required('POI type is required')],
});

validator.addFieldValidation({
  field: 'position',
  rules: [
    validator.rules.required('POI position is required'),
    validator.rules.custom<Position>(
      value => value.x != null && value.y != null,
      'Position must have x and y coordinates',
      'INVALID_POSITION'
    ),
  ],
});

// Add service integration types
interface POILoadOptions {
  includeChunks?: boolean;
  chunkRadius?: number;
}

// Create the store
export const usePoiStore = create<POIState>()((set, get) => ({
  // State
  pois: {},
  activePOIs: [],
  currentPOI: null,
  playerPosition: null,
  error: null,
  isLoading: false,

  // Selectors
  getPOI: (id: string) => get().pois[id],
  getActivePOIs: () => get().activePOIs.map(id => get().pois[id]),
  getCurrentPOI: () => {
    const currentId = get().currentPOI;
    return currentId ? get().pois[currentId] : null;
  },

  // Error handling
  setError: (error: string | null) => set({ error }),
  clearError: () => set({ error: null }),

  // Loading state
  setLoading: (isLoading: boolean) => set({ isLoading }),

  // POI Management Functions
  createPOI: async (poi: Omit<POI, 'chunks' | 'activeChunks' | 'isActive'>) => {
    set({ isLoading: true, error: null });
    try {
      // Validate POI data
      const validation = await validator.validateState(poi as POI);
      if (!validation.isValid) {
        set({ error: validation.errors[0].message });
        return;
      }

      const newPOI = {
        ...poi,
        chunks: {},
        activeChunks: [],
        isActive: false,
      };

      set(state => ({
        pois: {
          ...state.pois,
          [poi.id]: newPOI,
        },
      }));

      await persistence.saveState('pois', get().pois);
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to create POI',
      });
    } finally {
      set({ isLoading: false });
    }
  },

  updatePOI: async (id: string, updates: Partial<POI>) => {
    set({ isLoading: true, error: null });
    try {
      const poi = get().pois[id];
      if (!poi) {
        throw new Error('POI not found');
      }

      const updatedPOI = { ...poi, ...updates };

      // Validate updated POI
      const validation = await validator.validateState(updatedPOI);
      if (!validation.isValid) {
        set({ error: validation.errors[0].message });
        return;
      }

      set(state => ({
        pois: {
          ...state.pois,
          [id]: updatedPOI,
        },
      }));

      await persistence.saveState('pois', get().pois);
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to update POI',
      });
    } finally {
      set({ isLoading: false });
    }
  },

  removePOI: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      set(state => {
        const { [id]: removed, ...pois } = state.pois;
        return {
          pois,
          activePOIs: state.activePOIs.filter(poiId => poiId !== id),
          currentPOI: state.currentPOI === id ? null : state.currentPOI,
        };
      });

      await persistence.saveState('pois', get().pois);
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to remove POI',
      });
    } finally {
      set({ isLoading: false });
    }
  },

  activatePOI: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const poi = get().pois[id];
      if (!poi) {
        throw new Error('POI not found');
      }

      set(state => ({
        pois: {
          ...state.pois,
          [id]: { ...poi, isActive: true },
        },
        activePOIs: state.activePOIs.includes(id)
          ? state.activePOIs
          : [...state.activePOIs, id],
      }));

      await persistence.saveState('pois', get().pois);
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : 'Failed to activate POI',
      });
    } finally {
      set({ isLoading: false });
    }
  },

  deactivatePOI: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const poi = get().pois[id];
      if (!poi) {
        throw new Error('POI not found');
      }

      set(state => ({
        pois: {
          ...state.pois,
          [id]: { ...poi, isActive: false, activeChunks: [] },
        },
        activePOIs: state.activePOIs.filter(poiId => poiId !== id),
        currentPOI: state.currentPOI === id ? null : state.currentPOI,
      }));

      await persistence.saveState('pois', get().pois);
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : 'Failed to deactivate POI',
      });
    } finally {
      set({ isLoading: false });
    }
  },

  setCurrentPOI: async (id: string | null) => {
    set({ isLoading: true, error: null });
    try {
      if (id && !get().pois[id]) {
        throw new Error('POI not found');
      }

      set({ currentPOI: id });
      await persistence.saveState('pois', get().pois);
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : 'Failed to set current POI',
      });
    } finally {
      set({ isLoading: false });
    }
  },

  updatePlayerPosition: async (position: Position) => {
    set({ isLoading: true, error: null });
    try {
      if (!get().currentPOI) {
        throw new Error('No POI selected');
      }

      const poi = get().pois[get().currentPOI];
      set(state => ({
        pois: {
          ...state.pois,
          [state.currentPOI!]: { ...poi, position },
        },
      }));

      await persistence.saveState('pois', get().pois);
    } catch (error) {
      set({
        error:
          error instanceof Error
            ? error.message
            : 'Failed to update player position',
      });
    } finally {
      set({ isLoading: false });
    }
  },

  // Chunk Management Functions
  addChunk: async (poiId: string, chunk: Omit<POIChunk, 'lastAccessed'>) => {
    set({ isLoading: true, error: null });
    try {
      const poi = get().pois[poiId];
      if (!poi) {
        throw new Error('POI not found');
      }

      const chunkKey = getChunkKey(chunk.position);
      set(state => ({
        pois: {
          ...state.pois,
          [poiId]: {
            ...poi,
            chunks: {
              ...poi.chunks,
              [chunkKey]: {
                ...chunk,
                lastAccessed: Date.now(),
              },
            },
          },
        },
      }));

      await persistence.saveState('pois', get().pois);
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to add chunk',
      });
    } finally {
      set({ isLoading: false });
    }
  },

  activateChunk: async (poiId: string, position: Position) => {
    set({ isLoading: true, error: null });
    try {
      const poi = get().pois[poiId];
      if (!poi) {
        throw new Error('POI not found');
      }

      const chunkKey = getChunkKey(position);
      if (!poi.chunks[chunkKey]) {
        throw new Error('Chunk not found');
      }

      if (!poi.activeChunks.includes(chunkKey)) {
        set(state => ({
          pois: {
            ...state.pois,
            [poiId]: {
              ...poi,
              activeChunks: [...poi.activeChunks, chunkKey],
            },
          },
        }));

        await persistence.saveState('pois', get().pois);
      }
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : 'Failed to activate chunk',
      });
    } finally {
      set({ isLoading: false });
    }
  },

  deactivateChunk: async (poiId: string, position: Position) => {
    set({ isLoading: true, error: null });
    try {
      const poi = get().pois[poiId];
      if (!poi) {
        throw new Error('POI not found');
      }

      const chunkKey = getChunkKey(position);
      set(state => ({
        pois: {
          ...state.pois,
          [poiId]: {
            ...poi,
            activeChunks: poi.activeChunks.filter(key => key !== chunkKey),
          },
        },
      }));

      await persistence.saveState('pois', get().pois);
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : 'Failed to deactivate chunk',
      });
    } finally {
      set({ isLoading: false });
    }
  },

  removeChunk: async (poiId: string, position: Position) => {
    set({ isLoading: true, error: null });
    try {
      const poi = get().pois[poiId];
      if (!poi) {
        throw new Error('POI not found');
      }

      const chunkKey = getChunkKey(position);
      const { [chunkKey]: removed, ...chunks } = poi.chunks;

      set(state => ({
        pois: {
          ...state.pois,
          [poiId]: {
            ...poi,
            chunks,
            activeChunks: poi.activeChunks.filter(key => key !== chunkKey),
          },
        },
      }));

      await persistence.saveState('pois', get().pois);
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : 'Failed to remove chunk',
      });
    } finally {
      set({ isLoading: false });
    }
  },

  cleanupInactiveChunks: async (poiId: string, maxChunks?: number) => {
    set({ isLoading: true, error: null });
    try {
      const poi = get().pois[poiId];
      if (!poi) {
        throw new Error('POI not found');
      }

      const sortedChunks = Object.entries(poi.chunks)
        .sort(([, a], [, b]) => b.lastAccessed - a.lastAccessed)
        .slice(0, maxChunks || 100);

      set(state => ({
        pois: {
          ...state.pois,
          [poiId]: {
            ...poi,
            chunks: Object.fromEntries(sortedChunks),
            activeChunks: poi.activeChunks.filter(key =>
              sortedChunks.some(([k]) => k === key)
            ),
          },
        },
      }));

      await persistence.saveState('pois', get().pois);
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : 'Failed to cleanup chunks',
      });
    } finally {
      set({ isLoading: false });
    }
  },

  // Entity Management Functions
  addEntity: async (
    poiId: string,
    chunkPosition: Position,
    entity: Omit<POIEntity, 'id'>
  ) => {
    set({ isLoading: true, error: null });
    try {
      const poi = get().pois[poiId];
      if (!poi) {
        throw new Error('POI not found');
      }

      const chunkKey = getChunkKey(chunkPosition);
      const chunk = poi.chunks[chunkKey];
      if (!chunk) {
        throw new Error('Chunk not found');
      }

      const entityId = crypto.randomUUID();
      set(state => ({
        pois: {
          ...state.pois,
          [poiId]: {
            ...poi,
            chunks: {
              ...poi.chunks,
              [chunkKey]: {
                ...chunk,
                entities: [...chunk.entities, { ...entity, id: entityId }],
                lastAccessed: Date.now(),
                isDirty: true,
              },
            },
          },
        },
      }));

      await persistence.saveState('pois', get().pois);
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to add entity',
      });
    } finally {
      set({ isLoading: false });
    }
  },

  updateEntity: async (
    poiId: string,
    chunkPosition: Position,
    entityId: string,
    updates: Partial<POIEntity>
  ) => {
    set({ isLoading: true, error: null });
    try {
      const poi = get().pois[poiId];
      if (!poi) {
        throw new Error('POI not found');
      }

      const chunkKey = getChunkKey(chunkPosition);
      const chunk = poi.chunks[chunkKey];
      if (!chunk) {
        throw new Error('Chunk not found');
      }

      set(state => ({
        pois: {
          ...state.pois,
          [poiId]: {
            ...poi,
            chunks: {
              ...poi.chunks,
              [chunkKey]: {
                ...chunk,
                entities: chunk.entities.map(entity => {
                  if (entity.id === entityId) {
                    // Deep merge properties if present
                    if (updates.properties) {
                      return {
                        ...entity,
                        ...updates,
                        properties: {
                          ...entity.properties,
                          ...updates.properties,
                        },
                      };
                    }
                    return { ...entity, ...updates };
                  }
                  return entity;
                }),
                lastAccessed: Date.now(),
                isDirty: true,
              },
            },
          },
        },
      }));

      await persistence.saveState('pois', get().pois);
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : 'Failed to update entity',
      });
    } finally {
      set({ isLoading: false });
    }
  },

  removeEntity: async (
    poiId: string,
    chunkPosition: Position,
    entityId: string
  ) => {
    set({ isLoading: true, error: null });
    try {
      const poi = get().pois[poiId];
      if (!poi) {
        throw new Error('POI not found');
      }

      const chunkKey = getChunkKey(chunkPosition);
      const chunk = poi.chunks[chunkKey];
      if (!chunk) {
        throw new Error('Chunk not found');
      }

      set(state => ({
        pois: {
          ...state.pois,
          [poiId]: {
            ...poi,
            chunks: {
              ...poi.chunks,
              [chunkKey]: {
                ...chunk,
                entities: chunk.entities.filter(
                  entity => entity.id !== entityId
                ),
                lastAccessed: Date.now(),
                isDirty: true,
              },
            },
          },
        },
      }));

      await persistence.saveState('pois', get().pois);
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : 'Failed to remove entity',
      });
    } finally {
      set({ isLoading: false });
    }
  },

  moveEntity: async (
    poiId: string,
    entityId: string,
    fromChunkPosition: Position,
    toChunkPosition: Position,
    newPosition: Position
  ) => {
    set({ isLoading: true, error: null });
    try {
      const poi = get().pois[poiId];
      if (!poi) {
        throw new Error('POI not found');
      }

      const fromChunkKey = getChunkKey(fromChunkPosition);
      const toChunkKey = getChunkKey(toChunkPosition);
      const fromChunk = poi.chunks[fromChunkKey];
      const toChunk = poi.chunks[toChunkKey];

      if (!fromChunk || !toChunk) {
        throw new Error('Source or target chunk not found');
      }

      const entity = fromChunk.entities.find(e => e.id === entityId);
      if (!entity) {
        throw new Error('Entity not found');
      }

      const updatedEntity = { ...entity, position: newPosition };

      set(state => ({
        pois: {
          ...state.pois,
          [poiId]: {
            ...poi,
            chunks: {
              ...poi.chunks,
              [fromChunkKey]: {
                ...fromChunk,
                entities: fromChunk.entities.filter(e => e.id !== entityId),
                lastAccessed: Date.now(),
                isDirty: true,
              },
              [toChunkKey]: {
                ...toChunk,
                entities: [...toChunk.entities, updatedEntity],
                lastAccessed: Date.now(),
                isDirty: true,
              },
            },
          },
        },
      }));

      await persistence.saveState('pois', get().pois);
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to move entity',
      });
    } finally {
      set({ isLoading: false });
    }
  },

  // Service Integration Functions
  loadPOI: async (
    id: string,
    options: POILoadOptions = {}
  ): Promise<POIServiceResponse> => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch(`/api/pois/${id}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to load POI');
      }

      set(state => ({
        pois: {
          ...state.pois,
          [id]: {
            ...data,
            chunks: options.includeChunks ? data.chunks : {},
            activeChunks: [],
            isActive: false,
          },
        },
      }));

      return { success: true, data };
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to load POI';
      set({ error: errorMessage });
      return { success: false, error: errorMessage };
    } finally {
      set({ isLoading: false });
    }
  },

  savePOIState: async (poiId: string): Promise<POIServiceResponse> => {
    set({ isLoading: true, error: null });
    try {
      const poi = get().pois[poiId];
      if (!poi) {
        throw new Error('POI not found');
      }

      const response = await fetch(`/api/pois/${poiId}/state`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          chunks: poi.chunks,
          activeChunks: poi.activeChunks,
          isActive: poi.isActive,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Failed to save POI state');
      }

      return { success: true, data };
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to save POI state';
      set({ error: errorMessage });
      return { success: false, error: errorMessage };
    } finally {
      set({ isLoading: false });
    }
  },

  syncWithMapStore: (mapChunks: Record<string, any>) => {
    set(state => {
      const updatedPOIs = { ...state.pois };

      // Update POI visibility based on map chunks
      Object.entries(state.pois).forEach(([poiId, poi]) => {
        const poiChunkKey = getChunkKey(poi.position);
        const isVisible = poiChunkKey in mapChunks;

        if (isVisible !== poi.isActive) {
          updatedPOIs[poiId] = {
            ...poi,
            isActive: isVisible,
            activeChunks: isVisible ? poi.activeChunks : [],
          };
        }
      });

      return {
        pois: updatedPOIs,
        activePOIs: Object.entries(updatedPOIs)
          .filter(([, poi]) => poi.isActive)
          .map(([id]) => id),
      };
    });
  },

  // Initialize state from persistence
  initializeFromStorage: async () => {
    set({ isLoading: true, error: null });
    try {
      const state = await persistence.getStoredState('pois');
      if (state) {
        set(state => ({
          ...state,
          ...state,
        }));
      }
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to load state',
      });
    } finally {
      set({ isLoading: false });
    }
  },
}));
