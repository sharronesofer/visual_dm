import { ResourceType, ResourceData } from './EconomicTypes';

// Resource Category Enum
export enum ResourceCategory {
    RENEWABLE = 'RENEWABLE',
    NON_RENEWABLE = 'NON_RENEWABLE',
    CONSUMABLE = 'CONSUMABLE',
    DURABLE = 'DURABLE',
}

// Resource Dependency Edge
export interface ResourceDependency {
    from: string; // resource id
    to: string;   // resource id
    transformationRule?: string;
}

// Core Resource Model
export interface EconomicResource {
    id: string;
    type: ResourceType;
    name: string;
    quantity: number;
    quality: number; // 0-100
    decayRate?: number; // per tick or per time unit
    category: ResourceCategory;
    dependencies?: ResourceDependency[];
    createdAt: number;
    updatedAt: number;
}

// Resource Repository for storage and retrieval
export class ResourceRepository {
    private resources: Map<string, EconomicResource> = new Map();

    add(resource: EconomicResource): void {
        this.resources.set(resource.id, resource);
    }

    get(id: string): EconomicResource | undefined {
        return this.resources.get(id);
    }

    update(id: string, update: Partial<EconomicResource>): void {
        const resource = this.resources.get(id);
        if (resource) {
            Object.assign(resource, update);
            resource.updatedAt = Date.now();
        }
    }

    remove(id: string): void {
        this.resources.delete(id);
    }

    getAll(): EconomicResource[] {
        return Array.from(this.resources.values());
    }

    serialize(): string {
        return JSON.stringify(this.getAll());
    }

    deserialize(data: string): void {
        const arr: EconomicResource[] = JSON.parse(data);
        arr.forEach(r => this.resources.set(r.id, r));
    }

    clear(): void {
        this.resources.clear();
    }
}

// Directed graph for resource dependency chains
export class ResourceDependencyGraph {
    private edges: ResourceDependency[] = [];

    addEdge(edge: ResourceDependency): void {
        this.edges.push(edge);
    }

    getDependencies(resourceId: string): ResourceDependency[] {
        return this.edges.filter(e => e.from === resourceId);
    }

    getDependents(resourceId: string): ResourceDependency[] {
        return this.edges.filter(e => e.to === resourceId);
    }

    clear(): void {
        this.edges = [];
    }
}

// Type for agent priority (could be extended with more sophisticated logic)
export interface AgentPriority {
    agentId: string;
    priority: number; // Higher = more important
}

// Type for group pooling
export interface ResourcePool {
    groupId: string;
    resourceIds: string[];
    shared: boolean;
}

// Allocation request
interface AllocationRequest {
    agentId: string;
    resourceId: string;
    quantity: number;
    priority: number;
    timestamp: number;
    expiresAt?: number;
}

// Allocation Manager for priority-based allocation, reservation, pooling, and conflict resolution
export class AllocationManager {
    private reservations: Map<string, AllocationRequest[]> = new Map();
    private pools: Map<string, ResourcePool> = new Map();

    // Reserve resources for an agent, with priority
    reserve(agentId: string, resourceId: string, quantity: number, priority = 0, expiresAt?: number): boolean {
        if (!this.reservations.has(resourceId)) {
            this.reservations.set(resourceId, []);
        }
        // Add request
        const req: AllocationRequest = { agentId, resourceId, quantity, priority, timestamp: Date.now(), expiresAt };
        this.reservations.get(resourceId)!.push(req);
        // Sort by priority (descending), then timestamp (FIFO for same priority)
        this.reservations.get(resourceId)!.sort((a, b) => b.priority - a.priority || a.timestamp - b.timestamp);
        return true;
    }

    // Release reservation
    release(agentId: string, resourceId: string): void {
        const res = this.reservations.get(resourceId);
        if (res) {
            this.reservations.set(resourceId, res.filter(r => r.agentId !== agentId));
        }
    }

    // Get reservations for a resource
    getReservations(resourceId: string): AllocationRequest[] {
        return this.reservations.get(resourceId) || [];
    }

    // Pooling: create or update a resource pool for a group
    createOrUpdatePool(groupId: string, resourceIds: string[], shared = true): void {
        this.pools.set(groupId, { groupId, resourceIds, shared });
    }

