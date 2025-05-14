import { createHash } from 'crypto';
import { join } from 'path';
import { mkdir, readFile, writeFile, unlink, stat, readdir } from 'fs/promises';
import { ThumbnailOptions, ThumbnailResult } from './ThumbnailGenerator';
import { Logger } from '../../utils/logger';

/**
 * Cache configuration options
 */
export interface ThumbnailCacheConfig {
  maxMemoryEntries?: number; // Maximum number of entries to keep in memory
  maxCacheSize?: number; // Maximum size of cache in bytes
  cachePath?: string; // Path to store cached thumbnails
  ttl?: number; // Time to live in milliseconds
}

/**
 * Cache entry structure
 */
interface CacheEntry {
  key: string;
  result: ThumbnailResult;
  timestamp: number;
  size: number;
}

/**
 * Thumbnail caching service
 */
export class ThumbnailCache {
  private readonly logger: Logger;
  private readonly cache: Map<string, CacheEntry>;
  private readonly config: Required<ThumbnailCacheConfig>;
  private currentSize: number;

  constructor(config?: ThumbnailCacheConfig) {
    this.logger = Logger.getInstance().child('ThumbnailCache');
    this.cache = new Map();
    this.currentSize = 0;
    this.config = {
      maxMemoryEntries: config?.maxMemoryEntries ?? 1000,
      maxCacheSize: config?.maxCacheSize ?? 1024 * 1024 * 1024, // 1GB
      cachePath: config?.cachePath ?? join(process.cwd(), 'cache', 'thumbnails'),
      ttl: config?.ttl ?? 24 * 60 * 60 * 1000 // 24 hours
    };
  }

  /**
   * Initialize the cache
   */
  async initialize(): Promise<void> {
    try {
      await mkdir(this.config.cachePath, { recursive: true });
      this.logger.info('Thumbnail cache initialized', { path: this.config.cachePath });
    } catch (error) {
      if (error instanceof Error) {
        this.logger.error('Failed to initialize thumbnail cache', undefined, { error: error.message });
      }
      throw error;
    }
  }

  /**
   * Generate a cache key from file content and options
   */
  private generateKey(fileContent: Buffer | string, options: ThumbnailOptions): string {
    const content = Buffer.isBuffer(fileContent) ? fileContent : Buffer.from(fileContent);
    const optionsStr = JSON.stringify(options);
    return createHash('sha256')
      .update(content)
      .update(optionsStr)
      .digest('hex');
  }

  /**
   * Get the file path for a cached thumbnail
   */
  private getCacheFilePath(key: string): string {
    return join(this.config.cachePath, `${key}.bin`);
  }

  /**
   * Check if a cached thumbnail is still valid
   */
  private isValid(entry: CacheEntry): boolean {
    return Date.now() - entry.timestamp < this.config.ttl;
  }

  /**
   * Clean up old entries when cache is full
   */
  private async cleanup(): Promise<void> {
    // Remove expired entries
    for (const [key, entry] of this.cache.entries()) {
      if (!this.isValid(entry)) {
        this.cache.delete(key);
        this.currentSize -= entry.size;
        await this.removeFromDisk(key);
      }
    }

    // If still over limit, remove oldest entries
    if (this.cache.size > this.config.maxMemoryEntries || this.currentSize > this.config.maxCacheSize) {
      const entries = Array.from(this.cache.entries())
        .sort(([, a], [, b]) => a.timestamp - b.timestamp);

      while (
        (this.cache.size > this.config.maxMemoryEntries || this.currentSize > this.config.maxCacheSize) &&
        entries.length > 0
      ) {
        const [key, entry] = entries.shift()!;
        this.cache.delete(key);
        this.currentSize -= entry.size;
        await this.removeFromDisk(key);
      }
    }
  }

  /**
   * Remove a cached thumbnail from disk
   */
  private async removeFromDisk(key: string): Promise<void> {
    try {
      await unlink(this.getCacheFilePath(key));
    } catch (error) {
      if (error instanceof Error) {
        this.logger.warn('Failed to remove cached thumbnail from disk', { error: error.message });
      }
    }
  }

  /**
   * Get a cached thumbnail
   */
  async get(fileContent: Buffer | string, options: ThumbnailOptions): Promise<ThumbnailResult | null> {
    const key = this.generateKey(fileContent, options);

    // Check memory cache first
    const memoryEntry = this.cache.get(key);
    if (memoryEntry && this.isValid(memoryEntry)) {
      this.logger.debug('Thumbnail found in memory cache', { key });
      return memoryEntry.result;
    }

    // Check disk cache
    try {
      const filePath = this.getCacheFilePath(key);
      const stats = await stat(filePath);
      const data = await readFile(filePath);

      const entry: CacheEntry = {
        key,
        result: JSON.parse(data.toString()),
        timestamp: stats.mtimeMs,
        size: stats.size
      };

      if (this.isValid(entry)) {
        // Add to memory cache
        this.cache.set(key, entry);
        this.currentSize += entry.size;
        await this.cleanup();
        this.logger.debug('Thumbnail found in disk cache', { key });
        return entry.result;
      } else {
        // Remove expired entry
        await this.removeFromDisk(key);
        return null;
      }
    } catch (error) {
      if (error instanceof Error) {
        const nodeError = error as NodeJS.ErrnoException;
        if (nodeError.code !== 'ENOENT') {
          this.logger.warn('Failed to read cached thumbnail', { error: error.message, code: nodeError.code });
        }
      }
      return null;
    }
  }

  /**
   * Store a thumbnail in the cache
   */
  async set(fileContent: Buffer | string, options: ThumbnailOptions, result: ThumbnailResult): Promise<void> {
    const key = this.generateKey(fileContent, options);
    const entry: CacheEntry = {
      key,
      result,
      timestamp: Date.now(),
      size: result.data.length
    };

    // Add to memory cache
    this.cache.set(key, entry);
    this.currentSize += entry.size;

    // Write to disk
    try {
      await writeFile(
        this.getCacheFilePath(key),
        JSON.stringify(result),
        { encoding: 'utf8' }
      );
    } catch (error) {
      if (error instanceof Error) {
        this.logger.error('Failed to write thumbnail to disk cache', undefined, { error: error.message });
      }
    }

    // Clean up if needed
    await this.cleanup();
  }

  /**
   * Clear the entire cache
   */
  async clear(): Promise<void> {
    // Clear memory cache
    this.cache.clear();
    this.currentSize = 0;

    // Clear disk cache
    try {
      const files = await readdir(this.config.cachePath);
      await Promise.all(
        files.map(file => unlink(join(this.config.cachePath, file)))
      );
    } catch (error) {
      if (error instanceof Error) {
        this.logger.error('Failed to clear disk cache', undefined, { error: error.message });
      }
      throw error;
    }
  }
} 