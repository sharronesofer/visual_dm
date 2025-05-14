/**
 * Scene Hooks API
 * This file provides a simple API facade for the Scene Hooks system
 * to make it easier for other systems to register and use scene lifecycle hooks.
 */

import { v4 as uuidv4 } from 'uuid';
import { SceneEventType } from './SceneEventTypes';
import { SceneHookManager } from './SceneHookManager';
import {
    CallbackPriority,
    ExecutionPhase,
    ErrorHandlingStrategy,
    ICallbackOptions,
    ICallbackContext,
    HookCallback
} from './SceneHooks';

/**
 * Scene Hooks API class
 * Provides a simplified interface to the Scene Hooks system
 */
export class SceneHooks {
    private static instance: SceneHooks;
    private hookManager: SceneHookManager;

    private constructor() {
        this.hookManager = SceneHookManager.getInstance();
    }

    /**
     * Get the singleton instance
     */
    public static getInstance(): SceneHooks {
        if (!SceneHooks.instance) {
            SceneHooks.instance = new SceneHooks();
        }
        return SceneHooks.instance;
    }

    /**
     * Enable or disable debug mode
     */
    public setDebugMode(enable: boolean): void {
        this.hookManager.setDebugMode(enable);
    }

    /**
     * Register a callback for the onScenePreLoad hook
     */
    public onScenePreLoad(callback: HookCallback, options?: ICallbackOptions): string {
        return this.hookManager.register(SceneEventType.SCENE_PRE_LOAD, callback, options);
    }

    /**
     * Register a callback for the onSceneLoaded hook
     */
    public onSceneLoaded(callback: HookCallback, options?: ICallbackOptions): string {
        return this.hookManager.register(SceneEventType.SCENE_LOADED, callback, options);
    }

    /**
     * Register a callback for the onScenePreUnload hook
     */
    public onScenePreUnload(callback: HookCallback, options?: ICallbackOptions): string {
        return this.hookManager.register(SceneEventType.SCENE_PRE_UNLOAD, callback, options);
    }

    /**
     * Register a callback for the onSceneUnloaded hook
     */
    public onSceneUnloaded(callback: HookCallback, options?: ICallbackOptions): string {
        return this.hookManager.register(SceneEventType.SCENE_UNLOADED, callback, options);
    }

    /**
     * Register a callback for the onSceneLoadFailed hook
     */
    public onSceneLoadFailed(callback: HookCallback, options?: ICallbackOptions): string {
        return this.hookManager.register(SceneEventType.SCENE_LOAD_FAILED, callback, options);
    }

    /**
     * Register a callback for the onSceneActivated hook
     */
    public onSceneActivated(callback: HookCallback, options?: ICallbackOptions): string {
        return this.hookManager.register(SceneEventType.SCENE_ACTIVATED, callback, options);
    }

    /**
     * Register a callback for the onSceneDeactivated hook
     */
    public onSceneDeactivated(callback: HookCallback, options?: ICallbackOptions): string {
        return this.hookManager.register(SceneEventType.SCENE_DEACTIVATED, callback, options);
    }

    /**
     * Register a callback for the onSceneObjectAdded hook
     */
    public onSceneObjectAdded(callback: HookCallback, options?: ICallbackOptions): string {
        return this.hookManager.register(SceneEventType.SCENE_OBJECT_ADDED, callback, options);
    }

    /**
     * Register a callback for the onSceneObjectRemoved hook
     */
    public onSceneObjectRemoved(callback: HookCallback, options?: ICallbackOptions): string {
        return this.hookManager.register(SceneEventType.SCENE_OBJECT_REMOVED, callback, options);
    }

    /**
     * Register a callback for the onMemoryWarning hook
     */
    public onMemoryWarning(callback: HookCallback, options?: ICallbackOptions): string {
        return this.hookManager.register(SceneEventType.MEMORY_WARNING, callback, options);
    }

    /**
     * Register a callback for the onMemoryCritical hook
     */
    public onMemoryCritical(callback: HookCallback, options?: ICallbackOptions): string {
        return this.hookManager.register(SceneEventType.MEMORY_CRITICAL, callback, options);
    }

    /**
     * Register a callback for the onRegionEntered hook
     */
    public onRegionEntered(callback: HookCallback, options?: ICallbackOptions): string {
        return this.hookManager.register(SceneEventType.REGION_ENTERED, callback, options);
    }

    /**
     * Register a callback for the onRegionExited hook
     */
    public onRegionExited(callback: HookCallback, options?: ICallbackOptions): string {
        return this.hookManager.register(SceneEventType.REGION_EXITED, callback, options);
    }

    /**
     * Register a callback for the onCoordinatesChanged hook
     */
    public onCoordinatesChanged(callback: HookCallback, options?: ICallbackOptions): string {
        return this.hookManager.register(SceneEventType.COORDINATES_CHANGED, callback, options);
    }

    /**
     * Register a callback for the onBoundaryCrossed hook
     */
    public onBoundaryCrossed(callback: HookCallback, options?: ICallbackOptions): string {
        return this.hookManager.register(SceneEventType.BOUNDARY_CROSSED, callback, options);
    }

