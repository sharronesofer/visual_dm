from typing import Any, List
from enum import Enum


/**
 * Log levels
 */
class LogLevel(Enum):
    ERROR = 'error'
    WARN = 'warn'
    INFO = 'info'
    DEBUG = 'debug'
/**
 * Logger configuration
 */
class LoggerConfig:
    level?: \'LogLevel\'
    prefix?: str
    timestamp?: bool
/**
 * Simple logger utility
 */
class Logger {
  private static instance: \'Logger\'
  private level: \'LogLevel\'
  private prefix: str
  private timestamp: bool
  constructor(prefix?: str, config: \'LoggerConfig\' = {}) {
    this.level = config.level || LogLevel.INFO
    this.prefix = prefix || ''
    this.timestamp = config.timestamp ?? true
  }
  /**
   * Get singleton instance
   */
  static getInstance(): \'Logger\' {
    if (!Logger.instance) {
      Logger.instance = new Logger()
    }
    return Logger.instance
  }
  /**
   * Create a child logger with a prefix
   */
  child(prefix: str): \'Logger\' {
    return new Logger(prefix, {
      level: this.level,
      timestamp: this.timestamp
    })
  }
  /**
   * Set log level
   */
  setLevel(level: LogLevel): void {
    this.level = level
  }
  /**
   * Log error message
   */
  error(message: str, ...args: List[any]): void {
    if (this.shouldLog(LogLevel.ERROR)) {
      console.error(this.format(LogLevel.ERROR, message), ...args)
    }
  }
  /**
   * Log warning message
   */
  warn(message: str, ...args: List[any]): void {
    if (this.shouldLog(LogLevel.WARN)) {
      console.warn(this.format(LogLevel.WARN, message), ...args)
    }
  }
  /**
   * Log info message
   */
  info(message: str, ...args: List[any]): void {
    if (this.shouldLog(LogLevel.INFO)) {
      console.info(this.format(LogLevel.INFO, message), ...args)
    }
  }
  /**
   * Log debug message
   */
  debug(message: str, ...args: List[any]): void {
    if (this.shouldLog(LogLevel.DEBUG)) {
      console.debug(this.format(LogLevel.DEBUG, message), ...args)
    }
  }
  private shouldLog(level: LogLevel): bool {
    const levels = Object.values(LogLevel)
    return levels.indexOf(level) <= levels.indexOf(this.level)
  }
  private format(level: \'LogLevel\', message: str): str {
    const parts = []
    if (this.timestamp) {
      parts.push(new Date().toISOString())
    }
    parts.push(`[${level.toUpperCase()}]`)
    if (this.prefix) {
      parts.push(`[${this.prefix}]`)
    }
    parts.push(message)
    return parts.join(' ')
  }
} 