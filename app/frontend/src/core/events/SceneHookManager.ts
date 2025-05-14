/**
 * Scene Hook Manager Implementation
 * Provides the core implementation of the scene lifecycle hooks and callbacks system.
 */

import { v4 as uuidv4 } from 'uuid';
import { SceneEventType } from './SceneEventTypes';
import { EventBus } from './EventBus';
import {
    CallbackPriority,
    ExecutionPhase,
    ErrorHandlingStrategy,
    ICallbackOptions,
    ICallbackContext,
    HookCallback,
    ICallbackRegistration,
    ICallbackExecutionResult,
    IHookExecutionResult,
    ISceneHookManager
} from './SceneHooks';
import { ISceneEvent } from './SceneEventTypes';

/**
 * Implementation of the Scene Hook Manager
 * Manages registration and execution of callbacks for scene lifecycle events
 */
export class SceneHookManager implements ISceneHookManager {
    private static instance: SceneHookManager;

    // Map of hook types to their registered callbacks
    // Map<HookType, Map<CallbackId, CallbackRegistration>>
    private hooks: Map<SceneEventType, Map<string, ICallbackRegistration>> = new Map();

    // Track dependencies between callbacks for correct execution ordering
    private dependencyGraph: Map<string, Set<string>> = new Map();

    // Reference to the event bus for integrating with the event system
    private eventBus: EventBus;

    // Debug mode flag
    private debugMode: boolean = false;

    /**
     * Private constructor to enforce singleton pattern
     */
    private constructor() {
        this.eventBus = EventBus.getInstance();
    }

    /**
     * Get the singleton instance of SceneHookManager
     */
    public static getInstance(): SceneHookManager {
        if (!SceneHookManager.instance) {
            SceneHookManager.instance = new SceneHookManager();
        }
        return SceneHookManager.instance;
    }

    /**
     * Enable or disable debug mode
     */
    public setDebugMode(enable: boolean): void {
        this.debugMode = enable;
    }

    /**
     * Register a callback for a specific hook type
     * 
     * @param hookType The type of hook to register for
     * @param callback The callback function to execute when the hook fires
     * @param options Optional configuration for the callback execution
     * @returns A unique ID for the registered callback (used for unregistering)
     */
    public register(
        hookType: SceneEventType,
        callback: HookCallback,
        options: ICallbackOptions = {}
    ): string {
        // Ensure the hook type exists in our map
        if (!this.hooks.has(hookType)) {
            this.hooks.set(hookType, new Map());
        }

        // Generate an ID if one wasn't provided
        const callbackId = options.id || uuidv4();

        // Prepare the registration with defaults
        const registration: ICallbackRegistration = {
            callback,
            options: {
                priority: CallbackPriority.NORMAL,
                phase: ExecutionPhase.MAIN,
                errorHandling: ErrorHandlingStrategy.LOG,
                ...options,
                id: callbackId
            },
            executionCount: 0
        };

        // Store the callback
        this.hooks.get(hookType)!.set(callbackId, registration);

        // Process dependencies if any
        if (options.dependencies && options.dependencies.length > 0) {
            this.processDependencies(callbackId, options.dependencies);
        }

        if (this.debugMode) {
            console.log(`[SceneHookManager] Registered callback ${callbackId} for hook ${hookType}`);
        }

        return callbackId;
    }

    /**
     * Unregister a callback by its ID
     * 
     * @param callbackId The ID of the callback to unregister
     * @returns True if the callback was found and unregistered, false otherwise
     */
    public unregister(callbackId: string): boolean {
        let found = false;

        // Search through all hook types
        for (const [hookType, callbacks] of this.hooks.entries()) {
            if (callbacks.has(callbackId)) {
                callbacks.delete(callbackId);
                found = true;

                if (this.debugMode) {
                    console.log(`[SceneHookManager] Unregistered callback ${callbackId} from hook ${hookType}`);
                }

                // Remove from dependency graph if it exists
                this.removeDependency(callbackId);

                // Exit early once found
                break;
            }
        }

        return found;
    }

    /**
     * Unregister all callbacks for a specific hook type
     * 
     * @param hookType The hook type to clear callbacks for
     */
    public unregisterAll(hookType: SceneEventType): void {
        if (this.hooks.has(hookType)) {
            // Get all callback IDs to remove from dependency graph
            const callbackIds = Array.from(this.hooks.get(hookType)!.keys());

            // Clear the callbacks map
            this.hooks.get(hookType)!.clear();

            // Clean up dependencies
            for (const id of callbackIds) {
                this.removeDependency(id);
            }

            if (this.debugMode) {
                console.log(`[SceneHookManager] Unregistered all callbacks for hook ${hookType}`);
            }
        }
    }

