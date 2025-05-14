from typing import Any, Dict, List


/**
 * Interface for services that support caching operations
 */
class ICacheableService:
    /**
   * Clear the cache for this service
   * @param pattern Optional pattern to match specific cache keys
   */
  clearCache(pattern?: str): Awaitable[None>
    /**
   * Generate a cache key for a specific operation
   * @param method The method name
   * @param params Optional parameters to include in the key
   */
  getCacheKey(method: str, params?: Any[]): str
    /**
   * Configure caching behavior
   * @param config Cache configuration options
   */
  setCacheConfig(config: Dict[str, Any]
/**
 * Interface for services that support pagination
 */
interface IPaginatedService<T extends BaseEntity> {
  /**
   * Get a paginated list of entities
   * @param page The page number (1-based)
   * @param limit The number of items per page
   * @param params Optional filter parameters
   */
  listPaginated(
    page: float,
    limit: float,
    params?: Record<string, any>
  ): Promise<ServiceResponse<{
    items: List[T]
    total: float
    page: float
    limit: float
  }>>
}
/**
 * Interface for services that support search operations
 */
interface ISearchableService<T extends BaseEntity, P = Record<string, any>> {
  /**
   * Search for entities based on search parameters
   * @param params The search parameters
   * @param config Optional service configuration
   */
  search(params: P, config?: ServiceConfig): Promise<ServiceResponse<T[]>>
}
/**
 * Interface for services that support soft delete
 */
interface ISoftDeletableService<T extends BaseEntity> {
  /**
   * Soft delete an entity
   * @param id The entity ID
   */
  softDelete(id: T['id']): Promise<ServiceResponse<void>>
  /**
   * Restore a soft-deleted entity
   * @param id The entity ID
   */
  restore(id: T['id']): Promise<ServiceResponse<T>>
  /**
   * List soft-deleted entities
   * @param params Optional filter parameters
   */
  listDeleted(params?: Record<string, any>): Promise<ServiceResponse<T[]>>
}
/**
 * Interface for services that support versioning
 */
interface IVersionableService<T extends BaseEntity> {
  /**
   * Get the version history of an entity
   * @param id The entity ID
   */
  getVersions(id: T['id']): Promise<ServiceResponse<T[]>>
  /**
   * Revert to a specific version
   * @param id The entity ID
   * @param version The version number to revert to
   */
  revertToVersion(id: T['id'], version: float): Promise<ServiceResponse<T>>
}
/**
 * Interface for services that support bulk operations
 */
interface IBulkOperationsService<T extends BaseEntity> {
  /**
   * Create multiple entities
   * @param data Array of entity data
   */
  bulkCreate(data: Partial<T>[]): Promise<ServiceResponse<T[]>>
  /**
   * Update multiple entities
   * @param data Array of entity data with IDs
   */
  bulkUpdate(data: Partial<T>[]): Promise<ServiceResponse<T[]>>
  /**
   * Delete multiple entities
   * @param ids Array of entity IDs
   */
  bulkDelete(ids: T['id'][]): Promise<ServiceResponse<void>>
}
/**
 * Interface for services that support validation
 */
interface IValidatableService<T extends BaseEntity> {
  /**
   * Validate entity data before creation
   * @param data The entity data to validate
   */
  validateCreate(data: Partial<T>): Promise<ServiceResponse<void>>
  /**
   * Validate entity data before update
   * @param id The entity ID
   * @param data The update data to validate
   */
  validateUpdate(id: T['id'], data: Partial<T>): Promise<ServiceResponse<void>>
}
/**
 * Interface for services that support hooks
 */
interface IHookableService<T extends BaseEntity> {
  /**
   * Register a before-create hook
   * @param hook The hook function
   */
  beforeCreate(hook: (data: Partial<T>) => Promise<void>): void
  /**
   * Register an after-create hook
   * @param hook The hook function
   */
  afterCreate(hook: (entity: T) => Promise<void>): void
  /**
   * Register a before-update hook
   * @param hook The hook function
   */
  beforeUpdate(hook: (id: T['id'], data: Partial<T>) => Promise<void>): void
  /**
   * Register an after-update hook
   * @param hook The hook function
   */
  afterUpdate(hook: (entity: T) => Promise<void>): void
  /**
   * Register a before-delete hook
   * @param hook The hook function
   */
  beforeDelete(hook: (id: T['id']) => Promise<void>): void
  /**
   * Register an after-delete hook
   * @param hook The hook function
   */
  afterDelete(hook: (id: T['id']) => Promise<void>): void
}
/**
 * Interface for services that support transactions
 */
class ITransactionalService:
    /**
   * Begin a transaction
   */
  beginTransaction(): Awaitable[None>
    /**
   * Commit the current transaction
   */
  commitTransaction(): Awaitable[None>
    /**
   * Rollback the current transaction
   */
  rollbackTransaction(): Awaitable[None>
    /**
   * Execute operations within a transaction
   * @param fn The function to execute within the transaction
   */
  withTransaction<R>(fn: () => Awaitable[R>): Awaitable[R>
/**
 * Interface for services that support caching with advanced options
 */
class IAdvancedCacheableService:
    /**
   * Prefetch and cache data
   * @param keys Array of cache keys to prefetch
   */
  prefetch(keys: List[str]): Awaitable[None>
    /**
   * Warm up the cache with frequently accessed data
   */
  warmCache(): Awaitable[None>
    /**
   * Set cache tags for granular cache invalidation
   * @param key The cache key
   * @param tags Array of tags to associate with the cache entry
   */
  setCacheTags(key: str, tags: List[str]): Awaitable[None>
    /**
   * Invalidate cache entries by tags
   * @param tags Array of tags to invalidate
   */
  invalidateByTags(tags: List[str]): Awaitable[None>
/**
 * Interface for services that support rate limiting
 */
class IRateLimitedService:
    /**
   * Configure rate limiting
   * @param config Rate limit configuration
   */
  setRateLimit(config: Dict[str, Any]>
} 