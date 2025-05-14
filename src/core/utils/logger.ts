/**
 * Log levels
 */
export enum LogLevel {
  ERROR = 'error',
  WARN = 'warn',
  INFO = 'info',
  DEBUG = 'debug'
}

/**
 * Logger configuration
 */
export interface LoggerConfig {
  level?: LogLevel;
  prefix?: string;
  timestamp?: boolean;
}

/**
 * Simple logger utility
 */
export class Logger {
  private static instance: Logger;
  private level: LogLevel;
  private prefix: string;
  private timestamp: boolean;

  constructor(prefix?: string, config: LoggerConfig = {}) {
    this.level = config.level || LogLevel.INFO;
    this.prefix = prefix || '';
    this.timestamp = config.timestamp ?? true;
  }

  /**
   * Get singleton instance
   */
  static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  /**
   * Create a child logger with a prefix
   */
  child(prefix: string): Logger {
    return new Logger(prefix, {
      level: this.level,
      timestamp: this.timestamp
    });
  }

  /**
   * Set log level
   */
  setLevel(level: LogLevel): void {
    this.level = level;
  }

  /**
   * Log error message
   */
  error(message: string, ...args: any[]): void {
    if (this.shouldLog(LogLevel.ERROR)) {
      console.error(this.format(LogLevel.ERROR, message), ...args);
    }
  }

  /**
   * Log warning message
   */
  warn(message: string, ...args: any[]): void {
    if (this.shouldLog(LogLevel.WARN)) {
      console.warn(this.format(LogLevel.WARN, message), ...args);
    }
  }

  /**
   * Log info message
   */
  info(message: string, ...args: any[]): void {
    if (this.shouldLog(LogLevel.INFO)) {
      console.info(this.format(LogLevel.INFO, message), ...args);
    }
  }

  /**
   * Log debug message
   */
  debug(message: string, ...args: any[]): void {
    if (this.shouldLog(LogLevel.DEBUG)) {
      console.debug(this.format(LogLevel.DEBUG, message), ...args);
    }
  }

  private shouldLog(level: LogLevel): boolean {
    const levels = Object.values(LogLevel);
    return levels.indexOf(level) <= levels.indexOf(this.level);
  }

  private format(level: LogLevel, message: string): string {
    const parts = [];

    if (this.timestamp) {
      parts.push(new Date().toISOString());
    }

    parts.push(`[${level.toUpperCase()}]`);

    if (this.prefix) {
      parts.push(`[${this.prefix}]`);
    }

    parts.push(message);

    return parts.join(' ');
  }
} 