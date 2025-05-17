import { LogLevel as EnumLogLevel, EventType, LogEntry } from './types';
import { getRequestContext } from '../middleware/requestContext';
import fs from 'fs';
import path from 'path';
import client from 'prom-client';
import { setTimeout as sleep } from 'timers/promises';

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export interface LoggerTransport {
    log: (entry: Record<string, any> | string) => void;
}

export interface UnifiedLoggerConfig {
    level?: LogLevel | EnumLogLevel;
    module?: string;
    transports?: LoggerTransport[];
    enableMetrics?: boolean;
    filePath?: string;
    flushInterval?: number;
    format?: 'json' | 'text';
    maxSize?: number;
}

// Console transport
class ConsoleTransport implements LoggerTransport {
    log(entry: Record<string, any> | string) {
        if (typeof entry === 'string') {
            // Assume already formatted
            if (entry.includes('ERROR')) console.error(entry);
            else if (entry.includes('WARN')) console.warn(entry);
            else if (entry.includes('DEBUG')) console.debug(entry);
            else console.info(entry);
            return;
        }
        // Use console methods based on level
        const level = entry.level || entry.logLevel || 'info';
        const msg = JSON.stringify(entry);
        if (level === 'error') console.error(msg);
        else if (level === 'warn') console.warn(msg);
        else if (level === 'debug') console.debug(msg);
        else console.info(msg);
    }
}

// File transport (simple append, not rotating)
class FileTransport implements LoggerTransport {
    private file: string;
    constructor(filePath: string) {
        this.file = filePath;
        // Ensure directory exists
        fs.mkdirSync(path.dirname(filePath), { recursive: true });
    }
    log(entry: Record<string, any> | string) {
        if (typeof entry === 'string') {
            fs.appendFileSync(this.file, entry + '\n');
        } else {
            fs.appendFileSync(this.file, JSON.stringify(entry) + '\n');
        }
    }
}

// Prometheus metrics (optional)
const eventCounter = new client.Counter({
    name: 'app_log_events_total',
    help: 'Total number of log events',
    labelNames: ['level', 'module'],
});

// Utility for log rotation (daily/size-based)
function getRotatedFileName(base: string, date: Date = new Date()) {
    const day = date.toISOString().slice(0, 10);
    return `${base.replace(/\.log$/, '')}.${day}.log`;
}

class RotatingFileTransport implements LoggerTransport {
    private baseFile: string;
    private maxSize: number;
    private buffer: string[] = [];
    private flushInterval: number;
    private timer: NodeJS.Timeout | null = null;
    private currentFile: string;
    private lastFlush: number = Date.now();

    constructor(filePath: string, maxSize = 10 * 1024 * 1024, flushInterval = 1000) {
        this.baseFile = filePath;
        this.maxSize = maxSize;
        this.flushInterval = flushInterval;
        this.currentFile = getRotatedFileName(this.baseFile);
        this.startFlushTimer();
    }

    private startFlushTimer() {
        if (this.timer) clearInterval(this.timer);
        this.timer = setInterval(() => this.flush(), this.flushInterval);
    }

    private rotateIfNeeded() {
        const file = getRotatedFileName(this.baseFile);
        if (file !== this.currentFile) {
            this.currentFile = file;
        }
        try {
            if (fs.existsSync(this.currentFile) && fs.statSync(this.currentFile).size > this.maxSize) {
                // TODO: Implement size-based rotation, compression, and retention policy
                const rotated = this.currentFile.replace(/\.log$/, `.${Date.now()}.log`);
                fs.renameSync(this.currentFile, rotated);
                // Optionally compress rotated file here
            }
        } catch (e) { }
    }

    log(entry: Record<string, any> | string) {
        if (typeof entry === 'string') {
            this.buffer.push(entry);
        } else {
            this.buffer.push(JSON.stringify(entry));
        }
        if (this.buffer.length > 100) this.flush();
    }

    flush() {
        if (this.buffer.length === 0) return;
        this.rotateIfNeeded();
        fs.appendFileSync(this.currentFile, this.buffer.join('\n') + '\n');
        this.buffer = [];
        this.lastFlush = Date.now();
    }

    async shutdown() {
        if (this.timer) clearInterval(this.timer);
        this.flush();
    }
}

export class UnifiedLogger {
    private static instance: UnifiedLogger;
    private level: LogLevel;
    private module: string;
    private transports: LoggerTransport[];
    private enableMetrics: boolean;
    private flushInterval: number;
    private shutdownHandlers: (() => Promise<void>)[] = [];
    private format: 'json' | 'text';

