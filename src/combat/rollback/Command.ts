export interface Command {
    id: string;
    description?: string;
    execute(): Promise<void>;
    undo(): Promise<void>;
}

export abstract class BaseCommand implements Command {
    id: string;
    description?: string;

    constructor(id: string, description?: string) {
        this.id = id;
        this.description = description;
    }

    abstract execute(): Promise<void>;
    abstract undo(): Promise<void>;
} 