    // Get pool for a group
    getPool(groupId: string): ResourcePool | undefined {
        return this.pools.get(groupId);
    }

    // Conflict resolution: allocate available quantity based on priority
    allocate(resourceId: string, availableQuantity: number): { [agentId: string]: number } {
        const requests = this.getReservations(resourceId);
        let remaining = availableQuantity;
        const allocation: { [agentId: string]: number } = {};
        for (const req of requests) {
            if (remaining <= 0) break;
            const alloc = Math.min(req.quantity, remaining);
            allocation[req.agentId] = (allocation[req.agentId] || 0) + alloc;
            remaining -= alloc;
        }
        return allocation;
    }

    // Cleanup expired reservations
    cleanupExpired(): void {
        const now = Date.now();
        for (const [resourceId, reqs] of this.reservations.entries()) {
            this.reservations.set(resourceId, reqs.filter(r => !r.expiresAt || r.expiresAt > now));
        }
    }

    // TODO: Add thread/concurrency safety if running in a true multi-threaded environment
    // TODO: Add advanced conflict resolution (fairness, market rules, etc.)
}

// Consumption Tracker for real-time usage statistics and forecasting
export class ConsumptionTracker {
    private consumptionLog: Map<string, { agentId: string; quantity: number; timestamp: number; modifiers?: Record<string, number> }[]> = new Map();
    private consumptionCache: Map<string, { total: number; count: number; lastUpdated: number }> = new Map();

    // Log consumption with optional modifiers (e.g., agent state, environment)
    logConsumption(agentId: string, resourceId: string, quantity: number, modifiers?: Record<string, number>): void {
        if (!this.consumptionLog.has(resourceId)) {
            this.consumptionLog.set(resourceId, []);
        }
        const entry = { agentId, quantity, timestamp: Date.now(), modifiers };
        this.consumptionLog.get(resourceId)!.push(entry);
        // Update cache
        const cache = this.consumptionCache.get(resourceId) || { total: 0, count: 0, lastUpdated: 0 };
        cache.total += quantity;
        cache.count += 1;
        cache.lastUpdated = entry.timestamp;
        this.consumptionCache.set(resourceId, cache);
    }

    getConsumption(resourceId: string): { agentId: string; quantity: number; timestamp: number; modifiers?: Record<string, number> }[] {
        return this.consumptionLog.get(resourceId) || [];
    }

    // Get average consumption rate for a resource (optionally for an agent, and/or time window)
    getAverageConsumption(resourceId: string, agentId?: string, windowMs?: number): number {
        const now = Date.now();
        let entries = this.getConsumption(resourceId);
        if (agentId) entries = entries.filter(e => e.agentId === agentId);
        if (windowMs) entries = entries.filter(e => now - e.timestamp <= windowMs);
        if (!entries.length) return 0;
        const total = entries.reduce((sum, e) => sum + e.quantity, 0);
        return total / entries.length;
    }

    // Simple moving average forecast for next period
    forecastConsumption(resourceId: string, periods = 5): number {
        const entries = this.getConsumption(resourceId);
        if (entries.length < periods) return this.getAverageConsumption(resourceId);
        const recent = entries.slice(-periods);
        return recent.reduce((sum, e) => sum + e.quantity, 0) / periods;
    }

    // Exponential smoothing forecast
    forecastConsumptionExponential(resourceId: string, alpha = 0.5): number {
        const entries = this.getConsumption(resourceId);
        if (!entries.length) return 0;
        let forecast = entries[0].quantity;
        for (let i = 1; i < entries.length; i++) {
            forecast = alpha * entries[i].quantity + (1 - alpha) * forecast;
        }
        return forecast;
    }

    // Efficiency: resource used per agent, per window
    getEfficiency(resourceId: string, agentId: string, windowMs?: number): number {
        return this.getAverageConsumption(resourceId, agentId, windowMs);
    }

    // Get cached stats for a resource
    getCachedStats(resourceId: string) {
        return this.consumptionCache.get(resourceId);
    }

    // Clear cache (for testing or periodic reset)
    clearCache(): void {
        this.consumptionCache.clear();
    }
}

// Plugin interface for extensibility
export interface ResourcePlugin {
    name: string;
    apply(resource: EconomicResource): void;
}

