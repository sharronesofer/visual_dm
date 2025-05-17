// BuildingCache.ts
// LRU cache for building templates and generation results

export interface BuildingCacheEntry<T> {
    key: string;
    value: T;
    lastAccess: number;
}

export class BuildingCache<T> {
    private maxSize: number;
    private cache: Map<string, BuildingCacheEntry<T>> = new Map();
    private hits = 0;
    private misses = 0;

    constructor(maxSize: number = 100) {
        this.maxSize = maxSize;
    }

    /**
     * Get a value from the cache, updating LRU order
     */
    get(key: string): T | undefined {
        const entry = this.cache.get(key);
        if (entry) {
            entry.lastAccess = Date.now();
            this.cache.delete(key);
            this.cache.set(key, entry);
            this.hits++;
            return entry.value;
        } else {
            this.misses++;
            return undefined;
        }
    }

    /**
     * Set a value in the cache, evicting LRU if needed
     */
    set(key: string, value: T) {
        if (this.cache.has(key)) {
            this.cache.delete(key);
        } else if (this.cache.size >= this.maxSize) {
            // Evict least recently used
            const lruKey = this.cache.keys().next().value;
            this.cache.delete(lruKey);
        }
        this.cache.set(key, { key, value, lastAccess: Date.now() });
    }

    /**
     * Invalidate a cache entry
     */
    invalidate(key: string) {
        this.cache.delete(key);
    }

    /**
     * Clear the entire cache
     */
    clear() {
        this.cache.clear();
        this.hits = 0;
        this.misses = 0;
    }

    /**
     * Get cache hit/miss metrics
     */
    getMetrics() {
        return { hits: this.hits, misses: this.misses, size: this.cache.size };
    }
} 