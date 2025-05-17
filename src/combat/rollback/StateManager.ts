import { CommandManager } from './CommandManager';
import { Command } from './Command';
import { CombatStateSnapshot } from './CombatStateSnapshot';

export class StateManager<T = any> {
    private commandManager = new CommandManager();
    private currentState: T;
    private snapshots: CombatStateSnapshot<T>[] = [];

    constructor(initialState: T) {
        this.currentState = JSON.parse(JSON.stringify(initialState));
        this.snapshots.push(new CombatStateSnapshot<T>(this.currentState));
    }

    getState(): T {
        return JSON.parse(JSON.stringify(this.currentState));
    }

    async applyCommand(command: Command): Promise<void> {
        await this.commandManager.executeCommand(command);
        // After command, take a new snapshot
        this.currentState = this.getStateFromCommand(command);
        this.snapshots.push(new CombatStateSnapshot<T>(this.currentState));
    }

    async undo(): Promise<void> {
        await this.commandManager.undo();
        // Restore previous snapshot
        if (this.snapshots.length > 1) {
            this.snapshots.pop();
            this.currentState = this.snapshots[this.snapshots.length - 1].clone().state;
        }
    }

    async redo(): Promise<void> {
        await this.commandManager.redo();
        // Redo should apply the next snapshot if available
        // (In a real system, would re-execute the command and snapshot)
    }

    takeSnapshot(): void {
        this.snapshots.push(new CombatStateSnapshot<T>(this.currentState));
    }

    restoreSnapshot(index: number): void {
        if (index >= 0 && index < this.snapshots.length) {
            this.currentState = this.snapshots[index].clone().state;
        }
    }

    getSnapshots(): CombatStateSnapshot<T>[] {
        return this.snapshots.map(s => s.clone());
    }

    private getStateFromCommand(command: Command): T {
        // In a real system, the command would mutate the state and return it
        // Here, just return the current state for demonstration
        return this.currentState;
    }
} 