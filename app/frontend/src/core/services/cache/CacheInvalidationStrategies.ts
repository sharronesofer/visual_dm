import { Logger } from '../../utils/logger';
import { TagBasedCache } from './TagBasedCache';
import { EventDrivenInvalidation, InvalidationEventData } from './EventDrivenInvalidation';

/**
 * Configuration options for cache invalidation strategies
 */
export interface CacheInvalidationConfig {
    /** Enable time-based invalidation */
    enableTimeBasedInvalidation?: boolean;
    /** Enable tag-based invalidation */
    enableTagBasedInvalidation?: boolean;
    /** Enable event-driven invalidation */
    enableEventDrivenInvalidation?: boolean;
    /** Default time-to-live for entries in seconds */
    defaultTTL?: number;
    /** Enable verbose logging */
    debug?: boolean;
}

/**
 * Manages different cache invalidation strategies
 */
export class CacheInvalidationStrategies {
    private readonly logger: Logger;
    private readonly enableTimeBasedInvalidation: boolean;
    private readonly enableTagBasedInvalidation: boolean;
    private readonly enableEventDrivenInvalidation: boolean;
    private readonly defaultTTL: number;
    private tagBasedCache: TagBasedCache | null = null;
    private eventSystem: EventDrivenInvalidation | null = null;
    private unsubscribeFunctions: Array<() => void> = [];

    /**
     * Create a new cache invalidation strategies manager
     * @param config Configuration options
     */
    constructor(config?: CacheInvalidationConfig) {
        this.logger = Logger.getInstance().child('CacheInvalidationStrategies');
        this.enableTimeBasedInvalidation = config?.enableTimeBasedInvalidation ?? true;
        this.enableTagBasedInvalidation = config?.enableTagBasedInvalidation ?? true;
        this.enableEventDrivenInvalidation = config?.enableEventDrivenInvalidation ?? true;
        this.defaultTTL = config?.defaultTTL ?? 3600; // 1 hour default

        if (config?.debug) {
            this.logger.debug('Cache invalidation strategies initialized');
        }
    }

    /**
     * Start monitoring for cache invalidation events
     * @param tagBasedCache The tag-based cache to manage
     */
    public startInvalidationMonitoring(tagBasedCache: TagBasedCache): void {
        this.tagBasedCache = tagBasedCache;

        // Set up time-based invalidation
        if (this.enableTimeBasedInvalidation) {
            this.setupTimeBasedInvalidation();
        }

        // Set up event-driven invalidation
        if (this.enableEventDrivenInvalidation) {
            this.setupEventDrivenInvalidation();
        }

        this.logger.debug('Cache invalidation monitoring started');
    }

    /**
     * Stop all invalidation monitoring and clean up resources
     */
    public stopInvalidationMonitoring(): void {
        // Unsubscribe from all events
        this.unsubscribeFunctions.forEach(unsubscribe => unsubscribe());
        this.unsubscribeFunctions = [];

        this.tagBasedCache = null;
        this.logger.debug('Cache invalidation monitoring stopped');
    }

    /**
     * Setup time-based invalidation with scheduled cleanup
     */
    private setupTimeBasedInvalidation(): void {
        // Run cleanup every minute to remove expired entries
        const cleanupInterval = setInterval(() => {
            if (!this.tagBasedCache) {
                clearInterval(cleanupInterval);
                return;
            }

            const now = Date.now();
            const removedCount = this.tagBasedCache.removeExpired();

            if (removedCount > 0) {
                this.logger.debug(`Removed ${removedCount} expired cache entries`);
            }
        }, 60000); // 1 minute interval

        // Store cleanup function for later removal
        this.unsubscribeFunctions.push(() => clearInterval(cleanupInterval));
    }

    /**
     * Setup event-driven invalidation with event handlers
     */
    private setupEventDrivenInvalidation(): void {
        if (!this.tagBasedCache) {
            return;
        }

        this.eventSystem = EventDrivenInvalidation.getInstance();

        // Subscribe to all invalidation events
        const unsubscribeAll = this.eventSystem.subscribeToAll(
            (eventType: string, data: InvalidationEventData) => {
                this.handleInvalidationEvent(eventType, data);
            }
        );

        this.unsubscribeFunctions.push(unsubscribeAll);
    }

    /**
     * Process an invalidation event
     * @param eventType Type of event
     * @param data Event data
     */
    private handleInvalidationEvent(eventType: string, data: InvalidationEventData): void {
        if (!this.tagBasedCache) {
            return;
        }

        this.logger.debug(`Processing invalidation event: ${eventType}`, data);

        // Extract entity type and operation from event type
        const [entityType, operation] = eventType.split(':');

        // Handle different operations
        switch (operation) {
            case 'created':
            case 'updated':
            case 'deleted':
                // Invalidate by entity type and ID if available
                if (data.entityId !== undefined) {
                    // Invalidate by specific entity ID
                    const specificTag = `${entityType}:${data.entityId}`;
                    this.tagBasedCache.invalidateByTags([specificTag]);

                    // Also invalidate collection queries for this entity type
                    this.tagBasedCache.invalidateByTags([entityType]);
                } else {
                    // If no ID provided, invalidate all entries with this entity type
                    this.tagBasedCache.invalidateByTags([entityType]);
                }
                break;

            case 'bulk':
            case 'import':
            case 'migrate':
                // For bulk operations, invalidate everything related to this entity type
                this.tagBasedCache.invalidateByTags([entityType]);
                break;

            default:
                if (data.entityType) {
                    // For unknown operations with entity type, invalidate by entity type
                    this.tagBasedCache.invalidateByTags([data.entityType]);
                }
        }
    }

    /**
     * Manually invalidate cache entries by tags
     * @param tags Tags to invalidate
     * @returns Number of cache entries removed
     */
    public invalidateByTags(tags: string[]): number {
        if (!this.tagBasedCache || !this.enableTagBasedInvalidation) {
            return 0;
        }

        const count = this.tagBasedCache.invalidateByTags(tags);
        this.logger.debug(`Manually invalidated ${count} cache entries with tags: ${tags.join(', ')}`);
        return count;
    }

    /**
     * Generate expiration timestamp based on TTL
     * @param ttl Time-to-live in seconds
     * @returns Expiration timestamp
     */
    public getExpirationTime(ttl?: number): number {
        const seconds = ttl ?? this.defaultTTL;
        return Date.now() + (seconds * 1000);
    }

    /**
* Manually invalidate all cache entries
* @returns Number of entries removed
*/
    public invalidateAll(): number {
        if (!this.tagBasedCache) {
            return 0;
        }

        // Use the clear method which now returns the count of removed entries
        const count = this.tagBasedCache.clear();

        this.logger.debug(`Manually invalidated all ${count} cache entries`);
        return count;
    }

    /**
     * Publish an invalidation event
     * @param eventType Event type
     * @param entityType Entity type
     * @param entityId Optional entity ID
     * @param metadata Optional metadata
     */
    public publishInvalidationEvent(
        eventType: string,
        entityType: string,
        entityId?: string | number,
        metadata?: Record<string, any>
    ): void {
        if (!this.enableEventDrivenInvalidation || !this.eventSystem) {
            return;
        }

        this.eventSystem.publish(`${entityType}:${eventType}`, {
            entityType,
            entityId,
            metadata
        });
    }
} 