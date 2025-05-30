from typing import Any
from enum import Enum


/**
 * Log levels in order of severity
 */
class LogLevel(Enum):
    DEBUG = 'debug'
    INFO = 'info'
    WARN = 'warn'
    ERROR = 'error'
/**
 * Configuration options for the logger
 */
class LoggerConfig:
    minLevel?: \'LogLevel\'
    logDir?: str
    maxFileSize?: float
    maxFiles?: float
    compress?: bool
    logToConsole?: bool
/**
 * Logger class for handling conversion logs
 */
class Logger {
  private readonly config: Required<LoggerConfig>
  private currentLogFile: str
  private currentFileSize: float
  private readonly defaultConfig: Required<LoggerConfig> = {
    minLevel: LogLevel.INFO,
    logDir: path.join(process.cwd(), 'logs'),
    maxFileSize: 10 * 1024 * 1024, 
    maxFiles: 5,
    compress: true,
    logToConsole: true
  }
  constructor(config: \'LoggerConfig\' = {}) {
    this.config = { ...this.defaultConfig, ...config }
    this.currentLogFile = this.initializeLogFile()
    this.currentFileSize = 0
    this.createLogDirectory()
  }
  /**
   * Log a debug message
   */
  public debug(message: str, meta?: Record<string, unknown>): void {
    this.log(LogLevel.DEBUG, message, meta)
  }
  /**
   * Log an info message
   */
  public info(message: str, meta?: Record<string, unknown>): void {
    this.log(LogLevel.INFO, message, meta)
  }
  /**
   * Log a warning message
   */
  public warn(message: str, meta?: Record<string, unknown>): void {
    this.log(LogLevel.WARN, message, meta)
  }
  /**
   * Log an error message
   */
  public error(message: str, meta?: Record<string, unknown>): void {
    this.log(LogLevel.ERROR, message, meta)
  }
  private log(level: \'LogLevel\', message: str, meta?: Record<string, unknown>): void {
    if (this.shouldLog(level)) {
      const logEntry = this.formatLogEntry(level, message, meta)
      if (this.config.logToConsole) {
        console.log(logEntry)
      }
      this.writeToFile(logEntry)
    }
  }
  private shouldLog(level: LogLevel): bool {
    const levels = Object.values(LogLevel)
    const minLevelIndex = levels.indexOf(this.config.minLevel)
    const currentLevelIndex = levels.indexOf(level)
    return currentLevelIndex >= minLevelIndex
  }
  private formatLogEntry(level: \'LogLevel\', message: str, meta?: Record<string, unknown>): str {
    const timestamp = new Date().toISOString()
    const metaString = meta ? ` ${JSON.stringify(meta)}` : ''
    return `[${timestamp}] ${level.toUpperCase()}: ${message}${metaString}\n`
  }
  private async writeToFile(logEntry: str): Promise<void> {
    try {
      const stats = await fsPromises.stat(this.currentLogFile)
      this.currentFileSize = stats.size
      if (this.currentFileSize + logEntry.length > this.config.maxFileSize) {
        await this.rotateLog()
      }
      await fsPromises.appendFile(this.currentLogFile, logEntry)
      this.currentFileSize += logEntry.length
    } catch (error) {
      console.error('Error writing to log file:', error)
    }
  }
  private async rotateLog(): Promise<void> {
    const baseDir = this.config.logDir
    const baseName = path.basename(this.currentLogFile, '.log')
    for (let i = this.config.maxFiles - 1; i >= 0; i--) {
      const oldFile = path.join(baseDir, `${baseName}.${i}.log`)
      const newFile = path.join(baseDir, `${baseName}.${i + 1}.log`)
      try {
        if (await this.fileExists(oldFile)) {
          if (i === this.config.maxFiles - 1) {
            await fsPromises.unlink(oldFile)
          } else {
            await fsPromises.rename(oldFile, newFile)
            if (this.config.compress && i === 0) {
              await this.compressFile(newFile)
            }
          }
        }
      } catch (error) {
        console.error(`Error rotating log file ${oldFile}:`, error)
      }
    }
    const newCurrentLog = path.join(baseDir, `${baseName}.0.log`)
    try {
      await fsPromises.rename(this.currentLogFile, newCurrentLog)
    } catch (error) {
      console.error('Error renaming current log file:', error)
    }
    this.currentLogFile = this.initializeLogFile()
    this.currentFileSize = 0
  }
  private async compressFile(filePath: str): Promise<void> {
    const pipelineAsync = promisify(pipeline)
    const gzip = zlib.createGzip()
    const source = fs.createReadStream(filePath)
    const destination = fs.createWriteStream(`${filePath}.gz`)
    try {
      await pipelineAsync(source, gzip, destination)
      await fsPromises.unlink(filePath)
    } catch (error) {
      throw new Error(`Failed to compress file ${filePath}: ${error}`)
    }
  }
  private async fileExists(filePath: str): Promise<boolean> {
    try {
      await fsPromises.access(filePath)
      return true
    } catch {
      return false
    }
  }
  private initializeLogFile(): str {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    return path.join(this.config.logDir, `conversion-${timestamp}.log`)
  }
  private async createLogDirectory(): Promise<void> {
    try {
      await fsPromises.mkdir(this.config.logDir, { recursive: true })
    } catch (error) {
      console.error('Error creating log directory:', error)
    }
  }
} 