import { useInteractionStore } from '../core/interactionStore';

describe('Interaction Store', () => {
    beforeEach(() => {
        useInteractionStore.getState().reset();
    });

    it('should initialize with empty state', () => {
        const state = useInteractionStore.getState();
        expect(state.stateTree).toEqual({});
        expect(state.snapshots).toEqual([]);
        expect(state.validation).toBeNull();
        expect(state.debug.actionLog).toEqual([]);
        expect(state.isLoading).toBe(false);
        expect(state.error).toBeNull();
    });

    it('should update state via action', async () => {
        await useInteractionStore.getState().updateState({ foo: 'bar' });
        const state = useInteractionStore.getState();
        expect(state.stateTree.foo).toBe('bar');
    });

    it('should create and restore snapshots', async () => {
        await useInteractionStore.getState().updateState({ a: 1 });
        await useInteractionStore.getState().snapshot();
        await useInteractionStore.getState().updateState({ a: 2 });
        const snap = useInteractionStore.getState().snapshots[0];
        expect(snap.state.a).toBe(1);
        await useInteractionStore.getState().restoreSnapshot(snap.timestamp);
        expect(useInteractionStore.getState().stateTree.a).toBe(1);
    });

    it('should validate state on update', async () => {
        await useInteractionStore.getState().updateState({ test: 'value' });
        const validation = useInteractionStore.getState().validation;
        expect(validation).toBeDefined();
        expect(typeof validation.isValid).toBe('boolean');
    });

    it('should log actions', async () => {
        await useInteractionStore.getState().updateState({ x: 42 });
        const log = useInteractionStore.getState().debug.actionLog;
        expect(log.length).toBeGreaterThan(0);
        expect(log[log.length - 1].action).toBe('UPDATE_STATE');
    });
}); 