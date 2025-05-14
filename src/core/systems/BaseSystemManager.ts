/**
 * BaseSystemManager.ts
 * 
 * Provides a foundation for all system managers with common functionality like
 * initialization, event handling, dependencies, and lifecycle management.
 */

import { globalDatabase, DatabaseAdapter, Repository } from './DatabaseLayer';
import { BaseEntity } from './DataModels';

export interface SystemDependency {
    name: string;
    required: boolean;
}

export interface SystemEvent {
    type: string;
    source: string;
    timestamp: number;
    data: any;
}

export interface SystemEventHandler {
    (event: SystemEvent): Promise<void> | void;
}

export interface SystemConfig {
    name: string;
    dependencies?: SystemDependency[];
    autoInitialize?: boolean;
    database?: DatabaseAdapter;
    debug?: boolean;
}

/**
 * Base class for all system managers
 */
export abstract class BaseSystemManager {
    protected name: string;
    protected initialized: boolean = false;
    protected dependencies: Map<string, SystemDependency>;
    protected eventHandlers: Map<string, SystemEventHandler[]>;
    protected repositories: Map<string, Repository<any>>;
    protected db: DatabaseAdapter;
    protected debug: boolean;

    constructor(config: SystemConfig) {
        this.name = config.name;
        this.dependencies = new Map();
        this.eventHandlers = new Map();
        this.repositories = new Map();
        this.db = config.database || globalDatabase;
        this.debug = config.debug || false;

        // Register dependencies
        if (config.dependencies) {
            config.dependencies.forEach(dep => {
                this.dependencies.set(dep.name, dep);
            });
        }

        // Auto-initialize if specified
        if (config.autoInitialize) {
            this.initialize().catch(err => {
                this.logError(`Error auto-initializing system ${this.name}:`, err);
            });
        }
    }

    /**
     * Initialize the system
     */
    public async initialize(): Promise<void> {
        if (this.initialized) {
            this.logWarn(`System ${this.name} is already initialized`);
            return;
        }

        this.logInfo(`Initializing system: ${this.name}`);

        try {
            // Check dependencies
            const missingDeps = this.checkDependencies();
            if (missingDeps.length > 0) {
                const requiredMissing = missingDeps.filter(dep => dep.required);
                if (requiredMissing.length > 0) {
                    throw new Error(`Missing required dependencies: ${requiredMissing.map(d => d.name).join(', ')}`);
                } else {
                    this.logWarn(`Missing optional dependencies: ${missingDeps.map(d => d.name).join(', ')}`);
                }
            }

            // Initialize repositories
            await this.initializeRepositories();

            // Initialize specific system
            await this.initializeSystem();

            this.initialized = true;
            this.logInfo(`System ${this.name} initialized successfully`);

            // Emit initialization event
            this.emitEvent({
                type: 'system:initialized',
                source: this.name,
                timestamp: Date.now(),
                data: { name: this.name }
            });
        } catch (error) {
            this.logError(`Failed to initialize system ${this.name}:`, error);
            throw error;
        }
    }

    /**
     * Shutdown the system gracefully
     */
    public async shutdown(): Promise<void> {
        if (!this.initialized) {
            this.logWarn(`System ${this.name} is not initialized`);
            return;
        }

        this.logInfo(`Shutting down system: ${this.name}`);

        try {
            // Shutdown specific system
            await this.shutdownSystem();

            this.initialized = false;
            this.logInfo(`System ${this.name} shut down successfully`);

            // Emit shutdown event
            this.emitEvent({
                type: 'system:shutdown',
                source: this.name,
                timestamp: Date.now(),
                data: { name: this.name }
            });
        } catch (error) {
            this.logError(`Failed to shut down system ${this.name}:`, error);
            throw error;
        }
    }

    /**
     * Register an event handler
     */
    public on(eventType: string, handler: SystemEventHandler): void {
        if (!this.eventHandlers.has(eventType)) {
            this.eventHandlers.set(eventType, []);
        }
        this.eventHandlers.get(eventType)?.push(handler);
        this.logDebug(`Registered handler for event: ${eventType}`);
    }

    /**
     * Unregister an event handler
     */
    public off(eventType: string, handler: SystemEventHandler): void {
        if (!this.eventHandlers.has(eventType)) return;

        const handlers = this.eventHandlers.get(eventType) || [];
        const index = handlers.indexOf(handler);
        if (index !== -1) {
            handlers.splice(index, 1);
            this.logDebug(`Unregistered handler for event: ${eventType}`);
        }
    }

    /**
     * Emit an event
     */
    public async emitEvent(event: SystemEvent): Promise<void> {
        if (!this.initialized && event.type !== 'system:initialized') {
            this.logWarn(`Attempted to emit event ${event.type} from uninitialized system ${this.name}`);
            return;
        }

        this.logDebug(`Emitting event: ${event.type} from ${event.source}`);

        const handlers = this.eventHandlers.get(event.type) || [];
        const globalHandlers = this.eventHandlers.get('*') || [];
        const allHandlers = [...handlers, ...globalHandlers];

        for (const handler of allHandlers) {
            try {
                await Promise.resolve(handler(event));
            } catch (error) {
                this.logError(`Error in event handler for ${event.type}:`, error);
            }
        }
    }

