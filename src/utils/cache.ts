import { CACHE_CONFIG } from '../constants';
import { Logger } from './logger';

/**
 * Cache entry interface
 */
interface CacheEntry<T> {
  value: T;
  expiry: number;
}

/**
 * Cache service options interface
 */
interface CacheServiceOptions {
  namespace?: string;
  maxItems?: number;
  checkPeriod?: number;
  pruneThreshold?: number;
  logger?: Logger;
}

export interface CacheOptions {
  ttl?: number;
  maxItems?: number;
  checkPeriod?: number;
}

export interface CacheConfig {
  ttl?: number;
  policy?: 'memory' | 'session' | 'none';
  bypassCache?: boolean;
}

/**
 * Cache service for storing and retrieving data with TTL
 */
export class CacheService {
  private cache: Map<string, { data: any; timestamp: number }> = new Map();
  private readonly namespace: string;
  private readonly maxItems: number;
  private readonly checkPeriod: number;
  private readonly pruneThreshold: number;
  private readonly logger: Logger;
  private cleanupInterval: NodeJS.Timeout | null = null;
  private config: CacheConfig = {
    policy: 'memory',
    bypassCache: false,
  };

  constructor(options: CacheOptions = {}) {
    this.maxItems = options.maxItems || 1000;
    this.checkPeriod = options.checkPeriod || 60 * 1000; // 1 minute default
    this.namespace = CACHE_CONFIG.NAMESPACE;
    this.pruneThreshold = CACHE_CONFIG.PRUNE_THRESHOLD;
    this.logger = new Logger({ prefix: 'CacheService' });
    this.startCleanup();
  }

  /**
   * Get a value from cache
   */
  get<T>(key: string): T | null {
    const item = this.cache.get(key);
    if (!item) return null;

    if (Date.now() > item.timestamp) {
      this.cache.delete(key);
      return null;
    }

    return item.data as T;
  }

  /**
   * Set a value in cache with TTL
   */
  set(key: string, value: any, ttl?: number): void {
    if (this.cache.size >= this.maxItems) {
      // Remove oldest item if cache is full
      const oldestKey = Array.from(this.cache.keys())[0];
      this.cache.delete(oldestKey);
    }

    this.cache.set(key, {
      data: value,
      timestamp: Date.now() + (ttl || this.checkPeriod),
    });
  }

  /**
   * Delete all cache entries matching a pattern
   * @param pattern - The pattern to match (supports * wildcard)
   */
  async deletePattern(pattern: string): Promise<void> {
    const namespacedPattern = this.getNamespacedKey(pattern);
    const regex = new RegExp('^' + namespacedPattern.replace(/\*/g, '.*') + '$');

    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.cache.delete(key);
        this.logger.debug('Cache deleted by pattern', { key, pattern: namespacedPattern });
      }
    }
  }

  /**
   * Delete a specific cache entry
   * @param key - The cache key to delete
   */
  delete(key: string): void {
    this.cache.delete(key);
  }

  /**
   * Clear all values from cache
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Get the size of the cache
   */
  size(): number {
    return this.cache.size;
  }

  /**
   * Stop the periodic check
   */
  dispose(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
    }
    this.cache.clear();
  }

  /**
   * Get a namespaced key
   */
  private getNamespacedKey(key: string): string {
    return `${this.namespace}:${key}`;
  }

  private startCleanup(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }

    this.cleanupInterval = setInterval(() => {
      const now = Date.now();
      for (const [key, value] of this.cache.entries()) {
        if (now > value.timestamp) {
          this.cache.delete(key);
        }
      }
    }, this.checkPeriod);
  }

  setConfig(config: CacheConfig): void {
    this.config = { ...this.config, ...config };
  }

  getConfig(): CacheConfig {
    return { ...this.config };
  }

  async setMany(items: Record<string, any>, ttl?: number): Promise<void> {
    Object.entries(items).forEach(([key, value]) => {
      this.set(key, value, ttl);
    });
  }

  async setTags(key: string, tags: string[]): Promise<void> {
    const item = this.cache.get(key);
    if (item) {
      item.data = { ...item.data, __tags: tags };
      this.cache.set(key, item);
    }
  }

  async invalidateByTags(tags: string[]): Promise<void> {
    for (const [key, item] of this.cache.entries()) {
      const itemTags = (item.data?.__tags || []) as string[];
      if (tags.some(tag => itemTags.includes(tag))) {
        this.cache.delete(key);
      }
    }
  }

  async ttl(key: string): Promise<number> {
    const item = this.cache.get(key);
    if (!item) return 0;
    return Math.max(0, item.timestamp - Date.now());
  }
}
