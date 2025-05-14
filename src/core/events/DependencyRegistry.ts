/**
 * DependencyRegistry: Allows systems to register interest in specific scene elements or properties for event filtering.
 */

export type DependencyDescriptor =
    | { type: 'scene'; sceneId: string }
    | { type: 'object'; objectId: string }
    | { type: 'property'; objectId: string; property: string }
    | { type: 'custom'; filter: (event: any) => boolean };

/**
 * Registry for managing event dependencies for subscribers.
 */
export class DependencyRegistry {
    private static instance: DependencyRegistry;
    private subscriberToDeps: Map<string, Set<DependencyDescriptor>> = new Map();
    private depToSubscribers: Map<string, Set<string>> = new Map();

    private constructor() { }

    /**
     * Get the singleton instance
     */
    public static getInstance(): DependencyRegistry {
        if (!DependencyRegistry.instance) {
            DependencyRegistry.instance = new DependencyRegistry();
        }
        return DependencyRegistry.instance;
    }

    /**
     * Register a dependency for a subscriber
     */
    public registerDependency(subscriberId: string, dep: DependencyDescriptor): void {
        if (!this.subscriberToDeps.has(subscriberId)) {
            this.subscriberToDeps.set(subscriberId, new Set());
        }
        this.subscriberToDeps.get(subscriberId)!.add(dep);
        const depKey = this.getDepKey(dep);
        if (!this.depToSubscribers.has(depKey)) {
            this.depToSubscribers.set(depKey, new Set());
        }
        this.depToSubscribers.get(depKey)!.add(subscriberId);
    }

    /**
     * Unregister a dependency for a subscriber
     */
    public unregisterDependency(subscriberId: string, dep: DependencyDescriptor): void {
        if (!this.subscriberToDeps.has(subscriberId)) return;
        this.subscriberToDeps.get(subscriberId)!.delete(dep);
        const depKey = this.getDepKey(dep);
        if (this.depToSubscribers.has(depKey)) {
            this.depToSubscribers.get(depKey)!.delete(subscriberId);
            if (this.depToSubscribers.get(depKey)!.size === 0) {
                this.depToSubscribers.delete(depKey);
            }
        }
    }

    /**
     * Clear all dependencies for a subscriber
     */
    public clearDependencies(subscriberId: string): void {
        if (!this.subscriberToDeps.has(subscriberId)) return;
        for (const dep of this.subscriberToDeps.get(subscriberId)!) {
            const depKey = this.getDepKey(dep);
            if (this.depToSubscribers.has(depKey)) {
                this.depToSubscribers.get(depKey)!.delete(subscriberId);
                if (this.depToSubscribers.get(depKey)!.size === 0) {
                    this.depToSubscribers.delete(depKey);
                }
            }
        }
        this.subscriberToDeps.delete(subscriberId);
    }

    /**
     * Get all dependencies for a subscriber
     */
    public getDependencies(subscriberId: string): Set<DependencyDescriptor> | undefined {
        return this.subscriberToDeps.get(subscriberId);
    }

    /**
     * Find all subscribers interested in a given event
     */
    public getInterestedSubscribers(event: any): Set<string> {
        const interested = new Set<string>();
        // Check sceneId
        if (event.sceneId) {
            const depKey = this.getDepKey({ type: 'scene', sceneId: event.sceneId });
            if (this.depToSubscribers.has(depKey)) {
                for (const sub of this.depToSubscribers.get(depKey)!) {
                    interested.add(sub);
                }
            }
        }
        // Check objectId
        if (event.objectId) {
            const depKey = this.getDepKey({ type: 'object', objectId: event.objectId });
            if (this.depToSubscribers.has(depKey)) {
                for (const sub of this.depToSubscribers.get(depKey)!) {
                    interested.add(sub);
                }
            }
        }
        // Check property
        if (event.objectId && event.property) {
            const depKey = this.getDepKey({ type: 'property', objectId: event.objectId, property: event.property });
            if (this.depToSubscribers.has(depKey)) {
                for (const sub of this.depToSubscribers.get(depKey)!) {
                    interested.add(sub);
                }
            }
        }
        // Check custom filters
        for (const [subscriberId, deps] of this.subscriberToDeps.entries()) {
            for (const dep of deps) {
                if (dep.type === 'custom' && dep.filter(event)) {
                    interested.add(subscriberId);
                }
            }
        }
        return interested;
    }

    /**
     * Helper to create a unique key for a dependency descriptor
     */
    private getDepKey(dep: DependencyDescriptor): string {
        switch (dep.type) {
            case 'scene':
                return `scene:${dep.sceneId}`;
            case 'object':
                return `object:${dep.objectId}`;
            case 'property':
                return `property:${dep.objectId}:${dep.property}`;
            case 'custom':
                return `custom:${dep.filter.toString()}`;
            default:
                return 'unknown';
        }
    }
} 