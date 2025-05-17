/**
 * Comprehensive error categories for cross-system error handling.
 */
export enum ErrorCategory {
    API = 'api',
    VALIDATION = 'validation',
    NETWORK = 'network',
    DATABASE = 'database',
    CACHE = 'cache',
    UNKNOWN = 'unknown',
    SYSTEM = 'system',
    SECURITY = 'security',
    AUTHORIZATION = 'authorization',
    DATA_INTEGRITY = 'data_integrity',
    TIMEOUT = 'timeout',
    RESOURCE_EXHAUSTION = 'resource_exhaustion',
}

/**
 * Utility for categorizing errors by type or message.
 */
export function categorizeError(error: any): ErrorCategory {
    if (!error) return ErrorCategory.UNKNOWN;
    const msg = error.message?.toLowerCase?.() || '';
    if (msg.includes('timeout')) return ErrorCategory.TIMEOUT;
    if (msg.includes('network')) return ErrorCategory.NETWORK;
    if (msg.includes('auth')) return ErrorCategory.AUTHORIZATION;
    if (msg.includes('validate')) return ErrorCategory.VALIDATION;
    if (msg.includes('db') || msg.includes('database')) return ErrorCategory.DATABASE;
    if (msg.includes('cache')) return ErrorCategory.CACHE;
    if (msg.includes('security')) return ErrorCategory.SECURITY;
    if (msg.includes('integrity')) return ErrorCategory.DATA_INTEGRITY;
    if (msg.includes('resource')) return ErrorCategory.RESOURCE_EXHAUSTION;
    if (msg.includes('system')) return ErrorCategory.SYSTEM;
    return ErrorCategory.UNKNOWN;
}

import { SceneEventType, ISceneEvent } from '../events/SceneEventTypes';

/**
 * Event published for critical errors across system boundaries.
 */
export interface ErrorEvent extends ISceneEvent {
    type: SceneEventType.ERROR_EVENT;
    error: ErrorContext;
}

/**
 * Interface for custom error handlers.
 */
export interface ErrorHandler {
    handleError(ctx: ErrorContext): Promise<void> | void;
    category?: ErrorCategory;
    priority?: number;
}

/**
 * Maintains error state and history across retry attempts.
 */
export class ErrorContext {
    public readonly category: ErrorCategory;
    public readonly message: string;
    public readonly details?: any;
    public readonly service?: string;
    public readonly operation?: string;
    public timestamp: number;
    public readonly history: Array<{ timestamp: number; message: string; }>; // retry attempts, etc.

    constructor(params: {
        category: ErrorCategory;
        message: string;
        details?: any;
        service?: string;
        operation?: string;
        timestamp?: number;
        history?: Array<{ timestamp: number; message: string; }>;
    }) {
        this.category = params.category;
        this.message = params.message;
        this.details = params.details;
        this.service = params.service;
        this.operation = params.operation;
        this.timestamp = typeof params.timestamp === 'number' ? params.timestamp : Date.now();
        this.history = params.history ?? [];
    }

    /**
     * Add a new entry to the error history (returns a new ErrorContext).
     */
    withHistoryEntry(message: string): ErrorContext {
        const originalTimestamp = this.timestamp;
        return new ErrorContext({
            category: this.category,
            message: this.message,
            details: this.details,
            service: this.service,
            operation: this.operation,
            timestamp: originalTimestamp,
            history: [...this.history, { timestamp: Date.now(), message }],
        });
    }
}

export class ErrorHandlingService {
    private static instance: ErrorHandlingService;
    private errorLog: ErrorContext[] = [];
    private listeners: Array<(ctx: ErrorContext) => void> = [];
    private handlers: ErrorHandler[] = [];

    private constructor() { }

    public static getInstance(): ErrorHandlingService {
        if (!ErrorHandlingService.instance) {
            ErrorHandlingService.instance = new ErrorHandlingService();
        }
        return ErrorHandlingService.instance;
    }

