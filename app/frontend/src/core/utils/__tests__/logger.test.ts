import { logger } from '../logger';

describe('logger', () => {
  let consoleLogSpy: jest.SpyInstance;
  let consoleErrorSpy: jest.SpyInstance;
  let consoleWarnSpy: jest.SpyInstance;
  let consoleDebugSpy: jest.SpyInstance;

  beforeEach(() => {
    consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
    consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();
    consoleDebugSpy = jest.spyOn(console, 'debug').mockImplementation();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('info', () => {
    it('should log info message with timestamp', () => {
      logger.info('test message');
      expect(consoleLogSpy).toHaveBeenCalledWith(expect.stringMatching(/^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z\] INFO: test message$/));
    });

    it('should include metadata in log message', () => {
      logger.info('test message', { key: 'value' });
      expect(consoleLogSpy).toHaveBeenCalledWith(expect.stringMatching(/^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z\] INFO: test message \| {"timestamp":".+","level":"info","key":"value"}$/));
    });
  });

  describe('error', () => {
    it('should log error message with timestamp', () => {
      logger.error('test error');
      expect(consoleErrorSpy).toHaveBeenCalledWith(expect.stringMatching(/^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z\] ERROR: test error$/));
    });

    it('should include error details in log message', () => {
      const error = new Error('test error');
      logger.error('error occurred', error);
      expect(consoleErrorSpy).toHaveBeenCalledWith(expect.stringMatching(/^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z\] ERROR: error occurred \| {"timestamp":".+","level":"error","error":{"name":"Error","message":"test error","stack":".+"}}$/));
    });

    it('should include metadata and error details', () => {
      const error = new Error('test error');
      logger.error('error occurred', error, { context: 'test' });
      expect(consoleErrorSpy).toHaveBeenCalledWith(expect.stringMatching(/^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z\] ERROR: error occurred \| {"timestamp":".+","level":"error","context":"test","error":{"name":"Error","message":"test error","stack":".+"}}$/));
    });
  });

  describe('warn', () => {
    it('should log warning message with timestamp', () => {
      logger.warn('test warning');
      expect(consoleWarnSpy).toHaveBeenCalledWith(expect.stringMatching(/^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z\] WARN: test warning$/));
    });

    it('should include metadata in log message', () => {
      logger.warn('test warning', { key: 'value' });
      expect(consoleWarnSpy).toHaveBeenCalledWith(expect.stringMatching(/^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z\] WARN: test warning \| {"timestamp":".+","level":"warn","key":"value"}$/));
    });
  });

  describe('debug', () => {
    const originalDebug = process.env.DEBUG;

    beforeEach(() => {
      process.env.DEBUG = 'true';
    });

    afterEach(() => {
      process.env.DEBUG = originalDebug;
    });

    it('should log debug message when DEBUG is true', () => {
      logger.debug('test debug');
      expect(consoleDebugSpy).toHaveBeenCalledWith(expect.stringMatching(/^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z\] DEBUG: test debug$/));
    });

    it('should include metadata in debug message', () => {
      logger.debug('test debug', { key: 'value' });
      expect(consoleDebugSpy).toHaveBeenCalledWith(expect.stringMatching(/^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z\] DEBUG: test debug \| {"timestamp":".+","level":"debug","key":"value"}$/));
    });

    it('should not log debug message when DEBUG is false', () => {
      process.env.DEBUG = 'false';
      logger.debug('test debug');
      expect(consoleDebugSpy).not.toHaveBeenCalled();
    });
  });
}); 