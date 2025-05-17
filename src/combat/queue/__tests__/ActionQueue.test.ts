import { expect } from 'chai';
import { ActionQueue } from '../ActionQueue';
import { CombatAction, ActionResult } from '../CombatAction';
import { ActionQueueVisualizer } from '../ActionQueueVisualizer';

describe('ActionQueue', () => {
    class MockAction extends CombatAction {
        constructor(
            public id: string,
            private priority: number = 0,
            private prereqs: CombatAction[] = [],
            private interruptible: boolean = true
        ) { super(); }
        async execute(): Promise<ActionResult> { return { success: true, message: this.id + ' executed' }; }
        cancel(): void { }
        getPrerequisites(): CombatAction[] { return this.prereqs; }
        getPriority(): number { return this.priority; }
        getInterruptible(): boolean { return this.interruptible; }
    }

    it('enqueues and dequeues actions in priority order', async () => {
        const queue = new ActionQueue();
        const a1 = new MockAction('a1', 1);
        const a2 = new MockAction('a2', 3);
        const a3 = new MockAction('a3', 2);
        queue.enqueue(a1);
        queue.enqueue(a2);
        queue.enqueue(a3);
        const ids = queue.getQueue().map(a => a.id);
        expect(ids).to.deep.equal(['a2', 'a3', 'a1']);
        const result = await queue.executeNext();
        expect(result?.success).to.equal(true);
        expect(result?.message).to.include('a2');
    });

    it('removes actions and triggers callbacks', () => {
        const queue = new ActionQueue();
        const a1 = new MockAction('a1', 1);
        let removedId = '';
        queue.onActionRemoved(a => { removedId = a.id; });
        queue.enqueue(a1);
        const removed = queue.remove('a1');
        expect(removed).to.equal(true);
        expect(removedId).to.equal('a1');
    });

    it('handles dependencies (prerequisites)', async () => {
        const a1 = new MockAction('a1', 2);
        const a2 = new MockAction('a2', 1, [a1]);
        const queue = new ActionQueue();
        queue.enqueue(a2);
        queue.enqueue(a1);
        // a2 should not execute before a1
        let result = await queue.executeNext();
        expect(result?.success).to.equal(true);
        expect(result?.message).to.include('a1');
        result = await queue.executeNext();
        expect(result?.success).to.equal(true);
        expect(result?.message).to.include('a2');
    });

    it('visualizes the queue', () => {
        const queue = new ActionQueue();
        const a1 = new MockAction('a1', 1);
        const a2 = new MockAction('a2', 2, [a1]);
        queue.enqueue(a1);
        queue.enqueue(a2);
        ActionQueueVisualizer.printQueue(queue.getQueue());
    });
}); 