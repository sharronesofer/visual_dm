/**
 * Scene Event System for integration between Scene Management and related systems.
 * 
 * This system provides a specialized interface for scene-related events and manages
 * the integration between the Scene Manager and dependent systems like spatial, 
 * region, worldgen, and analytics systems.
 */

import { EventBus, EventHandler, EventPriority, EventSubscriptionOptions } from './EventBus';
import { ISceneEvent, SceneEventType } from './SceneEventTypes';

/**
 * Types of dependencies a system can have on scenes
 */
export enum DependencyType {
    /** Dependent on all scene changes */
    ALL = 'all',
    /** Dependent on scene creation/activation/etc. */
    SCENE_LIFECYCLE = 'scene',
    /** Dependent on asset loading/unloading */
    ASSETS = 'assets',
    /** Dependent on scene spatial properties */
    SPATIAL = 'spatial',
    /** Dependent on scene world generation */
    WORLDGEN = 'worldgen',
    /** Dependent on memory management events */
    MEMORY = 'memory',
    /** Dependent on analytics data */
    ANALYTICS = 'analytics'
}

/**
 * Helper for creating a scene event
 */
export function createSceneEvent(
    type: SceneEventType,
    sceneId?: string,
    source: string = 'SceneManager',
    data?: Record<string, any>
): ISceneEvent {
    return {
        type,
        sceneId,
        source,
        timestamp: Date.now(),
        data
    };
}

/**
 * Manages event-driven integration between Scene Manager and other systems.
 */
export class SceneEventSystem {
    private static instance: SceneEventSystem;

    /** The underlying event bus */
    private eventBus: EventBus;

    /** Mapping of system IDs to their dependency types */
    private systemDependencies: Map<string, Set<DependencyType>> = new Map();

    /** Scene-specific event listeners */
    private sceneListeners: Map<string, Map<SceneEventType, EventHandler[]>> = new Map();

    /** Configuration options */
    private config = {
        logEvents: true,
        propagateImmediately: false,  // If true, bypass queue for critical events
        maxQueuedEvents: 1000         // Maximum events to queue before dropping
    };

    /**
     * Private constructor to enforce singleton pattern
     */
    private constructor() {
        this.eventBus = EventBus.getInstance();
    }

    /**
     * Get the singleton instance
     */
    public static getInstance(): SceneEventSystem {
        if (!SceneEventSystem.instance) {
            SceneEventSystem.instance = new SceneEventSystem();
        }
        return SceneEventSystem.instance;
    }

    /**
     * Register a system's dependency on specific scene event types
     * 
     * @param systemId Unique identifier for the system
     * @param dependencies Types of dependencies this system has
     */
    public registerSystemDependency(
        systemId: string,
        dependencies: DependencyType[]
    ): void {
        if (!this.systemDependencies.has(systemId)) {
            this.systemDependencies.set(systemId, new Set());
        }

        const systemDeps = this.systemDependencies.get(systemId)!;
        for (const dep of dependencies) {
            systemDeps.add(dep);
        }

        console.log(`[SceneEventSystem] Registered system '${systemId}' with dependencies:`,
            Array.from(systemDeps).join(', ')
        );
    }

    /**
     * Unregister a system's dependencies
     * 
     * @param systemId Unique identifier for the system
     */
    public unregisterSystemDependency(systemId: string): void {
        if (this.systemDependencies.has(systemId)) {
            this.systemDependencies.delete(systemId);
            console.log(`[SceneEventSystem] Unregistered system '${systemId}'`);
        }
    }

    /**
     * Register a listener for a specific scene and event type
     * 
     * @param sceneId Scene to listen for events from
     * @param eventType Type of event to listen for
     * @param handler Function to call when event occurs
     */
    public registerSceneListener(
        sceneId: string,
        eventType: SceneEventType,
        handler: EventHandler
    ): void {
        if (!this.sceneListeners.has(sceneId)) {
            this.sceneListeners.set(sceneId, new Map());
        }

        const sceneEvents = this.sceneListeners.get(sceneId)!;
        if (!sceneEvents.has(eventType)) {
            sceneEvents.set(eventType, []);
        }

        sceneEvents.get(eventType)!.push(handler);

        // Subscribe to the event in the event bus
        this.ensureEventBusSubscription(eventType);

        console.log(`[SceneEventSystem] Registered listener for scene '${sceneId}', event ${eventType}`);
    }

    /**
     * Unregister a listener for a specific scene and event type
     * 
     * @param sceneId Scene ID
     * @param eventType Event type
     * @param handler Callback to remove
     * @returns True if found and removed, False otherwise
     */
    public unregisterSceneListener(
        sceneId: string,
        eventType: SceneEventType,
        handler: EventHandler
    ): boolean {
        if (!this.sceneListeners.has(sceneId) ||
            !this.sceneListeners.get(sceneId)!.has(eventType)) {
            return false;
        }

        const handlers = this.sceneListeners.get(sceneId)!.get(eventType)!;
        const index = handlers.indexOf(handler);

        if (index !== -1) {
            handlers.splice(index, 1);
            console.log(`[SceneEventSystem] Unregistered listener for scene '${sceneId}', event ${eventType}`);
            return true;
        }

        return false;
    }

    /**
     * Register a global listener for all scenes of a particular event type
     * 
     * @param eventType Type of event to listen for
     * @param handler Function to call when event occurs
     * @param options Subscription options
     */
    public registerGlobalListener(
        eventType: SceneEventType,
        handler: EventHandler,
        options: EventSubscriptionOptions = {}
    ): void {
        this.eventBus.on(eventType, handler, options);
        console.log(`[SceneEventSystem] Registered global listener for event ${eventType}`);
    }

