/**
 * Cache interface
 * @module core/base/interfaces/cached
 */

import { BaseEntity } from '../types/entity';
import { CacheOptions } from '../types/common';

/**
 * Interface for services that support caching
 */
export interface ICacheableService<T extends BaseEntity> {
  /**
   * Clear all cached data for this service
   */
  clearCache(): void;

  /**
   * Invalidate cache for a specific entity
   * @param id Entity ID
   */
  invalidateCache(id: T['id']): void;

  /**
   * Set cache options for this service
   * @param options Cache configuration options
   */
  setCacheOptions(options: CacheOptions): void;

  /**
   * Get current cache options
   */
  getCacheOptions(): CacheOptions;

  /**
   * Check if an item exists in cache
   * @param key Cache key
   */
  hasCache(key: string): Promise<boolean>;

  /**
   * Get an item from cache
   * @param key Cache key
   */
  getFromCache<R>(key: string): Promise<R | null>;

  /**
   * Set an item in cache
   * @param key Cache key
   * @param value Value to cache
   * @param ttl Optional TTL in seconds
   */
  setInCache<R>(key: string, value: R, ttl?: number): Promise<void>;

  /**
   * Remove an item from cache
   * @param key Cache key
   */
  removeFromCache(key: string): Promise<void>;
} 