    /**
     * Execute all callbacks registered for a specific hook
     * 
     * @param hookType The type of hook to execute
     * @param sceneId The ID of the scene this hook is related to
     * @param data Optional data to pass to callbacks
     * @param source The source of the hook execution (for tracking)
     * @returns Promise that resolves with execution results
     */
    public async executeHook<T = any>(
        hookType: SceneEventType,
        sceneId: string,
        data: T = {} as T,
        source: string = 'system'
    ): Promise<IHookExecutionResult> {
        const startTime = performance.now();
        const callbackResults: ICallbackExecutionResult[] = [];

        // If no callbacks are registered for this hook, return early
        if (!this.hasCallbacks(hookType)) {
            return {
                hookType,
                sceneId,
                callbackResults: [],
                totalExecutionTimeMs: 0,
                successCount: 0,
                failureCount: 0
            };
        }

        // Create the context object to pass to callbacks
        const context: ICallbackContext<T> = {
            sceneId,
            hookType,
            timestamp: Date.now(),
            data,
            source
        };

        if (this.debugMode) {
            console.log(`[SceneHookManager] Executing hook ${hookType} for scene ${sceneId}`);
        }

        // Get callbacks for this hook
        const callbacks = this.hooks.get(hookType)!;

        // Also create an event for the EventBus
        this.eventBus.emit({
            type: hookType,
            sceneId,
            source,
            timestamp: context.timestamp,
            data: (typeof data === 'object' && data !== null) ? (data as Record<string, any>) : undefined
        });

        // Execute callbacks in three phases: PRE, MAIN, POST
        for (const phase of [ExecutionPhase.PRE, ExecutionPhase.MAIN, ExecutionPhase.POST]) {
            // Filter and sort callbacks for this phase
            const phaseCallbacks = Array.from(callbacks.entries())
                .filter(([_, reg]) => (reg.options.phase || ExecutionPhase.MAIN) === phase)
                .sort((a, b) => {
                    // Sort by priority (lower number first)
                    const priorityA = a[1].options.priority || CallbackPriority.NORMAL;
                    const priorityB = b[1].options.priority || CallbackPriority.NORMAL;
                    return priorityA - priorityB;
                });

            // Sort based on dependencies (topological sort)
            const sortedCallbacks = this.sortByDependencies(phaseCallbacks.map(([id]) => id));

            // Execute each callback in order
            for (const callbackId of sortedCallbacks) {
                if (!callbacks.has(callbackId)) continue; // Skip if removed during execution

                const registration = callbacks.get(callbackId)!;
                const result = await this.executeCallback(callbackId, registration, context);
                callbackResults.push(result);

                // Handle maxExecutions limit
                if (result.removed) {
                    callbacks.delete(callbackId);
                    this.removeDependency(callbackId);
                }
            }
        }

        // Calculate summary statistics
        const endTime = performance.now();
        const totalExecutionTimeMs = endTime - startTime;
        const successCount = callbackResults.filter(r => r.success).length;
        const failureCount = callbackResults.length - successCount;

        const result: IHookExecutionResult = {
            hookType,
            sceneId,
            callbackResults,
            totalExecutionTimeMs,
            successCount,
            failureCount
        };

        if (this.debugMode) {
            console.log(`[SceneHookManager] Hook ${hookType} execution complete:`,
                `${successCount} succeeded, ${failureCount} failed, ${totalExecutionTimeMs.toFixed(2)}ms`);
        }

        return result;
    }

    /**
     * Check if a hook has any registered callbacks
     * 
     * @param hookType The hook type to check
     * @returns True if the hook has at least one callback registered
     */
    public hasCallbacks(hookType: SceneEventType): boolean {
        return this.hooks.has(hookType) && this.hooks.get(hookType)!.size > 0;
    }

    /**
     * Get the number of callbacks registered for a hook
     * 
     * @param hookType The hook type to check
     * @returns The number of callbacks registered
     */
    public getCallbackCount(hookType: SceneEventType): number {
        if (!this.hooks.has(hookType)) {
            return 0;
        }
        return this.hooks.get(hookType)!.size;
    }

    /**
     * Execute a single callback with error handling and timeout management
     * 
     * @param callbackId ID of the callback
     * @param registration The callback registration
     * @param context The context to pass to the callback
     * @returns Result of the execution
     */
    private async executeCallback<T>(
        callbackId: string,
        registration: ICallbackRegistration,
        context: ICallbackContext<T>
    ): Promise<ICallbackExecutionResult> {
        const { callback, options } = registration;
        const { timeoutMs, errorHandling, maxRetries, fallback } = options;

        const startTime = performance.now();
        let success = false;
        let error: Error | undefined;
        let removed = false;

        try {
            // If timeout is specified, wrap the callback in a promise race
            if (timeoutMs && timeoutMs > 0) {
                await Promise.race([
                    this.executeWithRetries(callback, context, errorHandling, maxRetries),
                    new Promise((_, reject) =>
                        setTimeout(() => reject(new Error(`Callback timeout after ${timeoutMs}ms`)), timeoutMs)
                    )
                ]);
            } else {
                // Otherwise just execute with retry logic
                await this.executeWithRetries(callback, context, errorHandling, maxRetries);
            }

            success = true;
        } catch (err) {
            error = err as Error;
            success = false;

            // Handle errors based on the specified strategy
            if (errorHandling === ErrorHandlingStrategy.THROW) {
                // Propagate the error
                throw error;
            } else if (errorHandling === ErrorHandlingStrategy.FALLBACK && fallback) {
                try {
                    // Try the fallback function
                    await fallback(error, context);
                    success = true; // Fallback succeeded
                } catch (fallbackError) {
                    // Fallback also failed
                    if (this.debugMode) {
                        console.error(`[SceneHookManager] Fallback for callback ${callbackId} also failed:`, fallbackError);
                    }
                }
            }

            // Log the error for all strategies
            if (this.debugMode || errorHandling === ErrorHandlingStrategy.LOG) {
                console.error(`[SceneHookManager] Error in callback ${callbackId}:`, error);
            }
        }

        // Update the callback's execution count
        registration.executionCount++;
        registration.lastExecuted = Date.now();

        // Check if we need to remove the callback due to maxExecutions
        if (options.maxExecutions && registration.executionCount >= options.maxExecutions) {
            removed = true;
        }

        const endTime = performance.now();
        const executionTimeMs = endTime - startTime;

        return {
            callbackId,
            success,
            error,
            executionTimeMs,
            removed
        };
    }

