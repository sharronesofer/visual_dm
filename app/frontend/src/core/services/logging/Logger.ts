import winston from 'winston';
import DailyRotateFile from 'winston-daily-rotate-file';

export enum LogLevel {
  ERROR = 'error',
  WARN = 'warn',
  INFO = 'info',
  DEBUG = 'debug'
}

export interface LoggerConfig {
  level: LogLevel;
  format?: string;
  transports?: {
    console?: boolean;
    file?: {
      enabled: boolean;
      filename: string;
      rotation?: {
        frequency?: string; // e.g., '1d'
        maxFiles?: string; // e.g., '30d'
        zippedArchive?: boolean;
      };
    };
  };
}

export class Logger {
  private logger: winston.Logger;

  constructor(config?: LoggerConfig) {
    this.logger = winston.createLogger({
      level: config?.level || LogLevel.INFO,
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      ),
      transports: this.configureTransports(config)
    });
  }

  public error(message: string, meta?: any): void {
    this.logger.error(message, meta);
  }

  public warn(message: string, meta?: any): void {
    this.logger.warn(message, meta);
  }

  public info(message: string, meta?: any): void {
    this.logger.info(message, meta);
  }

  public debug(message: string, meta?: any): void {
    this.logger.debug(message, meta);
  }

  public setLevel(level: LogLevel): void {
    this.logger.level = level;
  }

  public addTransport(transport: winston.transport): void {
    this.logger.add(transport);
  }

  public removeTransport(transport: winston.transport): void {
    this.logger.remove(transport);
  }

  private configureTransports(config?: LoggerConfig): winston.transport[] {
    const transports: winston.transport[] = [];

    // Always add console transport unless explicitly disabled
    if (config?.transports?.console !== false) {
      transports.push(
        new winston.transports.Console({
          format: winston.format.combine(
            winston.format.timestamp(),
            winston.format.json()
          )
        })
      );
    }

    // Add file transport with rotation if configured
    if (config?.transports?.file?.enabled) {
      const fileConfig = config.transports.file;
      if (fileConfig.rotation) {
        transports.push(
          new DailyRotateFile({
            filename: fileConfig.filename.replace(/\.log$/, '') + '-%DATE%.log',
            datePattern: 'YYYY-MM-DD',
            zippedArchive: fileConfig.rotation.zippedArchive ?? true,
            maxFiles: fileConfig.rotation.maxFiles ?? '30d',
            frequency: fileConfig.rotation.frequency ?? undefined,
            format: winston.format.combine(
              winston.format.timestamp(),
              winston.format.json()
            )
          })
        );
      } else {
        transports.push(
          new winston.transports.File({
            filename: fileConfig.filename,
            format: winston.format.combine(
              winston.format.timestamp(),
              winston.format.json()
            )
          })
        );
      }
    }

    return transports;
  }
} 