    /**
     * Register a dependency on another system
     */
    public registerDependency(name: string, required: boolean = true): void {
        this.dependencies.set(name, { name, required });
        this.logDebug(`Registered ${required ? 'required' : 'optional'} dependency on: ${name}`);
    }

    /**
     * Get system status
     */
    public getStatus(): { name: string; initialized: boolean; dependencies: SystemDependency[] } {
        return {
            name: this.name,
            initialized: this.initialized,
            dependencies: Array.from(this.dependencies.values())
        };
    }

    /**
     * Create a repository for an entity type
     */
    protected createRepository<T extends BaseEntity>(
        name: string,
        indexedFields: string[] = []
    ): Repository<T> {
        const repository = new Repository<T>(this.db, `${this.name}_${name}`, indexedFields);
        this.repositories.set(name, repository);
        return repository;
    }

    /**
     * Methods that must be implemented by subclasses
     */
    protected abstract initializeSystem(): Promise<void>;
    protected abstract shutdownSystem(): Promise<void>;
    protected abstract initializeRepositories(): Promise<void>;

    /**
     * Check if all required dependencies are available
     */
    private checkDependencies(): SystemDependency[] {
        const missing: SystemDependency[] = [];

        for (const dep of this.dependencies.values()) {
            // In a real implementation, this would check a system registry
            // For now, we'll just simulate that all dependencies are available
            const isAvailable = true; // Placeholder for actual dependency check

            if (!isAvailable) {
                missing.push(dep);
            }
        }

        return missing;
    }

    /**
     * Logging methods
     */
    protected logDebug(message: string, ...args: any[]): void {
        if (this.debug) {
            console.debug(`[${this.name}] ${message}`, ...args);
        }
    }

    protected logInfo(message: string, ...args: any[]): void {
        console.info(`[${this.name}] ${message}`, ...args);
    }

    protected logWarn(message: string, ...args: any[]): void {
        console.warn(`[${this.name}] ${message}`, ...args);
    }

    protected logError(message: string, ...args: any[]): void {
        console.error(`[${this.name}] ${message}`, ...args);
    }
}

/**
 * System registry for managing system dependencies
 */
export class SystemRegistry {
    private static instance: SystemRegistry;
    private systems: Map<string, BaseSystemManager>;

    private constructor() {
        this.systems = new Map();
    }

    public static getInstance(): SystemRegistry {
        if (!SystemRegistry.instance) {
            SystemRegistry.instance = new SystemRegistry();
        }
        return SystemRegistry.instance;
    }

    /**
     * Register a system
     */
    public registerSystem(system: BaseSystemManager): void {
        const { name } = system.getStatus();
        this.systems.set(name, system);
        console.info(`System registered: ${name}`);
    }

    /**
     * Get a system by name
     */
    public getSystem<T extends BaseSystemManager>(name: string): T | null {
        return (this.systems.get(name) as T) || null;
    }

    /**
     * Check if a system is registered
     */
    public hasSystem(name: string): boolean {
        return this.systems.has(name);
    }

    /**
     * Initialize all systems respecting dependencies
     */
    public async initializeAllSystems(): Promise<void> {
        const initialized = new Set<string>();
        const systemNames = Array.from(this.systems.keys());

        // Keep track of which systems have been initialized to avoid infinite loops
        let progress = true;
        while (progress && initialized.size < systemNames.length) {
            progress = false;

            for (const name of systemNames) {
                if (initialized.has(name)) continue;

                const system = this.systems.get(name)!;
                const { dependencies } = system.getStatus();
                const requiredDeps = dependencies.filter(d => d.required);

                // Check if all required dependencies are initialized
                const canInitialize = requiredDeps.every(dep =>
                    !this.systems.has(dep.name) || initialized.has(dep.name)
                );

                if (canInitialize) {
                    try {
                        await system.initialize();
                        initialized.add(name);
                        progress = true;
                        console.info(`Initialized system: ${name}`);
                    } catch (error) {
                        console.error(`Failed to initialize system ${name}:`, error);
                        throw error;
                    }
                }
            }
        }

        // Check for uninitialized systems
        const uninitialized = systemNames.filter(name => !initialized.has(name));
        if (uninitialized.length > 0) {
            console.error(`Unable to initialize systems: ${uninitialized.join(', ')}`);
            throw new Error(`Failed to initialize all systems. Possible circular dependencies.`);
        }
    }

    /**
     * Shutdown all systems in reverse dependency order
     */
    public async shutdownAllSystems(): Promise<void> {
        // Shutdown in reverse initialization order
        const systemNames = Array.from(this.systems.keys());

        for (let i = systemNames.length - 1; i >= 0; i--) {
            const name = systemNames[i];
            const system = this.systems.get(name)!;

            try {
                await system.shutdown();
                console.info(`Shut down system: ${name}`);
            } catch (error) {
                console.error(`Failed to shut down system ${name}:`, error);
            }
        }
    }
}

/**
 * Global system registry instance
 */
export const systemRegistry = SystemRegistry.getInstance(); 