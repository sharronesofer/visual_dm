/**
 * Central Event Bus implementation for cross-system notifications
 */

import { ISceneEvent, SceneEventType } from './SceneEventTypes';
import { DependencyRegistry } from './DependencyRegistry';

/**
 * Priority levels for event handlers
 */
export enum EventPriority {
    HIGH = 0,
    NORMAL = 1,
    LOW = 2,
    BACKGROUND = 3
}

/**
 * Options for event subscription
 */
export interface EventSubscriptionOptions {
    /** Priority of this handler (lower number = higher priority) */
    priority?: EventPriority;
    /** If true, the handler is executed only once */
    once?: boolean;
    /** Optional filter function to determine if handler should be executed */
    filter?: (event: ISceneEvent) => boolean;
}

/**
 * Handler type for scene events
 */
export type EventHandler = (event: ISceneEvent) => void | Promise<void>;

/**
 * Interface for event handler registration with metadata
 */
interface IEventHandlerRegistration {
    /** The handler function */
    handler: EventHandler;
    /** Handler options */
    options: EventSubscriptionOptions;
    /** Optional subscriber ID for dependency filtering */
    subscriberId?: string;
}

/**
 * Configuration for advanced event filtering and optimization
 */
export interface EventBusConfig {
    batchSize?: number;
    batchIntervalMs?: number;
    debounceIntervals?: Partial<Record<SceneEventType, number>>;
    throttleIntervals?: Partial<Record<SceneEventType, number>>;
    spatialFilters?: Partial<Record<SceneEventType, (event: ISceneEvent) => boolean>>;
    temporalFilters?: Partial<Record<SceneEventType, (event: ISceneEvent) => boolean>>;
    enableBatching?: boolean;
    enableDebounce?: boolean;
    enableThrottle?: boolean;
}

/**
 * Log levels for EventBus
 */
export enum EventBusLogLevel {
    ERROR = 0,
    WARN = 1,
    INFO = 2,
    DEBUG = 3
}

/**
 * Central Event Bus implementation for scene management.
 * Follows the Singleton pattern for global access.
 */
export class EventBus {
    private static instance: EventBus;

    /** 
     * Mapping of event types to their registered handlers
     * Map<EventType, Array<{handler, options}>>
     */
    private handlers: Map<SceneEventType, IEventHandlerRegistration[]> = new Map();

    /** Statistics for monitoring and debugging */
    private stats = {
        emitted: new Map<SceneEventType, number>(),
        handled: new Map<SceneEventType, number>(),
        lastEvent: new Map<SceneEventType, number>(),
        errors: new Map<SceneEventType, number>()
    };

    /** Flag to enable/disable event logging */
    private logEvents = true;

    private config: EventBusConfig = {
        batchSize: 10,
        batchIntervalMs: 50,
        debounceIntervals: {},
        throttleIntervals: {},
        spatialFilters: {},
        temporalFilters: {},
        enableBatching: true,
        enableDebounce: true,
        enableThrottle: true
    };
    private batchQueue: ISceneEvent[] = [];
    private batchTimer: NodeJS.Timeout | null = null;
    private lastEventTimestamps: Map<SceneEventType, number> = new Map();
    private debounceTimers: Map<SceneEventType, NodeJS.Timeout> = new Map();
    private throttleTimestamps: Map<SceneEventType, number> = new Map();
    private metrics = {
        batchedEvents: 0,
        droppedEvents: 0,
        filteredEvents: 0,
        throughput: 0,
        handlerTimes: [] as number[],
    };

    private logLevel: EventBusLogLevel = EventBusLogLevel.INFO;
    private eventReplayBuffer: ISceneEvent[] = [];
    private replayBufferSize = 1000;
    private handlerFailureCounts: Map<EventHandler, number> = new Map();
    private circuitBreakerThreshold = 5;
    private circuitBreakerTimeout = 60000; // 1 min
    private circuitBreakerStates: Map<EventHandler, 'closed' | 'open' | 'half-open'> = new Map();
    private circuitBreakerTimers: Map<EventHandler, NodeJS.Timeout> = new Map();
    private retryConfigs: Map<EventHandler, { attempts: number; maxAttempts: number; backoff: number; }> = new Map();

    /**
     * Private constructor to prevent direct instantiation
     */
    private constructor() { }

    /**
     * Get the singleton instance
     */
    public static getInstance(): EventBus {
        if (!EventBus.instance) {
            EventBus.instance = new EventBus();
        }
        return EventBus.instance;
    }

