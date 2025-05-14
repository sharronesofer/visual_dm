/**
 * Scene Management System Hooks and Callbacks Interfaces
 * This file defines the interfaces for the hooks and callbacks system
 * that allows other systems to register and react to scene lifecycle events.
 */

import { ISceneEvent, SceneEventType } from './SceneEventTypes';

/**
 * Priority levels for callback execution
 */
export enum CallbackPriority {
    CRITICAL = 0,    // System-critical operations that must run first
    HIGH = 1,        // High priority operations
    NORMAL = 2,      // Default priority
    LOW = 3,         // Low priority operations
    BACKGROUND = 4   // Background tasks that can run last
}

/**
 * Execution phase for callbacks
 */
export enum ExecutionPhase {
    PRE = 'pre',     // Before main operation
    MAIN = 'main',   // During main operation
    POST = 'post'    // After main operation
}

/**
 * Error handling strategies for callbacks
 */
export enum ErrorHandlingStrategy {
    THROW = 'throw',             // Rethrow errors, stopping execution
    LOG = 'log',                 // Log errors and continue execution
    RETRY = 'retry',             // Retry the callback (up to a limit)
    FALLBACK = 'fallback'        // Execute a fallback function
}

/**
 * Options for hook callback registration
 */
export interface ICallbackOptions {
    /** Priority level for callback execution order */
    priority?: CallbackPriority;

    /** Execution phase for the callback */
    phase?: ExecutionPhase;

    /** If set, the callback will be removed after this number of executions */
    maxExecutions?: number;

    /** Timeout in ms for async callbacks */
    timeoutMs?: number;

    /** Error handling strategy */
    errorHandling?: ErrorHandlingStrategy;

    /** Function to execute when the callback throws an error (if using FALLBACK strategy) */
    fallback?: (error: Error, context: any) => void | Promise<void>;

    /** Maximum number of retry attempts (if using RETRY strategy) */
    maxRetries?: number;

    /** Dependencies on other callbacks (callbacks that must execute before this one) */
    dependencies?: string[];

    /** A unique ID for this callback (auto-generated if not provided) */
    id?: string;

    /** Optional metadata for the callback */
    metadata?: Record<string, any>;
}

/**
 * Context object passed to callbacks
 */
export interface ICallbackContext<T = any> {
    /** The scene ID */
    sceneId: string;

    /** The hook type being executed */
    hookType: SceneEventType;

    /** Timestamp when the hook execution started */
    timestamp: number;

    /** Any additional data for the callback */
    data: T;

    /** Source of the hook call */
    source: string;
}

/**
 * Type definition for a hook callback
 */
export type HookCallback<T = any> = (
    context: ICallbackContext<T>
) => void | Promise<void>;

/**
 * Callback registration info (internal use)
 */
export interface ICallbackRegistration {
    /** The callback function */
    callback: HookCallback;

    /** Callback options */
    options: ICallbackOptions;

    /** Number of times this callback has been executed */
    executionCount: number;

    /** Timestamp of the last execution */
    lastExecuted?: number;
}

/**
 * Results from a callback execution
 */
export interface ICallbackExecutionResult {
    /** Callback ID */
    callbackId: string;

    /** Whether the callback executed successfully */
    success: boolean;

    /** Any error that occurred during execution */
    error?: Error;

    /** Time taken to execute in ms */
    executionTimeMs: number;

    /** Whether the callback was removed after execution */
    removed: boolean;
}

/**
 * Results from a hook execution
 */
export interface IHookExecutionResult {
    /** Hook type */
    hookType: SceneEventType;

    /** Scene ID */
    sceneId: string;

    /** Individual callback results */
    callbackResults: ICallbackExecutionResult[];

    /** Total time taken to execute all callbacks */
    totalExecutionTimeMs: number;

    /** Number of successful callbacks */
    successCount: number;

    /** Number of failed callbacks */
    failureCount: number;
}

/**
 * Interface for the Scene Hooks Management System
 */
export interface ISceneHookManager {
    /**
     * Register a callback for a specific hook
     */
    register(
        hookType: SceneEventType,
        callback: HookCallback,
        options?: ICallbackOptions
    ): string;

    /**
     * Unregister a callback
     */
    unregister(callbackId: string): boolean;

    /**
     * Unregister all callbacks for a specific hook
     */
    unregisterAll(hookType: SceneEventType): void;

    /**
     * Execute all callbacks for a hook
     */
    executeHook<T = any>(
        hookType: SceneEventType,
        sceneId: string,
        data?: T,
        source?: string
    ): Promise<IHookExecutionResult>;

    /**
     * Check if a hook has any registered callbacks
     */
    hasCallbacks(hookType: SceneEventType): boolean;

    /**
     * Get count of registered callbacks for a hook
     */
    getCallbackCount(hookType: SceneEventType): number;
} 