import { RedisCacheService } from './RedisCacheService';
import { Logger } from '../utils/logger';

type WarmerFn = (cache: RedisCacheService) => Promise<void>;

export class CacheWarmer {
    private cache: RedisCacheService;
    private logger: Logger;
    private warmers: Map<string, WarmerFn> = new Map();

    constructor(cache: RedisCacheService, logger?: Logger) {
        this.cache = cache;
        this.logger = logger || new Logger({ prefix: 'CacheWarmer' });
    }

    register(name: string, fn: WarmerFn) {
        this.warmers.set(name, fn);
        this.logger.info(`Registered cache warmer: ${name}`);
    }

    async warmAll() {
        for (const [name, fn] of this.warmers.entries()) {
            try {
                this.logger.info(`Warming cache: ${name}`);
                await fn(this.cache);
                this.logger.info(`Cache warmed: ${name}`);
            } catch (err) {
                this.logger.error(`Cache warming failed: ${name}`, { err });
            }
        }
    }

    async warm(name: string) {
        const fn = this.warmers.get(name);
        if (!fn) {
            this.logger.warn(`No cache warmer registered for: ${name}`);
            return;
        }
        try {
            this.logger.info(`Warming cache: ${name}`);
            await fn(this.cache);
            this.logger.info(`Cache warmed: ${name}`);
        } catch (err) {
            this.logger.error(`Cache warming failed: ${name}`, { err });
        }
    }

    // Optionally, schedule background refresh
    scheduleAll(intervalMs: number) {
        setInterval(() => {
            this.warmAll();
        }, intervalMs);
        this.logger.info(`Scheduled cache warming every ${intervalMs}ms`);
    }
} 