import {
  Logger,
  LogLevel,
  LogEntry,
  LogHandler,
  ConsoleLogHandler,
} from '../logger';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

describe('Logger', () => {
  let logger: Logger;
  const originalConsole = { ...console };

  beforeEach(() => {
    console.log = vi.fn();
    console.warn = vi.fn();
    console.error = vi.fn();
    logger = Logger.getInstance();
  });

  afterEach(() => {
    Object.assign(console, originalConsole);
    vi.clearAllMocks();
    // @ts-expect-error: Resetting singleton for testing
    Logger.instance = undefined;
  });

  it('logs info messages', () => {
    logger.info('Test message');
    expect(console.info).toHaveBeenCalledWith(
      expect.stringContaining('[INFO] Test message')
    );
  });

  it('logs warning messages', () => {
    logger.warn('Test warning');
    expect(console.warn).toHaveBeenCalledWith(
      expect.stringContaining('[WARN] Test warning')
    );
  });

  it('logs error messages', () => {
    logger.error('Test error');
    expect(console.error).toHaveBeenCalledWith(
      expect.stringContaining('[ERROR] Test error')
    );
  });

  it('logs error messages with Error objects', () => {
    const error = new Error('Test error');
    logger.error('Error occurred', error);
    expect(console.error).toHaveBeenCalledWith(
      expect.stringContaining('[ERROR] Error occurred')
    );
    expect(console.error).toHaveBeenCalledWith(error);
  });

  describe('Log Levels', () => {
    it('should respect minimum log level', () => {
      logger = Logger.getInstance({ 
        minLevel: LogLevel.WARN 
      });
      const mockHandler = new (class implements LogHandler {
        handle(entry: LogEntry): void {}
      })();
      const handleSpy = vi.spyOn(mockHandler, 'handle');
      
      logger.addHandler(mockHandler);
      logger.info('Should not log');
      logger.warn('Should log');
      
      expect(handleSpy).toHaveBeenCalledTimes(1);
      expect(handleSpy).toHaveBeenCalledWith(expect.objectContaining({
        level: LogLevel.WARN,
        message: 'Should log'
      }));
    });
  });

  describe('Timestamp Handling', () => {
    it('should include timestamp when enabled', () => {
      logger = Logger.getInstance({ 
        enableTimestamp: true 
      });
      const mockHandler = new (class implements LogHandler {
        handle(entry: LogEntry): void {}
      })();
      const handleSpy = vi.spyOn(mockHandler, 'handle');
      
      logger.addHandler(mockHandler);
      logger.info('Test message');
      
      expect(handleSpy).toHaveBeenCalledWith(expect.objectContaining({
        timestamp: expect.any(String)
      }));
    });

    it('should exclude timestamp when disabled', () => {
      logger = Logger.getInstance({ 
        enableTimestamp: false 
      });
      const mockHandler = new (class implements LogHandler {
        handle(entry: LogEntry): void {}
      })();
      const handleSpy = vi.spyOn(mockHandler, 'handle');
      
      logger.addHandler(mockHandler);
      logger.info('Test message');
      
      expect(handleSpy).toHaveBeenCalledWith(expect.objectContaining({
        timestamp: ''
      }));
    });
  });

  describe('Error Logging', () => {
    it('should properly handle error objects', () => {
      const mockHandler = new (class implements LogHandler {
        handle(entry: LogEntry): void {}
      })();
      const handleSpy = vi.spyOn(mockHandler, 'handle');
      
      logger.addHandler(mockHandler);
      const error = new Error('Test error');
      logger.error('An error occurred', error);
      
      expect(handleSpy).toHaveBeenCalledWith(expect.objectContaining({
        level: LogLevel.ERROR,
        message: 'An error occurred',
        error: error
      }));
    });
  });
});
