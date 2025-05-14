from typing import Any, Dict, List



/**
 * Generic cache provider interface for key-value caching
 */
interface CacheProvider<K, V> {
  get(key: K): V | undefined
  set(key: K, value: V, ttl?: float): void
  delete(key: K): void
  clear(): void
  has(key: K): bool
  stats(): {
    entries: float
    totalSize?: float
    maxSize?: float
  }
}
/**
 * Cache entry with value and expiration
 */
interface CacheEntry<T> {
  value: T
  expiresAt: float
  size: float
}
/**
 * Cache configuration options
 */
class StorageCacheConfig:
    /** Maximum number of items in cache */
  maxItems?: float
    /** Maximum cache size in bytes */
  maxSize?: float
    /** Default TTL in milliseconds */
  defaultTTL?: float
    /** Whether to cache metadata */
  cacheMetadata?: bool
    /** Whether to cache file contents */
  cacheContents?: bool
    /** Whether to cache file listings */
  cacheListings?: bool
/**
 * In-memory cache provider with TTL and LRU support
 */
class MemoryCacheProvider<V> implements CacheProvider<string, V> {
  private cache = new Map<string, { value: V; expiresAt: float; size: float }>()
  private currentSize = 0
  private readonly maxItems: float
  private readonly maxSize: float
  private readonly defaultTTL: float
  /**
   * @param options.maxItems Maximum number of items
   * @param options.maxSize Maximum total size in bytes
   * @param options.defaultTTL Default TTL in ms
   */
  constructor(options: Dict[str, Any] = {}) {
    this.maxItems = options.maxItems ?? 1000
    this.maxSize = options.maxSize ?? 100 * 1024 * 1024
    this.defaultTTL = options.defaultTTL ?? 5 * 60 * 1000
  }
  /**
   * Get a value from the cache
   */
  get(key: str): V | undefined {
    const entry = this.cache.get(key)
    if (!entry) return undefined
    if (entry.expiresAt <= Date.now()) {
      this.delete(key)
      return undefined
    }
    this.cache.delete(key)
    this.cache.set(key, entry)
    return entry.value
  }
  /**
   * Set a value in the cache
   */
  set(key: str, value: V, ttl?: float): void {
    const size = this.estimateSize(value)
    if (this.cache.has(key)) {
      this.currentSize -= this.cache.get(key)!.size
      this.cache.delete(key)
    }
    if (this.currentSize + size > this.maxSize) {
      this.evict(size)
    }
    const expiresAt = Date.now() + (ttl ?? this.defaultTTL)
    this.cache.set(key, { value, expiresAt, size })
    this.currentSize += size
    while (this.cache.size > this.maxItems) {
      const firstKey = this.cache.keys().next().value
      if (firstKey) this.delete(firstKey)
    }
  }
  /**
   * Delete a value from the cache
   */
  delete(key: str): void {
    if (this.cache.has(key)) {
      this.currentSize -= this.cache.get(key)!.size
      this.cache.delete(key)
    }
  }
  /**
   * Clear the cache
   */
  clear(): void {
    this.cache.clear()
    this.currentSize = 0
  }
  /**
   * Check if a key exists and is not expired
   */
  has(key: str): bool {
    return this.get(key) !== undefined
  }
  /**
   * Get cache statistics
   */
  stats() {
    return {
      entries: this.cache.size,
      totalSize: this.currentSize,
      maxSize: this.maxSize,
    }
  }
  /**
   * Estimate the size of a value (bytes)
   */
  private estimateSize(value: V): float {
    if (typeof value === 'string') return value.length * 2
    if (Buffer.isBuffer(value)) return value.length
    try {
      return JSON.stringify(value).length
    } catch {
      return 1024 
    }
  }
  /**
   * Evict entries to make room for new ones
   */
  private evict(requiredSize: float): void {
    this.evictExpired()
    while (this.currentSize + requiredSize > this.maxSize && this.cache.size > 0) {
      const firstKey = this.cache.keys().next().value
      if (firstKey) this.delete(firstKey)
    }
  }
  /**
   * Remove all expired entries
   */
  private evictExpired(): void {
    const now = Date.now()
    for (const [key, entry] of this.cache.entries()) {
      if (entry.expiresAt <= now) {
        this.delete(key)
      }
    }
  }
}
/**
 * LRU cache implementation for storage operations
 */
