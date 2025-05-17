import { create } from 'zustand';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import { createValidator, ValidationResult, ValidationError } from '../utils/validation';
import { createPersistence } from '../utils/persistence';
import { NPCData } from '../../core/interfaces/types/npc/npc';
import { Memory, MemoryEventType } from '../../core/interfaces/types/npc/memory';
import shallow from 'zustand/shallow';
import { useMemo } from 'react';
import { interruptionConfig } from '../../config/interruptionConfig';
import type { StateCreator } from 'zustand';

export enum InterruptionState {
    NONE = 'NONE',
    TEMPORARY_PAUSE = 'TEMPORARY_PAUSE',
    SYSTEM_ERROR = 'SYSTEM_ERROR',
    USER_EXIT = 'USER_EXIT',
    UNKNOWN = 'UNKNOWN',
}

export interface InterruptionMeta {
    timestamp: number;
    event: string;
    details?: any;
}

/**
 * Interaction System State
 */
export interface InteractionState {
    /**
     * The entire state tree for the Interaction System
     */
    stateTree: Record<string, any>;
    /**
     * Snapshots for recovery and time-travel
     */
    snapshots: InteractionSnapshot[];
    /**
     * Validation results for the current state
     */
    validation: ValidationResult | null;
    /**
     * Debugging info (action log, errors, etc.)
     */
    debug: InteractionDebugInfo;
    /**
     * Loading and error states
     */
    isLoading: boolean;
    error: string | null;
    interruptionState: InterruptionState;
    interruptionMeta: InterruptionMeta | null;
}

export interface InteractionSnapshot {
    timestamp: number;
    state: Record<string, any>;
    meta: {
        version: number;
        context: string;
    };
}

export interface InteractionDebugInfo {
    actionLog: InteractionActionLogEntry[];
    lastAction?: string;
    performance?: {
        lastUpdateDuration: number;
        lastValidationDuration: number;
    };
    lastValidationError?: ValidationError[];
}

export interface InteractionActionLogEntry {
    action: string;
    payload: any;
    beforeState: Record<string, any>;
    afterState: Record<string, any>;
    timestamp: number;
}

/**
 * Action types for the Interaction System
 */
export type InteractionAction =
    | { type: 'INIT'; payload?: any }
    | { type: 'UPDATE_STATE'; payload: Partial<Record<string, any>> }
    | { type: 'RESET' }
    | { type: 'SNAPSHOT' }
    | { type: 'RESTORE_SNAPSHOT'; payload: number }
    | { type: 'VALIDATE' }
    | { type: 'LOG_ACTION'; payload: { action: string; payload: any } }
    | { type: 'ERROR'; payload: string }
    | { type: 'SET_INTERRUPTION_STATE'; payload: { state: InterruptionState; meta: InterruptionMeta } }
    | { type: 'CLEAR_INTERRUPTION_STATE' };

/**
 * Pure reducer for state transitions
 */
export function interactionReducer(
    state: InteractionState,
    action: InteractionAction
): InteractionState {
    switch (action.type) {
        case 'INIT':
            return {
                ...state,
                stateTree: action.payload || {},
                error: null,
            };
        case 'UPDATE_STATE':
            return {
                ...state,
                stateTree: { ...state.stateTree, ...action.payload },
                error: null,
            };
        case 'RESET':
            return {
                ...state,
                stateTree: {},
                error: null,
            };
        case 'SNAPSHOT': {
            const snapshot: InteractionSnapshot = {
                timestamp: Date.now(),
                state: { ...state.stateTree },
                meta: { version: 1, context: 'auto' },
            };
            return {
                ...state,
                snapshots: [...state.snapshots, snapshot],
            };
        }
        case 'RESTORE_SNAPSHOT': {
            const snapshot = state.snapshots.find(s => s.timestamp === action.payload);
            if (!snapshot) return { ...state, error: 'Snapshot not found' };
            return {
                ...state,
                stateTree: { ...snapshot.state },
                error: null,
            };
        }
        case 'VALIDATE':
            // Validation handled in middleware/action
            return state;
        case 'LOG_ACTION': {
            const entry: InteractionActionLogEntry = {
                action: typeof action === 'string' ? action : action.type,
                payload: 'payload' in action ? action.payload : undefined,
                beforeState: { ...state.stateTree },
                afterState: { ...state.stateTree },
                timestamp: Date.now(),
            };
            return {
                ...state,
                debug: {
                    ...state.debug,
                    actionLog: [...state.debug.actionLog, entry],
                    lastAction: entry.action,
                },
            };
        }
        case 'ERROR':
            return { ...state, error: action.payload };
        case 'SET_INTERRUPTION_STATE':
            return {
                ...state,
                interruptionState: action.payload.state,
                interruptionMeta: action.payload.meta,
                error: null,
            };
        case 'CLEAR_INTERRUPTION_STATE':
            return {
                ...state,
                interruptionState: InterruptionState.NONE,
                interruptionMeta: null,
                error: null,
            };
        default:
            return state;
    }
}

