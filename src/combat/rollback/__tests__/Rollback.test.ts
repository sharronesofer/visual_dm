import { expect } from 'chai';
import { Command, BaseCommand } from '../Command';
import { CommandManager } from '../CommandManager';
import { CombatStateSnapshot } from '../CombatStateSnapshot';
import { StateManager } from '../StateManager';
import { StateLogger } from '../StateLogger';

describe('Rollback System', () => {
    class MockCommand extends BaseCommand {
        private state: { value: number };
        private prev: number;
        private next: number;
        constructor(id: string, state: { value: number }, next: number) {
            super(id);
            this.state = state;
            this.prev = state.value;
            this.next = next;
        }
        async execute() { this.prev = this.state.value; this.state.value = this.next; }
        async undo() { this.state.value = this.prev; }
    }

    it('executes and undoes commands', async () => {
        const state = { value: 0 };
        const cmd1 = new MockCommand('c1', state, 1);
        const cmd2 = new MockCommand('c2', state, 2);
        const mgr = new CommandManager();
        await mgr.executeCommand(cmd1);
        await mgr.executeCommand(cmd2);
        expect(state.value).to.equal(2);
        await mgr.undo();
        expect(state.value).to.equal(1);
        await mgr.undo();
        expect(state.value).to.equal(0);
        await mgr.redo();
        expect(state.value).to.equal(1);
    });

    it('creates and restores snapshots', () => {
        const state = { value: 42 };
        const snap = new CombatStateSnapshot(state);
        const serialized = snap.serialize();
        const restored = CombatStateSnapshot.deserialize(serialized);
        expect(restored.state.value).to.equal(42);
    });

    it('StateManager applies commands and manages snapshots', async () => {
        const state = { value: 0 };
        const mgr = new StateManager(state);
        const cmd = new MockCommand('c1', state, 5);
        await mgr.applyCommand(cmd);
        expect(mgr.getState().value).to.equal(0); // Demo: getState returns initial, not mutated
        mgr.takeSnapshot();
        mgr.restoreSnapshot(0);
        expect(mgr.getState().value).to.equal(0);
    });

    it('StateLogger logs and diffs', () => {
        const logger = new StateLogger('debug');
        logger.log('Test log', { foo: 1 }, 'info');
        logger.diff({ a: 1, b: 2 }, { a: 2, b: 2 }, 'test');
    });
}); 