    /**
     * Unregister a global listener
     * 
     * @param eventType Event type
     * @param handler Callback to remove
     * @returns True if found and removed, False otherwise
     */
    public unregisterGlobalListener(
        eventType: SceneEventType,
        handler: EventHandler
    ): boolean {
        // There's no direct way to check if removal was successful,
        // but we can check before and after subscriber counts
        const beforeCount = this.eventBus.getSubscriberCount(eventType);
        this.eventBus.off(eventType, handler);
        const afterCount = this.eventBus.getSubscriberCount(eventType);

        const removed = beforeCount > afterCount;
        if (removed) {
            console.log(`[SceneEventSystem] Unregistered global listener for event ${eventType}`);
        }

        return removed;
    }

    /**
     * Ensure we have an event bus subscription for this event type
     * This is called automatically when registering scene listeners
     * 
     * @param eventType Event type to subscribe to
     */
    private ensureEventBusSubscription(eventType: SceneEventType): void {
        // Check if we already have the handler registered
        if (this.eventBus.hasSubscribers(eventType)) {
            return;
        }

        // Subscribe to the event bus with our handler
        this.eventBus.on(
            eventType,
            (event) => this.handleEvent(event),
            { priority: EventPriority.HIGH }
        );
    }

    /**
     * Handle an event from the event bus
     * This is the callback registered with the event bus
     * 
     * @param event Event to handle
     */
    private handleEvent(event: ISceneEvent): void {
        try {
            const eventType = event.type;
            const sceneId = event.sceneId;

            // Log the event if configured
            if (this.config.logEvents) {
                console.log(`[SceneEventSystem] Handling event ${eventType}`,
                    sceneId ? `for scene ${sceneId}` : '',
                    event.data ? `with data: ${JSON.stringify(event.data)}` : ''
                );
            }

            // Call scene-specific listeners if applicable
            if (sceneId && this.sceneListeners.has(sceneId)) {
                const sceneEvents = this.sceneListeners.get(sceneId)!;
                if (sceneEvents.has(eventType)) {
                    for (const handler of sceneEvents.get(eventType)!) {
                        try {
                            handler(event);
                        } catch (error) {
                            console.error(`[SceneEventSystem] Error in scene event listener: ${error}`);
                        }
                    }
                }
            }
        } catch (error) {
            console.error(`[SceneEventSystem] Error handling event: ${error}`);
        }
    }

    /**
     * Emit a scene event to all listeners
     * 
     * @param eventType Type of event from SceneEventType enum
     * @param sceneId Optional ID of the scene related to this event
     * @param source Component/system that generated this event
     * @param data Additional data to include with the event
     * @param immediate Override config to publish immediately if True
     */
    public emitSceneEvent(
        eventType: SceneEventType,
        sceneId?: string,
        source: string = 'SceneManager',
        data?: Record<string, any>,
        immediate?: boolean
    ): void {
        const event = createSceneEvent(eventType, sceneId, source, data);

        // Determine if we should publish immediately
        const shouldPublishImmediate = immediate ?? this.config.propagateImmediately;

        // Emit the event (async by default, but can be immediate)
        if (shouldPublishImmediate) {
            this.eventBus.emit(event);
        } else {
            // Use setTimeout to make this async
            setTimeout(() => {
                this.eventBus.emit(event);
            }, 0);
        }
    }

    /**
     * Update a configuration setting
     * 
     * @param key Configuration key
     * @param value New value
     */
    public setConfig<K extends keyof SceneEventSystem['config']>(
        key: K,
        value: SceneEventSystem['config'][K]
    ): void {
        if (key in this.config) {
            this.config[key] = value;
            console.log(`[SceneEventSystem] Updated config: ${key} = ${value}`);
        } else {
            console.warn(`[SceneEventSystem] Unknown config key: ${key}`);
        }
    }

    /**
     * Get a configuration value
     * 
     * @param key Configuration key
     * @returns Configuration value
     */
    public getConfig<K extends keyof SceneEventSystem['config']>(
        key: K
    ): SceneEventSystem['config'][K] {
        return this.config[key];
    }

    /**
     * Get statistics about event processing
     * 
     * @returns Event system statistics
     */
    public getStats(): Record<string, any> {
        const stats = this.eventBus.getStats();

        // Add our own stats
        stats.systemDependencies = Object.fromEntries(
            Array.from(this.systemDependencies.entries()).map(
                ([systemId, deps]) => [systemId, Array.from(deps)]
            )
        );

        stats.sceneListeners = Object.fromEntries(
            Array.from(this.sceneListeners.entries()).map(
                ([sceneId, eventMap]) => [
                    sceneId,
                    Object.fromEntries(
                        Array.from(eventMap.entries()).map(
                            ([eventType, handlers]) => [eventType, handlers.length]
                        )
                    )
                ]
            )
        );

        return stats;
    }

    /**
     * Clear event statistics
     */
    public clearStats(): void {
        this.eventBus.clearStats();
    }

    /**
     * Shut down the scene event system
     */
    public shutdown(): void {
        // Clear all subscriptions
        this.systemDependencies.clear();
        this.sceneListeners.clear();

        // The event bus manages its own handler map
        this.eventBus.clearAllSubscribers();

        console.log('[SceneEventSystem] Shut down');
    }
} 