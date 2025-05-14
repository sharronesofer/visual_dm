import { Logger } from '../../utils/logger';

/**
 * Tag metadata associated with a cache entry
 */
export interface TagMetadata {
    /** Tags associated with this cache entry */
    tags: string[];
    /** Cache entry key */
    key: string;
    /** Timestamp when the entry was cached */
    timestamp: number;
}

/**
 * Cache entry with value, expiration and tags
 */
export interface TaggedCacheEntry<T> {
    /** Cached value */
    value: T;
    /** Timestamp when the entry expires */
    expiresAt: number;
    /** Size of the entry in bytes (approximate) */
    size: number;
    /** Tags associated with this cache entry */
    tags: string[];
}

/**
 * Configuration options for the tag-based cache
 */
export interface TagBasedCacheConfig {
    /** Maximum number of items in cache */
    maxItems?: number;
    /** Maximum cache size in bytes */
    maxSize?: number;
    /** Default TTL in milliseconds */
    defaultTTL?: number;
    /** Enable debug logging */
    debug?: boolean;
}

/**
 * Tag-based cache implementation that supports invalidation by tags
 */
export class TagBasedCache<T = any> {
    private cache = new Map<string, TaggedCacheEntry<T>>();
    private tagRegistry = new Map<string, Set<string>>();
    private currentSize = 0;
    private readonly maxItems: number;
    private readonly maxSize: number;
    private readonly defaultTTL: number;
    private readonly logger: Logger;

    /**
     * Creates a new tag-based cache instance
     * @param options Configuration options
     */
    constructor(options: TagBasedCacheConfig = {}) {
        this.maxItems = options.maxItems ?? 1000;
        this.maxSize = options.maxSize ?? 100 * 1024 * 1024;
        this.defaultTTL = options.defaultTTL ?? 5 * 60 * 1000;
        this.logger = Logger.getInstance().child('TagBasedCache');

        if (options.debug) {
            // Enable verbose logging if debug flag is set
            this.logger.debug('Tag-based cache initialized with debug logging');
        }
    }

    /**
     * Get a value from the cache
     * @param key Cache key
     * @returns The cached value or undefined if not found or expired
     */
    get(key: string): T | undefined {
        const entry = this.cache.get(key);
        if (!entry) return undefined;

        // Check if expired
        if (entry.expiresAt < Date.now()) {
            this.delete(key);
            return undefined;
        }

        this.logger.debug(`Cache hit: ${key}`);
        return entry.value;
    }

    /**
     * Set a value in the cache with associated tags
     * @param key Cache key
     * @param value Value to cache
     * @param tags Tags to associate with this entry
     * @param ttl Time-to-live in milliseconds (defaults to configured defaultTTL)
     */
    set(key: string, value: T, tags: string[] = [], ttl?: number): void {
        // Calculate entry size (approximate)
        const valueSize = this.estimateSize(value);

        // Check if we need to make room
        this.ensureCapacity(valueSize);

        // If entry already exists, update tag registry
        if (this.cache.has(key)) {
            const existingEntry = this.cache.get(key)!;
            this.currentSize -= existingEntry.size;

            // Remove existing tags
            for (const tag of existingEntry.tags) {
                const tagEntries = this.tagRegistry.get(tag);
                if (tagEntries) {
                    tagEntries.delete(key);
                    if (tagEntries.size === 0) {
                        this.tagRegistry.delete(tag);
                    }
                }
            }
        }

        // Create the new entry
        const entry: TaggedCacheEntry<T> = {
            value,
            expiresAt: Date.now() + (ttl ?? this.defaultTTL),
            size: valueSize,
            tags: [...tags]
        };

        // Update the cache
        this.cache.set(key, entry);
        this.currentSize += valueSize;

        // Update tag registry
        for (const tag of tags) {
            if (!this.tagRegistry.has(tag)) {
                this.tagRegistry.set(tag, new Set<string>());
            }
            this.tagRegistry.get(tag)!.add(key);
        }

        this.logger.debug(`Cache set: ${key}, tags: [${tags.join(', ')}]`);
    }

