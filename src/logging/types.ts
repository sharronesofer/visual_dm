export enum LogLevel {
    ERROR = 'ERROR',
    WARN = 'WARN',
    INFO = 'INFO',
    DEBUG = 'DEBUG',
    TRACE = 'TRACE',
}

export enum EventType {
    STATE_CHANGE = 'state_change',
    ERROR = 'error',
    EDGE_CASE = 'edge_case',
    PERFORMANCE = 'performance',
}

export interface LogEntry {
    poiId: string | number;
    poiType: string;
    eventType: EventType;
    eventSubtype: string;
    timestamp: string; // ISO8601 UTC
    actor: string;
    beforeState?: Record<string, any>;
    afterState?: Record<string, any>;
    correlationId: string;
    message: string;
    logLevel: LogLevel;
}