    /**
     * Subscribe to a specific event type
     * 
     * @param type The event type to subscribe to
     * @param handler The handler function to be called
     * @param options Subscription options
     * @param subscriberId Optional subscriber ID for dependency filtering
     * @returns The event bus instance for chaining
     */
    public on(
        type: SceneEventType,
        handler: EventHandler,
        options: EventSubscriptionOptions = {},
        subscriberId?: string
    ): EventBus {
        if (!this.handlers.has(type)) {
            this.handlers.set(type, []);
        }
        const finalOptions: EventSubscriptionOptions = {
            priority: EventPriority.NORMAL,
            ...options
        };
        const handlers = this.handlers.get(type)!;
        handlers.push({ handler, options: finalOptions, subscriberId });
        handlers.sort((a, b) =>
            (a.options.priority ?? EventPriority.NORMAL) -
            (b.options.priority ?? EventPriority.NORMAL)
        );
        return this;
    }

    /**
     * Subscribe to an event type and automatically unsubscribe after first execution
     * 
     * @param type The event type to subscribe to
     * @param handler The handler function to be called
     * @param options Subscription options
     * @returns The event bus instance for chaining
     */
    public once(
        type: SceneEventType,
        handler: EventHandler,
        options: EventSubscriptionOptions = {}
    ): EventBus {
        return this.on(type, handler, { ...options, once: true });
    }

    /**
     * Unsubscribe a handler from an event type
     * 
     * @param type The event type to unsubscribe from
     * @param handler The handler function to remove
     * @returns The event bus instance for chaining
     */
    public off(type: SceneEventType, handler: EventHandler): EventBus {
        if (!this.handlers.has(type)) {
            return this;
        }

        const handlers = this.handlers.get(type)!;
        const index = handlers.findIndex(reg => reg.handler === handler);

        if (index !== -1) {
            handlers.splice(index, 1);
        }

        return this;
    }

    /**
     * Set configuration for event bus optimizations
     */
    public setConfig(config: Partial<EventBusConfig>): void {
        this.config = { ...this.config, ...config };
    }

    /**
     * Emit an event to all subscribed handlers, with batching, filtering, and optimization
     */
    public async emit(event: ISceneEvent): Promise<boolean> {
        // Set timestamp if not already set
        if (!event.timestamp) {
            event.timestamp = Date.now();
        }

        const type = event.type;

        // Update statistics
        this.incrementStat(this.stats.emitted, type);
        this.stats.lastEvent.set(type, event.timestamp);

        // Log the event if configured
        if (this.logEvents) {
            console.log(`[EventBus] Emitting ${type}`,
                event.sceneId ? `for scene ${event.sceneId}` : '',
                event.data ? `with data: ${JSON.stringify(event.data)}` : ''
            );
        }

        // Debounce logic
        if (this.config.enableDebounce && this.config.debounceIntervals?.[type]) {
            if (this.debounceTimers.has(type)) {
                clearTimeout(this.debounceTimers.get(type)!);
            }
            this.debounceTimers.set(type, setTimeout(() => {
                this._emitWithOptimizations(event);
                this.debounceTimers.delete(type);
            }, this.config.debounceIntervals[type]));
            return true;
        }
        // Throttle logic
        if (this.config.enableThrottle && this.config.throttleIntervals?.[type]) {
            const now = Date.now();
            const last = this.throttleTimestamps.get(type) || 0;
            if (now - last < this.config.throttleIntervals[type]!) {
                this.metrics.droppedEvents++;
                return false;
            }
            this.throttleTimestamps.set(type, now);
        }
        // Batching logic
        if (this.config.enableBatching && this.isBatchCompatible(type)) {
            this.batchQueue.push(event);
            if (!this.batchTimer) {
                this.batchTimer = setTimeout(() => {
                    this._emitBatch();
                }, this.config.batchIntervalMs);
            }
            if (this.batchQueue.length >= this.config.batchSize!) {
                this._emitBatch();
            }
            return true;
        }
        // Otherwise, emit immediately with filtering
        return this._emitWithOptimizations(event);
    }

    /**
     * Internal: Emit a batch of events
     */
    private async _emitBatch() {
        const batch = this.batchQueue.splice(0, this.batchQueue.length);
        this.batchTimer = null;
        for (const event of batch) {
            await this._emitWithOptimizations(event);
        }
        this.metrics.batchedEvents += batch.length;
    }

