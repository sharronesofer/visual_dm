import * as fs from 'fs';
import * as path from 'path';

export interface ReputationAuditEvent {
    timestamp: string;
    sourceSystem: string;
    targetEntity: string;
    valueChange: number;
    context?: string;
    callingSystem: string;
}

export class ReputationAuditLogger {
    private static logFilePath = path.resolve(process.cwd(), 'logs/reputation_audit.log');
    private static instance: ReputationAuditLogger;

    private constructor() {
        // Ensure log directory exists
        const dir = path.dirname(ReputationAuditLogger.logFilePath);
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
    }

    public static getInstance(): ReputationAuditLogger {
        if (!ReputationAuditLogger.instance) {
            ReputationAuditLogger.instance = new ReputationAuditLogger();
        }
        return ReputationAuditLogger.instance;
    }

    public logChange(event: ReputationAuditEvent): void {
        const logEntry = JSON.stringify(event) + '\n';
        fs.appendFileSync(ReputationAuditLogger.logFilePath, logEntry, { encoding: 'utf8' });
        if (process.env.NODE_ENV !== 'production') {
            // Also log to console in development
            // eslint-disable-next-line no-console
            console.log('[ReputationAudit]', event);
        }
    }

    // Convenience static method
    public static log(event: ReputationAuditEvent): void {
        ReputationAuditLogger.getInstance().logChange(event);
    }
}

// Example usage:
// ReputationAuditLogger.log({
//   timestamp: new Date().toISOString(),
//   sourceSystem: 'QuestSystem',
//   targetEntity: 'FactionA',
//   valueChange: 10,
//   context: 'Quest completion',
//   callingSystem: 'FactionQuestSystem.updateStandings'
// }); 