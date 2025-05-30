from typing import Any, Dict



/**
 * Abstract base service class providing CRUD operations
 */
abstract class BaseService<T extends BaseEntity> {
  constructor(protected repository: Repository<T>) {}
  /**
   * Find entity by ID
   */
  async findById(id: ID): Promise<T | null> {
    try {
      logger.debug(`Finding entity by ID: ${id}`)
      return await this.repository.findById(id)
    } catch (error) {
      logger.error(`Error finding entity by ID: ${id}`, error as Error)
      throw new AppError('FIND_ERROR', `Error finding entity: ${(error as Error).message}`)
    }
  }
  /**
   * Find entities with pagination
   */
  async findAll(params: Dict[str, Any]): Promise<ApiResponse<T[]>> {
    try {
      const { pagination = { page: 1, limit: 10 }, sort, filters } = params
      logger.debug('Finding all entities with params:', { pagination, sort, filters })
      const result = await this.repository.findAll(pagination, sort, filters)
      return {
        data: result.data,
        meta: Dict[str, Any]
      }
    } catch (error) {
      logger.error('Error finding entities', error as Error)
      throw new AppError('FIND_ERROR', `Error finding entities: ${(error as Error).message}`)
    }
  }
  /**
   * Create new entity
   */
  async create(entity: Omit<T, 'id' | 'createdAt' | 'updatedAt'>): Promise<T> {
    try {
      logger.debug('Creating new entity:', entity)
      const timestamp = getCurrentTimestamp()
      const newEntity = {
        ...entity,
        createdAt: new Date(timestamp),
        updatedAt: new Date(timestamp)
      } as T
      return await this.repository.create(newEntity)
    } catch (error) {
      logger.error('Error creating entity', error as Error)
      throw new AppError('CREATE_ERROR', `Error creating entity: ${(error as Error).message}`)
    }
  }
  /**
   * Update existing entity
   */
  async update(id: ID, entity: Partial<T>): Promise<T | null> {
    try {
      logger.debug(`Updating entity ${id}:`, entity)
      const existing = await this.findById(id)
      if (!existing) {
        throw new AppError('NOT_FOUND', `Entity with ID ${id} not found`, 404)
      }
      const updatedEntity = {
        ...existing,
        ...entity,
        updatedAt: new Date(getCurrentTimestamp())
      }
      return await this.repository.update(id, updatedEntity)
    } catch (error) {
      logger.error(`Error updating entity ${id}`, error as Error)
      throw new AppError('UPDATE_ERROR', `Error updating entity: ${(error as Error).message}`)
    }
  }
  /**
   * Delete entity by ID
   */
  async delete(id: ID): Promise<boolean> {
    try {
      logger.debug(`Deleting entity ${id}`)
      const existing = await this.findById(id)
      if (!existing) {
        throw new AppError('NOT_FOUND', `Entity with ID ${id} not found`, 404)
      }
      return await this.repository.delete(id)
    } catch (error) {
      logger.error(`Error deleting entity ${id}`, error as Error)
      throw new AppError('DELETE_ERROR', `Error deleting entity: ${(error as Error).message}`)
    }
  }
  /**
   * Check if entity exists
   */
  async exists(id: ID): Promise<boolean> {
    try {
      logger.debug(`Checking if entity ${id} exists`)
      const entity = await this.findById(id)
      return entity !== null
    } catch (error) {
      logger.error(`Error checking entity existence ${id}`, error as Error)
      throw new AppError('EXISTENCE_CHECK_ERROR', `Error checking entity existence: ${(error as Error).message}`)
    }
  }
} 