    /**
     * Internal: Emit with spatial/temporal filtering and metrics
     */
    private async _emitWithOptimizations(event: ISceneEvent): Promise<boolean> {
        const type = event.type;
        // Spatial filtering
        if (this.config.spatialFilters?.[type] && !this.config.spatialFilters[type]!(event)) {
            this.metrics.filteredEvents++;
            return false;
        }
        // Temporal filtering
        if (this.config.temporalFilters?.[type] && !this.config.temporalFilters[type]!(event)) {
            this.metrics.filteredEvents++;
            return false;
        }
        // Dependency-aware filtering
        const depRegistry = DependencyRegistry.getInstance();
        const interested = depRegistry.getInterestedSubscribers(event);
        const useDependencyFiltering = interested.size > 0;
        // Track handlers to remove (for 'once' subscriptions)
        const handlersToRemove: EventHandler[] = [];
        // Call all handlers
        for (const registration of this.handlers.get(type)!) {
            try {
                const { handler, options, subscriberId } = registration;
                // If dependency filtering is active, skip handlers not in the interested set
                if (useDependencyFiltering && subscriberId && !interested.has(subscriberId)) {
                    continue;
                }
                if (options.filter && !options.filter(event)) {
                    continue;
                }
                if (options.once) {
                    handlersToRemove.push(handler);
                }
                await Promise.resolve(handler(event));
                this.incrementStat(this.stats.handled, type);
            } catch (error) {
                this.incrementStat(this.stats.errors, type);
                console.error(`[EventBus] Error in handler for ${type}:`, error);
            }
        }
        for (const handler of handlersToRemove) {
            this.off(type, handler);
        }
        const start = performance.now?.() ?? Date.now();
        const result = await this._emitToHandlers(event);
        const end = performance.now?.() ?? Date.now();
        this.metrics.handlerTimes.push(end - start);
        this.metrics.throughput++;
        return result;
    }

    /**
     * Internal: Emit to handlers (with error handling, circuit breaker, and logging)
     */
    private async _emitToHandlers(event: ISceneEvent): Promise<boolean> {
        const type = event.type;
        if (!this.handlers.has(type)) {
            return false;
        }
        const handlers = this.handlers.get(type)!;
        if (handlers.length === 0) {
            return false;
        }
        // Add to replay buffer
        this.eventReplayBuffer.push(event);
        if (this.eventReplayBuffer.length > this.replayBufferSize) {
            this.eventReplayBuffer.shift();
        }
        const handlersToRemove: EventHandler[] = [];
        for (const registration of handlers) {
            const { handler, options, subscriberId } = registration;
            // Circuit breaker: skip if open
            if (this.circuitBreakerStates.get(handler) === 'open') {
                this.log(EventBusLogLevel.WARN, 'Handler skipped due to open circuit breaker', { handler });
                continue;
            }
            try {
                this.log(EventBusLogLevel.DEBUG, 'Delivering event to handler', { event, handler, subscriberId });
                const start = performance.now?.() ?? Date.now();
                await Promise.resolve(handler(event));
                const end = performance.now?.() ?? Date.now();
                this.metrics.handlerTimes.push(end - start);
                this.metrics.throughput++;
                this.handlerFailureCounts.set(handler, 0);
                if (this.circuitBreakerStates.get(handler) === 'half-open') {
                    this.circuitBreakerStates.set(handler, 'closed');
                    this.log(EventBusLogLevel.INFO, 'Circuit breaker closed for handler', { handler });
                }
                if (options.once) {
                    handlersToRemove.push(handler);
                }
            } catch (error) {
                await this.handleError(handler, event, error);
            }
        }
        for (const handler of handlersToRemove) {
            this.off(type, handler);
        }
        return true;
    }

    /**
     * Check if an event type is batch-compatible
     */
    private isBatchCompatible(type: SceneEventType): boolean {
        // Batch object transform and boundary events (see SceneEventTypes.ts)
        return [
            SceneEventType.COORDINATES_CHANGED,
            SceneEventType.BOUNDARY_CROSSED
        ].includes(type);
    }

    /**
     * Expose performance metrics
     */
    public getMetrics() {
        return { ...this.metrics };
    }

    /**
     * Get the number of subscribers for a specific event type
     * 
     * @param type The event type
     * @returns The number of subscribers
     */
    public getSubscriberCount(type: SceneEventType): number {
        if (!this.handlers.has(type)) {
            return 0;
        }
        return this.handlers.get(type)!.length;
    }

    /**
     * Check if there are any subscribers for a specific event type
     * 
     * @param type The event type
     * @returns True if there are subscribers
     */
    public hasSubscribers(type: SceneEventType): boolean {
        return this.getSubscriberCount(type) > 0;
    }

    /**
     * Clear all subscribers for a specific event type
     * 
     * @param type The event type
     * @returns The event bus instance for chaining
     */
    public clearSubscribers(type: SceneEventType): EventBus {
        if (this.handlers.has(type)) {
            this.handlers.set(type, []);
        }
        return this;
    }

    /**
     * Clear all subscribers for all event types
     * 
     * @returns The event bus instance for chaining
     */
    public clearAllSubscribers(): EventBus {
        this.handlers.clear();
        return this;
    }

    /**
     * Set whether events should be logged
     * 
     * @param enable True to enable logging, false to disable
     * @returns The event bus instance for chaining
     */
    public setLogging(enable: boolean): EventBus {
        this.logEvents = enable;
        return this;
    }

