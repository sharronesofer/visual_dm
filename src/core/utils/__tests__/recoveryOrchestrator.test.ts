import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
    RecoveryOrchestrator,
    ResumeStrategy,
    GracefulDegradationStrategy,
    StatePreservationStrategy,
    FallbackStrategy,
    RecoveryContext,
    InterruptionState,
    RecoveryResult
} from '../recoveryOrchestrator';

const mockContext = (state: InterruptionState): RecoveryContext => ({
    interruptionState: state,
    interruptionMeta: { timestamp: Date.now(), event: 'test' },
    preservedContext: { foo: { key: 'foo', value: 'bar', priority: 'essential' } },
});

describe('Recovery Strategies', () => {
    it('ResumeStrategy succeeds for temporary pause', async () => {
        const strat = new ResumeStrategy();
        const ctx = mockContext(InterruptionState.TEMPORARY_PAUSE);
        const result = await strat.recover(ctx);
        expect(result.success).toBe(true);
        expect(result.message).toMatch(/Resumed/);
    });

    it('GracefulDegradationStrategy fails for system error', async () => {
        const strat = new GracefulDegradationStrategy();
        const ctx = mockContext(InterruptionState.SYSTEM_ERROR);
        const result = await strat.recover(ctx);
        expect(result.success).toBe(false);
        expect(result.message).toMatch(/degraded/);
        expect(result.error).toBeInstanceOf(Error);
    });

    it('StatePreservationStrategy succeeds for user exit', async () => {
        const strat = new StatePreservationStrategy();
        const ctx = mockContext(InterruptionState.USER_EXIT);
        const result = await strat.recover(ctx);
        expect(result.success).toBe(true);
        expect(result.message).toMatch(/State saved/);
    });

    it('FallbackStrategy always fails', async () => {
        const strat = new FallbackStrategy();
        const ctx = mockContext(InterruptionState.UNKNOWN);
        const result = await strat.recover(ctx);
        expect(result.success).toBe(false);
        expect(result.message).toMatch(/Unrecoverable/);
        expect(result.error).toBeInstanceOf(Error);
    });
});

describe('RecoveryOrchestrator', () => {
    let orchestrator: RecoveryOrchestrator;
    beforeEach(() => {
        orchestrator = new RecoveryOrchestrator({ maxRetries: 2, baseInterval: 10 });
        orchestrator.resetCircuitBreaker();
    });

    it('selects correct strategy for TEMPORARY_PAUSE', async () => {
        const ctx = mockContext(InterruptionState.TEMPORARY_PAUSE);
        const result = await orchestrator.recover(ctx);
        expect(result.success).toBe(true);
        expect(result.message).toMatch(/Resumed/);
    });

    it('selects correct strategy for SYSTEM_ERROR', async () => {
        const ctx = mockContext(InterruptionState.SYSTEM_ERROR);
        const result = await orchestrator.recover(ctx);
        expect(result.success).toBe(false);
        expect(result.message).toMatch(/degraded/);
    });

    it('selects correct strategy for USER_EXIT', async () => {
        const ctx = mockContext(InterruptionState.USER_EXIT);
        const result = await orchestrator.recover(ctx);
        expect(result.success).toBe(true);
        expect(result.message).toMatch(/State saved/);
    });

    it('uses fallback for unknown state', async () => {
        const ctx = mockContext(InterruptionState.UNKNOWN);
        const result = await orchestrator.recover(ctx);
        expect(result.success).toBe(false);
        expect(result.message).toMatch(/Unrecoverable/);
    });

    it('creates and rolls back to checkpoint', async () => {
        const ctx = mockContext(InterruptionState.TEMPORARY_PAUSE);
        const result = await orchestrator.recover(ctx);
        orchestrator.createCheckpoint(result.recoveredState);
        const rollback = orchestrator.rollback();
        expect(rollback).toEqual(result.recoveredState);
    });

    it('trips circuit breaker after max retries', async () => {
        // Patch strategy to always throw
        orchestrator['strategies'].set(InterruptionState.TEMPORARY_PAUSE, {
            name: 'FailingStrategy',
            async recover() { throw new Error('fail'); }
        });
        const ctx = mockContext(InterruptionState.TEMPORARY_PAUSE);
        const result = await orchestrator.recover(ctx);
        expect(result.success).toBe(false);
        expect(result.message).toMatch(/Unrecoverable/);
    });

    it('resets circuit breaker', async () => {
        orchestrator['circuitBreakerTripped'] = true;
        orchestrator.resetCircuitBreaker();
        expect(orchestrator['circuitBreakerTripped']).toBe(false);
    });
}); 