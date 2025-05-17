export interface ActionResult {
    success: boolean;
    message?: string;
    [key: string]: any;
}

export abstract class CombatAction {
    abstract id: string;
    abstract execute(): Promise<ActionResult>;
    abstract cancel(reason?: string): void;
    abstract getPrerequisites(): CombatAction[];
    abstract getPriority(): number;
    abstract getInterruptible(): boolean;
} 