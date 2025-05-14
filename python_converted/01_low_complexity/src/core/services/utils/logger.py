from typing import Any, List



class LoggerConfig:
    level: str
    format?: str
    transports?: List[Any]
    silent?: bool
class Logger {
  private static instance: \'Logger\'
  private logger: winston.Logger
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
    })
  }
  public static getInstance(): \'Logger\' {
    if (!Logger.instance) {
      Logger.instance = new Logger()
    }
    return Logger.instance
  }
  public configure(config: LoggerConfig): void {
    if (config.level) {
      this.logger.level = config.level
    }
    if (config.format) {
      this.logger.format = winston.format[config.format]()
    }
    if (config.transports) {
      this.logger.clear()
      config.transports.forEach(transport => {
        this.logger.add(transport)
      })
    }
    if (config.silent !== undefined) {
      this.logger.silent = config.silent
    }
  }
  public debug(message: str, meta?: Any): void {
    this.logger.debug(message, meta)
  }
  public info(message: str, meta?: Any): void {
    this.logger.info(message, meta)
  }
  public warn(message: str, meta?: Any): void {
    this.logger.warn(message, meta)
  }
  public error(message: str, meta?: Any): void {
    this.logger.error(message, meta)
  }
} 