    constructor(config: UnifiedLoggerConfig = {}) {
        this.level = this.normalizeLevel(config.level || 'info');
        this.module = config.module || '';
        this.transports = config.transports || [new ConsoleTransport()];
        this.enableMetrics = config.enableMetrics || false;
        this.flushInterval = (config as any).flushInterval || 1000;
        this.format = (config as any).format || 'json';
        if (config.filePath) {
            const rotating = new RotatingFileTransport(config.filePath, (config as any).maxSize || 10 * 1024 * 1024, this.flushInterval);
            this.transports.push(rotating);
            this.shutdownHandlers.push(() => rotating.shutdown());
        }
    }

    public static getInstance(config?: UnifiedLoggerConfig): UnifiedLogger {
        if (!UnifiedLogger.instance) {
            UnifiedLogger.instance = new UnifiedLogger(config);
            // Register shutdown handler
            process.on('exit', async () => {
                await UnifiedLogger.instance.shutdown();
            });
            process.on('SIGINT', async () => {
                await UnifiedLogger.instance.shutdown();
                process.exit(0);
            });
        }
        return UnifiedLogger.instance;
    }

    public child(module: string): UnifiedLogger {
        return new UnifiedLogger({
            level: this.level,
            module: this.module ? `${this.module}:${module}` : module,
            transports: this.transports,
            enableMetrics: this.enableMetrics,
            flushInterval: this.flushInterval,
            format: this.format,
        });
    }

    public setLevel(level: LogLevel | EnumLogLevel) {
        this.level = this.normalizeLevel(level);
    }

    public getLevel(): LogLevel {
        return this.level;
    }

    public debug(message: string, meta?: Record<string, any>) {
        this.log('debug', message, meta);
    }
    public info(message: string, meta?: Record<string, any>) {
        this.log('info', message, meta);
    }
    public warn(message: string, meta?: Record<string, any>) {
        this.log('warn', message, meta);
    }
    public error(message: string, meta?: Record<string, any>) {
        this.log('error', message, meta);
    }

    private log(level: LogLevel, message: string, meta?: Record<string, any>) {
        if (!this.shouldLog(level)) return;
        const timestamp = new Date().toISOString();
        const requestContext = getRequestContext();
        const entry = {
            timestamp,
            level,
            module: this.module,
            message,
            requestId: requestContext?.requestId,
            userId: requestContext?.userId,
            ...meta,
        };
        for (const transport of this.transports) {
            transport.log(this.format === 'json' ? entry : this.formatText(entry));
        }
        if (this.enableMetrics) {
            eventCounter.inc({ level, module: this.module });
        }
    }

    private formatText(entry: Record<string, any>): string {
        // Simple plain text formatter with color coding for console
        const { timestamp, level, module, message, ...meta } = entry;
        const color = (lvl: string) => {
            switch (lvl) {
                case 'error': return '\x1b[31m';
                case 'warn': return '\x1b[33m';
                case 'info': return '\x1b[32m';
                case 'debug': return '\x1b[36m';
                default: return '';
            }
        };
        const reset = '\x1b[0m';
        const prefix = module ? `[${module}]` : '';
        const metaStr = Object.keys(meta).length ? ` ${JSON.stringify(meta)}` : '';
        return `${color(level)}${timestamp} ${prefix} ${level.toUpperCase()}: ${message}${metaStr}${reset}`;
    }

    private shouldLog(level: LogLevel): boolean {
        const order: LogLevel[] = ['error', 'warn', 'info', 'debug'];
        return order.indexOf(level) <= order.indexOf(this.level);
    }

    private normalizeLevel(level: LogLevel | EnumLogLevel): LogLevel {
        if (typeof level === 'string') {
            return level.toLowerCase() as LogLevel;
        }
        switch (level) {
            case EnumLogLevel.ERROR: return 'error';
            case EnumLogLevel.WARN: return 'warn';
            case EnumLogLevel.INFO: return 'info';
            case EnumLogLevel.DEBUG:
            case EnumLogLevel.TRACE: return 'debug';
            default: return 'info';
        }
    }

    /**
     * Flush and shutdown all async transports (for graceful shutdown)
     */
    public async shutdown() {
        for (const handler of this.shutdownHandlers) {
            await handler();
        }
    }
}

// Backward compatibility adapter for src/utils/logger.ts
/**
 * @deprecated Use UnifiedLogger from src/logging/Logger.ts directly. This adapter will be removed in a future release.
 */
export const logger = UnifiedLogger.getInstance();
