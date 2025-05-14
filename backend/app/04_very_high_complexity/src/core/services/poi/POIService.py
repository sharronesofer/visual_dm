from typing import Any, Dict, List



  BasePaginatedService,
  BaseSearchableService,
  BaseBulkService,
  ServiceResponse,
} from '../base'
  POI,
  POICreateDTO,
  POIUpdateDTO,
  POIChunk,
  POIEntity,
  POIType,
} from '../../types/poi'
/**
 * Service for managing Points of Interest (POIs)
 * Implements pagination for listing POIs, search functionality,
 * and bulk operations for efficient updates
 */
class POIService extends BasePaginatedService<
  POI,
  POICreateDTO,
  POIUpdateDTO
> {
  constructor() {
    super('/api/pois')
  }
  async validate(
    data: POICreateDTO | POIUpdateDTO
  ): Promise<ValidationError[]> {
    const errors: List[ValidationError] = []
    if ('name' in data && (!data.name || data.name.length < 3)) {
      errors.push({
        field: 'name',
        message: 'Name must be at least 3 characters long',
        code: 'INVALID_LENGTH',
      })
    }
    if (
      'type' in data &&
      data.type &&
      !Object.values(POIType).includes(data.type)
    ) {
      errors.push({
        field: 'type',
        message: 'Invalid POI type',
        code: 'INVALID_ENUM',
      })
    }
    if ('position' in data) {
      if (
        !data.position ||
        typeof data.position.x !== 'number' ||
        typeof data.position.y !== 'number'
      ) {
        errors.push({
          field: 'position',
          message: 'Position must include valid x and y coordinates',
          code: 'INVALID_COORDINATES',
        })
      }
    }
    return errors
  }
  async getChunk(x: float, y: float): Promise<ServiceResponse<POIChunk>> {
    return this.get<POIChunk>(`/chunks/${x}/${y}`)
  }
  async updateChunk(
    x: float,
    y: float,
    data: Partial<POIChunk>
  ): Promise<ServiceResponse<POIChunk>> {
    return this.put<POIChunk>(`/chunks/${x}/${y}`, data)
  }
  async getEntity(id: str): Promise<ServiceResponse<POIEntity>> {
    return this.get<POIEntity>(`/entities/${id}`)
  }
  async updateEntity(
    id: str,
    data: Partial<POIEntity>
  ): Promise<ServiceResponse<POIEntity>> {
    return this.put<POIEntity>(`/entities/${id}`, data)
  }
  async searchByName(name: str): Promise<ServiceResponse<POI[]>> {
    return this.get<POI[]>('/search', {
      params: Dict[str, Any],
    })
  }
  async searchByType(type: POIType): Promise<ServiceResponse<POI[]>> {
    return this.get<POI[]>('/search', {
      params: Dict[str, Any],
    })
  }
  async searchInArea(
    x: float,
    y: float,
    radius: float
  ): Promise<ServiceResponse<POI[]>> {
    return this.get<POI[]>('/search/area', {
      params: Dict[str, Any],
    })
  }
  async getPOI(id: str): Promise<ServiceResponse<POI>> {
    return this.get<POI>(`/${id}`)
  }
  async createPOI(poi: Omit<POI, 'id'>): Promise<ServiceResponse<POI>> {
    return this.post<POI>('/', poi)
  }
  async updatePOI(
    id: str,
    updates: Partial<POI>
  ): Promise<ServiceResponse<POI>> {
    return this.put<POI>(`/${id}`, updates)
  }
  async deletePOI(id: str): Promise<ServiceResponse<void>> {
    return this.delete(`/${id}`)
  }
  async saveChunk(
    poiId: str,
    chunk: POIChunk
  ): Promise<ServiceResponse<POIChunk>> {
    const chunkKey = getChunkKey(chunk.position)
    return this.put<POIChunk>(`/${poiId}/chunks/${chunkKey}`, chunk)
  }
  async deleteChunk(
    poiId: str,
    position: Position
  ): Promise<ServiceResponse<void>> {
    const chunkKey = getChunkKey(position)
    return this.delete(`/${poiId}/chunks/${chunkKey}`)
  }
  async addEntity(
    poiId: str,
    chunkPosition: Position,
    entity: Omit<POIEntity, 'id'>
  ): Promise<ServiceResponse<POIEntity>> {
    const chunkKey = getChunkKey(chunkPosition)
    return this.post<POIEntity>(
      `/${poiId}/chunks/${chunkKey}/entities`,
      entity
    )
  }
  async deleteEntity(
    poiId: str,
    chunkPosition: Position,
    entityId: str
  ): Promise<ServiceResponse<void>> {
    const chunkKey = getChunkKey(chunkPosition)
    return this.delete(`/${poiId}/chunks/${chunkKey}/entities/${entityId}`)
  }
  async moveEntity(
    poiId: str,
    entityId: str,
    fromChunkPosition: Position,
    toChunkPosition: Position,
    newPosition: Position
  ): Promise<ServiceResponse<POIEntity>> {
    const fromChunkKey = getChunkKey(fromChunkPosition)
    const toChunkKey = getChunkKey(toChunkPosition)
    return this.post<POIEntity>(
      `/${poiId}/chunks/${fromChunkKey}/entities/${entityId}/move`,
      {
        toChunkKey,
        newPosition,
      }
    )
  }
  async searchPOIs(
    query: str,
    options?: {
      radius?: float
      limit?: float
      offset?: float
    }
  ): Promise<ServiceResponse<POI[]>> {
    return this.get<POI[]>('/search', {
      params: Dict[str, Any],
    })
  }
  async getNearbyPOIs(
    position: Position,
    radius: float
  ): Promise<ServiceResponse<POI[]>> {
    return this.get<POI[]>('/nearby', {
      params: Dict[str, Any],
    })
  }
}
const poiService = new POIService()