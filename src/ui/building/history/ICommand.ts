// ICommand.ts
export interface ICommand {
    execute(): void;
    undo(): void;
    redo(): void;
} 