// Transaction state types
export type TransactionState = 'pending' | 'in-progress' | 'completed' | 'failed';

// Exception types
export class InsufficientResourcesException extends Error { }
export class InvalidBuildingStateException extends Error { }
export class TransactionFailedException extends Error {
    constructor(message: string, public readonly cause?: Error) {
        super(message);
        this.name = 'TransactionFailedException';
    }
}

// Abstract Command pattern for upgrade steps
export abstract class UpgradeCommand {
    abstract execute(): Promise<void>;
    abstract rollback(): Promise<void>;
    // Optionally, serialize/deserialize for checkpointing
}

// Example concrete command: ResourceDeductionCommand
export class ResourceDeductionCommand extends UpgradeCommand {
    constructor(private playerResources: any, private cost: any) { super(); }
    private deducted: any = {};
    async execute() {
        // Deduct resources, record what was deducted
        for (const [resource, amount] of Object.entries(this.cost.resources) as [string, number][]) {
            if ((this.playerResources[resource] || 0) < amount) {
                throw new InsufficientResourcesException('Not enough resources');
            }
            this.playerResources[resource] -= amount;
            this.deducted[resource] = amount;
        }
    }
    async rollback() {
        // Restore deducted resources
        for (const [resource, amount] of Object.entries(this.deducted) as [string, number][]) {
            this.playerResources[resource] += amount;
        }
    }
}

// Example concrete command: BuildingStateChangeCommand
export class BuildingStateChangeCommand extends UpgradeCommand {
    constructor(private building: any, private newState: any) { super(); }
    private prevState: any;
    async execute() {
        this.prevState = { ...this.building };
        Object.assign(this.building, this.newState);
    }
    async rollback() {
        Object.assign(this.building, this.prevState);
    }
}

// Transaction logger (simple version)
export class TransactionLogger {
    logs: any[] = [];
    log(entry: any) { this.logs.push({ ...entry, timestamp: new Date().toISOString() }); }
}

// Main transaction manager
export class BuildingUpgradeTransaction {
    private state: TransactionState = 'pending';
    private executedCommands: UpgradeCommand[] = [];
    private checkpointData: any = null;
    private logger: TransactionLogger;

    constructor(private commands: UpgradeCommand[], logger?: TransactionLogger) {
        this.logger = logger || new TransactionLogger();
    }

    getState() { return this.state; }

    async start() {
        this.state = 'in-progress';
        this.logger.log({ event: 'transaction_start' });
        try {
            for (const command of this.commands) {
                await command.execute();
                this.executedCommands.push(command);
                this.saveCheckpoint();
                this.logger.log({ event: 'command_executed', command: command.constructor.name });
            }
            this.state = 'completed';
            this.logger.log({ event: 'transaction_completed' });
        } catch (err) {
            this.state = 'failed';
            this.logger.log({ event: 'transaction_failed', error: err.message });
            await this.rollback();
            throw new TransactionFailedException('Upgrade transaction failed', err);
        }
    }

    private async rollback() {
        for (let i = this.executedCommands.length - 1; i >= 0; i--) {
            try {
                await this.executedCommands[i].rollback();
                this.logger.log({ event: 'command_rolled_back', command: this.executedCommands[i].constructor.name });
            } catch (err) {
                this.logger.log({ event: 'rollback_failed', error: err.message });
            }
        }
    }

    private saveCheckpoint() {
        // For demonstration, just store the number of executed commands
        this.checkpointData = { executed: this.executedCommands.length };
        this.logger.log({ event: 'checkpoint_saved', data: this.checkpointData });
    }

    getCheckpoint() {
        return this.checkpointData;
    }

    getLogs() {
        return this.logger.logs;
    }
} 