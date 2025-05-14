/**
 * Tests for the Scene Hooks and Callbacks system
 */

import { SceneEventType } from '../SceneEventTypes';
import { SceneHookManager } from '../SceneHookManager';
import { SceneHooks, CallbackBuilder } from '../SceneHooksAPI';
import {
    CallbackPriority,
    ExecutionPhase,
    ErrorHandlingStrategy,
    ICallbackContext
} from '../SceneHooks';

// Mock the uuid module to have predictable IDs
jest.mock('uuid', () => ({
    v4: jest.fn().mockReturnValue('mock-uuid')
}));

describe('Scene Hooks System', () => {
    // Reset mocks and instances before each test
    beforeEach(() => {
        jest.clearAllMocks();
        // Reset singleton instances (using any to access private property)
        (SceneHookManager as any).instance = undefined;
        (SceneHooks as any).instance = undefined;
    });

    describe('SceneHookManager', () => {
        it('should be a singleton', () => {
            const instance1 = SceneHookManager.getInstance();
            const instance2 = SceneHookManager.getInstance();
            expect(instance1).toBe(instance2);
        });

        it('should register callbacks for hooks', () => {
            const manager = SceneHookManager.getInstance();
            const callback = jest.fn();

            const id = manager.register(SceneEventType.SCENE_LOADED, callback);

            expect(id).toBeDefined();
            expect(manager.hasCallbacks(SceneEventType.SCENE_LOADED)).toBe(true);
            expect(manager.getCallbackCount(SceneEventType.SCENE_LOADED)).toBe(1);
        });

        it('should unregister callbacks by ID', () => {
            const manager = SceneHookManager.getInstance();
            const callback = jest.fn();

            const id = manager.register(SceneEventType.SCENE_LOADED, callback);
            const result = manager.unregister(id);

            expect(result).toBe(true);
            expect(manager.hasCallbacks(SceneEventType.SCENE_LOADED)).toBe(false);
        });

        it('should unregister all callbacks for a hook type', () => {
            const manager = SceneHookManager.getInstance();

            manager.register(SceneEventType.SCENE_LOADED, jest.fn());
            manager.register(SceneEventType.SCENE_LOADED, jest.fn());
            manager.register(SceneEventType.SCENE_UNLOADED, jest.fn());

            manager.unregisterAll(SceneEventType.SCENE_LOADED);

            expect(manager.hasCallbacks(SceneEventType.SCENE_LOADED)).toBe(false);
            expect(manager.hasCallbacks(SceneEventType.SCENE_UNLOADED)).toBe(true);
        });

        it('should execute callbacks in order of priority', async () => {
            const manager = SceneHookManager.getInstance();
            const executionOrder: number[] = [];

            manager.register(
                SceneEventType.SCENE_LOADED,
                () => { executionOrder.push(3); },
                { priority: CallbackPriority.LOW }
            );

            manager.register(
                SceneEventType.SCENE_LOADED,
                () => { executionOrder.push(1); },
                { priority: CallbackPriority.HIGH }
            );

            manager.register(
                SceneEventType.SCENE_LOADED,
                () => { executionOrder.push(2); },
                { priority: CallbackPriority.NORMAL }
            );

            await manager.executeHook(SceneEventType.SCENE_LOADED, 'test-scene');

            expect(executionOrder).toEqual([1, 2, 3]);
        });

        it('should execute callbacks in phases', async () => {
            const manager = SceneHookManager.getInstance();
            const executionOrder: string[] = [];

            manager.register(
                SceneEventType.SCENE_LOADED,
                () => { executionOrder.push('pre'); },
                { phase: ExecutionPhase.PRE }
            );

            manager.register(
                SceneEventType.SCENE_LOADED,
                () => { executionOrder.push('main'); },
                { phase: ExecutionPhase.MAIN }
            );

            manager.register(
                SceneEventType.SCENE_LOADED,
                () => { executionOrder.push('post'); },
                { phase: ExecutionPhase.POST }
            );

            await manager.executeHook(SceneEventType.SCENE_LOADED, 'test-scene');

            expect(executionOrder).toEqual(['pre', 'main', 'post']);
        });

        it('should handle callback errors based on strategy', async () => {
            const manager = SceneHookManager.getInstance();

            // LOG strategy
            const logCallback = jest.fn().mockImplementation(() => {
                throw new Error('Test error');
            });

            manager.register(
                SceneEventType.SCENE_LOADED,
                logCallback,
                { errorHandling: ErrorHandlingStrategy.LOG }
            );

            // This should not throw
            const result = await manager.executeHook(SceneEventType.SCENE_LOADED, 'test-scene');

            expect(result.failureCount).toBe(1);
            expect(result.successCount).toBe(0);
            expect(logCallback).toHaveBeenCalled();
        });

        it('should respect maxExecutions option', async () => {
            const manager = SceneHookManager.getInstance();
            const callback = jest.fn();

            manager.register(
                SceneEventType.SCENE_LOADED,
                callback,
                { maxExecutions: 2 }
            );

            // First execution
            await manager.executeHook(SceneEventType.SCENE_LOADED, 'test-scene');
            expect(callback).toHaveBeenCalledTimes(1);
            expect(manager.getCallbackCount(SceneEventType.SCENE_LOADED)).toBe(1);

            // Second execution
            await manager.executeHook(SceneEventType.SCENE_LOADED, 'test-scene');
            expect(callback).toHaveBeenCalledTimes(2);
            expect(manager.getCallbackCount(SceneEventType.SCENE_LOADED)).toBe(0);
        });
    });

    describe('SceneHooks API', () => {
        it('should be a singleton', () => {
            const instance1 = SceneHooks.getInstance();
            const instance2 = SceneHooks.getInstance();
            expect(instance1).toBe(instance2);
        });

        it('should provide named methods for each hook type', () => {
            const hooks = SceneHooks.getInstance();
            const callback = jest.fn();

            const id1 = hooks.onSceneLoaded(callback);
            const id2 = hooks.onScenePreUnload(callback);

            expect(id1).toBeDefined();
            expect(id2).toBeDefined();
            expect(hooks.hasCallbacks(SceneEventType.SCENE_LOADED)).toBe(true);
            expect(hooks.hasCallbacks(SceneEventType.SCENE_PRE_UNLOAD)).toBe(true);
        });

        it('should allow unregistering callbacks', () => {
            const hooks = SceneHooks.getInstance();
            const callback = jest.fn();

            const id = hooks.onSceneLoaded(callback);
            const result = hooks.off(id);

            expect(result).toBe(true);
            expect(hooks.hasCallbacks(SceneEventType.SCENE_LOADED)).toBe(false);
        });

        it('should trigger hooks with correct parameters', async () => {
            const hooks = SceneHooks.getInstance();
            const callback = jest.fn();

            hooks.onSceneLoaded(callback);

            const testData = { test: 'data' };
            await hooks.trigger(SceneEventType.SCENE_LOADED, 'test-scene', testData);

            expect(callback).toHaveBeenCalledTimes(1);
            expect(callback.mock.calls[0][0].sceneId).toBe('test-scene');
            expect(callback.mock.calls[0][0].data).toBe(testData);
        });

        it('should provide a fluent builder API', () => {
            const hooks = SceneHooks.getInstance();
            const callback = jest.fn();

            const id = hooks.create()
                .for(SceneEventType.SCENE_LOADED)
                .do(callback)
                .withPriority(CallbackPriority.HIGH)
                .inPrePhase()
                .runOnce()
                .register();

            expect(id).toBeDefined();
            expect(hooks.hasCallbacks(SceneEventType.SCENE_LOADED)).toBe(true);
        });
    });

    describe('CallbackBuilder', () => {
        it('should build callback configurations', () => {
            const manager = SceneHookManager.getInstance();
            const callback = jest.fn();

            // Create spy on register method to check options
            const registerSpy = jest.spyOn(manager, 'register');

            // Use the builder
            const builder = new CallbackBuilder(manager);
            builder
                .for(SceneEventType.SCENE_LOADED)
                .do(callback)
                .withPriority(CallbackPriority.HIGH)
                .inPrePhase()
                .withTimeout(1000)
                .runTimes(2)
                .handleErrorsWith(ErrorHandlingStrategy.RETRY)
                .withRetries(5)
                .withMetadata({ source: 'test' })
                .register();

            // Check that register was called with correct options
            expect(registerSpy).toHaveBeenCalledTimes(1);
            const options = registerSpy.mock.calls[0][2];

            expect(options.priority).toBe(CallbackPriority.HIGH);
            expect(options.phase).toBe(ExecutionPhase.PRE);
            expect(options.timeoutMs).toBe(1000);
            expect(options.maxExecutions).toBe(2);
            expect(options.errorHandling).toBe(ErrorHandlingStrategy.RETRY);
            expect(options.maxRetries).toBe(5);
            expect(options.metadata).toEqual({ source: 'test' });
        });

        it('should throw if hook type is not specified', () => {
            const manager = SceneHookManager.getInstance();
            const callback = jest.fn();

            const builder = new CallbackBuilder(manager);
            builder.do(callback);

            expect(() => builder.register()).toThrow('Hook type must be specified');
        });

        it('should throw if callback is not specified', () => {
            const manager = SceneHookManager.getInstance();

            const builder = new CallbackBuilder(manager);
            builder.for(SceneEventType.SCENE_LOADED);

            expect(() => builder.register()).toThrow('Callback function must be specified');
        });
    });
}); 