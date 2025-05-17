import { Command } from './Command';

export class CommandManager {
    private history: Command[] = [];
    private index: number = -1;

    async executeCommand(command: Command): Promise<void> {
        // Remove any redoable commands
        if (this.index < this.history.length - 1) {
            this.history = this.history.slice(0, this.index + 1);
        }
        await command.execute();
        this.history.push(command);
        this.index++;
    }

    async undo(): Promise<void> {
        if (this.index >= 0) {
            const command = this.history[this.index];
            await command.undo();
            this.index--;
        }
    }

    async redo(): Promise<void> {
        if (this.index < this.history.length - 1) {
            this.index++;
            const command = this.history[this.index];
            await command.execute();
        }
    }

    canUndo(): boolean {
        return this.index >= 0;
    }

    canRedo(): boolean {
        return this.index < this.history.length - 1;
    }

    getHistory(): Command[] {
        return this.history.slice();
    }

    getCurrentIndex(): number {
        return this.index;
    }
} 