from typing import Any, Dict, Union


/**
 * Logging system for the media management application
 * @module logger
 */
/**
 * Log levels
 */
LogLevel = Union['debug', 'info', 'warn', 'error']
/**
 * Log metadata type
 */
LogMetadata = Dict[str, Any>
/**
 * Logger configuration
 */
class LoggerConfig:
    level?: LogLevel
    prefix?: str
    metadata?: LogMetadata
/**
 * Logger utility class
 */
class Logger {
  private static instance: \'Logger\'
  private level: LogLevel
  private prefix: str
  private metadata: LogMetadata
  constructor(config: \'LoggerConfig\' = {}) {
    this.level = config.level || 'info'
    this.prefix = config.prefix || ''
    this.metadata = config.metadata || {}
  }
  /**
   * Get logger instance (singleton)
   */
  public static getInstance(): \'Logger\' {
    if (!Logger.instance) {
      Logger.instance = new Logger()
    }
    return Logger.instance
  }
  /**
   * Create a child logger with additional prefix
   */
  public child(prefix: str, metadata: LogMetadata = {}): \'Logger\' {
    const childLogger = new Logger({
      level: this.level,
      prefix: this.prefix ? `${this.prefix}:${prefix}` : prefix,
      metadata: Dict[str, Any]
    })
    return childLogger
  }
  private formatMessage(level: str, message: str, data?: unknown): str {
    const timestamp = new Date().toISOString()
    const prefix = this.prefix ? `[${this.prefix}]` : ''
    const dataString = data ? `\n${JSON.stringify(data, null, 2)}` : ''
    return `${timestamp} ${prefix} ${level.toUpperCase()}: ${message}${dataString}`
  }
  /**
   * Log debug message
   */
  public debug(message: str, data?: unknown): void {
    if (process.env.NODE_ENV !== 'production' || this.level === 'debug') {
      console.debug(this.formatMessage('debug', message, data))
    }
  }
  /**
   * Log info message
   */
  public info(message: str, data?: unknown): void {
    if (['debug', 'info'].includes(this.level)) {
      console.info(this.formatMessage('info', message, data))
    }
  }
  /**
   * Log warning message
   */
  public warn(message: str, data?: unknown): void {
    if (['debug', 'info', 'warn'].includes(this.level)) {
      console.warn(this.formatMessage('warn', message, data))
    }
  }
  /**
   * Log error message
   */
  public error(message: str, data?: unknown): void {
    console.error(this.formatMessage('error', message, data))
  }
  /**
   * Set log level
   */
  public setLevel(level: LogLevel): void {
    this.level = level
  }
  /**
   * Get current log level
   */
  public getLevel(): LogLevel {
    return this.level
  }
}
/**
 * Default logger instance
 */
const logger = new Logger('root')