/**
 * Validation Layer
 */
const VALIDATION_ENABLED = process.env.NODE_ENV !== 'production';

/**
 * Invariant assertion utility
 */
function assertInvariants(state: Record<string, any>): string[] {
    const errors: string[] = [];
    // Example invariants (customize as needed):
    if (!state) errors.push('State is undefined');
    // Add more invariants here (e.g., required fields, valid relationships)
    return errors;
}

/**
 * Custom validator registry
 */
const customValidators: Array<(state: Record<string, any>) => Promise<string[]>> = [];

export function registerCustomValidator(fn: (state: Record<string, any>) => Promise<string[]>) {
    customValidators.push(fn);
}

/**
 * Middleware for logging, validation, and async ops
 */
function withMiddleware(set, get, api) {
    return async (action: InteractionAction) => {
        const prevState = get();
        let nextState = interactionReducer(prevState, action);
        // Logging
        if (action.type !== 'LOG_ACTION') {
            nextState = interactionReducer(nextState, {
                type: 'LOG_ACTION',
                payload: { action: action.type, payload: 'payload' in action ? action.payload : undefined },
            });
        }
        // Validation
        if (VALIDATION_ENABLED && (action.type === 'UPDATE_STATE' || action.type === 'INIT')) {
            const validator = createValidator<Record<string, any>>();
            // Add schema rules here as needed (extendable)
            let validation = await validator.validateState(nextState.stateTree);
            // Invariant assertions
            const invariantErrors = assertInvariants(nextState.stateTree);
            // Custom validators
            for (const fn of customValidators) {
                const customErrors = await fn(nextState.stateTree);
                if (customErrors && customErrors.length) {
                    validation = {
                        ...validation,
                        isValid: false,
                        errors: [...validation.errors, ...customErrors.map(msg => ({ field: 'custom', message: msg, code: 'CUSTOM' }))],
                    };
                }
            }
            if (invariantErrors.length) {
                validation = {
                    ...validation,
                    isValid: false,
                    errors: [...validation.errors, ...invariantErrors.map(msg => ({ field: 'invariant', message: msg, code: 'INVARIANT' }))],
                };
            }
            nextState = { ...nextState, validation };
            // Error reporting
            if (!validation.isValid) {
                nextState = {
                    ...nextState,
                    error: 'Validation failed',
                    debug: {
                        ...nextState.debug,
                        lastValidationError: validation.errors,
                    },
                };
            }
        }
        set(nextState);
    };
}

/**
 * Persistence handler
 */
const persistence = createPersistence({
    prefix: 'vdm_interaction_',
    debounceTime: 1000,
    version: 1,
});

/**
 * Utility: Serialize state tree (with optional compression stub)
 */
export function serializeState(state: Record<string, any>): string {
    // Placeholder for future compression (e.g., LZ-string, gzip)
    return JSON.stringify(state);
}

/**
 * Utility: Deserialize state tree
 */
export function deserializeState(serialized: string): Record<string, any> {
    // Placeholder for future decompression
    return JSON.parse(serialized);
}

/**
 * Snapshot Manager
 */
const MAX_SNAPSHOTS = 10;

function createSnapshot(state: Record<string, any>, context = 'manual'): InteractionSnapshot {
    return {
        timestamp: Date.now(),
        state: JSON.parse(JSON.stringify(state)), // deep clone
        meta: {
            version: 1,
            context,
        },
    };
}

function pruneSnapshots(snapshots: InteractionSnapshot[]): InteractionSnapshot[] {
    if (snapshots.length <= MAX_SNAPSHOTS) return snapshots;
    // Remove oldest snapshots
    return snapshots.slice(snapshots.length - MAX_SNAPSHOTS);
}

/**
 * Debugging Tools
 */
const MAX_ACTION_LOG = 100;

function logAction(debug: InteractionDebugInfo, action: InteractionAction, prevState: Record<string, any>, nextState: Record<string, any>, error?: string): InteractionDebugInfo {
    const entry: InteractionActionLogEntry = {
        action: typeof action === 'string' ? action : action.type,
        payload: 'payload' in action ? action.payload : undefined,
        beforeState: prevState,
        afterState: nextState,
        timestamp: Date.now(),
    };
    const newLog = [...(debug.actionLog || []), entry];
    return {
        ...debug,
        actionLog: newLog.slice(-MAX_ACTION_LOG),
        lastAction: entry.action,
        lastValidationError: debug.lastValidationError,
    };
}

type StoreMutators = [['zustand/devtools', never], ['zustand/subscribeWithSelector', never]];

