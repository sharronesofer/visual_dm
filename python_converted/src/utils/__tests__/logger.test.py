from typing import Any, Dict


  Logger,
  LogLevel,
  LogHandler,
  LogEntry,
  ConsoleLogHandler,
  FileLogHandler
} from '../logger'
const mockConsole = {
  debug: jest.spyOn(console, 'debug').mockImplementation(),
  info: jest.spyOn(console, 'info').mockImplementation(),
  warn: jest.spyOn(console, 'warn').mockImplementation(),
  error: jest.spyOn(console, 'error').mockImplementation()
}
jest.mock('fs', () => ({
  mkdirSync: jest.fn(),
  statSync: jest.fn(),
  appendFileSync: jest.fn(),
  unlinkSync: jest.fn(),
  renameSync: jest.fn()
}))
describe('Logger', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    (Logger as any)['instance'] = undefined
  })
  describe('ConsoleLogHandler', () => {
    let handler: ConsoleLogHandler
    beforeEach(() => {
      handler = new ConsoleLogHandler()
    })
    it('should log debug messages correctly', () => {
      const entry: LogEntry = {
        level: LogLevel.DEBUG,
        message: 'Debug message',
        timestamp: '2024-01-01T00:00:00.000Z',
        context: 'test',
        metadata: Dict[str, Any]
      }
      handler.handle(entry)
      expect(mockConsole.debug).toHaveBeenCalledWith(
        '[2024-01-01T00:00:00.000Z] [test] Debug message {"foo":"bar"}'
      )
    })
    it('should log info messages correctly', () => {
      const entry: LogEntry = {
        level: LogLevel.INFO,
        message: 'Info message',
        timestamp: '2024-01-01T00:00:00.000Z'
      }
      handler.handle(entry)
      expect(mockConsole.info).toHaveBeenCalledWith(
        '[2024-01-01T00:00:00.000Z] Info message'
      )
    })
    it('should log error messages with error object', () => {
      const error = new Error('Test error')
      const entry: LogEntry = {
        level: LogLevel.ERROR,
        message: 'Error message',
        timestamp: '2024-01-01T00:00:00.000Z',
        error
      }
      handler.handle(entry)
      expect(mockConsole.error).toHaveBeenCalledWith(
        '[2024-01-01T00:00:00.000Z] Error message'
      )
      expect(mockConsole.error).toHaveBeenCalledWith(error)
    })
  })
  describe('FileLogHandler', () => {
    let handler: FileLogHandler
    const testLogPath = 'logs/test.log'
    beforeEach(() => {
      handler = new FileLogHandler({
        filePath: testLogPath,
        maxFileSize: 1000,
        maxFiles: 3
      })
    })
    it('should create log directory if it does not exist', () => {
      expect(fs.mkdirSync).toHaveBeenCalledWith('logs', { recursive: true })
    })
    it('should write log entries to file', () => {
      const entry: LogEntry = {
        level: LogLevel.INFO,
        message: 'Test message',
        timestamp: '2024-01-01T00:00:00.000Z',
        context: 'test',
        metadata: Dict[str, Any]
      }
      (fs.statSync as jest.Mock).mockReturnValue({ size: 0 })
      handler.handle(entry)
      expect(fs.appendFileSync).toHaveBeenCalledWith(
        testLogPath,
        expect.stringContaining('"message":"Test message"')
      )
    })
    it('should rotate files when size limit is reached', () => {
      const entry: LogEntry = {
        level: LogLevel.INFO,
        message: 'Test message',
        timestamp: '2024-01-01T00:00:00.000Z'
      }
      (fs.statSync as jest.Mock).mockReturnValue({ size: 999 })
      handler.handle(entry)
      expect(fs.renameSync).toHaveBeenCalled()
      expect(fs.appendFileSync).toHaveBeenCalled()
    })
    it('should handle file system errors gracefully', () => {
      const entry: LogEntry = {
        level: LogLevel.INFO,
        message: 'Test message',
        timestamp: '2024-01-01T00:00:00.000Z'
      }
      (fs.statSync as jest.Mock).mockImplementation(() => {
        throw new Error('File not found')
      })
      expect(() => handler.handle(entry)).not.toThrow()
      expect(fs.appendFileSync).toHaveBeenCalled()
    })
  })
  describe('Logger', () => {
    let mockHandler: jest.Mocked<LogHandler>
    beforeEach(() => {
      mockHandler = {
        handle: jest.fn()
      }
    })
    it('should create singleton instance with default config', () => {
      const logger = Logger.getInstance()
      expect(logger).toBeDefined()
      expect(Logger.getInstance()).toBe(logger)
    })
    it('should respect minimum log level', () => {
      const logger = Logger.getInstance({
        minLevel: LogLevel.WARN,
        enableConsole: false,
        customHandlers: [mockHandler]
      })
      logger.debug('Debug message')
      logger.info('Info message')
      logger.warn('Warning message')
      logger.error('Error message')
      expect(mockHandler.handle).toHaveBeenCalledTimes(2)
      expect(mockHandler.handle).toHaveBeenCalledWith(
        expect.objectContaining({
          level: LogLevel.WARN,
          message: 'Warning message'
        })
      )
      expect(mockHandler.handle).toHaveBeenCalledWith(
        expect.objectContaining({
          level: LogLevel.ERROR,
          message: 'Error message'
        })
      )
    })
    it('should create child loggers with inherited context', () => {
      const logger = Logger.getInstance({
        context: 'parent',
        metadata: Dict[str, Any],
        enableConsole: false,
        customHandlers: [mockHandler]
      })
      const childLogger = logger.child('child', { module: 'auth' })
      childLogger.info('Child message')
      expect(mockHandler.handle).toHaveBeenCalledWith(
        expect.objectContaining({
          context: 'parent:child',
          metadata: Dict[str, Any],
          message: 'Child message'
        })
      )
    })
    it('should handle errors with stack traces', () => {
      const logger = Logger.getInstance({
        enableConsole: false,
        customHandlers: [mockHandler]
      })
      const error = new Error('Test error')
      logger.error('Error occurred', error, { userId: '123' })
      expect(mockHandler.handle).toHaveBeenCalledWith(
        expect.objectContaining({
          level: LogLevel.ERROR,
          message: 'Error occurred',
          error,
          metadata: Dict[str, Any]
        })
      )
    })
    it('should allow adding custom handlers', () => {
      const logger = Logger.getInstance({
        enableConsole: false
      })
      const customHandler: LogHandler = {
        handle: jest.fn()
      }
      logger.addHandler(customHandler)
      logger.info('Test message')
      expect(customHandler.handle).toHaveBeenCalled()
    })
  })
}) 