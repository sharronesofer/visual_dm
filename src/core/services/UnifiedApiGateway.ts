import { EconomicSystemAdapter } from '../../systems/economy/EconomicSystemAdapter';
import { ReputationSystemAdapter } from '../../systems/npc/ReputationSystemAdapter';
import { InventorySystemAdapter } from '../systems/InventorySystemAdapter';

// Service registry for dynamic discovery
export class ServiceRegistry {
    private static instance: ServiceRegistry;
    private services: Map<string, any> = new Map();
    private capabilities: Map<string, SystemCapability> = new Map();
    private healthStatus: Map<string, 'healthy' | 'degraded' | 'unavailable'> = new Map();

    private constructor() { }

    public static getInstance(): ServiceRegistry {
        if (!ServiceRegistry.instance) {
            ServiceRegistry.instance = new ServiceRegistry();
        }
        return ServiceRegistry.instance;
    }

    public registerService(name: string, service: any) {
        this.services.set(name, service);
    }

    public getService<T>(name: string): T | undefined {
        return this.services.get(name);
    }

    public listServices(): string[] {
        return Array.from(this.services.keys());
    }

    public registerCapability(name: string, capability: SystemCapability) {
        this.capabilities.set(name, capability);
    }

    public getCapability(name: string): SystemCapability | undefined {
        return this.capabilities.get(name);
    }

    public setHealth(name: string, status: 'healthy' | 'degraded' | 'unavailable') {
        this.healthStatus.set(name, status);
    }

    public getHealth(name: string): 'healthy' | 'degraded' | 'unavailable' | undefined {
        return this.healthStatus.get(name);
    }

    public listCapabilities(): SystemCapability[] {
        return Array.from(this.capabilities.values());
    }
}

// Unified API Gateway
export class UnifiedApiGateway {
    private static instance: UnifiedApiGateway;
    private registry: ServiceRegistry;
    private version: string = '1.0.0';
    private throttlers: Map<string, TokenBucket> = new Map();

    private constructor() {
        this.registry = ServiceRegistry.getInstance();
    }

    public static getInstance(): UnifiedApiGateway {
        if (!UnifiedApiGateway.instance) {
            UnifiedApiGateway.instance = new UnifiedApiGateway();
        }
        return UnifiedApiGateway.instance;
    }

    // Register a system adapter
    public registerAdapter(name: string, adapter: any) {
        this.registry.registerService(name, adapter);
    }

    // Register a throttler
    public registerThrottler(service: string, capacity: number, refillRate: number) {
        this.throttlers.set(service, new TokenBucket(capacity, refillRate));
    }

    // Invoke a method on a registered adapter
    public async invoke(
        serviceName: string,
        method: string,
        args: any[] = [],
        version: string = this.version
    ): Promise<APIResponse> {
        // Throttling
        const throttler = this.throttlers.get(serviceName);
        if (throttler && !throttler.tryRemoveToken()) {
            return { success: false, error: 'Rate limit exceeded', version };
        }
        const service = this.registry.getService<any>(serviceName);
        if (!service) {
            return { success: false, error: `Service '${serviceName}' not found`, version };
        }
        // Contract enforcement
        let contract: any;
        switch (serviceName) {
            case 'economy':
                contract = (service as EconomyApi);
                break;
            case 'reputation':
                contract = (service as ReputationApi);
                break;
            case 'inventory':
                contract = (service as InventoryApi);
                break;
            default:
                contract = service;
        }
        if (typeof contract[method] !== 'function') {
            return { success: false, error: `Method '${method}' not found on service '${serviceName}'`, version };
        }
        try {
            const result = await contract[method](...args);
            return { success: true, data: result, version };
        } catch (err: any) {
            return { success: false, error: err?.message || String(err), version };
        }
    }

    public getVersion(): string {
        return this.version;
    }

    public listServices(): string[] {
        return this.registry.listServices();
    }

    public getCapabilities(): SystemCapability[] {
        return this.registry.listCapabilities();
    }

    public getHealth(service: string): 'healthy' | 'degraded' | 'unavailable' | undefined {
        return this.registry.getHealth(service);
    }
}

// --- API Request/Response and Capability Models ---
/**
 * Represents a request to a system API via the UnifiedApiGateway.
 */