// Configuration system for resource properties and behavior
export interface ResourceConfig {
    [resourceType: string]: Partial<EconomicResource>;
}

// Resource compatibility matrix for substitution
export type ResourceCompatibilityMatrix = {
    [resourceType: string]: string[]; // compatible substitutes
};

// Agent personality traits (stub)
export interface AgentPersonality {
    riskTolerance: number; // 0-1
    cooperation: number;   // 0-1
    hoarding: number;      // 0-1
    competitiveness: number; // 0-1
}

// Scarcity Response Manager
export class ScarcityResponseManager {
    private resourceThresholds: Map<string, number> = new Map(); // resourceId -> scarcity threshold
    private compatibilityMatrix: ResourceCompatibilityMatrix;
    private agentPersonalities: Map<string, AgentPersonality> = new Map();
    private reservationAdjustments: Map<string, number> = new Map(); // agentId -> hoarding factor

    constructor(compatibilityMatrix: ResourceCompatibilityMatrix = {}) {
        this.compatibilityMatrix = compatibilityMatrix;
    }

    // Set scarcity threshold for a resource
    setThreshold(resourceId: string, threshold: number) {
        this.resourceThresholds.set(resourceId, threshold);
    }

    // Register agent personality
    setAgentPersonality(agentId: string, personality: AgentPersonality) {
        this.agentPersonalities.set(agentId, personality);
    }

    // Check and trigger scarcity response for an agent
    handleScarcity(agentId: string, resourceId: string, currentLevel: number): ScarcityResponse {
        const threshold = this.resourceThresholds.get(resourceId) ?? 10;
        const personality = this.agentPersonalities.get(agentId) ?? { riskTolerance: 0.5, cooperation: 0.5, hoarding: 0.5, competitiveness: 0.5 };
        let response: ScarcityResponse = { agentId, resourceId, actions: [] };
        if (currentLevel < threshold) {
            // Substitution
            const substitutes = this.compatibilityMatrix[resourceId] || [];
            if (substitutes.length) {
                response.actions.push({ type: 'substitute', substitutes });
            }
            // Hoarding
            if (personality.hoarding > 0.7) {
                this.reservationAdjustments.set(agentId, 1.5); // Increase reservation by 50%
                response.actions.push({ type: 'hoard', factor: 1.5 });
            }
            // Competition
            if (personality.competitiveness > 0.7) {
                response.actions.push({ type: 'compete', strategy: 'bid-up' });
            }
            // Cooperation
            if (personality.cooperation > 0.7) {
                response.actions.push({ type: 'cooperate', strategy: 'share' });
            }
        }
        return response;
    }

    // Get hoarding factor for an agent
    getHoardingFactor(agentId: string): number {
        return this.reservationAdjustments.get(agentId) ?? 1.0;
    }

    // Stub: Alliance formation
    formAlliance(agentIds: string[]): void {
        // TODO: Implement alliance logic
    }

    // Stub: Resource sharing
    shareResource(agentId: string, resourceId: string, quantity: number): void {
        // TODO: Implement sharing logic
    }
}

// Scarcity response action types
export type ScarcityResponse = {
    agentId: string;
    resourceId: string;
    actions: Array<
        | { type: 'substitute'; substitutes: string[] }
        | { type: 'hoard'; factor: number }
        | { type: 'compete'; strategy: string }
        | { type: 'cooperate'; strategy: string }
    >;
};

// Simple observer/event system for event-based communication
export type ResourceEvent = 'resourceAdded' | 'resourceUpdated' | 'resourceRemoved' | 'resourceScarcity' | string;
export type ResourceEventHandler = (payload: any) => void;

export class ResourceEventBus {
    private listeners: Map<ResourceEvent, Set<ResourceEventHandler>> = new Map();

    on(event: ResourceEvent, handler: ResourceEventHandler) {
        if (!this.listeners.has(event)) this.listeners.set(event, new Set());
        this.listeners.get(event)!.add(handler);
    }
    off(event: ResourceEvent, handler: ResourceEventHandler) {
        this.listeners.get(event)?.delete(handler);
    }
    emit(event: ResourceEvent, payload: any) {
        this.listeners.get(event)?.forEach(handler => handler(payload));
    }
    clear() {
        this.listeners.clear();
    }
}

