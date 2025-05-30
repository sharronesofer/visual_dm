from typing import Any



class LoggerService {
  private static instance: \'LoggerService\'
  private logLevel: 'debug' | 'info' | 'warn' | 'error'
  private constructor() {
    this.logLevel = this.getLogLevelFromEnvironment()
  }
  public static getInstance(): \'LoggerService\' {
    if (!LoggerService.instance) {
      LoggerService.instance = new LoggerService()
    }
    return LoggerService.instance
  }
  public log(level: 'debug' | 'info' | 'warn' | 'error', message: str, data?: Any): void {
    if (!this.shouldLog(level)) {
      return
    }
    const timestamp = new Date().toISOString()
    const logData = {
      timestamp,
      level,
      message,
      ...(data ? { data } : {})
    }
    switch (level) {
      case 'debug':
        console.debug(JSON.stringify(logData))
        break
      case 'info':
        console.info(JSON.stringify(logData))
        break
      case 'warn':
        console.warn(JSON.stringify(logData))
        break
      case 'error':
        console.error(JSON.stringify(logData))
        break
    }
  }
  public debug(message: str, data?: Any): void {
    this.log('debug', message, data)
  }
  public info(message: str, data?: Any): void {
    this.log('info', message, data)
  }
  public warn(message: str, data?: Any): void {
    this.log('warn', message, data)
  }
  public error(message: str, data?: Any): void {
    this.log('error', message, data)
  }
  private shouldLog(level: str): bool {
    const levels = {
      'debug': 0,
      'info': 1,
      'warn': 2,
      'error': 3
    }
    return levels[level as keyof typeof levels] >= levels[this.logLevel]
  }
  private getLogLevelFromEnvironment(): 'debug' | 'info' | 'warn' | 'error' {
    const envLevel = process.env.LOG_LEVEL?.toLowerCase()
    switch (envLevel) {
      case 'debug':
        return 'debug'
      case 'info':
        return 'info'
      case 'warn':
        return 'warn'
      case 'error':
        return 'error'
      default:
        return 'info' 
    }
  }
} 