import { Logger } from '../../utils/logger';
import { EventEmitter } from 'events';

/**
 * Event data for cache invalidation events
 */
export interface InvalidationEventData {
    /** The type of event that triggered the invalidation */
    eventType: string;
    /** The entity type that was affected */
    entityType: string;
    /** The ID of the entity that was affected */
    entityId?: string | number;
    /** Additional metadata for the invalidation event */
    metadata?: Record<string, any>;
    /** Timestamp when the event occurred */
    timestamp: number;
}

/**
 * Configuration options for event-driven invalidation
 */
export interface EventDrivenInvalidationConfig {
    /** Enable debouncing to prevent invalidation storms */
    enableDebouncing?: boolean;
    /** Debounce time in milliseconds */
    debounceTime?: number;
    /** Enable verbose logging */
    debug?: boolean;
}

/**
 * Handles event-driven cache invalidation through a pub-sub mechanism
 */
export class EventDrivenInvalidation {
    private eventEmitter = new EventEmitter();
    private debounceTimers: Map<string, NodeJS.Timeout> = new Map();
    private readonly enableDebouncing: boolean;
    private readonly debounceTime: number;
    private readonly logger: Logger;

    // Singleton instance
    private static instance: EventDrivenInvalidation;

    /**
     * Get the singleton instance
     * @param config Configuration options
     * @returns The EventDrivenInvalidation instance
     */
    public static getInstance(config?: EventDrivenInvalidationConfig): EventDrivenInvalidation {
        if (!EventDrivenInvalidation.instance) {
            EventDrivenInvalidation.instance = new EventDrivenInvalidation(config);
        }
        return EventDrivenInvalidation.instance;
    }

    /**
     * Creates a new EventDrivenInvalidation instance
     * @param config Configuration options
     */
    private constructor(config?: EventDrivenInvalidationConfig) {
        this.enableDebouncing = config?.enableDebouncing ?? true;
        this.debounceTime = config?.debounceTime ?? 300; // milliseconds
        this.logger = Logger.getInstance().child('EventDrivenInvalidation');

        // Set maximum number of listeners to avoid memory leaks
        this.eventEmitter.setMaxListeners(100);

        if (config?.debug) {
            this.logger.debug('Event-driven invalidation system initialized');
        }
    }

    /**
     * Subscribe to invalidation events
     * @param eventType Type of event to listen for
     * @param handler Function to call when the event occurs
     * @returns Unsubscribe function
     */
    public subscribe(
        eventType: string,
        handler: (data: InvalidationEventData) => void
    ): () => void {
        this.eventEmitter.on(eventType, handler);
        this.logger.debug(`Subscribed to invalidation event: ${eventType}`);

        // Return unsubscribe function
        return () => {
            this.eventEmitter.off(eventType, handler);
            this.logger.debug(`Unsubscribed from invalidation event: ${eventType}`);
        };
    }

    /**
     * Subscribe to all invalidation events
     * @param handler Function to call when any event occurs
     * @returns Unsubscribe function
     */
    public subscribeToAll(
        handler: (eventType: string, data: InvalidationEventData) => void
    ): () => void {
        const wrappedHandler = (data: InvalidationEventData) => {
            handler(data.eventType, data);
        };

        this.eventEmitter.on('*', wrappedHandler);
        this.logger.debug('Subscribed to all invalidation events');

        // Return unsubscribe function
        return () => {
            this.eventEmitter.off('*', wrappedHandler);
            this.logger.debug('Unsubscribed from all invalidation events');
        };
    }

    /**
     * Publish an invalidation event
     * @param eventType Type of event to publish
     * @param data Event data
     */
    public publish(
        eventType: string,
        data: Omit<InvalidationEventData, 'eventType' | 'timestamp'>
    ): void {
        const fullData: InvalidationEventData = {
            ...data,
            eventType,
            timestamp: Date.now()
        };

        if (this.enableDebouncing) {
            this.publishWithDebounce(eventType, fullData);
        } else {
            this.publishImmediate(eventType, fullData);
        }
    }

    /**
     * Publish an event for an entity creation
     * @param entityType Type of entity
     * @param entityId Entity ID
     * @param metadata Additional metadata
     */
    public publishCreate(
        entityType: string,
        entityId: string | number,
        metadata?: Record<string, any>
    ): void {
        this.publish(`${entityType}:created`, {
            entityType,
            entityId,
            metadata
        });
    }

    /**
     * Publish an event for an entity update
     * @param entityType Type of entity
     * @param entityId Entity ID
     * @param metadata Additional metadata
     */
    public publishUpdate(
        entityType: string,
        entityId: string | number,
        metadata?: Record<string, any>
    ): void {
        this.publish(`${entityType}:updated`, {
            entityType,
            entityId,
            metadata
        });
    }

    /**
     * Publish an event for an entity deletion
     * @param entityType Type of entity
     * @param entityId Entity ID
     * @param metadata Additional metadata
     */
    public publishDelete(
        entityType: string,
        entityId: string | number,
        metadata?: Record<string, any>
    ): void {
        this.publish(`${entityType}:deleted`, {
            entityType,
            entityId,
            metadata
        });
    }

    /**
     * Publish an event for a bulk operation
     * @param entityType Type of entity
     * @param operation Operation type (e.g., 'import', 'migrate')
     * @param metadata Additional metadata
     */
    public publishBulkOperation(
        entityType: string,
        operation: string,
        metadata?: Record<string, any>
    ): void {
        this.publish(`${entityType}:${operation}`, {
            entityType,
            metadata
        });
    }

    /**
     * Generate a unique key for debouncing events
     * @param eventType Event type
     * @param data Event data
     * @returns Debounce key
     */
    private getDebounceKey(eventType: string, data: InvalidationEventData): string {
        // Include entityId if available for more specific debouncing
        if (data.entityId !== undefined) {
            return `${eventType}:${data.entityType}:${data.entityId}`;
        }
        // Otherwise just use event type and entity type
        return `${eventType}:${data.entityType}`;
    }

    /**
     * Publish an event with debouncing
     * @param eventType Event type
     * @param data Event data
     */
    private publishWithDebounce(eventType: string, data: InvalidationEventData): void {
        const debounceKey = this.getDebounceKey(eventType, data);

        // Clear existing timer if any
        if (this.debounceTimers.has(debounceKey)) {
            clearTimeout(this.debounceTimers.get(debounceKey)!);
        }

        // Set new timer
        const timer = setTimeout(() => {
            this.publishImmediate(eventType, data);
            this.debounceTimers.delete(debounceKey);
        }, this.debounceTime);

        this.debounceTimers.set(debounceKey, timer);
    }

    /**
     * Publish an event immediately
     * @param eventType Event type
     * @param data Event data
     */
    private publishImmediate(eventType: string, data: InvalidationEventData): void {
        this.logger.debug(`Publishing invalidation event: ${eventType}`, data);

        // Emit specific event
        this.eventEmitter.emit(eventType, data);

        // Also emit wildcard event
        this.eventEmitter.emit('*', data);
    }
} 