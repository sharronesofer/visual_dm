from typing import Any, List


  POIType,
  POIMetadata,
  POILayout,
  POIEntity,
  POIChunk,
  POIServiceResponse,
  POILoadOptions,
  POIEntityState,
  POI,
  POICreateDTO,
  POIUpdateDTO
} from '../types/poi'
  ExtendedBaseEntity, 
  ServiceResponseType,
  SuccessResponse,
  ErrorResponse,
  ServiceOperation,
  adaptServiceResponse,
  createErrorResponse 
} from './adapters/types'
class POIServiceConfig:
    chunkSize: float
    maxCachedChunks: float
    autoSaveInterval: float
const DEFAULT_CONFIG: \'POIServiceConfig\' = {
  baseURL: '/api/pois',
  chunkSize: 16,
  maxCachedChunks: 64,
  autoSaveInterval: 60000, 
  timeout: 5000,
  headers: {},
}
/**
 * Service class for managing Points of Interest (POIs)
 * Handles data operations, chunk management, and state synchronization
 */
class POIService extends ServiceAdapter<POI & ExtendedBaseEntity, POICreateDTO, POIUpdateDTO> {
  private config: \'POIServiceConfig\'
  private autoSaveTimer?: NodeJS.Timeout
  private chunkManager: POIChunkManager
  constructor(config: Partial<POIServiceConfig> = {}) {
    const mergedConfig = { ...DEFAULT_CONFIG, ...config }
    super('pois', mergedConfig)
    this.config = mergedConfig
    this.chunkManager = new POIChunkManager((endpoint: str, options?: RequestInit) => {
      return this.getResource(endpoint, options as ServiceConfig)
    }, {
      chunkSize: this.config.chunkSize,
      maxCachedChunks: this.config.maxCachedChunks,
      saveInterval: this.config.autoSaveInterval,
    })
    this.startAutoSave()
  }
  public async validate(data: POICreateDTO | POIUpdateDTO): Promise<ValidationError[]> {
    const errors: List[ValidationError] = []
    if ('name' in data && data.name !== undefined) {
      if (typeof data.name !== 'string' || data.name.length < 2) {
        errors.push({ field: 'name', message: 'Name must be at least 2 characters long' })
      }
    }
    if ('type' in data && data.type !== undefined) {
      if (!Object.values(POIType).includes(data.type)) {
        errors.push({ field: 'type', message: 'Invalid POI type' })
      }
    }
    if ('position' in data && data.position !== undefined) {
      if (typeof data.position.x !== 'number' || typeof data.position.y !== 'number') {
        errors.push({ field: 'position', message: 'Position must include valid x and y coordinates' })
      }
    }
    return errors
  }
  public async validateField(field: keyof (POICreateDTO | POIUpdateDTO), value: unknown): Promise<ValidationError[]> {
    const data = { [field]: value } as POICreateDTO | POIUpdateDTO
    return this.validate(data)
  }
  protected override async adaptServiceResponse<R>(
    operation: () => Promise<BaseServiceResponse<R>>
  ): Promise<ServiceResponseType<R>> {
    const response = await operation()
    const store = usePoiStore.getState()
    if (response.data && typeof response.data === 'object' && 'id' in response.data && 'type' in response.data) {
      const data = response.data as unknown as POI
      const poiData: Partial<POI> = {
        id: data.id,
        type: data.type,
        name: data.name,
        position: data.position,
        size: data.size,
        theme: data.theme,
        coordinates: [data.position.x, data.position.y],
        state: 'inactive',
        regionId: data.regionId || 'default',
        createdAt: new Date(data.createdAt),
        updatedAt: new Date(data.updatedAt),
        description: data.description,
      }
      if (data.id) {
        store.updatePOI(data.id, poiData)
      } else {
        store.createPOI(poiData as Omit<POI, 'chunks'>)
      }
    }
    return adaptServiceResponse(response)
  }
  async saveChunkState(poiId: str, chunkPosition: Position): Promise<ServiceResponseType<void>> {
    try {
      const response = await this.chunkManager.saveChunk(poiId, chunkPosition)
      if (response.success) {
        return {
          success: true,
          data: undefined,
          meta: response.meta
        }
      }
      return createErrorResponse(
        new ServiceError('SAVE_CHUNK_ERROR', response.error || 'Failed to save chunk')
      )
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save chunk state'
      return createErrorResponse(
        new ServiceError('SAVE_CHUNK_ERROR', errorMessage)
      )
    }
  }
  private startAutoSave(): void {
    if (this.autoSaveTimer) {
      clearInterval(this.autoSaveTimer)
    }
    this.autoSaveTimer = setInterval(() => {
      this.chunkManager.saveAllChunks().catch(error => {
        console.error('Auto-save failed:', error)
      })
    }, this.config.autoSaveInterval)
  }
  async loadPOIChunks(
    poiId: str,
    centerPosition: Position,
    radius: float
  ): Promise<POIServiceResponse<POIChunk[]>> {
    try {
      const response = await this.chunkManager.loadChunksInRadius(poiId, centerPosition, radius)
      if (response.success) {
        const store = usePoiStore.getState()
        const loadedChunks = this.chunkManager.getLoadedChunks(poiId)
        loadedChunks.forEach(chunk => {
          store.addChunk(poiId, chunk)
        })
        store.cleanupInactiveChunks(poiId, this.config.maxCachedChunks)
        return {
          success: true,
          data: loadedChunks
        }
      }
      return {
        success: false,
        error: response.error || 'Failed to load chunks'
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load POI chunks'
      usePoiStore.getState().setError(errorMessage)
      return { success: false, error: errorMessage }
    }
  }
  async addEntity(
    poiId: str,
    chunkPosition: Position,
    entity: Omit<POIEntity, 'id'>
  ): Promise<POIServiceResponse<POIEntity>> {
    try {
      if (!this.chunkManager.isChunkLoaded(poiId, chunkPosition)) {
        await this.loadPOIChunks(poiId, chunkPosition, 1)
      }
      const response = await this.getResource<POIEntity>(
        `/${poiId}/chunks/${chunkPosition.x},${chunkPosition.y}/entities`,
        {
          method: 'POST',
          body: JSON.stringify(entity),
        }
      )
      if (response) {
        const store = usePoiStore.getState()
        store.addEntity(poiId, chunkPosition, response)
      }
      return { success: true, data: response }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to add entity'
      usePoiStore.getState().setError(errorMessage)
      return { success: false, error: errorMessage }
    }
  }
  async updateEntity(
    poiId: str,
    chunkPosition: Position,
    entityId: str,
    updates: Partial<POIEntity>
  ): Promise<POIServiceResponse<POIEntity>> {
    try {
      const response = await this.getResource<POIEntity>(
        `/${poiId}/chunks/${chunkPosition.x},${chunkPosition.y}/entities/${entityId}`,
        {
          method: 'PATCH',
          body: JSON.stringify(updates),
        }
      )
      usePoiStore.getState().updateEntity(poiId, chunkPosition, entityId, updates)
      return { success: true, data: response }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update entity'
      usePoiStore.getState().setError(errorMessage)
      return { success: false, error: errorMessage }
    }
  }
  async removeEntity(
    poiId: str,
    chunkPosition: Position,
    entityId: str
  ): Promise<POIServiceResponse<void>> {
    try {
      await this.getResource(
        `/${poiId}/chunks/${chunkPosition.x},${chunkPosition.y}/entities/${entityId}`,
        { method: 'DELETE' }
      )
      usePoiStore.getState().removeEntity(poiId, chunkPosition, entityId)
      return { success: true }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to remove entity'
      usePoiStore.getState().setError(errorMessage)
      return { success: false, error: errorMessage }
    }
  }
  async moveEntity(
    poiId: str,
    entityId: str,
    fromChunkPosition: Position,
    toChunkPosition: Position,
    newPosition: Position
  ): Promise<POIServiceResponse<POIEntity>> {
    try {
      await Promise.all([
        this.chunkManager.loadChunk(poiId, fromChunkPosition),
        this.chunkManager.loadChunk(poiId, toChunkPosition),
      ])
      const response = await this.getResource<POIEntity>(
        `/${poiId}/chunks/${fromChunkPosition.x},${fromChunkPosition.y}/entities/${entityId}/move`,
        {
          method: 'POST',
          body: JSON.stringify({
            toChunk: toChunkPosition,
            position: newPosition,
          }),
        }
      )
      usePoiStore
        .getState()
        .moveEntity(poiId, entityId, fromChunkPosition, toChunkPosition, newPosition)
      const fromChunk = this.chunkManager
        .getLoadedChunks(poiId)
        .find(c => c.position.x === fromChunkPosition.x && c.position.y === fromChunkPosition.y)
      const toChunk = this.chunkManager
        .getLoadedChunks(poiId)
        .find(c => c.position.x === toChunkPosition.x && c.position.y === toChunkPosition.y)
      if (fromChunk) {
        const updatedFromEntities: Record<string, POIEntity> = {
          ...fromChunk.entities,
        }
        delete updatedFromEntities[entityId]
        this.chunkManager.updateChunk(poiId, fromChunkPosition, {
          entities: updatedFromEntities,
        })
      }
      if (toChunk) {
        const updatedToEntities: Record<string, POIEntity> = {
          ...toChunk.entities,
          [entityId]: { ...response, position: newPosition },
        }
        this.chunkManager.updateChunk(poiId, toChunkPosition, {
          entities: updatedToEntities,
        })
      }
      return { success: true, data: response }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to move entity'
      usePoiStore.getState().setError(errorMessage)
      return { success: false, error: errorMessage }
    }
  }
  async savePOIState(poiId: str): Promise<POIServiceResponse<void>> {
    try {
      const poi = usePoiStore.getState().getPOI(poiId)
      if (!poi) throw new Error('POI not found')
      const dirtyChunks = this.chunkManager.getDirtyChunks(poiId)
      await Promise.all(
        dirtyChunks.map(chunk => this.chunkManager.saveChunk(poiId, chunk.position))
      )
      await this.getResource(`/${poiId}/state`, {
        method: 'PUT',
        body: JSON.stringify({
          chunks: poi.chunks,
          activeChunks: poi.activeChunks,
          isActive: poi.isActive,
        }),
      })
      return { success: true }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save POI state'
      usePoiStore.getState().setError(errorMessage)
      return { success: false, error: errorMessage }
    }
  }
  syncWithMapStore(mapChunks: Record<string, any>): void {
    usePoiStore.getState().syncWithMapStore(mapChunks)
  }
  dispose(): void {
    if (this.autoSaveTimer) {
      clearInterval(this.autoSaveTimer)
    }
    this.chunkManager.dispose()
  }
}