// Integration interfaces for external systems
export interface TradingSystem {
    onResourceEvent(event: ResourceEvent, handler: ResourceEventHandler): void;
    // ... other trading system methods
}
export interface MarketSystem {
    onResourceEvent(event: ResourceEvent, handler: ResourceEventHandler): void;
    // ... other market system methods
}

// Spatial partitioning stub (grid-based, for future expansion)
export class ResourceSpatialGrid {
    // For large-scale: partition resources by (x, y) or regionId
    // Here, just a stub for extensibility
    addResource(resource: EconomicResource, location: { x: number; y: number }): void {
        // TODO: Implement spatial indexing
    }
    getResourcesInRegion(regionId: string): EconomicResource[] {
        // TODO: Implement region-based lookup
        return [];
    }
}

// Extend EconomicAgentResourceManagementSystem
export class EconomicAgentResourceManagementSystem {
    private repository: ResourceRepository;
    private dependencyGraph: ResourceDependencyGraph;
    private allocationManager: AllocationManager;
    private consumptionTracker: ConsumptionTracker;
    private plugins: ResourcePlugin[] = [];
    private config: ResourceConfig = {};
    private scarcityResponseManager: ScarcityResponseManager;
    private eventBus: ResourceEventBus = new ResourceEventBus();
    private tradingSystem?: TradingSystem;
    private marketSystem?: MarketSystem;
    private spatialGrid: ResourceSpatialGrid = new ResourceSpatialGrid();

    constructor(config?: ResourceConfig, compatibilityMatrix: ResourceCompatibilityMatrix = {}) {
        this.repository = new ResourceRepository();
        this.dependencyGraph = new ResourceDependencyGraph();
        this.allocationManager = new AllocationManager();
        this.consumptionTracker = new ConsumptionTracker();
        this.plugins = [];
        this.config = config || {};
        this.scarcityResponseManager = new ScarcityResponseManager(compatibilityMatrix);
    }

    // Register external systems
    registerTradingSystem(tradingSystem: TradingSystem) {
        this.tradingSystem = tradingSystem;
        // Forward resource events to trading system
        this.eventBus.on('resourceScarcity', payload => tradingSystem.onResourceEvent('resourceScarcity', payload));
    }
    registerMarketSystem(marketSystem: MarketSystem) {
        this.marketSystem = marketSystem;
        // Forward resource events to market system
        this.eventBus.on('resourceScarcity', payload => marketSystem.onResourceEvent('resourceScarcity', payload));
    }

    // Event hooks for plugins
    registerPlugin(plugin: ResourcePlugin): void {
        this.plugins.push(plugin);
        // Optionally allow plugins to listen to events
        if ((plugin as any).onResourceEvent) {
            this.eventBus.on('resourceAdded', (plugin as any).onResourceEvent);
        }
    }

    // Emit resource events
    private emitResourceEvent(event: ResourceEvent, payload: any) {
        this.eventBus.emit(event, payload);
    }

    // Resource CRUD
    addResource(resource: EconomicResource): void {
        // Apply config defaults
        const cfg = this.config[resource.type];
        if (cfg) Object.assign(resource, cfg);
        this.plugins.forEach(p => p.apply(resource));
        this.repository.add(resource);
        this.emitResourceEvent('resourceAdded', resource);
    }

    updateResource(id: string, update: Partial<EconomicResource>): void {
        this.repository.update(id, update);
        this.emitResourceEvent('resourceUpdated', { id, update });
    }

    removeResource(id: string): void {
        this.repository.remove(id);
        this.emitResourceEvent('resourceRemoved', { id });
    }

    getResource(id: string): EconomicResource | undefined {
        return this.repository.get(id);
    }

    // Allocation
    reserveResource(agentId: string, resourceId: string, quantity: number, priority = 0, expiresAt?: number): boolean {
        return this.allocationManager.reserve(agentId, resourceId, quantity, priority, expiresAt);
    }

    releaseResourceReservation(agentId: string, resourceId: string): void {
        this.allocationManager.release(agentId, resourceId);
    }

