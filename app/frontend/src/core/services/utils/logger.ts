import winston from 'winston';

export interface LoggerConfig {
  level: string;
  format?: string;
  transports?: any[];
  silent?: boolean;
}

export class Logger {
  private static instance: Logger;
  private logger: winston.Logger;

  private constructor() {
    this.logger = winston.createLogger({
      level: 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      ),
      transports: [
        new winston.transports.Console({
          format: winston.format.combine(
            winston.format.colorize(),
            winston.format.simple()
          )
        })
      ]
    });
  }

  public static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  public configure(config: LoggerConfig): void {
    if (config.level) {
      this.logger.level = config.level;
    }

    if (config.format) {
      this.logger.format = winston.format[config.format]();
    }

    if (config.transports) {
      this.logger.clear();
      config.transports.forEach(transport => {
        this.logger.add(transport);
      });
    }

    if (config.silent !== undefined) {
      this.logger.silent = config.silent;
    }
  }

  public debug(message: string, meta?: any): void {
    this.logger.debug(message, meta);
  }

  public info(message: string, meta?: any): void {
    this.logger.info(message, meta);
  }

  public warn(message: string, meta?: any): void {
    this.logger.warn(message, meta);
  }

  public error(message: string, meta?: any): void {
    this.logger.error(message, meta);
  }
} 