    /**
     * Delete a cache entry by key
     * @param key Cache key
     * @returns True if the entry was deleted, false if it didn't exist
     */
    delete(key: string): boolean {
        const entry = this.cache.get(key);
        if (!entry) return false;

        // Update cache size
        this.currentSize -= entry.size;

        // Remove from tag registry
        for (const tag of entry.tags) {
            const tagEntries = this.tagRegistry.get(tag);
            if (tagEntries) {
                tagEntries.delete(key);
                if (tagEntries.size === 0) {
                    this.tagRegistry.delete(tag);
                }
            }
        }

        // Remove from cache
        this.cache.delete(key);
        this.logger.debug(`Cache delete: ${key}`);
        return true;
    }

    /**
     * Check if a key exists in the cache
     * @param key Cache key
     * @returns True if the key exists and is not expired
     */
    has(key: string): boolean {
        const entry = this.cache.get(key);
        if (!entry) return false;

        // Check if expired
        if (entry.expiresAt < Date.now()) {
            this.delete(key);
            return false;
        }

        return true;
    }

    /**
     * Get all keys in the cache
     * @returns Array of cache keys
     */
    keys(): string[] {
        return Array.from(this.cache.keys());
    }

    /**
     * Invalidate all cache entries with the specified tag
     * @param tag Tag to invalidate
     * @returns Number of entries invalidated
     */
    invalidateByTag(tag: string): number {
        const tagEntries = this.tagRegistry.get(tag);
        if (!tagEntries) return 0;

        const keysToDelete = Array.from(tagEntries);
        let count = 0;

        for (const key of keysToDelete) {
            if (this.delete(key)) {
                count++;
            }
        }

        this.logger.debug(`Invalidated ${count} entries by tag: ${tag}`);
        return count;
    }

    /**
     * Invalidate all cache entries with any of the specified tags
     * @param tags Tags to invalidate
     * @returns Number of entries invalidated
     */
    invalidateByTags(tags: string[]): number {
        const keysToDelete = new Set<string>();

        for (const tag of tags) {
            const tagEntries = this.tagRegistry.get(tag);
            if (tagEntries) {
                for (const key of tagEntries) {
                    keysToDelete.add(key);
                }
            }
        }

        let count = 0;
        for (const key of keysToDelete) {
            if (this.delete(key)) {
                count++;
            }
        }

        this.logger.debug(`Invalidated ${count} entries by tags: [${tags.join(', ')}]`);
        return count;
    }

    /**
     * Invalidate cache entries by tag pattern
     * @param pattern Regex pattern to match against tags
     * @returns Number of entries invalidated
     */
    invalidateByPattern(pattern: RegExp): number {
        const matchingTags = Array.from(this.tagRegistry.keys())
            .filter(tag => pattern.test(tag));

        return this.invalidateByTags(matchingTags);
    }

    /**
     * Get all tags currently in the registry
     * @returns Array of tags
     */
    getTags(): string[] {
        return Array.from(this.tagRegistry.keys());
    }

    /**
     * Get keys associated with a specific tag
     * @param tag Tag to lookup
     * @returns Array of cache keys
     */
    getKeysByTag(tag: string): string[] {
        const tagEntries = this.tagRegistry.get(tag);
        if (!tagEntries) return [];
        return Array.from(tagEntries);
    }

    /**
     * Clear all cache entries
     * @returns Number of entries removed
     */
    clear(): number {
        const entryCount = this.cache.size;
        this.cache.clear();
        this.tagRegistry.clear();
        this.currentSize = 0;
        this.logger.debug(`Cache cleared, removed ${entryCount} entries`);
        return entryCount;
    }

