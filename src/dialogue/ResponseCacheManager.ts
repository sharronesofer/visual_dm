import { DialogueMetadata } from './types';

export interface CacheEntry {
    key: string;
    response: string;
    metadata: DialogueMetadata;
    timestamp: number;
}

export interface CacheAnalytics {
    hits: number;
    misses: number;
    mostFrequent: { [key: string]: number };
}

export interface ResponseCacheConfig {
    maxSize?: number;
    expiryMs?: number;
}

/**
 * ResponseCacheManager caches dialogue responses to reduce API usage and improve response times.
 * Provides analytics and pre-warming capabilities.
 */
export class ResponseCacheManager {
    private cache: Map<string, CacheEntry> = new Map();
    private analytics: CacheAnalytics = { hits: 0, misses: 0, mostFrequent: {} };
    private config: Required<ResponseCacheConfig>;

    constructor(config: ResponseCacheConfig = {}) {
        this.config = {
            maxSize: config.maxSize ?? 1000,
            expiryMs: config.expiryMs ?? 5 * 60 * 1000, // 5 minutes
        };
    }

    /**
     * Generates a cache key from prompt and context.
     */
    static makeKey(prompt: string, context: string[]): string {
        // Simple hash: prompt + context joined, can be improved for semantic similarity
        return `${prompt}::${context.join('||')}`;
    }

    /**
     * Retrieves a cached response if valid, or undefined if not found/expired.
     */
    get(prompt: string, context: string[]): string | undefined {
        const key = ResponseCacheManager.makeKey(prompt, context);
        const entry = this.cache.get(key);
        if (entry && Date.now() - entry.timestamp < this.config.expiryMs) {
            this.analytics.hits++;
            this.analytics.mostFrequent[key] = (this.analytics.mostFrequent[key] || 0) + 1;
            return entry.response;
        } else {
            if (entry) this.cache.delete(key); // Expired
            this.analytics.misses++;
            return undefined;
        }
    }

    /**
     * Stores a response in the cache.
     */
    set(prompt: string, context: string[], response: string, metadata: DialogueMetadata) {
        const key = ResponseCacheManager.makeKey(prompt, context);
        if (this.cache.size >= this.config.maxSize) {
            // Remove oldest entry (FIFO)
            const oldestKey = this.cache.keys().next().value;
            if (oldestKey !== undefined) {
                this.cache.delete(oldestKey);
            }
        }
        this.cache.set(key, { key, response, metadata, timestamp: Date.now() });
    }

    /**
     * Clears the cache.
     */
    clear() {
        this.cache.clear();
        this.analytics = { hits: 0, misses: 0, mostFrequent: {} };
    }

    /**
     * Invalidates cache entries based on a predicate (e.g., game state change).
     */
    invalidate(predicate: (entry: CacheEntry) => boolean) {
        for (const [key, entry] of this.cache.entries()) {
            if (predicate(entry)) {
                this.cache.delete(key);
            }
        }
    }

    /**
     * Returns analytics data.
     */
    getAnalytics(): CacheAnalytics {
        return { ...this.analytics };
    }

    /**
     * Returns all cache keys (for inspection/testing).
     */
    getKeys(): string[] {
        return Array.from(this.cache.keys());
    }

    /**
     * Pre-warms the cache with anticipated dialogue paths.
     */
    prewarm(entries: { prompt: string; context: string[]; response: string; metadata: DialogueMetadata }[]) {
        for (const entry of entries) {
            this.set(entry.prompt, entry.context, entry.response, entry.metadata);
        }
    }
} 