    // Pooling API
    createOrUpdateResourcePool(groupId: string, resourceIds: string[], shared = true): void {
        this.allocationManager.createOrUpdatePool(groupId, resourceIds, shared);
    }

    getResourcePool(groupId: string): ResourcePool | undefined {
        return this.allocationManager.getPool(groupId);
    }

    // Allocate available quantity based on priority
    allocateResource(resourceId: string, availableQuantity: number): { [agentId: string]: number } {
        return this.allocationManager.allocate(resourceId, availableQuantity);
    }

    // Cleanup expired reservations
    cleanupExpiredReservations(): void {
        this.allocationManager.cleanupExpired();
    }

    // Consumption
    logConsumption(agentId: string, resourceId: string, quantity: number, modifiers?: Record<string, number>): void {
        this.consumptionTracker.logConsumption(agentId, resourceId, quantity, modifiers);
    }

    getConsumption(resourceId: string) {
        return this.consumptionTracker.getConsumption(resourceId);
    }

    // Forecasting API
    forecastResourceConsumption(resourceId: string, method: 'sma' | 'exp' = 'sma', options?: { periods?: number; alpha?: number }): number {
        if (method === 'exp') {
            return this.consumptionTracker.forecastConsumptionExponential(resourceId, options?.alpha ?? 0.5);
        }
        return this.consumptionTracker.forecastConsumption(resourceId, options?.periods ?? 5);
    }

    // Efficiency API
    getResourceEfficiency(resourceId: string, agentId?: string, windowMs?: number): number {
        if (agentId) {
            return this.consumptionTracker.getEfficiency(resourceId, agentId, windowMs);
        }
        // Default: average for all agents
        return this.consumptionTracker.getAverageConsumption(resourceId, undefined, windowMs);
    }

    // Cached stats API
    getCachedConsumptionStats(resourceId: string) {
        return this.consumptionTracker.getCachedStats(resourceId);
    }

    // Serialization/Deserialization
    serialize(): string {
        return this.repository.serialize();
    }

    deserialize(data: string): void {
        this.repository.deserialize(data);
    }

    // Scenario-based resource distribution entry point
    distributeResourcesForScenario(scenario: string): void {
        // TODO: Implement scenario logic (e.g., disaster, abundance, scarcity)
        this.emitResourceEvent('scenarioDistribution', { scenario });
    }

    // Load resource config from JSON/YAML
    async loadResourceConfig(path: string): Promise<ResourceConfig> {
        if (path.endsWith('.json')) {
            const config = await import(/* @vite-ignore */ path);
            this.config = config.default || config;
            return this.config;
        } else if (path.endsWith('.yaml') || path.endsWith('.yml')) {
            // TODO: Add YAML parsing (e.g., js-yaml)
            throw new Error('YAML config loading not implemented');
        } else {
            throw new Error('Unsupported config file type');
        }
    }

    // Add resource to spatial grid (stub)
    addResourceToSpatialGrid(resource: EconomicResource, location: { x: number; y: number }): void {
        this.spatialGrid.addResource(resource, location);
    }
    getResourcesInRegion(regionId: string): EconomicResource[] {
        return this.spatialGrid.getResourcesInRegion(regionId);
    }

    // Scarcity response API
    setScarcityThreshold(resourceId: string, threshold: number) {
        this.scarcityResponseManager.setThreshold(resourceId, threshold);
    }
    setAgentPersonality(agentId: string, personality: AgentPersonality) {
        this.scarcityResponseManager.setAgentPersonality(agentId, personality);
    }
    handleScarcity(agentId: string, resourceId: string, currentLevel: number): ScarcityResponse {
        return this.scarcityResponseManager.handleScarcity(agentId, resourceId, currentLevel);
    }
    getHoardingFactor(agentId: string): number {
        return this.scarcityResponseManager.getHoardingFactor(agentId);
    }
    // Stubs for alliance and sharing
    formAlliance(agentIds: string[]): void {
        this.scarcityResponseManager.formAlliance(agentIds);
    }
    shareResource(agentId: string, resourceId: string, quantity: number): void {
        this.scarcityResponseManager.shareResource(agentId, resourceId, quantity);
    }

    // TODO: Add integration points for trading system, market features, and microservices
    // TODO: Add performance optimizations, caching, and plugin architecture
}

export { ResourceType }; 