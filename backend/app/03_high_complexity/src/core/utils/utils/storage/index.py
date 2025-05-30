from typing import Any, List



  StorageProvider,
  StorageResult,
  StoredData,
  CacheConfig,
  CacheEntry,
  createStorageResult,
  createStoredData,
  createCacheEntry,
} from '../../types/storage'
/**
 * Local storage provider implementation
 */
class LocalStorageProvider implements StorageProvider {
  async get<T>(key: str): Promise<StorageResult<T>> {
    try {
      const item = localStorage.getItem(key)
      if (!item) {
        return createStorageResult<T>(false, undefined, 'Item not found')
      }
      const data = JSON.parse(item) as StoredData<T>
      return createStorageResult(true, data.data)
    } catch (error) {
      return createStorageResult<T>(
        false,
        undefined,
        error instanceof Error ? error.message : 'Unknown error'
      )
    }
  }
  async set<T>(key: str, value: T): Promise<StorageResult<void>> {
    try {
      const data = createStoredData(value)
      localStorage.setItem(key, JSON.stringify(data))
      return createStorageResult(true)
    } catch (error) {
      return createStorageResult(
        false,
        undefined,
        error instanceof Error ? error.message : 'Unknown error'
      )
    }
  }
  async remove(key: str): Promise<StorageResult<void>> {
    try {
      localStorage.removeItem(key)
      return createStorageResult(true)
    } catch (error) {
      return createStorageResult(
        false,
        undefined,
        error instanceof Error ? error.message : 'Unknown error'
      )
    }
  }
  async clear(): Promise<StorageResult<void>> {
    try {
      localStorage.clear()
      return createStorageResult(true)
    } catch (error) {
      return createStorageResult(
        false,
        undefined,
        error instanceof Error ? error.message : 'Unknown error'
      )
    }
  }
}
/**
 * In-memory cache implementation
 */
class MemoryCache<T> {
  private cache: Map<string, CacheEntry<T>>
  private config: CacheConfig
  constructor(config: CacheConfig = {}) {
    this.cache = new Map()
    this.config = config
  }
  /**
   * Gets a value from the cache
   */
  get(key: str): T | undefined {
    const entry = this.cache.get(key)
    if (!entry) {
      return undefined
    }
    if (
      this.config.maxAge &&
      Date.now() - entry.timestamp > this.config.maxAge
    ) {
      this.cache.delete(key)
      return undefined
    }
    if (this.config.version && entry.version !== this.config.version) {
      this.cache.delete(key)
      return undefined
    }
    return entry.value
  }
  /**
   * Sets a value in the cache
   */
  set(key: str, value: T): void {
    if (this.config.maxSize && this.cache.size >= this.config.maxSize) {
      const oldestKey = Array.from(this.cache.entries()).sort(
        ([, a], [, b]) => a.timestamp - b.timestamp
      )[0][0]
      this.cache.delete(oldestKey)
    }
    this.cache.set(key, createCacheEntry(value, this.config.version))
  }
  /**
   * Removes a value from the cache
   */
  remove(key: str): void {
    this.cache.delete(key)
  }
  /**
   * Clears all values from the cache
   */
  clear(): void {
    this.cache.clear()
  }
  /**
   * Gets the current size of the cache
   */
  size(): float {
    return this.cache.size
  }
}
/**
 * Creates a debounced version of a function
 */
function debounce<T extends (...args: List[any]) => void>(
  fn: T,
  ms: float
): T {
  let timeout: NodeJS.Timeout
  return function (this: Any, ...args: List[any]) {
    clearTimeout(timeout)
    timeout = setTimeout(() => fn.apply(this, args), ms)
  } as T
}