    /**
     * Register a custom error handler.
     */
    public registerHandler(handler: ErrorHandler) {
        this.handlers.push(handler);
        // Sort by priority (lower number = higher priority)
        this.handlers.sort((a, b) => (a.priority ?? 10) - (b.priority ?? 10));
    }

    /**
     * Publish an error event to the event system.
     */
    public async publishErrorEvent(ctx: ErrorContext) {
        const event: ErrorEvent = {
            type: SceneEventType.ERROR_EVENT,
            error: ctx,
            source: 'ErrorHandlingService',
            timestamp: Date.now(),
        };
        // Assume EventBus is available globally or import as needed
        const bus = (global as any).EventBus?.getInstance?.() || undefined;
        if (bus && typeof bus.emit === 'function') {
            await bus.emit(event);
        }
    }

    /**
     * Handle an error with retry and circuit breaker logic.
     * @param fn The function to execute (should return a Promise)
     * @param ctx The error context for categorization
     * @param circuitBreakerKey Unique key for circuit breaker registry
     */
    public async handleWithRetry<T>(fn: () => Promise<T>, ctx: ErrorContext, circuitBreakerKey: string): Promise<T | undefined> {
        const breaker = CircuitBreakerRegistry.getBreaker(circuitBreakerKey);
        const policy = RetryPolicyFactory.getPolicy(ctx.category);
        let attempt = 0;
        let lastError: ErrorContext = ctx;
        while (policy.shouldRetry(attempt, lastError)) {
            if (!breaker.canRequest()) {
                // Circuit breaker is open
                await this.publishErrorEvent(lastError.withHistoryEntry('Circuit breaker open'));
                return undefined;
            }
            try {
                const result = await fn();
                breaker.recordSuccess();
                return result;
            } catch (err: any) {
                breaker.recordFailure();
                lastError = new ErrorContext({
                    ...lastError,
                    message: err?.message || String(err),
                    details: err,
                    timestamp: Date.now(),
                    history: [...lastError.history, { timestamp: Date.now(), message: err?.message || String(err) }],
                });
                this.logError(lastError);
                // Call custom handlers
                for (const handler of this.handlers) {
                    if (!handler.category || handler.category === lastError.category) {
                        await handler.handleError(lastError);
                    }
                }
                await this.publishErrorEvent(lastError);
                // Wait before retrying
                const delay = policy.getDelay(attempt);
                await new Promise(res => setTimeout(res, delay));
                attempt++;
            }
        }
        // All retries exhausted
        await this.publishErrorEvent(lastError.withHistoryEntry('All retries exhausted'));
        return undefined;
    }

    public logError(ctx: ErrorContext) {
        ctx.timestamp = ctx.timestamp || Date.now();
        this.errorLog.push(ctx);
        for (const listener of this.listeners) {
            try {
                listener(ctx);
            } catch (e) {
                // Ignore listener errors
            }
        }
        // Optionally: Integrate with external logging/monitoring
        // e.g., Sentry, Datadog, etc.
    }

    public getErrors(filter?: Partial<ErrorContext>): ErrorContext[] {
        if (!filter) return [...this.errorLog];
        return this.errorLog.filter(err => {
            for (const key in filter) {
                if ((err as any)[key] !== (filter as any)[key]) return false;
            }
            return true;
        });
    }

    public onError(listener: (ctx: ErrorContext) => void) {
        this.listeners.push(listener);
    }

    public clear() {
        this.errorLog = [];
    }
}

/**
 * Abstract base class for retry policies.
 */
export abstract class BaseRetryPolicy {
    abstract shouldRetry(attempt: number, error: ErrorContext): boolean;
    abstract getDelay(attempt: number): number;
}

/**
 * Exponential backoff retry policy.
 */