    /**
     * Remove all expired entries from the cache
     * @returns Number of expired entries removed
     */
    removeExpired(): number {
        const now = Date.now();
        let removedCount = 0;

        // Get keys to avoid concurrent modification
        const keys = Array.from(this.cache.keys());

        for (const key of keys) {
            const entry = this.cache.get(key);
            if (entry && entry.expiresAt < now) {
                if (this.delete(key)) {
                    removedCount++;
                }
            }
        }

        if (removedCount > 0) {
            this.logger.debug(`Removed ${removedCount} expired entries`);
        }

        return removedCount;
    }

    /**
     * Get cache statistics
     * @returns Cache statistics
     */
    stats(): {
        entries: number;
        tags: number;
        totalSize: number;
        maxSize: number;
    } {
        return {
            entries: this.cache.size,
            tags: this.tagRegistry.size,
            totalSize: this.currentSize,
            maxSize: this.maxSize
        };
    }

    /**
     * Add tags to an existing cache entry
     * @param key Cache key
     * @param tags Tags to add
     * @returns True if the tags were added, false if the key doesn't exist
     */
    addTags(key: string, tags: string[]): boolean {
        const entry = this.cache.get(key);
        if (!entry) return false;

        for (const tag of tags) {
            if (!entry.tags.includes(tag)) {
                entry.tags.push(tag);

                if (!this.tagRegistry.has(tag)) {
                    this.tagRegistry.set(tag, new Set<string>());
                }
                this.tagRegistry.get(tag)!.add(key);
            }
        }

        this.logger.debug(`Added tags to ${key}: [${tags.join(', ')}]`);
        return true;
    }

    /**
     * Remove tags from an existing cache entry
     * @param key Cache key
     * @param tags Tags to remove
     * @returns True if the tags were removed, false if the key doesn't exist
     */
    removeTags(key: string, tags: string[]): boolean {
        const entry = this.cache.get(key);
        if (!entry) return false;

        for (const tag of tags) {
            const index = entry.tags.indexOf(tag);
            if (index !== -1) {
                entry.tags.splice(index, 1);

                const tagEntries = this.tagRegistry.get(tag);
                if (tagEntries) {
                    tagEntries.delete(key);
                    if (tagEntries.size === 0) {
                        this.tagRegistry.delete(tag);
                    }
                }
            }
        }

        this.logger.debug(`Removed tags from ${key}: [${tags.join(', ')}]`);
        return true;
    }

    /**
     * Estimate the size of a value in bytes
     * @param value Value to estimate size for
     * @returns Approximate size in bytes
     */
    private estimateSize(value: any): number {
        if (value === null || value === undefined) return 0;
        if (typeof value === 'boolean') return 4;
        if (typeof value === 'number') return 8;
        if (typeof value === 'string') return value.length * 2;
        if (value instanceof Date) return 8;
        if (Array.isArray(value)) {
            return value.reduce((size, item) => size + this.estimateSize(item), 0);
        }
        if (typeof value === 'object') {
            return Object.keys(value).reduce(
                (size, key) => size + key.length * 2 + this.estimateSize(value[key]),
                0
            );
        }
        return 100; // Default size for unknown types
    }

    /**
     * Ensure there's enough capacity for a new entry
     * @param requiredSize Size of the new entry
     */
    private ensureCapacity(requiredSize: number): void {
        // Check if we need to make room in terms of size
        while (
            this.cache.size > 0 &&
            this.currentSize + requiredSize > this.maxSize
        ) {
            this.evictOldest();
        }

        // Check if we need to make room in terms of count
        while (
            this.cache.size >= this.maxItems
        ) {
            this.evictOldest();
        }
    }

    /**
     * Evict the oldest cache entry
     */
    private evictOldest(): void {
        if (this.cache.size === 0) return;

        // Find the entry with the earliest expiration time
        let oldestKey: string | null = null;
        let oldestExpiry = Number.MAX_SAFE_INTEGER;

        for (const [key, entry] of this.cache.entries()) {
            if (entry.expiresAt < oldestExpiry) {
                oldestKey = key;
                oldestExpiry = entry.expiresAt;
            }
        }

        if (oldestKey) {
            this.logger.debug(`Evicting oldest entry: ${oldestKey}`);
            this.delete(oldestKey);
        }
    }
} 