/**
 * Zustand store for the Interaction System
 */
export interface InteractionStore extends InteractionState {
    dispatch: (action: InteractionAction) => Promise<void>;
    init: (payload?: any) => Promise<void>;
    updateState: (payload: Partial<Record<string, any>>) => Promise<void>;
    reset: () => Promise<void>;
    snapshot: () => Promise<void>;
    restoreSnapshot: (timestamp: number) => Promise<void>;
    validate: () => Promise<void>;
    save: () => Promise<void>;
    load: () => Promise<void>;
    createSnapshot: (context?: string) => InteractionSnapshot;
    restoreSnapshotDirect: (timestamp: number) => void;
    listSnapshots: () => { timestamp: number; meta: any }[];
    serialize: () => string;
    deserialize: (serialized: string) => void;
    startSnapshotInterval: (ms?: number) => void;
    stopSnapshotInterval: () => void;
}

export const useInteractionStore = create<InteractionStore, StoreMutators>(
    devtools(
        subscribeWithSelector((set, get, api) => ({
            stateTree: {},
            snapshots: [],
            validation: null,
            debug: { actionLog: [] },
            isLoading: false,
            error: null,
            interruptionState: InterruptionState.NONE,
            interruptionMeta: null,

            /**
             * Dispatch an action to the reducer
             */
            dispatch: async (action: InteractionAction) => {
                await withMiddleware(set, get, api)(action);
            },

            /**
             * Action creators
             */
            init: async (payload?: any) => {
                await (get as any)().dispatch({ type: 'INIT', payload });
            },
            updateState: async (payload: Partial<Record<string, any>>) => {
                await (get as any)().dispatch({ type: 'UPDATE_STATE', payload });
            },
            reset: async () => {
                await (get as any)().dispatch({ type: 'RESET' });
            },
            snapshot: async () => {
                await (get as any)().dispatch({ type: 'SNAPSHOT' });
            },
            restoreSnapshot: async (timestamp: number) => {
                await (get as any)().dispatch({ type: 'RESTORE_SNAPSHOT', payload: timestamp });
            },
            validate: async () => {
                await (get as any)().dispatch({ type: 'VALIDATE' });
            },
            /**
             * Persistence
             */
            save: async () => {
                await persistence.saveState('interaction', (get as any)().stateTree);
            },
            load: async () => {
                const state = await persistence.getStoredState<Record<string, any>>('interaction');
                if (state) await (get as any)().init(state);
            },
            /**
             * Create a snapshot of the current state (manual or interval)
             */
            createSnapshot: (context = 'manual') => {
                const snap = createSnapshot((get as any)().stateTree, context);
                const pruned = pruneSnapshots([...(get as any)().snapshots, snap]);
                (set as any)({ snapshots: pruned });
                return snap;
            },
            restoreSnapshotDirect: (timestamp: number) => {
                const snap = (get as any)().snapshots.find(s => s.timestamp === timestamp);
                if (!snap) {
                    (set as any)({ error: 'Snapshot not found' });
                    return;
                }
                (set as any)({ stateTree: JSON.parse(JSON.stringify(snap.state)), error: null });
            },
            /**
             * List all snapshots (metadata only)
             */
            listSnapshots: () => {
                return (get as any)().snapshots.map(s => ({ timestamp: s.timestamp, meta: s.meta }));
            },
            /**
             * Serialize the current state tree
             */
            serialize: () => {
                return serializeState((get as any)().stateTree);
            },
            /**
             * Deserialize and load a state tree
             */
            deserialize: (serialized: string) => {
                const state = deserializeState(serialized);
                (set as any)({ stateTree: state });
            },
            /**
             * (Optional) Set up interval-based snapshotting (call in app init if desired)
             */
            startSnapshotInterval: (ms = 60000) => {
                if ((get as any)()._snapshotInterval) return;
                (get as any)()._snapshotInterval = setInterval(() => {
                    (get as any)().createSnapshot('interval');
                }, ms);
            },
            stopSnapshotInterval: () => {
                if ((get as any)()._snapshotInterval) {
                    clearInterval((get as any)()._snapshotInterval);
                    (get as any)()._snapshotInterval = undefined;
                }
            },
        }))
    )
);

/**
 * Selectors and debugging hooks
 */
export const useInteractionState = () => useInteractionStore(state => state.stateTree);
export const useInteractionSnapshots = () => useInteractionStore(state => state.snapshots);
export const useInteractionValidation = () => useInteractionStore(state => state.validation);
export const useInteractionDebug = () => useInteractionStore(state => state.debug);
export const useInterruptionState = () => useInteractionStore(state => state.interruptionState);
export const useInterruptionMeta = () => useInteractionStore(state => state.interruptionMeta);

/**
 * Adapter for legacy components: provides a Redux-like API
 */
