/**
 * Log levels enum
 */
export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error',
}

/**
 * Log entry interface
 */
export interface LogEntry {
  level: LogLevel;
  message: string;
  timestamp: string;
  context?: Record<string, any>;
  error?: Error;
}

/**
 * Logger configuration interface
 */
export interface LoggerConfig {
  minLevel: LogLevel;
  enableConsole: boolean;
  enableTimestamp: boolean;
  customHandlers?: LogHandler[];
}

/**
 * Log handler interface
 */
export interface LogHandler {
  handle(entry: LogEntry): void;
}

/**
 * Default logger configuration
 */
const defaultConfig: LoggerConfig = {
  minLevel: LogLevel.INFO,
  enableConsole: true,
  enableTimestamp: true,
};

/**
 * Console log handler
 */
export class ConsoleLogHandler implements LogHandler {
  handle(entry: LogEntry): void {
    const timestamp = entry.timestamp ? `[${entry.timestamp}] ` : '';
    const context = entry.context ? ` ${JSON.stringify(entry.context)}` : '';
    const message = `${timestamp}[${entry.level.toUpperCase()}] ${entry.message}${context}`;

    switch (entry.level) {
      case LogLevel.DEBUG:
        console.debug(message);
        break;
      case LogLevel.INFO:
        console.info(message);
        break;
      case LogLevel.WARN:
        console.warn(message);
        break;
      case LogLevel.ERROR:
        console.error(message);
        if (entry.error) {
          console.error(entry.error);
        }
        break;
    }
  }
}

/**
 * Logger class
 */
export class Logger {
  private static instance: Logger;
  private config: LoggerConfig;
  private handlers: LogHandler[];

  private constructor(config: Partial<LoggerConfig> = {}) {
    this.config = { ...defaultConfig, ...config };
    this.handlers = [];

    if (this.config.enableConsole) {
      this.addHandler(new ConsoleLogHandler());
    }

    if (this.config.customHandlers) {
      this.handlers.push(...this.config.customHandlers);
    }
  }

  /**
   * Get logger instance (singleton)
   */
  public static getInstance(config?: Partial<LoggerConfig>): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger(config);
    }
    return Logger.instance;
  }

  /**
   * Add a log handler
   */
  public addHandler(handler: LogHandler): void {
    this.handlers.push(handler);
  }

  /**
   * Remove a log handler
   */
  public removeHandler(handler: LogHandler): void {
    const index = this.handlers.indexOf(handler);
    if (index !== -1) {
      this.handlers.splice(index, 1);
    }
  }

  /**
   * Create a log entry
   */
  private createEntry(
    level: LogLevel,
    message: string,
    context?: Record<string, any>,
    error?: Error
  ): LogEntry {
    return {
      level,
      message,
      timestamp: this.config.enableTimestamp ? new Date().toISOString() : '',
      context,
      error,
    };
  }

  /**
   * Log a message
   */
  private log(
    level: LogLevel,
    message: string,
    context?: Record<string, any>,
    error?: Error
  ): void {
    if (level < this.config.minLevel) {
      return;
    }

    const entry = this.createEntry(level, message, context, error);
    this.handlers.forEach(handler => handler.handle(entry));
  }

  /**
   * Log a debug message
   */
  public debug(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.DEBUG, message, context);
  }

  /**
   * Log an info message
   */
  public info(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.INFO, message, context);
  }

  /**
   * Log a warning message
   */
  public warn(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.WARN, message, context);
  }

  /**
   * Log an error message
   */
  public error(
    message: string,
    error?: Error,
    context?: Record<string, any>
  ): void {
    this.log(LogLevel.ERROR, message, context, error);
  }
}

/**
 * Default logger instance
 */
export const logger = Logger.getInstance();

export default logger;
