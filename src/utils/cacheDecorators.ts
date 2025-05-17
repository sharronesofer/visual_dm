import { RedisCacheService } from '../services/RedisCacheService';
import { CacheService } from './cache';

interface CacheableOptions {
    key?: string | ((...args: any[]) => string);
    ttl?: number;
    condition?: (...args: any[]) => boolean;
    cacheService?: RedisCacheService | CacheService;
}

interface InvalidateCacheOptions {
    key?: string | ((...args: any[]) => string);
    cacheService?: RedisCacheService | CacheService;
}

// Default cache service (should be replaced with DI in real app)
const defaultCache = new RedisCacheService();

export function Cacheable(options: CacheableOptions = {}) {
    return function (
        target: any,
        propertyKey: string,
        descriptor: PropertyDescriptor
    ) {
        const originalMethod = descriptor.value;
        descriptor.value = async function (...args: any[]) {
            const cache = options.cacheService || defaultCache;
            const key = typeof options.key === 'function'
                ? options.key(...args)
                : options.key || `${propertyKey}:${JSON.stringify(args)}`;
            if (options.condition && !options.condition(...args)) {
                return await originalMethod.apply(this, args);
            }
            const cached = await cache.get(key);
            if (cached !== null && cached !== undefined) {
                return cached;
            }
            const result = await originalMethod.apply(this, args);
            await cache.set(key, result, options.ttl);
            return result;
        };
        return descriptor;
    };
}

export function InvalidateCache(options: InvalidateCacheOptions = {}) {
    return function (
        target: any,
        propertyKey: string,
        descriptor: PropertyDescriptor
    ) {
        const originalMethod = descriptor.value;
        descriptor.value = async function (...args: any[]) {
            const cache = options.cacheService || defaultCache;
            const key = typeof options.key === 'function'
                ? options.key(...args)
                : options.key || `${propertyKey}:${JSON.stringify(args)}`;
            const result = await originalMethod.apply(this, args);
            await cache.delete(key);
            return result;
        };
        return descriptor;
    };
} 