    /**
     * Register a callback for the onTerrainLoaded hook
     */
    public onTerrainLoaded(callback: HookCallback, options?: ICallbackOptions): string {
        return this.hookManager.register(SceneEventType.TERRAIN_LOADED, callback, options);
    }

    /**
     * Register a callback for the onTerrainUnloaded hook
     */
    public onTerrainUnloaded(callback: HookCallback, options?: ICallbackOptions): string {
        return this.hookManager.register(SceneEventType.TERRAIN_UNLOADED, callback, options);
    }

    /**
     * Register a callback for the onBiomeChanged hook
     */
    public onBiomeChanged(callback: HookCallback, options?: ICallbackOptions): string {
        return this.hookManager.register(SceneEventType.BIOME_CHANGED, callback, options);
    }

    /**
     * Unregister a callback by its ID
     */
    public off(callbackId: string): boolean {
        return this.hookManager.unregister(callbackId);
    }

    /**
     * Trigger a scene hook with the given parameters
     */
    public trigger<T = any>(
        hookType: SceneEventType,
        sceneId: string,
        data?: T,
        source: string = 'hooks-api'
    ): Promise<void> {
        return this.hookManager.executeHook(hookType, sceneId, data, source)
            .then(() => { });
    }

    /**
     * Check if a hook has any registered callbacks
     */
    public hasCallbacks(hookType: SceneEventType): boolean {
        return this.hookManager.hasCallbacks(hookType);
    }

    /**
     * Get the number of callbacks registered for a hook
     */
    public getCallbackCount(hookType: SceneEventType): number {
        return this.hookManager.getCallbackCount(hookType);
    }

    /**
     * Create a callback builder object for fluent API usage
     */
    public create(): CallbackBuilder {
        return new CallbackBuilder(this.hookManager);
    }
}

/**
 * Builder class for creating callback registrations with a fluent API
 */
export class CallbackBuilder {
    private options: ICallbackOptions = {};
    private manager: SceneHookManager;
    private hookType?: SceneEventType;
    private callbackFunction?: HookCallback;

    constructor(manager: SceneHookManager) {
        this.manager = manager;
        // Generate a unique ID by default
        this.options.id = uuidv4();
    }

    /**
     * Set the hook type to register for
     */
    public for(hookType: SceneEventType): CallbackBuilder {
        this.hookType = hookType;
        return this;
    }

    /**
     * Set the callback function
     */
    public do(callback: HookCallback): CallbackBuilder {
        this.callbackFunction = callback;
        return this;
    }

    /**
     * Set the priority for this callback
     */
    public withPriority(priority: CallbackPriority): CallbackBuilder {
        this.options.priority = priority;
        return this;
    }

    /**
     * Set this callback to execute in the PRE phase
     */
    public inPrePhase(): CallbackBuilder {
        this.options.phase = ExecutionPhase.PRE;
        return this;
    }

    /**
     * Set this callback to execute in the MAIN phase
     */
    public inMainPhase(): CallbackBuilder {
        this.options.phase = ExecutionPhase.MAIN;
        return this;
    }

    /**
     * Set this callback to execute in the POST phase
     */
    public inPostPhase(): CallbackBuilder {
        this.options.phase = ExecutionPhase.POST;
        return this;
    }

    /**
     * Set a timeout for this callback
     */
    public withTimeout(milliseconds: number): CallbackBuilder {
        this.options.timeoutMs = milliseconds;
        return this;
    }

    /**
     * Set max executions for this callback
     */
    public runTimes(count: number): CallbackBuilder {
        this.options.maxExecutions = count;
        return this;
    }

    /**
     * Configure this callback to run only once
     */
    public runOnce(): CallbackBuilder {
        this.options.maxExecutions = 1;
        return this;
    }

    /**
     * Set the error handling strategy
     */
    public handleErrorsWith(strategy: ErrorHandlingStrategy): CallbackBuilder {
        this.options.errorHandling = strategy;
        return this;
    }

    /**
     * Set error retries with optional max count
     */
    public withRetries(maxRetries: number = 3): CallbackBuilder {
        this.options.errorHandling = ErrorHandlingStrategy.RETRY;
        this.options.maxRetries = maxRetries;
        return this;
    }

    /**
     * Set a fallback function for errors
     */
    public withFallback(fallback: (error: Error, context: any) => void | Promise<void>): CallbackBuilder {
        this.options.errorHandling = ErrorHandlingStrategy.FALLBACK;
        this.options.fallback = fallback;
        return this;
    }

    /**
     * Set dependencies for this callback
     */
    public dependsOn(callbackIds: string[]): CallbackBuilder {
        this.options.dependencies = callbackIds;
        return this;
    }

    /**
     * Set additional metadata for this callback
     */
    public withMetadata(metadata: Record<string, any>): CallbackBuilder {
        this.options.metadata = metadata;
        return this;
    }

    /**
     * Register the callback with all configured options
     */
    public register(): string {
        if (!this.hookType) {
            throw new Error('Hook type must be specified using for() method');
        }

        if (!this.callbackFunction) {
            throw new Error('Callback function must be specified using do() method');
        }

        return this.manager.register(this.hookType, this.callbackFunction, this.options);
    }
} 