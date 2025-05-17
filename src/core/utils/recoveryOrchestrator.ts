import { InterruptionState, InterruptionMeta } from '../../store/core/interactionStore';
import { GPTContext } from './gptContextSerializer';
import { interruptionConfig } from '../../config/interruptionConfig';

/**
 * Recovery result type
 */
export interface RecoveryResult {
    success: boolean;
    message: string;
    recoveredState?: any;
    checkpoint?: any;
    error?: Error;
}

/**
 * Recovery context passed to strategies
 */
export interface RecoveryContext {
    interruptionState: InterruptionState;
    interruptionMeta: InterruptionMeta | null;
    preservedContext: GPTContext;
    lastCheckpoint?: any;
}

/**
 * Recovery strategy interface
 */
export interface RecoveryStrategy {
    recover(ctx: RecoveryContext): Promise<RecoveryResult>;
    name: string;
}

/**
 * Resume from interruption (temporary pause)
 */
export class ResumeStrategy implements RecoveryStrategy {
    name = 'ResumeStrategy';
    async recover(ctx: RecoveryContext): Promise<RecoveryResult> {
        // Attempt to resume from preserved context
        // (Stub: in real system, restore state, validate, etc.)
        return {
            success: true,
            message: 'Resumed from temporary interruption.',
            recoveredState: ctx.preservedContext,
        };
    }
}

/**
 * Graceful degradation for system errors
 */
export class GracefulDegradationStrategy implements RecoveryStrategy {
    name = 'GracefulDegradationStrategy';
    async recover(ctx: RecoveryContext): Promise<RecoveryResult> {
        // Attempt fallback, log error, notify user, etc.
        return {
            success: false,
            message: 'System error: entered degraded mode.',
            error: new Error('System error'),
        };
    }
}

/**
 * State preservation for user exit
 */
export class StatePreservationStrategy implements RecoveryStrategy {
    name = 'StatePreservationStrategy';
    async recover(ctx: RecoveryContext): Promise<RecoveryResult> {
        // Save state, cleanup, prepare for safe exit
        return {
            success: true,
            message: 'State saved and cleaned up for user exit.',
            recoveredState: ctx.preservedContext,
        };
    }
}

/**
 * Fallback for unrecoverable states
 */
export class FallbackStrategy implements RecoveryStrategy {
    name = 'FallbackStrategy';
    async recover(ctx: RecoveryContext): Promise<RecoveryResult> {
        // Cleanup, log, notify user
        return {
            success: false,
            message: 'Unrecoverable interruption. State cleanup performed.',
            error: new Error('Unrecoverable interruption'),
        };
    }
}

/**
 * Simple logger for analytics/telemetry
 */
function logRecoveryEvent(event: string, data: any) {
    // Replace with real telemetry as needed
    // eslint-disable-next-line no-console
    console.log(`[RecoveryAnalytics] ${event}`, data);
}

/**
 * RecoveryOrchestrator coordinates recovery using strategies, timeouts, checkpoints, and analytics
 */
export class RecoveryOrchestrator {
    private strategies: Map<InterruptionState, RecoveryStrategy>;
    private fallback: RecoveryStrategy;
    private maxRetries: number;
    private baseInterval: number;
    private circuitBreakerTripped: boolean;
    private lastCheckpoint: any;

    constructor(options?: { maxRetries?: number; baseInterval?: number }) {
        this.maxRetries = options?.maxRetries ?? interruptionConfig.maxRetries;
        this.baseInterval = options?.baseInterval ?? interruptionConfig.baseIntervalMs;
        this.strategies = new Map();
        this.fallback = new FallbackStrategy();
        this.circuitBreakerTripped = false;
        this.lastCheckpoint = null;
        this.strategies.set(InterruptionState.TEMPORARY_PAUSE, new ResumeStrategy());
        this.strategies.set(InterruptionState.SYSTEM_ERROR, new GracefulDegradationStrategy());
        this.strategies.set(InterruptionState.USER_EXIT, new StatePreservationStrategy());
    }

    /**
     * Main recovery entry point
     */
    async recover(ctx: RecoveryContext): Promise<RecoveryResult> {
        if (this.circuitBreakerTripped) {
            logRecoveryEvent('circuit_breaker_tripped', ctx);
            return this.fallback.recover(ctx);
        }
        const strategy = this.strategies.get(ctx.interruptionState) || this.fallback;
        let attempt = 0;
        let lastError: Error | undefined;
        let result: RecoveryResult | undefined;
        let interval = this.baseInterval;
        while (attempt < this.maxRetries) {
            try {
                logRecoveryEvent('recovery_attempt', { attempt, strategy: strategy.name, ctx });
                result = await strategy.recover({ ...ctx, lastCheckpoint: this.lastCheckpoint });
                if (result.success) {
                    this.createCheckpoint(result.recoveredState);
                    logRecoveryEvent('recovery_success', result);
                    return result;
                }
                lastError = result.error;
            } catch (e) {
                lastError = e instanceof Error ? e : new Error('Unknown recovery error');
                logRecoveryEvent('recovery_error', { attempt, error: lastError });
            }
            attempt++;
            await this.delay(interval);
            interval *= 2; // Exponential backoff
        }
        this.circuitBreakerTripped = true;
        logRecoveryEvent('circuit_breaker_activated', { lastError });
        return this.fallback.recover(ctx);
    }

    /**
     * Create a recovery checkpoint
     */
    createCheckpoint(state: any) {
        this.lastCheckpoint = state;
        logRecoveryEvent('checkpoint_created', { state });
    }

    /**
     * Rollback to last checkpoint
     */
    rollback(): any {
        logRecoveryEvent('rollback', { checkpoint: this.lastCheckpoint });
        return this.lastCheckpoint;
    }

    /**
     * Utility: async delay
     */
    private delay(ms: number) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Reset circuit breaker (for testing or after manual intervention)
     */
    resetCircuitBreaker() {
        this.circuitBreakerTripped = false;
        logRecoveryEvent('circuit_breaker_reset', {});
    }
}

/**
 * Example stub for integration:
 *   const orchestrator = new RecoveryOrchestrator();
 *   orchestrator.recover({ interruptionState, interruptionMeta, preservedContext })
 */

export { InterruptionState }; 