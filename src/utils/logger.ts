/**
 * Logging system for the media management application
 * @module logger
 */

/**
 * Log levels
 */
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

/**
 * Log metadata type
 */
export type LogMetadata = Record<string, any>;

/**
 * Logger configuration
 */
export interface LoggerConfig {
  level?: LogLevel;
  prefix?: string;
  metadata?: LogMetadata;
}

/**
 * Logger utility class
 */
export class Logger {
  private static instance: Logger;
  private level: LogLevel;
  private prefix: string;
  private metadata: LogMetadata;

  constructor(config: LoggerConfig = {}) {
    this.level = config.level || 'info';
    this.prefix = config.prefix || '';
    this.metadata = config.metadata || {};
  }

  /**
   * Get logger instance (singleton)
   */
  public static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  /**
   * Create a child logger with additional prefix
   */
  public child(prefix: string, metadata: LogMetadata = {}): Logger {
    const childLogger = new Logger({
      level: this.level,
      prefix: this.prefix ? `${this.prefix}:${prefix}` : prefix,
      metadata: { ...this.metadata, ...metadata }
    });
    return childLogger;
  }

  private formatMessage(level: string, message: string, data?: unknown): string {
    const timestamp = new Date().toISOString();
    const prefix = this.prefix ? `[${this.prefix}]` : '';
    const dataString = data ? `\n${JSON.stringify(data, null, 2)}` : '';
    return `${timestamp} ${prefix} ${level.toUpperCase()}: ${message}${dataString}`;
  }

  /**
   * Log debug message
   */
  public debug(message: string, data?: unknown): void {
    if (process.env.NODE_ENV !== 'production' || this.level === 'debug') {
      console.debug(this.formatMessage('debug', message, data));
    }
  }

  /**
   * Log info message
   */
  public info(message: string, data?: unknown): void {
    if (['debug', 'info'].includes(this.level)) {
      console.info(this.formatMessage('info', message, data));
    }
  }

  /**
   * Log warning message
   */
  public warn(message: string, data?: unknown): void {
    if (['debug', 'info', 'warn'].includes(this.level)) {
      console.warn(this.formatMessage('warn', message, data));
    }
  }

  /**
   * Log error message
   */
  public error(message: string, data?: unknown): void {
    console.error(this.formatMessage('error', message, data));
  }

  /**
   * Set log level
   */
  public setLevel(level: LogLevel): void {
    this.level = level;
  }

  /**
   * Get current log level
   */
  public getLevel(): LogLevel {
    return this.level;
  }
}

/**
 * Default logger instance
 */
export const logger = new Logger('root');