export class ExponentialBackoffRetryPolicy extends BaseRetryPolicy {
    constructor(
        private maxAttempts: number = 5,
        private baseDelay: number = 100,
        private maxDelay: number = 5000,
        private jitter: boolean = true
    ) { super(); }
    shouldRetry(attempt: number, error: ErrorContext): boolean {
        return attempt < this.maxAttempts;
    }
    getDelay(attempt: number): number {
        let delay = Math.min(this.baseDelay * Math.pow(2, attempt), this.maxDelay);
        if (this.jitter) {
            delay = delay * (0.5 + Math.random());
        }
        return Math.floor(delay);
    }
}

/**
 * Fixed interval retry policy.
 */
export class FixedIntervalRetryPolicy extends BaseRetryPolicy {
    constructor(private maxAttempts: number = 3, private interval: number = 200) { super(); }
    shouldRetry(attempt: number, error: ErrorContext): boolean {
        return attempt < this.maxAttempts;
    }
    getDelay(attempt: number): number {
        return this.interval;
    }
}

/**
 * Factory for creating retry policies based on error category.
 */
export class RetryPolicyFactory {
    static getPolicy(category: ErrorCategory): BaseRetryPolicy {
        switch (category) {
            case ErrorCategory.NETWORK:
            case ErrorCategory.TIMEOUT:
                return new ExponentialBackoffRetryPolicy(5, 100, 5000, true);
            case ErrorCategory.VALIDATION:
            case ErrorCategory.AUTHORIZATION:
                return new FixedIntervalRetryPolicy(1, 0); // No retry
            default:
                return new ExponentialBackoffRetryPolicy();
        }
    }
}

/**
 * Circuit breaker states.
 */
export enum CircuitBreakerState {
    CLOSED = 'closed',
    OPEN = 'open',
    HALF_OPEN = 'half_open',
}

/**
 * Circuit breaker for system dependencies.
 */
export class CircuitBreaker {
    private state: CircuitBreakerState = CircuitBreakerState.CLOSED;
    private failureCount = 0;
    private lastFailureTime = 0;
    private openTimeout: number;
    private failureThreshold: number;
    private halfOpenAttempts: number;
    private halfOpenMax: number;

    constructor(
        failureThreshold: number = 5,
        openTimeout: number = 10000,
        halfOpenMax: number = 2
    ) {
        this.failureThreshold = failureThreshold;
        this.openTimeout = openTimeout;
        this.halfOpenMax = halfOpenMax;
        this.halfOpenAttempts = 0;
    }

    canRequest(): boolean {
        if (this.state === CircuitBreakerState.OPEN) {
            if (Date.now() - this.lastFailureTime > this.openTimeout) {
                this.state = CircuitBreakerState.HALF_OPEN;
                this.halfOpenAttempts = 0;
                return true;
            }
            return false;
        }
        return true;
    }

    recordSuccess() {
        if (this.state === CircuitBreakerState.HALF_OPEN) {
            this.halfOpenAttempts++;
            if (this.halfOpenAttempts >= this.halfOpenMax) {
                this.state = CircuitBreakerState.CLOSED;
                this.failureCount = 0;
            }
        } else {
            this.failureCount = 0;
        }
    }

    recordFailure() {
        this.failureCount++;
        this.lastFailureTime = Date.now();
        if (this.failureCount >= this.failureThreshold) {
            this.state = CircuitBreakerState.OPEN;
        }
    }

    getState(): CircuitBreakerState {
        return this.state;
    }
}

/**
 * Registry for managing multiple circuit breakers.
 */
export class CircuitBreakerRegistry {
    private static breakers: Map<string, CircuitBreaker> = new Map();
    static getBreaker(key: string): CircuitBreaker {
        if (!this.breakers.has(key)) {
            this.breakers.set(key, new CircuitBreaker());
        }
        return this.breakers.get(key)!;
    }
    static setBreaker(key: string, breaker: CircuitBreaker) {
        this.breakers.set(key, breaker);
    }
    static getAll(): Map<string, CircuitBreaker> {
        return this.breakers;
    }
} 