    /**
     * Get statistics about event handling
     * 
     * @returns Event statistics
     */
    public getStats(): Record<string, any> {
        return {
            emitted: Object.fromEntries(this.stats.emitted),
            handled: Object.fromEntries(this.stats.handled),
            lastEvent: Object.fromEntries(this.stats.lastEvent),
            errors: Object.fromEntries(this.stats.errors),
            subscribers: Object.fromEntries(
                Array.from(this.handlers.entries()).map(
                    ([type, handlers]) => [type, handlers.length]
                )
            )
        };
    }

    /**
     * Clear event statistics
     * 
     * @returns The event bus instance for chaining
     */
    public clearStats(): EventBus {
        this.stats.emitted.clear();
        this.stats.handled.clear();
        this.stats.lastEvent.clear();
        this.stats.errors.clear();
        return this;
    }

    /**
     * Helper method to increment a value in a map
     */
    private incrementStat(map: Map<SceneEventType, number>, key: SceneEventType): void {
        map.set(key, (map.get(key) || 0) + 1);
    }

    /**
     * Set log level for EventBus
     */
    public setLogLevel(level: EventBusLogLevel): void {
        this.logLevel = level;
    }

    /**
     * Log a message with structured context
     */
    private log(level: EventBusLogLevel, msg: string, context?: Record<string, any>) {
        if (level > this.logLevel) return;
        const levelStr = EventBusLogLevel[level];
        const out = { level: levelStr, msg, ...context };
        if (level === EventBusLogLevel.ERROR) {
            console.error('[EventBus]', out);
        } else if (level === EventBusLogLevel.WARN) {
            console.warn('[EventBus]', out);
        } else if (level === EventBusLogLevel.INFO) {
            console.info('[EventBus]', out);
        } else {
            console.debug('[EventBus]', out);
        }
    }

    /**
     * Central error handler for event processing
     */
    private async handleError(handler: EventHandler, event: ISceneEvent, error: any) {
        this.incrementStat(this.stats.errors, event.type);
        this.metrics.handlerTimes.push(0);
        this.log(EventBusLogLevel.ERROR, 'Handler error', { handler, event, error });
        // Circuit breaker logic
        const count = (this.handlerFailureCounts.get(handler) || 0) + 1;
        this.handlerFailureCounts.set(handler, count);
        if (count >= this.circuitBreakerThreshold) {
            this.circuitBreakerStates.set(handler, 'open');
            this.log(EventBusLogLevel.WARN, 'Circuit breaker opened for handler', { handler });
            // Set timer to half-open after timeout
            if (!this.circuitBreakerTimers.has(handler)) {
                this.circuitBreakerTimers.set(handler, setTimeout(() => {
                    this.circuitBreakerStates.set(handler, 'half-open');
                    this.log(EventBusLogLevel.INFO, 'Circuit breaker half-open for handler', { handler });
                    this.circuitBreakerTimers.delete(handler);
                }, this.circuitBreakerTimeout));
            }
        }
        // Retry logic (if configured)
        const retryCfg = this.retryConfigs.get(handler);
        if (retryCfg && retryCfg.attempts < retryCfg.maxAttempts) {
            retryCfg.attempts++;
            const backoff = retryCfg.backoff * Math.pow(2, retryCfg.attempts - 1);
            this.log(EventBusLogLevel.INFO, 'Retrying handler', { handler, attempt: retryCfg.attempts, backoff });
            await new Promise(res => setTimeout(res, backoff));
            try {
                await handler(event);
                this.handlerFailureCounts.set(handler, 0);
                this.circuitBreakerStates.set(handler, 'closed');
                this.log(EventBusLogLevel.INFO, 'Handler recovered after retry', { handler });
            } catch (err) {
                await this.handleError(handler, event, err);
            }
        }
    }

    /**
     * Replay recent events through the EventBus
     */
    public async replayEvents(filter?: (event: ISceneEvent) => boolean) {
        const events = filter ? this.eventReplayBuffer.filter(filter) : this.eventReplayBuffer;
        for (const event of events) {
            await this.emit(event);
        }
    }

    /**
     * Configure retry policy for a handler
     */
    public setRetryPolicy(handler: EventHandler, maxAttempts: number, backoff: number) {
        this.retryConfigs.set(handler, { attempts: 0, maxAttempts, backoff });
    }

    /**
     * Manually reset a circuit breaker for a handler
     */
    public resetCircuitBreaker(handler: EventHandler) {
        this.circuitBreakerStates.set(handler, 'closed');
        this.handlerFailureCounts.set(handler, 0);
        if (this.circuitBreakerTimers.has(handler)) {
            clearTimeout(this.circuitBreakerTimers.get(handler)!);
            this.circuitBreakerTimers.delete(handler);
        }
        this.log(EventBusLogLevel.INFO, 'Circuit breaker manually reset for handler', { handler });
    }
} 