export const interactionStoreAdapter = {
    getState: () => useInteractionStore.getState().stateTree,
    dispatch: (action: InteractionAction) => useInteractionStore.getState().dispatch(action),
    subscribe: (listener: () => void) => useInteractionStore.subscribe(listener),
};

/**
 * Migration utility: transforms legacy state to new format
 * @param legacyState - The old state object
 * @returns New state shape for the Interaction System
 */
export function migrateLegacyState(legacyState: Record<string, any>): Record<string, any> {
    // Example: flatten nested keys, rename fields, etc.
    // This should be customized for the actual legacy format
    const newState: Record<string, any> = { ...legacyState };
    // Add transformation logic here as needed
    return newState;
}

/**
 * Facade for external consumers: simplified interface
 */
export class InteractionStateFacade {
    static get() { return useInteractionStore.getState().stateTree; }
    static set(newState: Record<string, any>) { useInteractionStore.setState({ stateTree: newState }); }
    static subscribe(listener: () => void) { return useInteractionStore.subscribe(listener); }
    static validate() { return useInteractionStore.getState().validate(); }
    static snapshot(context?: string) { return useInteractionStore.getState().createSnapshot(context); }
    static restore(timestamp: number) { return useInteractionStore.getState().restoreSnapshot(timestamp); }
}

/**
 * React connection utilities for UI integration
 */
export const useInteractionDispatch = () => useInteractionStore(state => state.dispatch);

/**
 * Integration & Migration Patterns
 *
 * - Use interactionStoreAdapter for legacy Redux-like components
 * - Use migrateLegacyState to convert old state data on load
 * - Use InteractionStateFacade for simplified, framework-agnostic access
 * - Use useInteractionState and useInteractionDispatch in React components
 * - Gradual adoption: keep old and new systems in sync during transition, using subscribe and setState hooks
 */

/**
 * Configurable performance options
 */
export const InteractionStoreConfig = {
    maxSnapshots: 10,
    enableBatching: true,
    enableMemoization: true,
};

/**
 * Selective state update hook using shallow comparison
 */
export const useShallowInteractionState = <T>(selector: (state: InteractionStore) => T) =>
    useInteractionStore(selector);

/**
 * Memoized selector for derived state
 */
export function useMemoizedInteractionSelector<T>(selector: (state: InteractionState) => T, deps: any[] = []) {
    return useMemo(() => selector(useInteractionStore.getState()), deps);
}

/**
 * Batched updates utility
 */
export function batchInteractionUpdates(updates: (() => void)[]) {
    if (InteractionStoreConfig.enableBatching && typeof window !== 'undefined' && (window as any).unstable_batchedUpdates) {
        (window as any).unstable_batchedUpdates(() => { updates.forEach(fn => fn()); });
    } else {
        updates.forEach(fn => fn());
    }
}

/**
 * Optimized snapshot creation (structural sharing)
 */
function createOptimizedSnapshot(state: Record<string, any>, context = 'manual'): InteractionSnapshot {
    // Use shallow copy for top-level, avoid deep clone unless necessary
    return {
        timestamp: Date.now(),
        state: { ...state },
        meta: {
            version: 1,
            context,
        },
    };
}

/**
 * Benchmark utility for store performance
 */
export async function benchmarkInteractionStore(iterations = 1000) {
    const start = performance.now();
    for (let i = 0; i < iterations; i++) {
        useInteractionStore.getState().updateState({ [`key${i}`]: i });
    }
    const end = performance.now();
    return { iterations, durationMs: end - start, avgMs: (end - start) / iterations };
}

/**
 * Interruption State Management API:
 * - setInterruptionState(state: InterruptionState, event: string, details?: any): sets the interruption state and logs metadata
 * - clearInterruptionState(): clears the interruption state
 * - useInterruptionState(): React hook to access current interruption state
 * - useInterruptionMeta(): React hook to access current interruption metadata
 *
 * All interruption state changes are timestamped and include event metadata for debugging and analytics.
 */

export const setInterruptionState = (state: InterruptionState, event: string, details?: any) => ({
    type: 'SET_INTERRUPTION_STATE',
    payload: {
        state,
        meta: {
            timestamp: Date.now(),
            event,
            details,
        },
    },
});

export const clearInterruptionState = () => ({ type: 'CLEAR_INTERRUPTION_STATE' });

/**
 * Selector to get interruption config
 */
export const selectInterruptionConfig = () => interruptionConfig;

// At the store creation:
export const interactionStore = useInteractionStore;

/**
 * External subscription utility for non-React consumers (e.g., DialogueManager)
 * @param callback Function to call with new state on every update
 * @returns Unsubscribe function
 */
export function subscribeToInteractionState(callback: (state: InteractionState) => void): () => void {
    return interactionStore.subscribe(callback);
} 