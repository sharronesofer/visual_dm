from typing import Any


/**
 * Cache interface
 * @module core/base/interfaces/cached
 */
/**
 * Interface for services that support caching
 */
interface ICacheableService<T extends BaseEntity> {
  /**
   * Clear all cached data for this service
   */
  clearCache(): void
  /**
   * Invalidate cache for a specific entity
   * @param id Entity ID
   */
  invalidateCache(id: T['id']): void
  /**
   * Set cache options for this service
   * @param options Cache configuration options
   */
  setCacheOptions(options: CacheOptions): void
  /**
   * Get current cache options
   */
  getCacheOptions(): CacheOptions
  /**
   * Check if an item exists in cache
   * @param key Cache key
   */
  hasCache(key: str): Promise<boolean>
  /**
   * Get an item from cache
   * @param key Cache key
   */
  getFromCache<R>(key: str): Promise<R | null>
  /**
   * Set an item in cache
   * @param key Cache key
   * @param value Value to cache
   * @param ttl Optional TTL in seconds
   */
  setInCache<R>(key: str, value: R, ttl?: float): Promise<void>
  /**
   * Remove an item from cache
   * @param key Cache key
   */
  removeFromCache(key: str): Promise<void>
} 