import { ServiceResponse, ServiceConfig } from '../base.service';
import { BaseEntity } from './index';

/**
 * Interface for services that support caching operations
 */
export interface ICacheableService {
  /**
   * Clear the cache for this service
   * @param pattern Optional pattern to match specific cache keys
   */
  clearCache(pattern?: string): Promise<void>;

  /**
   * Generate a cache key for a specific operation
   * @param method The method name
   * @param params Optional parameters to include in the key
   */
  getCacheKey(method: string, params?: any[]): string;

  /**
   * Configure caching behavior
   * @param config Cache configuration options
   */
  setCacheConfig(config: {
    ttl?: number;
    policy?: 'memory' | 'session' | 'none';
    bypassCache?: boolean;
  }): void;
}

/**
 * Interface for services that support pagination
 */
export interface IPaginatedService<T extends BaseEntity> {
  /**
   * Get a paginated list of entities
   * @param page The page number (1-based)
   * @param limit The number of items per page
   * @param params Optional filter parameters
   */
  listPaginated(
    page: number,
    limit: number,
    params?: Record<string, any>
  ): Promise<ServiceResponse<{
    items: T[];
    total: number;
    page: number;
    limit: number;
  }>>;
}

/**
 * Interface for services that support search operations
 */
export interface ISearchableService<T extends BaseEntity, P = Record<string, any>> {
  /**
   * Search for entities based on search parameters
   * @param params The search parameters
   * @param config Optional service configuration
   */
  search(params: P, config?: ServiceConfig): Promise<ServiceResponse<T[]>>;
}

/**
 * Interface for services that support soft delete
 */
export interface ISoftDeletableService<T extends BaseEntity> {
  /**
   * Soft delete an entity
   * @param id The entity ID
   */
  softDelete(id: T['id']): Promise<ServiceResponse<void>>;

  /**
   * Restore a soft-deleted entity
   * @param id The entity ID
   */
  restore(id: T['id']): Promise<ServiceResponse<T>>;

  /**
   * List soft-deleted entities
   * @param params Optional filter parameters
   */
  listDeleted(params?: Record<string, any>): Promise<ServiceResponse<T[]>>;
}

/**
 * Interface for services that support versioning
 */
export interface IVersionableService<T extends BaseEntity> {
  /**
   * Get the version history of an entity
   * @param id The entity ID
   */
  getVersions(id: T['id']): Promise<ServiceResponse<T[]>>;

  /**
   * Revert to a specific version
   * @param id The entity ID
   * @param version The version number to revert to
   */
  revertToVersion(id: T['id'], version: number): Promise<ServiceResponse<T>>;
}

/**
 * Interface for services that support bulk operations
 */
export interface IBulkOperationsService<T extends BaseEntity> {
  /**
   * Create multiple entities
   * @param data Array of entity data
   */
  bulkCreate(data: Partial<T>[]): Promise<ServiceResponse<T[]>>;

  /**
   * Update multiple entities
   * @param data Array of entity data with IDs
   */
  bulkUpdate(data: Partial<T>[]): Promise<ServiceResponse<T[]>>;

  /**
   * Delete multiple entities
   * @param ids Array of entity IDs
   */
  bulkDelete(ids: T['id'][]): Promise<ServiceResponse<void>>;
}

/**
 * Interface for services that support validation
 */
export interface IValidatableService<T extends BaseEntity> {
  /**
   * Validate entity data before creation
   * @param data The entity data to validate
   */
  validateCreate(data: Partial<T>): Promise<ServiceResponse<void>>;

  /**
   * Validate entity data before update
   * @param id The entity ID
   * @param data The update data to validate
   */
  validateUpdate(id: T['id'], data: Partial<T>): Promise<ServiceResponse<void>>;
}

/**
 * Interface for services that support hooks
 */
export interface IHookableService<T extends BaseEntity> {
  /**
   * Register a before-create hook
   * @param hook The hook function
   */
  beforeCreate(hook: (data: Partial<T>) => Promise<void>): void;

  /**
   * Register an after-create hook
   * @param hook The hook function
   */
  afterCreate(hook: (entity: T) => Promise<void>): void;

  /**
   * Register a before-update hook
   * @param hook The hook function
   */
  beforeUpdate(hook: (id: T['id'], data: Partial<T>) => Promise<void>): void;

  /**
   * Register an after-update hook
   * @param hook The hook function
   */
  afterUpdate(hook: (entity: T) => Promise<void>): void;

  /**
   * Register a before-delete hook
   * @param hook The hook function
   */
  beforeDelete(hook: (id: T['id']) => Promise<void>): void;

  /**
   * Register an after-delete hook
   * @param hook The hook function
   */
  afterDelete(hook: (id: T['id']) => Promise<void>): void;
}

/**
 * Interface for services that support transactions
 */
export interface ITransactionalService {
  /**
   * Begin a transaction
   */
  beginTransaction(): Promise<void>;

  /**
   * Commit the current transaction
   */
  commitTransaction(): Promise<void>;

  /**
   * Rollback the current transaction
   */
  rollbackTransaction(): Promise<void>;

  /**
   * Execute operations within a transaction
   * @param fn The function to execute within the transaction
   */
  withTransaction<R>(fn: () => Promise<R>): Promise<R>;
}

/**
 * Interface for services that support caching with advanced options
 */
export interface IAdvancedCacheableService extends ICacheableService {
  /**
   * Prefetch and cache data
   * @param keys Array of cache keys to prefetch
   */
  prefetch(keys: string[]): Promise<void>;

  /**
   * Warm up the cache with frequently accessed data
   */
  warmCache(): Promise<void>;

  /**
   * Set cache tags for granular cache invalidation
   * @param key The cache key
   * @param tags Array of tags to associate with the cache entry
   */
  setCacheTags(key: string, tags: string[]): Promise<void>;

  /**
   * Invalidate cache entries by tags
   * @param tags Array of tags to invalidate
   */
  invalidateByTags(tags: string[]): Promise<void>;
}

/**
 * Interface for services that support rate limiting
 */
export interface IRateLimitedService {
  /**
   * Configure rate limiting
   * @param config Rate limit configuration
   */
  setRateLimit(config: {
    windowMs: number;
    maxRequests: number;
    errorMessage?: string;
  }): void;

  /**
   * Check if operation is within rate limits
   * @param key The rate limit key (e.g., IP address, user ID)
   */
  checkRateLimit(key: string): Promise<boolean>;

  /**
   * Get current rate limit status
   * @param key The rate limit key
   */
  getRateLimitStatus(key: string): Promise<{
    remaining: number;
    reset: Date;
  }>;
} 