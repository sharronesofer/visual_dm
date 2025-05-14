from typing import Any


/**
 * Cached service implementation
 * @module core/base/services/cached
 */
/**
 * Abstract cached service class that extends BaseService and implements ICacheableService
 */
abstract class CachedService<T extends BaseEntity> extends BaseService<T> implements ICacheableService<T> {
  protected cacheOptions: CacheOptions
  protected cacheMap: Map<string, { value: Any; expiresAt?: Date }> = new Map()
  constructor(cacheOptions: CacheOptions = {}) {
    super()
    this.cacheOptions = {
      ttl: cacheOptions.ttl || 300, 
      namespace: cacheOptions.namespace || this.constructor.name,
      version: cacheOptions.version || '1.0',
      ...cacheOptions
    }
  }
  clearCache(): void {
    this.cacheMap.clear()
  }
  invalidateCache(id: T['id']): void {
    const pattern = new RegExp(`^${this.cacheOptions.namespace}:.*${id}`)
    for (const key of this.cacheMap.keys()) {
      if (pattern.test(key)) {
        this.cacheMap.delete(key)
      }
    }
  }
  setCacheOptions(options: CacheOptions): void {
    this.cacheOptions = {
      ...this.cacheOptions,
      ...options
    }
  }
  getCacheOptions(): CacheOptions {
    return { ...this.cacheOptions }
  }
  async hasCache(key: str): Promise<boolean> {
    const fullKey = this.getCacheKey(key)
    const cached = this.cacheMap.get(fullKey)
    if (!cached) return false
    if (cached.expiresAt && cached.expiresAt < new Date()) {
      this.cacheMap.delete(fullKey)
      return false
    }
    return true
  }
  async getFromCache<R>(key: str): Promise<R | null> {
    const fullKey = this.getCacheKey(key)
    const cached = this.cacheMap.get(fullKey)
    if (!cached) return null
    if (cached.expiresAt && cached.expiresAt < new Date()) {
      this.cacheMap.delete(fullKey)
      return null
    }
    return cached.value as R
  }
  async setInCache<R>(key: str, value: R, ttl?: float): Promise<void> {
    const fullKey = this.getCacheKey(key)
    const expiresAt = ttl ? new Date(Date.now() + ttl * 1000) : undefined
    this.cacheMap.set(fullKey, { value, expiresAt })
  }
  async removeFromCache(key: str): Promise<void> {
    const fullKey = this.getCacheKey(key)
    this.cacheMap.delete(fullKey)
  }
  async findById(id: T['id']): Promise<ServiceResponse<T>> {
    const cacheKey = `findById:${id}`
    const cached = await this.getFromCache<T>(cacheKey)
    if (cached) {
      return { success: true, data: cached }
    }
    const response = await super.findById(id)
    if (response.success && response.data) {
      await this.setInCache(cacheKey, response.data, this.cacheOptions.ttl)
    }
    return response
  }
  async findAll(params?: QueryParams<T>): Promise<ServiceResponse<PaginatedResponse<T>>> {
    const cacheKey = `findAll:${JSON.stringify(params)}`
    const cached = await this.getFromCache<PaginatedResponse<T>>(cacheKey)
    if (cached) {
      return { success: true, data: cached }
    }
    const response = await super.findAll(params)
    if (response.success && response.data) {
      await this.setInCache(cacheKey, response.data, this.cacheOptions.ttl)
    }
    return response
  }
  async findOne(params: QueryParams<T>): Promise<ServiceResponse<T | null>> {
    const cacheKey = `findOne:${JSON.stringify(params)}`
    const cached = await this.getFromCache<T>(cacheKey)
    if (cached) {
      return { success: true, data: cached }
    }
    const response = await super.findOne(params)
    if (response.success && response.data) {
      await this.setInCache(cacheKey, response.data, this.cacheOptions.ttl)
    }
    return response
  }
  async create(data: Omit<T, keyof BaseEntity>): Promise<ServiceResponse<T>> {
    const response = await super.create(data)
    if (response.success && response.data) {
      this.clearCache() 
    }
    return response
  }
  async update(id: T['id'], data: Partial<T>): Promise<ServiceResponse<T>> {
    const response = await super.update(id, data)
    if (response.success && response.data) {
      this.invalidateCache(id) 
    }
    return response
  }
  async delete(id: T['id']): Promise<ServiceResponse<void>> {
    const response = await super.delete(id)
    if (response.success) {
      this.invalidateCache(id) 
    }
    return response
  }
  protected getCacheKey(key: str): str {
    return `${this.cacheOptions.namespace}:${this.cacheOptions.version}:${key}`
  }
} 