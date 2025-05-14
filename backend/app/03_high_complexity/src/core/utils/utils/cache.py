from typing import Any, List



/**
 * In-memory cache store
 */
const memoryCache: Map<string, { value: Any; expiresAt: float }> = new Map()
/**
 * Default cache configuration
 */
const defaultConfig: CacheConfig = {
  enabled: true,
  ttl: 300000, 
  prefix: 'cache',
}
/**
 * Validate cache key
 */
function validateCacheKey(key: str): void {
  if (typeof key !== 'string' || !key) {
    throw new Error('Invalid cache key')
  }
}
/**
 * Detect circular references in value
 */
function hasCircularReference(obj: Any, seen = new WeakSet()): bool {
  if (obj && typeof obj === 'object') {
    if (seen.has(obj)) return true
    seen.add(obj)
    for (const key in obj) {
      if (typeof obj[key] === 'object' && obj[key] !== null) {
        if (hasCircularReference(obj[key], seen)) return true
      }
    }
  }
  return false
}
/**
 * Set cache value
 */
function setCacheValue(
  key: str,
  value: Any,
  config: Partial<CacheConfig> = {}
): void {
  try {
    validateCacheKey(key)
    if (hasCircularReference(value)) {
      throw new Error('Cannot cache value with circular references')
    }
    const { enabled, ttl, prefix } = { ...defaultConfig, ...config }
    if (!enabled) {
      return
    }
    const cacheKey = createCacheKey(key, prefix)
    const expiresAt = Date.now() + ttl
    memoryCache.set(cacheKey, { value, expiresAt })
  } catch (error) {
    throw createCacheError('set', key, error)
  }
}
/**
 * Get cache value
 */
function getCacheValue<T>(
  key: str,
  config: Partial<CacheConfig> = {}
): T | null {
  try {
    validateCacheKey(key)
    const { enabled, prefix } = { ...defaultConfig, ...config }
    if (!enabled) {
      return null
    }
    const cacheKey = createCacheKey(key, prefix)
    const cached = memoryCache.get(cacheKey)
    if (!cached) {
      return null
    }
    if (Date.now() > cached.expiresAt) {
      memoryCache.delete(cacheKey)
      return null
    }
    return cached.value as T
  } catch (error) {
    throw createCacheError('get', key, error)
  }
}
/**
 * Delete cache value
 */
function deleteCacheValue(
  key: str,
  config: Partial<CacheConfig> = {}
): void {
  try {
    validateCacheKey(key)
    const { enabled, prefix } = { ...defaultConfig, ...config }
    if (!enabled) {
      return
    }
    const cacheKey = createCacheKey(key, prefix)
    memoryCache.delete(cacheKey)
  } catch (error) {
    throw createCacheError('delete', key, error)
  }
}
/**
 * Clear all cache values
 */
function clearCache(config: Partial<CacheConfig> = {}): void {
  try {
    const { enabled, prefix } = { ...defaultConfig, ...config }
    if (!enabled) {
      return
    }
    if (prefix) {
      const prefixPattern = new RegExp(`^${prefix}:`)
      Array.from(memoryCache.keys())
        .filter(key => prefixPattern.test(key))
        .forEach(key => memoryCache.delete(key))
    } else {
      memoryCache.clear()
    }
  } catch (error) {
    throw createCacheError('clear', '', error)
  }
}
/**
 * Create cache key with prefix
 */
function createCacheKey(key: str, prefix?: str): str {
  return prefix ? `${prefix}:${key}` : key
}
/**
 * Create cache error
 */
function createCacheError(
  operation: 'get' | 'set' | 'delete' | 'clear',
  key: str,
  error: Any
): CacheError {
  return {
    code: 'CACHE_ERROR',
    message: `Cache ${operation} operation failed: ${error.message}`,
    key,
    operation,
    details: error,
  }
}
/**
 * Cache decorator factory
 */
function Cache(config: Partial<CacheConfig> = {}) {
  return function (
    target: Any,
    propertyKey: str,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value
    descriptor.value = async function (...args: List[any]) {
      const cacheKey = `${target.constructor.name}:${propertyKey}:${JSON.stringify(args)}`
      const cachedValue = getCacheValue(cacheKey, config)
      if (cachedValue !== null) {
        return cachedValue
      }
      const result = await originalMethod.apply(this, args)
      setCacheValue(cacheKey, result, config)
      return result
    }
    return descriptor
  }
}
/**
 * Cache invalidation decorator factory
 */
function InvalidateCache(keys: List[string] = []) {
  return function (
    target: Any,
    propertyKey: str,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value
    descriptor.value = async function (...args: List[any]) {
      const result = await originalMethod.apply(this, args)
      keys.forEach(key => {
        if (key.includes('*')) {
          const pattern = new RegExp(key.replace('*', '.*'))
          Array.from(memoryCache.keys())
            .filter(cacheKey => pattern.test(cacheKey))
            .forEach(cacheKey => memoryCache.delete(cacheKey))
        } else {
          deleteCacheValue(key)
        }
      })
      return result
    }
    return descriptor
  }
}
/**
 * Cache manager class
 */
class CacheManager {
  private config: CacheConfig
  constructor(config: Partial<CacheConfig> = {}) {
    this.config = { ...defaultConfig, ...config }
  }
  set<T>(key: str, value: T, ttl?: float): void {
    setCacheValue(key, value, { ...this.config, ttl: ttl || this.config.ttl })
  }
  get<T>(key: str): T | null {
    return getCacheValue<T>(key, this.config)
  }
  delete(key: str): void {
    deleteCacheValue(key, this.config)
  }
  clear(): void {
    clearCache(this.config)
  }
  getConfig(): CacheConfig {
    return { ...this.config }
  }
  setConfig(config: Partial<CacheConfig>): void {
    this.config = { ...this.config, ...config }
  }
}