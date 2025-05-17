import Redis from 'ioredis';
import { CACHE_KEYS, CACHE_TTL, CACHE_CONFIG } from '../core/constants/cache';
import { Logger } from '../utils/logger';
import { CacheService } from '../utils/cache';

interface RedisCacheServiceOptions {
    url?: string;
    namespace?: string;
    logger?: Logger;
    defaultTTL?: number;
}

export class RedisCacheService {
    private redis: Redis;
    private fallback: CacheService;
    private logger: Logger;
    private namespace: string;
    private defaultTTL: number;
    private hitCount = 0;
    private missCount = 0;
    private errorCount = 0;

    constructor(options: RedisCacheServiceOptions = {}) {
        this.redis = new Redis(options.url || process.env.REDIS_URL || 'redis://localhost:6379');
        this.fallback = new CacheService();
        this.logger = options.logger || new Logger({ prefix: 'RedisCacheService' });
        this.namespace = options.namespace || 'app';
        this.defaultTTL = options.defaultTTL || CACHE_TTL.MEDIUM;
        this.redis.on('error', (err) => {
            this.logger.error('Redis error', { err });
            this.errorCount++;
        });
    }

    private getKey(key: string): string {
        return `${this.namespace}:${key}`;
    }

    async get<T>(key: string): Promise<T | null> {
        try {
            const value = await this.redis.get(this.getKey(key));
            if (value === null) {
                this.missCount++;
                return this.fallback.get<T>(key);
            }
            this.hitCount++;
            return JSON.parse(value) as T;
        } catch (err) {
            this.logger.warn('Redis get failed, using fallback', { key, err });
            this.errorCount++;
            return this.fallback.get<T>(key);
        }
    }

    async set(key: string, value: any, ttl?: number): Promise<void> {
        try {
            await this.redis.set(this.getKey(key), JSON.stringify(value), 'PX', ttl || this.defaultTTL);
        } catch (err) {
            this.logger.warn('Redis set failed, using fallback', { key, err });
            this.errorCount++;
            this.fallback.set(key, value, ttl);
        }
    }

    async delete(key: string): Promise<void> {
        try {
            await this.redis.del(this.getKey(key));
        } catch (err) {
            this.logger.warn('Redis delete failed, using fallback', { key, err });
            this.errorCount++;
            this.fallback.delete(key);
        }
    }

    async setMany(items: Record<string, any>, ttl?: number): Promise<void> {
        const pipeline = this.redis.pipeline();
        try {
            for (const [key, value] of Object.entries(items)) {
                pipeline.set(this.getKey(key), JSON.stringify(value), 'PX', ttl || this.defaultTTL);
            }
            await pipeline.exec();
        } catch (err) {
            this.logger.warn('Redis setMany failed, using fallback', { err });
            this.errorCount++;
            await this.fallback.setMany(items, ttl);
        }
    }

    async deletePattern(pattern: string): Promise<void> {
        try {
            const keys = await this.redis.keys(this.getKey(pattern.replace('*', '*')));
            if (keys.length > 0) {
                await this.redis.del(...keys);
            }
        } catch (err) {
            this.logger.warn('Redis deletePattern failed, using fallback', { pattern, err });
            this.errorCount++;
            await this.fallback.deletePattern(pattern);
        }
    }

    async setTags(key: string, tags: string[]): Promise<void> {
        try {
            const value = await this.get<any>(key);
            if (value) {
                value.__tags = tags;
                await this.set(key, value);
            }
        } catch (err) {
            this.logger.warn('Redis setTags failed', { key, err });
            this.errorCount++;
        }
    }

    async invalidateByTags(tags: string[]): Promise<void> {
        try {
            const keys = await this.redis.keys(this.getKey('*'));
            for (const key of keys) {
                const value = await this.redis.get(key);
                if (value) {
                    const parsed = JSON.parse(value);
                    const itemTags = parsed.__tags || [];
                    if (tags.some(tag => itemTags.includes(tag))) {
                        await this.redis.del(key);
                    }
                }
            }
        } catch (err) {
            this.logger.warn('Redis invalidateByTags failed, using fallback', { tags, err });
            this.errorCount++;
            await this.fallback.invalidateByTags(tags);
        }
    }

    async ttl(key: string): Promise<number> {
        try {
            const ttl = await this.redis.pttl(this.getKey(key));
            return ttl > 0 ? ttl : 0;
        } catch (err) {
            this.logger.warn('Redis ttl failed, using fallback', { key, err });
            this.errorCount++;
            return this.fallback.ttl(key);
        }
    }

    async clear(): Promise<void> {
        try {
            const keys = await this.redis.keys(this.getKey('*'));
            if (keys.length > 0) {
                await this.redis.del(...keys);
            }
        } catch (err) {
            this.logger.warn('Redis clear failed, using fallback', { err });
            this.errorCount++;
            this.fallback.clear();
        }
    }

    getMetrics() {
        return {
            hits: this.hitCount,
            misses: this.missCount,
            errors: this.errorCount,
        };
    }

    // For Prometheus integration
    exposeMetrics() {
        return `# HELP redis_cache_hits Total cache hits\n# TYPE redis_cache_hits counter\nredis_cache_hits ${this.hitCount}\n# HELP redis_cache_misses Total cache misses\n# TYPE redis_cache_misses counter\nredis_cache_misses ${this.missCount}\n# HELP redis_cache_errors Total cache errors\n# TYPE redis_cache_errors counter\nredis_cache_errors ${this.errorCount}`;
    }
} 