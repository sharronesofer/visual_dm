import { CombatAction } from './CombatAction';

export class InterruptSystem {
    private interrupts: CombatAction[] = [];

    registerInterrupt(action: CombatAction): void {
        this.interrupts.push(action);
        // Sort by priority (higher first)
        this.interrupts.sort((a, b) => b.getPriority() - a.getPriority());
    }

    resolveInterrupts(): CombatAction[] {
        // Return and clear all interrupts (could be more sophisticated)
        const resolved = [...this.interrupts];
        this.interrupts = [];
        return resolved;
    }

    pauseAction(action: CombatAction): void {
        // Stub: mark action as paused (extend as needed)
        // Could add a pausedActions list or flag
    }

    resumeAction(action: CombatAction): void {
        // Stub: resume a paused action
    }
} 