class StorageCache {
  private readonly metadata = new Map<string, CacheEntry<StorageMetadata>>()
  private readonly contents = new Map<string, CacheEntry<Buffer>>()
  private readonly listings = new Map<string, CacheEntry<string[]>>()
  private readonly logger: Logger
  private currentSize = 0
  private readonly config: Required<StorageCacheConfig>
  constructor(config: \'StorageCacheConfig\' = {}) {
    this.logger = Logger.getInstance().child('StorageCache')
    this.config = {
      maxItems: config.maxItems ?? 1000,
      maxSize: config.maxSize ?? 100 * 1024 * 1024, 
      defaultTTL: config.defaultTTL ?? 5 * 60 * 1000, 
      cacheMetadata: config.cacheMetadata ?? true,
      cacheContents: config.cacheContents ?? true,
      cacheListings: config.cacheListings ?? true,
    }
  }
  /**
   * Get metadata from cache
   */
  public getMetadata(path: str): StorageMetadata | undefined {
    if (!this.config.cacheMetadata) return undefined
    return this.get(this.metadata, path)?.value
  }
  /**
   * Set metadata in cache
   */
  public setMetadata(path: str, metadata: StorageMetadata, ttl?: float): void {
    if (!this.config.cacheMetadata) return
    const size = JSON.stringify(metadata).length
    this.set(this.metadata, path, metadata, size, ttl)
  }
  /**
   * Get file contents from cache
   */
  public getContents(path: str): Buffer | undefined {
    if (!this.config.cacheContents) return undefined
    return this.get(this.contents, path)?.value
  }
  /**
   * Set file contents in cache
   */
  public setContents(path: str, contents: Buffer, ttl?: float): void {
    if (!this.config.cacheContents) return
    this.set(this.contents, path, contents, contents.length, ttl)
  }
  /**
   * Get directory listing from cache
   */
  public getListing(path: str): string[] | undefined {
    if (!this.config.cacheListings) return undefined
    return this.get(this.listings, path)?.value
  }
  /**
   * Set directory listing in cache
   */
  public setListing(path: str, listing: List[string], ttl?: float): void {
    if (!this.config.cacheListings) return
    const size = JSON.stringify(listing).length
    this.set(this.listings, path, listing, size, ttl)
  }
  /**
   * Invalidate cache entries for a path
   */
  public invalidate(path: str): void {
    this.logger.debug(`Invalidating cache for path: ${path}`)
    if (this.metadata.has(path)) {
      this.currentSize -= this.metadata.get(path)!.size
      this.metadata.delete(path)
    }
    if (this.contents.has(path)) {
      this.currentSize -= this.contents.get(path)!.size
      this.contents.delete(path)
    }
    if (this.listings.has(path)) {
      this.currentSize -= this.listings.get(path)!.size
      this.listings.delete(path)
    }
  }
  /**
   * Clear all cache entries
   */
  public clear(): void {
    this.logger.debug('Clearing all cache entries')
    this.metadata.clear()
    this.contents.clear()
    this.listings.clear()
    this.currentSize = 0
  }
  /**
   * Get cache statistics
   */
  public getStats(): {
    metadataEntries: float
    contentsEntries: float
    listingEntries: float
    totalSize: float
    maxSize: float
  } {
    return {
      metadataEntries: this.metadata.size,
      contentsEntries: this.contents.size,
      listingEntries: this.listings.size,
      totalSize: this.currentSize,
      maxSize: this.config.maxSize,
    }
  }
  /**
   * Get a value from a cache map
   */
  private get<T>(cache: Map<string, CacheEntry<T>>, key: str): CacheEntry<T> | undefined {
    const entry = cache.get(key)
    if (!entry) {
      return undefined
    }
    if (entry.expiresAt <= Date.now()) {
      this.logger.debug(`Cache entry expired: ${key}`)
      this.invalidate(key)
      return undefined
    }
    cache.delete(key)
    cache.set(key, entry)
    return entry
  }
  /**
   * Set a value in a cache map
   */
  private set<T>(
    cache: Map<string, CacheEntry<T>>,
    key: str,
    value: T,
    size: float,
    ttl?: float
  ): void {
    if (cache.has(key)) {
      this.currentSize -= cache.get(key)!.size
      cache.delete(key)
    }
    if (this.currentSize + size > this.config.maxSize) {
      this.evict(size)
    }
    const entry: CacheEntry<T> = {
      value,
      size,
      expiresAt: Date.now() + (ttl ?? this.config.defaultTTL),
    }
    cache.set(key, entry)
    this.currentSize += size
    while (cache.size > this.config.maxItems) {
      const firstKey = cache.keys().next().value
      if (firstKey) {
        this.invalidate(firstKey)
      }
    }
  }
  /**
   * Evict entries to make room for new ones
   */
  private evict(requiredSize: float): void {
    this.logger.debug(`Evicting cache entries to free up ${requiredSize} bytes`)
    this.evictExpired()
    const caches = [this.metadata, this.contents, this.listings]
    while (this.currentSize + requiredSize > this.config.maxSize && caches.some(c => c.size > 0)) {
      for (const cache of caches) {
        if (cache.size > 0) {
          const firstKey = cache.keys().next().value
          if (firstKey) {
            this.invalidate(firstKey)
            break
          }
        }
      }
    }
  }
  /**
   * Remove all expired entries
   */
  private evictExpired(): void {
    const now = Date.now()
    for (const [cache, name] of [
      [this.metadata, 'metadata'],
      [this.contents, 'contents'],
      [this.listings, 'listings'],
    ] as const) {
      for (const [key, entry] of cache.entries()) {
        if (entry.expiresAt <= now) {
          this.logger.debug(`Evicting expired ${name} entry: ${key}`)
          this.invalidate(key)
        }
      }
    }
  }
}