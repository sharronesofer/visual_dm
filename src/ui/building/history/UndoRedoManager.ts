// UndoRedoManager.ts
import { ICommand } from './ICommand';

export class UndoRedoManager {
    private history: ICommand[] = [];
    private redoStack: ICommand[] = [];
    private maxDepth: number;

    constructor(maxDepth: number = 20) {
        this.maxDepth = maxDepth;
    }

    executeCommand(cmd: ICommand) {
        cmd.execute();
        this.history.push(cmd);
        if (this.history.length > this.maxDepth) {
            this.history.shift();
        }
        this.redoStack = [];
    }

    undo() {
        if (this.history.length === 0) return;
        const cmd = this.history.pop()!;
        cmd.undo();
        this.redoStack.push(cmd);
    }

    redo() {
        if (this.redoStack.length === 0) return;
        const cmd = this.redoStack.pop()!;
        cmd.redo();
        this.history.push(cmd);
    }

    clear() {
        this.history = [];
        this.redoStack = [];
    }

    canUndo() {
        return this.history.length > 0;
    }

    canRedo() {
        return this.redoStack.length > 0;
    }
} 