import { CombatAction } from './CombatAction';

export class ActionQueueVisualizer {
    static printQueue(queue: CombatAction[]): void {
        console.log('--- Action Queue ---');
        for (const action of queue) {
            const deps = action.getPrerequisites().map(a => a.id).join(', ');
            console.log(`ID: ${action.id} | Priority: ${action.getPriority()} | Deps: [${deps}] | Interruptible: ${action.getInterruptible()}`);
        }
        console.log('--------------------');
    }
} 