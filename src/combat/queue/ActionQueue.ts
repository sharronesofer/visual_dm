import { CombatAction, ActionResult } from './CombatAction';

type ActionCallback = (action: CombatAction) => void;
type ResultCallback = (result: ActionResult) => void;
type VoidCallback = () => void;

export class ActionQueue {
    private queue: CombatAction[] = [];
    private onActionAddedCallbacks: ActionCallback[] = [];
    private onActionRemovedCallbacks: ActionCallback[] = [];
    private onActionExecutedCallbacks: ResultCallback[] = [];
    private onQueueEmptyCallbacks: VoidCallback[] = [];

    enqueue(action: CombatAction): void {
        this.queue.push(action);
        this.sort();
        this.onActionAddedCallbacks.forEach(cb => cb(action));
    }

    dequeue(): CombatAction | undefined {
        const action = this.queue.shift();
        if (action) this.onActionRemovedCallbacks.forEach(cb => cb(action));
        if (this.queue.length === 0) this.onQueueEmptyCallbacks.forEach(cb => cb());
        return action;
    }

    peek(): CombatAction | undefined {
        return this.queue[0];
    }

    remove(actionId: string): boolean {
        const idx = this.queue.findIndex(a => a.id === actionId);
        if (idx !== -1) {
            const [removed] = this.queue.splice(idx, 1);
            this.onActionRemovedCallbacks.forEach(cb => cb(removed));
            if (this.queue.length === 0) this.onQueueEmptyCallbacks.forEach(cb => cb());
            return true;
        }
        return false;
    }

    sort(): void {
        // Sort by priority (desc), then by id for stability
        this.queue.sort((a, b) => b.getPriority() - a.getPriority() || a.id.localeCompare(b.id));
        // TODO: Add dependency-aware topological sort
    }

    async executeNext(): Promise<ActionResult | undefined> {
        const action = this.peek();
        if (!action) return undefined;
        // Check prerequisites
        const prereqs = action.getPrerequisites();
        if (prereqs && prereqs.length > 0) {
            // Only execute if all prereqs are not in the queue
            const pending = prereqs.filter(pr => this.queue.some(a => a.id === pr.id));
            if (pending.length > 0) return { success: false, message: 'Prerequisites not met' };
        }
        this.dequeue();
        const result = await action.execute();
        this.onActionExecutedCallbacks.forEach(cb => cb(result));
        return result;
    }

    // Event registration
    onActionAdded(cb: ActionCallback) { this.onActionAddedCallbacks.push(cb); }
    onActionRemoved(cb: ActionCallback) { this.onActionRemovedCallbacks.push(cb); }
    onActionExecuted(cb: ResultCallback) { this.onActionExecutedCallbacks.push(cb); }
    onQueueEmpty(cb: VoidCallback) { this.onQueueEmptyCallbacks.push(cb); }

    // Additional queue modification methods
    insertBefore(actionId: string, newAction: CombatAction): void {
        const idx = this.queue.findIndex(a => a.id === actionId);
        if (idx !== -1) {
            this.queue.splice(idx, 0, newAction);
            this.sort();
            this.onActionAddedCallbacks.forEach(cb => cb(newAction));
        } else {
            this.enqueue(newAction);
        }
    }

    insertAfter(actionId: string, newAction: CombatAction): void {
        const idx = this.queue.findIndex(a => a.id === actionId);
        if (idx !== -1) {
            this.queue.splice(idx + 1, 0, newAction);
            this.sort();
            this.onActionAddedCallbacks.forEach(cb => cb(newAction));
        } else {
            this.enqueue(newAction);
        }
    }

    modifyPriority(actionId: string, newPriority: number): void {
        const action = this.queue.find(a => a.id === actionId);
        if (action) {
            // @ts-ignore
            action.priority = newPriority;
            this.sort();
        }
    }

    clearQueue(): void {
        while (this.queue.length > 0) {
            const action = this.queue.shift();
            if (action) this.onActionRemovedCallbacks.forEach(cb => cb(action));
        }
        this.onQueueEmptyCallbacks.forEach(cb => cb());
    }

    getQueue(): CombatAction[] {
        return [...this.queue];
    }
} 