export interface APIRequest {
    /** Target service name (e.g., 'economy', 'reputation', 'inventory') */
    service: string;
    /** Method to invoke on the service */
    method: string;
    /** Arguments to pass to the method */
    args: any[];
    /** Optional API version */
    version?: string;
    /** Optional metadata for tracing, auth, etc. */
    metadata?: Record<string, any>;
}

/**
 * Standardized response from a system API call.
 */
export interface APIResponse {
    /** Whether the call was successful */
    success: boolean;
    /** Data returned from the call, if any */
    data?: any;
    /** Error message, if the call failed */
    error?: string;
    /** API version */
    version?: string;
    /** Optional metadata */
    metadata?: Record<string, any>;
}

/**
 * Describes the capabilities of a registered system service.
 */
export interface SystemCapability {
    /** Service name */
    name: string;
    /** Human-readable description */
    description?: string;
    /** List of supported operations */
    operations: string[];
    /** Version of the service */
    version: string;
    /** Health status */
    health?: 'healthy' | 'degraded' | 'unavailable';
}

// --- TokenBucket for Throttling ---
/**
 * Implements a token bucket algorithm for request rate limiting.
 */
class TokenBucket {
    private tokens: number;
    private lastRefill: number;
    /**
     * @param capacity Maximum number of tokens in the bucket
     * @param refillRate Tokens added per second
     */
    constructor(private capacity: number, private refillRate: number) {
        this.tokens = capacity;
        this.lastRefill = Date.now();
    }
    /**
     * Attempt to remove a token. Returns true if allowed, false if rate-limited.
     */
    tryRemoveToken(): boolean {
        this.refill();
        if (this.tokens > 0) {
            this.tokens--;
            return true;
        }
        return false;
    }
    /**
     * Refill tokens based on elapsed time.
     */
    refill() {
        const now = Date.now();
        const elapsed = (now - this.lastRefill) / 1000;
        const refillAmount = Math.floor(elapsed * this.refillRate);
        if (refillAmount > 0) {
            this.tokens = Math.min(this.capacity, this.tokens + refillAmount);
            this.lastRefill = now;
        }
    }
}

// --- Serialization Utilities ---
/**
 * Utility for serializing and deserializing API requests and responses.
 * Designed for future extensibility (e.g., Protocol Buffers).
 */
export class SerializationUtil {
    /** Serialize an APIRequest to a string (JSON for now) */
    static serializeRequest(request: APIRequest): string {
        return JSON.stringify(request);
    }
    /** Deserialize a string to an APIRequest */
    static deserializeRequest(data: string): APIRequest {
        return JSON.parse(data);
    }
    /** Serialize an APIResponse to a string (JSON for now) */
    static serializeResponse(response: APIResponse): string {
        return JSON.stringify(response);
    }
    /** Deserialize a string to an APIResponse */
    static deserializeResponse(data: string): APIResponse {
        return JSON.parse(data);
    }
}

// --- System-Specific API Contracts ---
/**
 * Contract for the Economy system API.
 */
export interface EconomyApi {
    /** Get the balance for an agent */
    getBalance(agentId: string): Promise<number>;
    /** Transfer funds between agents */
    transferFunds(fromAgentId: string, toAgentId: string, amount: number): Promise<boolean>;
    /** Get transaction history for an agent */
    getTransactionHistory(agentId: string): Promise<any[]>;
}

/**
 * Contract for the Reputation system API.
 */
export interface ReputationApi {
    /** Get the reputation score for an agent */
    getReputation(agentId: string): Promise<number>;
    /** Modify the reputation score for an agent */
    modifyReputation(agentId: string, delta: number): Promise<boolean>;
    /** Get reputation history for an agent */
    getReputationHistory(agentId: string): Promise<any[]>;
}

/**
 * Contract for the Inventory system API.
 */
export interface InventoryApi {
    /** Get the inventory for an agent */
    getInventory(agentId: string): Promise<any[]>;
    /** Add an item to an agent's inventory */
    addItem(agentId: string, item: any): Promise<boolean>;
    /** Remove an item from an agent's inventory */
    removeItem(agentId: string, itemId: string): Promise<boolean>;
    /** Update an item in an agent's inventory */
    updateItem(agentId: string, item: any): Promise<boolean>;
} 