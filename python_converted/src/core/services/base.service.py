from typing import Any, Dict, List, Union


MetadataValue = Union[str, float, bool, None, None, List[MetadataValue], { [key: str]: MetadataValue }]
ServiceMetadata = {
  total?: float
  error?: AppError
  [key: string]: MetadataValue | AppError | undefined
}
/**
 * Base interface for all entities
 */
class BaseEntity:
    id: Union[str, float]
    createdAt?: Date
    updatedAt?: Date
    deletedAt?: Union[Date, None]
/**
 * Interface for entities that support soft deletion
 */
class SoftDeletableEntity:
    deletedAt?: Date
    isDeleted?: bool
/**
 * Interface for entities that support versioning
 */
class VersionedEntity:
    version: float
/**
 * Interface for entities that support ownership
 */
class OwnedEntity:
    ownerId: Union[str, float]
    ownerType?: str
/**
 * Service response wrapper
 */
interface ServiceResponse<T> {
  data: T
  meta?: ServiceMetadata
}
/**
 * Base query parameters interface
 */
class BaseQueryParams:
    page?: float
    limit?: float
    sort?: str
    order?: Union['asc', 'desc']
    search?: str
    filter?: Dict[str, MetadataValue>
    [key: Union[str]: MetadataValue, None]
/**
 * Bulk operation response interface
 */
interface BulkOperationResponse<T> {
  successful: List[T]
  failed: Array<{
    item: Partial<T>
    error: AppError
  }>
  totalProcessed: float
  totalSuccessful: float
  totalFailed: float
}
/**
 * Base service options interface with retry configuration
 */
class BaseServiceOptions:
    baseURL?: str
    cacheEnabled?: bool
    cacheTTL?: float
    cachePrefix?: str
    cacheVersion?: str
    logger?: Logger
    retry?: {
    maxRetries?: float
    retryDelay?: float
    retryableStatuses?: List[float]
}
/**
 * Cache options for individual operations
 */
class CacheOptions:
    enabled?: bool
    ttl?: float
    invalidateOnError?: bool
/**
 * Service configuration interface
 */
class ServiceConfig:
    cacheConfig?: {
    ttl?: float
    policy?: Union['memory', 'session', 'none']
    bypassCache?: bool
  params?: Record<string, MetadataValue>
}
/**
 * Base service class providing CRUD operations with enhanced features
 */
abstract class BaseService<T extends BaseEntity> {
  protected readonly http: AxiosInstance
  protected readonly cache: CacheService
  protected readonly logger: Logger
  protected readonly resourcePath: str
  protected readonly cacheEnabled: bool
  protected readonly cacheTTL: float
  protected readonly cachePrefix: str
  protected readonly cacheVersion: str
  protected readonly maxRetries: float
  protected readonly retryDelay: float
  protected readonly retryableStatuses: List[number]
  constructor(resourcePath: str, options: \'BaseServiceOptions\' = {}) {
    const {
      baseURL,
      cacheEnabled = true,
      cacheTTL = 300, 
      cachePrefix = this.constructor.name,
      cacheVersion = '1',
      logger = Logger.getInstance(),
      retry = {
        maxRetries: 3,
        retryDelay: 1000,
        retryableStatuses: [
          HTTP_STATUS.REQUEST_TIMEOUT,
          HTTP_STATUS.TOO_MANY_REQUESTS,
          HTTP_STATUS.BAD_GATEWAY,
          HTTP_STATUS.SERVICE_UNAVAILABLE,
          HTTP_STATUS.GATEWAY_TIMEOUT,
        ],
      },
    } = options
    this.http = createAxiosInstance({ baseURL })
    this.cache = new CacheService()
    this.logger = logger
    this.resourcePath = resourcePath
    this.cacheEnabled = cacheEnabled
    this.cacheTTL = cacheTTL
    this.cachePrefix = cachePrefix
    this.cacheVersion = cacheVersion
    this.maxRetries = retry.maxRetries ?? 3
    this.retryDelay = retry.retryDelay ?? 1000
    this.retryableStatuses = retry.retryableStatuses ?? [
      HTTP_STATUS.REQUEST_TIMEOUT,
      HTTP_STATUS.TOO_MANY_REQUESTS,
      HTTP_STATUS.BAD_GATEWAY,
      HTTP_STATUS.SERVICE_UNAVAILABLE,
      HTTP_STATUS.GATEWAY_TIMEOUT,
    ]
  }
  /**
   * Generate cache key for a resource
   */
  protected getCacheKey(method?: str, params?: unknown): str {
    const base = `${this.cachePrefix}:${this.cacheVersion}:${this.resourcePath}`
    if (method) return `${base}:${method}`
    if (params) return `${base}:${JSON.stringify(params)}`
    return base
  }
  /**
   * Get the full resource URL
   * @param path - Optional path to append
   * @returns The complete URL
   */
  protected getResourceUrl(path: str = ''): str {
    return `${this.resourcePath}${path}`
  }
  /**
   * Execute a function with retry logic
   * @param fn - The function to execute
   * @returns The function result
   * @throws The last error encountered
   */
  protected async executeWithRetry<R>(fn: () => Promise<R>): Promise<R> {
    let lastError: Error | null = null
    let attempt = 0
    while (attempt < this.maxRetries) {
      try {
        return await fn()
      } catch (error) {
        lastError = error as Error
        const status = (error as any)?.response?.status
        if (!this.retryableStatuses.includes(status)) {
          throw this.handleError(error)
        }
        this.logger.warn(`Retry attempt ${attempt + 1}/${this.maxRetries}`, {
          error: lastError.message,
          status,
        })
        await new Promise(resolve => setTimeout(resolve, this.retryDelay * (attempt + 1)))
        attempt++
      }
    }
    throw this.handleError(lastError!)
  }
  /**
   * Handle errors and convert them to AppError format
   */
  protected handleError(error: Error | AxiosError | unknown): AppError {
    if (error instanceof AppError) {
      return error
    }
    if (error instanceof Error) {
      const isAxiosError = (error as AxiosError).isAxiosError
      if (isAxiosError) {
        const axiosError = error as AxiosError
        return new AppError(
          axiosError.message,
          axiosError.response?.status || HTTP_STATUS.INTERNAL_SERVER_ERROR,
          true
        )
      }
      return new AppError(
        error.message,
        HTTP_STATUS.INTERNAL_SERVER_ERROR,
        true
      )
    }
    return new AppError(
      'An unknown error occurred',
      HTTP_STATUS.INTERNAL_SERVER_ERROR,
      true
    )
  }
  /**
   * Warm up the cache with initial data
   * @param data - The data to cache
   * @param params - Optional query parameters for list data
   */
  async warmCache(data: T | T[], params?: BaseQueryParams): Promise<void> {
    if (!this.cacheEnabled) return
    if (Array.isArray(data)) {
      const cacheKey = this.getCacheKey('list', params)
      await this.cache.set(cacheKey, { data, meta: Dict[str, Any] }, this.cacheTTL)
    } else {
      const cacheKey = this.getCacheKey('get', data.id.toString())
      await this.cache.set(cacheKey, { data }, this.cacheTTL)
    }
  }
  /**
   * Clear all cache entries for this service
   */
  async clearCache(): Promise<void> {
    if (!this.cacheEnabled) return
    const pattern = `${this.cachePrefix}:${this.cacheVersion}:${this.resourcePath}*`
    await this.cache.deletePattern(pattern)
  }
  /**
   * Invalidate cache for specific IDs
   * @param ids - Array of entity IDs to invalidate
   */
  async invalidateCache(ids: Array<string | number>): Promise<void> {
    if (!this.cacheEnabled) return
    await Promise.all([
      ...ids.map(id => this.cache.delete(this.getCacheKey('get', id.toString()))),
      this.cache.delete(this.getCacheKey('list')),
    ])
  }
  /**
   * Get a list of entities with advanced filtering and sorting
   * @param params - Query parameters for filtering, sorting, and pagination
   * @param cacheOptions - Cache options for this operation
   * @returns A paginated list of entities
   */
  async list(
    params?: \'BaseQueryParams\',
    cacheOptions: \'CacheOptions\' = {}
  ): Promise<ServiceResponse<T[]>> {
    const {
      enabled = this.cacheEnabled,
      ttl = this.cacheTTL,
      invalidateOnError = true,
    } = cacheOptions
    const cacheKey = this.getCacheKey('list', params)
    if (enabled) {
      const cached = await this.cache.get<ServiceResponse<T[]>>(cacheKey)
      if (cached) {
        this.logger.debug('Returning cached list data', { cacheKey })
        return cached
      }
    }
    try {
      const response = await this.executeWithRetry(async () => {
        const result = await this.http.get<ServiceResponse<T[]>>(this.getResourceUrl(), { params })
        return result.data
      })
      if (enabled) {
        await this.cache.set(cacheKey, response, ttl)
      }
      return response
    } catch (error) {
      if (enabled && invalidateOnError) {
        await this.cache.delete(cacheKey)
      }
      throw error
    }
  }
  /**
   * Get a single entity by ID
   * @param id - The entity ID
   * @param cacheOptions - Cache options for this operation
   * @returns The entity
   * @throws AppError if the entity is not found
   */
  async get(id: str | number, cacheOptions: \'CacheOptions\' = {}): Promise<ServiceResponse<T>> {
    const {
      enabled = this.cacheEnabled,
      ttl = this.cacheTTL,
      invalidateOnError = true,
    } = cacheOptions
    const cacheKey = this.getCacheKey('get', id.toString())
    if (enabled) {
      const cached = await this.cache.get<ServiceResponse<T>>(cacheKey)
      if (cached) {
        this.logger.debug('Returning cached entity data', { cacheKey })
        return cached
      }
    }
    try {
      const response = await this.executeWithRetry(async () => {
        const result = await this.http.get<ServiceResponse<T>>(this.getResourceUrl(`/${id}`))
        return result.data
      })
      if (enabled) {
        await this.cache.set(cacheKey, response, ttl)
      }
      return response
    } catch (error) {
      if (enabled && invalidateOnError) {
        await this.cache.delete(cacheKey)
      }
      throw error
    }
  }
  /**
   * Create a new entity
   * @param data - The entity data
   * @returns The created entity
   */
  async create(data: Omit<T, keyof BaseEntity>): Promise<ServiceResponse<T>> {
    const response = await this.executeWithRetry(async () => {
      const result = await this.http.post<ServiceResponse<T>>(this.getResourceUrl(), data)
      return result.data
    })
    await this.clearCache()
    return response
  }
  /**
   * Update an existing entity
   * @param id - The entity ID
   * @param data - The update data
   * @returns The updated entity
   */
  async update(
    id: str | number,
    data: Partial<Omit<T, keyof BaseEntity>>
  ): Promise<ServiceResponse<T>> {
    const response = await this.executeWithRetry(async () => {
      const result = await this.http.put<ServiceResponse<T>>(this.getResourceUrl(`/${id}`), data)
      return result.data
    })
    await this.invalidateCache([id])
    return response
  }
  /**
   * Delete an entity
   * @param id - The entity ID
   * @returns The deleted entity
   */
  async delete(id: str | number): Promise<ServiceResponse<T>> {
    const response = await this.executeWithRetry(async () => {
      const result = await this.http.delete<ServiceResponse<T>>(this.getResourceUrl(`/${id}`))
      return result.data
    })
    await this.invalidateCache([id])
    return response
  }
  /**
   * Perform bulk create operation
   * @param items - Array of items to create
   * @returns Bulk operation response with success and failure details
   */
  async bulkCreate(items: Partial<T>[]): Promise<BulkOperationResponse<T>> {
    const result: BulkOperationResponse<T> = {
      successful: [],
      failed: [],
      totalProcessed: items.length,
      totalSuccessful: 0,
      totalFailed: 0,
    }
    await Promise.all(
      items.map(async item => {
        try {
          const created = await this.create(item as Omit<T, keyof BaseEntity>)
          result.successful.push(created.data)
          result.totalSuccessful++
        } catch (error) {
          result.failed.push({
            item,
            error: this.handleError(error),
          })
          result.totalFailed++
        }
      })
    )
    return result
  }
  /**
   * Perform bulk update operation
   * @param items - Array of items with IDs to update
   * @returns Bulk operation response with success and failure details
   */
  async bulkUpdate(
    items: Array<{ id: str | number } & Partial<T>>
  ): Promise<BulkOperationResponse<T>> {
    const result: BulkOperationResponse<T> = {
      successful: [],
      failed: [],
      totalProcessed: items.length,
      totalSuccessful: 0,
      totalFailed: 0,
    }
    await Promise.all(
      items.map(async ({ id, ...data }) => {
        try {
          const updated = await this.update(id, data as Partial<Omit<T, keyof BaseEntity>>)
          result.successful.push(updated.data)
          result.totalSuccessful++
        } catch (error) {
          result.failed.push({
            item: Dict[str, Any] as Partial<T>,
            error: this.handleError(error),
          })
          result.totalFailed++
        }
      })
    )
    return result
  }
  /**
   * Perform bulk delete operation
   * @param ids - Array of entity IDs to delete
   * @returns Bulk operation response with success and failure details
   */
  async bulkDelete(ids: Array<string | number>): Promise<BulkOperationResponse<T>> {
    const result: BulkOperationResponse<T> = {
      successful: [],
      failed: [],
      totalProcessed: ids.length,
      totalSuccessful: 0,
      totalFailed: 0,
    }
    await Promise.all(
      ids.map(async id => {
        try {
          const deleted = await this.delete(id)
          result.successful.push(deleted.data)
          result.totalSuccessful++
        } catch (error) {
          result.failed.push({
            item: Dict[str, Any] as Partial<T>,
            error: this.handleError(error),
          })
          result.totalFailed++
        }
      })
    )
    return result
  }
  /**
   * Get a resource by ID
   */
  async findById(
    id: str | number,
    cacheOptions: \'CacheOptions\' = {}
  ): Promise<ServiceResponse<T>> {
    const cacheKey = this.getCacheKey('get', id.toString())
    if (this.cacheEnabled && cacheOptions.enabled !== false) {
      const cached = await this.cache.get<T>(cacheKey)
      if (cached) {
        return { data: cached }
      }
    }
    const response = await this.executeWithRetry(() => this.getResource<T>(`/${id}`))
    if (this.cacheEnabled && cacheOptions.enabled !== false && response.data) {
      await this.cache.set(cacheKey, response.data, cacheOptions.ttl || this.cacheTTL)
    }
    return response
  }
  /**
   * Make a GET request to the API
   */
  protected async getResource<R>(
    path: str,
    config?: \'ServiceConfig\'
  ): Promise<ServiceResponse<R>> {
    try {
      const response = await this.http.get<R>(this.getResourceUrl(path), config)
      return { data: response.data }
    } catch (error) {
      throw this.handleError(error)
    }
  }
  /**
   * Make a POST request to the API
   */
  protected async postResource<R>(
    path: str,
    data?: unknown,
    config?: \'ServiceConfig\'
  ): Promise<ServiceResponse<R>> {
    try {
      const response = await this.http.post<ServiceResponse<R>>(
        this.getResourceUrl(path),
        data,
        this.getRequestConfig(config)
      )
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }
  /**
   * Make a PUT request to the API
   */
  protected async putResource<R>(
    path: str,
    data?: unknown,
    config?: \'ServiceConfig\'
  ): Promise<ServiceResponse<R>> {
    try {
      const response = await this.http.put<ServiceResponse<R>>(
        this.getResourceUrl(path),
        data,
        this.getRequestConfig(config)
      )
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }
  /**
   * Make a DELETE request to the API
   */
  protected async deleteResource<R>(
    path: str,
    config?: \'ServiceConfig\'
  ): Promise<ServiceResponse<R>> {
    try {
      const response = await this.http.delete<R>(this.getResourceUrl(path), config)
      return { data: response.data }
    } catch (error) {
      throw this.handleError(error)
    }
  }
  /**
   * Get request configuration
   */
  protected getRequestConfig(config?: ServiceConfig): Any {
    if (config) {
      const { cacheConfig, params } = config
      const requestConfig: Any = { params }
      if (cacheConfig) {
        const { ttl, policy, bypassCache } = cacheConfig
        if (ttl) requestConfig.timeout = ttl
        if (policy) requestConfig.maxRedirects = 0
        if (bypassCache) requestConfig.cache = false
      }
      return requestConfig
    }
    return {}
  }
}