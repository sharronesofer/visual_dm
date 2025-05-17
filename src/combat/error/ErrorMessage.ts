import { ErrorCategory } from './ErrorCategory';

export enum SeverityLevel {
    CRITICAL = 'CRITICAL',
    ERROR = 'ERROR',
    WARNING = 'WARNING',
    INFO = 'INFO',
}

export class ErrorMessage {
    readonly category: ErrorCategory;
    readonly severity: SeverityLevel;
    readonly description: string;
    readonly suggestion?: string;
    readonly metadata?: Record<string, any>;

    constructor(
        category: ErrorCategory,
        severity: SeverityLevel,
        description: string,
        suggestion?: string,
        metadata?: Record<string, any>
    ) {
        this.category = category;
        this.severity = severity;
        this.description = description;
        this.suggestion = suggestion;
        this.metadata = metadata;
    }
} 