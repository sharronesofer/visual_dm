export { Cache } from './Cache';
export { TagBasedCache, type TaggedCacheEntry, type TagMetadata, type TagBasedCacheConfig } from './TagBasedCache';
export { EventDrivenInvalidation, type InvalidationEventData, type EventDrivenInvalidationConfig } from './EventDrivenInvalidation';
export { CacheInvalidationStrategies, type CacheInvalidationConfig } from './CacheInvalidationStrategies';

// Create a default instance
import { TagBasedCache } from './TagBasedCache';
import { CacheInvalidationStrategies } from './CacheInvalidationStrategies';
import { EventDrivenInvalidation } from './EventDrivenInvalidation';

// Default singleton instances
export const defaultTagBasedCache = new TagBasedCache({
    maxItems: 5000,
    maxSize: 50 * 1024 * 1024, // 50MB
    defaultTTL: 5 * 60 * 1000, // 5 minutes
});

export const defaultInvalidationSystem = new CacheInvalidationStrategies({
    enableTimeBasedInvalidation: true,
    enableTagBasedInvalidation: true,
    enableEventDrivenInvalidation: true,
    defaultTTL: 3600 // 1 hour in seconds
});

// Initialize the invalidation system with the default cache
defaultInvalidationSystem.startInvalidationMonitoring(defaultTagBasedCache);

// Helper to invalidate by tags
export const invalidateByTags = (tags: string[]): number => {
    return defaultInvalidationSystem.invalidateByTags(tags);
};

// Helper to publish invalidation events
export const publishInvalidationEvent = (
    eventType: string,
    entityType: string,
    entityId?: string | number,
    metadata?: Record<string, any>
): void => {
    defaultInvalidationSystem.publishInvalidationEvent(eventType, entityType, entityId, metadata);
};

// Convenience functions for common invalidation operations
export const invalidateOnCreate = (
    entityType: string,
    entityId: string | number,
    metadata?: Record<string, any>
): void => {
    publishInvalidationEvent('created', entityType, entityId, metadata);
};

export const invalidateOnUpdate = (
    entityType: string,
    entityId: string | number,
    metadata?: Record<string, any>
): void => {
    publishInvalidationEvent('updated', entityType, entityId, metadata);
};

export const invalidateOnDelete = (
    entityType: string,
    entityId: string | number,
    metadata?: Record<string, any>
): void => {
    publishInvalidationEvent('deleted', entityType, entityId, metadata);
};

// Initialize the event-driven system
export const eventDrivenInvalidation = EventDrivenInvalidation.getInstance({
    enableDebouncing: true,
    debounceTime: 300,
    debug: process.env.NODE_ENV === 'development'
}); 