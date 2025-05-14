import { EventEmitter } from 'events';
import { ConversionEventType, ConversionProgress, ConversionStage } from '../types';
import { ConversionError } from '../errors/ConversionError';
import * as fs from 'fs';
import * as path from 'path';
import * as zlib from 'zlib';
import { promisify } from 'util';
import { Readable, Writable, pipeline } from 'stream';
import { promises as fsPromises } from 'fs';
import { v4 as uuidv4 } from 'uuid';

/**
 * Log levels in order of severity
 */
export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error'
}

/**
 * Configuration options for the logger
 */
export interface LoggerConfig {
  minLevel?: LogLevel;
  logDir?: string;
  maxFileSize?: number; // in bytes
  maxFiles?: number;
  compress?: boolean;
  logToConsole?: boolean;
}

/**
 * Logger class for handling conversion logs
 */
export class Logger {
  private readonly config: Required<LoggerConfig>;
  private currentLogFile: string;
  private currentFileSize: number;
  private readonly defaultConfig: Required<LoggerConfig> = {
    minLevel: LogLevel.INFO,
    logDir: path.join(process.cwd(), 'logs'),
    maxFileSize: 10 * 1024 * 1024, // 10MB
    maxFiles: 5,
    compress: true,
    logToConsole: true
  };

  constructor(config: LoggerConfig = {}) {
    this.config = { ...this.defaultConfig, ...config };
    this.currentLogFile = this.initializeLogFile();
    this.currentFileSize = 0;
    this.createLogDirectory();
  }

  /**
   * Log a debug message
   */
  public debug(message: string, meta?: Record<string, unknown>): void {
    this.log(LogLevel.DEBUG, message, meta);
  }

  /**
   * Log an info message
   */
  public info(message: string, meta?: Record<string, unknown>): void {
    this.log(LogLevel.INFO, message, meta);
  }

  /**
   * Log a warning message
   */
  public warn(message: string, meta?: Record<string, unknown>): void {
    this.log(LogLevel.WARN, message, meta);
  }

  /**
   * Log an error message
   */
  public error(message: string, meta?: Record<string, unknown>): void {
    this.log(LogLevel.ERROR, message, meta);
  }

  private log(level: LogLevel, message: string, meta?: Record<string, unknown>): void {
    if (this.shouldLog(level)) {
      const logEntry = this.formatLogEntry(level, message, meta);
      
      if (this.config.logToConsole) {
        console.log(logEntry);
      }

      this.writeToFile(logEntry);
    }
  }

  private shouldLog(level: LogLevel): boolean {
    const levels = Object.values(LogLevel);
    const minLevelIndex = levels.indexOf(this.config.minLevel);
    const currentLevelIndex = levels.indexOf(level);
    return currentLevelIndex >= minLevelIndex;
  }

  private formatLogEntry(level: LogLevel, message: string, meta?: Record<string, unknown>): string {
    const timestamp = new Date().toISOString();
    const metaString = meta ? ` ${JSON.stringify(meta)}` : '';
    return `[${timestamp}] ${level.toUpperCase()}: ${message}${metaString}\n`;
  }

  private async writeToFile(logEntry: string): Promise<void> {
    try {
      const stats = await fsPromises.stat(this.currentLogFile);
      this.currentFileSize = stats.size;

      if (this.currentFileSize + logEntry.length > this.config.maxFileSize) {
        await this.rotateLog();
      }

      await fsPromises.appendFile(this.currentLogFile, logEntry);
      this.currentFileSize += logEntry.length;
    } catch (error) {
      console.error('Error writing to log file:', error);
    }
  }

  private async rotateLog(): Promise<void> {
    const baseDir = this.config.logDir;
    const baseName = path.basename(this.currentLogFile, '.log');
    
    // Shift existing log files
    for (let i = this.config.maxFiles - 1; i >= 0; i--) {
      const oldFile = path.join(baseDir, `${baseName}.${i}.log`);
      const newFile = path.join(baseDir, `${baseName}.${i + 1}.log`);
      
      try {
        if (await this.fileExists(oldFile)) {
          if (i === this.config.maxFiles - 1) {
            // Delete the oldest log file
            await fsPromises.unlink(oldFile);
          } else {
            // Rename the file
            await fsPromises.rename(oldFile, newFile);
            
            // Compress if needed
            if (this.config.compress && i === 0) {
              await this.compressFile(newFile);
            }
          }
        }
      } catch (error) {
        console.error(`Error rotating log file ${oldFile}:`, error);
      }
    }

    // Rename current log file
    const newCurrentLog = path.join(baseDir, `${baseName}.0.log`);
    try {
      await fsPromises.rename(this.currentLogFile, newCurrentLog);
    } catch (error) {
      console.error('Error renaming current log file:', error);
    }

    // Create new log file
    this.currentLogFile = this.initializeLogFile();
    this.currentFileSize = 0;
  }

  private async compressFile(filePath: string): Promise<void> {
    const pipelineAsync = promisify(pipeline);
    const gzip = zlib.createGzip();
    const source = fs.createReadStream(filePath);
    const destination = fs.createWriteStream(`${filePath}.gz`);

    try {
      await pipelineAsync(source, gzip, destination);
      await fsPromises.unlink(filePath);
    } catch (error) {
      throw new Error(`Failed to compress file ${filePath}: ${error}`);
    }
  }

  private async fileExists(filePath: string): Promise<boolean> {
    try {
      await fsPromises.access(filePath);
      return true;
    } catch {
      return false;
    }
  }

  private initializeLogFile(): string {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    return path.join(this.config.logDir, `conversion-${timestamp}.log`);
  }

  private async createLogDirectory(): Promise<void> {
    try {
      await fsPromises.mkdir(this.config.logDir, { recursive: true });
    } catch (error) {
      console.error('Error creating log directory:', error);
    }
  }
} 