    /**
     * Execute a callback with retry logic
     * 
     * @param callback The callback function to execute
     * @param context The context to pass to the callback
     * @param errorHandling The error handling strategy
     * @param maxRetries Maximum number of retries
     */
    private async executeWithRetries<T>(
        callback: HookCallback<T>,
        context: ICallbackContext<T>,
        errorHandling?: ErrorHandlingStrategy,
        maxRetries: number = 3
    ): Promise<void> {
        let lastError: Error | undefined;
        const shouldRetry = errorHandling === ErrorHandlingStrategy.RETRY;

        // Try up to maxRetries + 1 times (initial + retries)
        for (let attempt = 0; attempt <= (shouldRetry ? maxRetries : 0); attempt++) {
            try {
                await callback(context);
                return; // Success, exit
            } catch (err) {
                lastError = err as Error;

                // Only retry if we're not on the last attempt
                if (shouldRetry && attempt < maxRetries) {
                    if (this.debugMode) {
                        console.warn(`[SceneHookManager] Retrying callback, attempt ${attempt + 1}/${maxRetries}`);
                    }
                    // Could implement exponential backoff here if needed
                    await new Promise(resolve => setTimeout(resolve, 50 * Math.pow(2, attempt)));
                } else {
                    // No more retries, rethrow
                    throw lastError;
                }
            }
        }

        // If we get here, all retries failed, throw the last error
        throw lastError;
    }

    /**
     * Process and store callback dependencies
     * 
     * @param callbackId The callback ID
     * @param dependencies IDs of callbacks this one depends on
     */
    private processDependencies(callbackId: string, dependencies: string[]): void {
        // Add to dependency graph
        for (const dependencyId of dependencies) {
            if (!this.dependencyGraph.has(dependencyId)) {
                this.dependencyGraph.set(dependencyId, new Set());
            }
            this.dependencyGraph.get(dependencyId)!.add(callbackId);
        }
    }

    /**
     * Remove a callback ID from the dependency graph
     * 
     * @param callbackId The callback ID to remove
     */
    private removeDependency(callbackId: string): void {
        // Remove as a dependency source
        this.dependencyGraph.delete(callbackId);

        // Remove as a dependent from other callbacks
        for (const deps of this.dependencyGraph.values()) {
            deps.delete(callbackId);
        }
    }

    /**
     * Sort callback IDs based on dependencies (topological sort)
     * 
     * @param callbackIds Array of callback IDs to sort
     * @returns Sorted array of callback IDs
     */
    private sortByDependencies(callbackIds: string[]): string[] {
        // Simple topological sort for dependencies
        const visited = new Set<string>();
        const result: string[] = [];

        // Helper function for depth-first traversal
        const visit = (id: string) => {
            if (visited.has(id)) return;
            visited.add(id);

            // Visit all callbacks that depend on this one
            if (this.dependencyGraph.has(id)) {
                for (const dependentId of this.dependencyGraph.get(id)!) {
                    // Only process if the dependent is in our filtered list
                    if (callbackIds.includes(dependentId)) {
                        visit(dependentId);
                    }
                }
            }

            result.push(id);
        };

        // Visit all nodes
        for (const id of callbackIds) {
            visit(id);
        }

        return result;
    }

    /**
     * Emit a strongly-typed scene event to the event bus
     *
     * @param event The strongly-typed scene event to emit
     */
    public emitTypedSceneEvent(event: ISceneEvent): void {
        // This method allows emitting any event that extends ISceneEvent
        this.eventBus.emit(event);
        if (this.debugMode) {
            console.log(`[SceneHookManager] Emitted typed scene event:`, event);
        }
    }

    /**
     * Example usage for emitting specific event types:
     *
     * const event: SceneLoadedEvent = {
     *   type: SceneEventType.SCENE_LOADED,
     *   sceneId: 'scene-123',
     *   source: 'SceneManager',
     *   timestamp: Date.now(),
     *   loadTime: 1234
     * };
     * SceneHookManager.getInstance().emitTypedSceneEvent(event);
     */
} 