from typing import Any


describe('Logger', () => {
  let consoleSpy: jest.SpyInstance
  let logger: Logger
  beforeEach(() => {
    logger = new Logger()
    consoleSpy = jest.spyOn(console, 'debug').mockImplementation()
    jest.spyOn(console, 'info').mockImplementation()
    jest.spyOn(console, 'warn').mockImplementation()
    jest.spyOn(console, 'error').mockImplementation()
  })
  afterEach(() => {
    jest.restoreAllMocks()
  })
  describe('Log Level Filtering', () => {
    it('should log all levels when minLevel is DEBUG', () => {
      logger.configure({ minLevel: LogLevel.DEBUG })
      logger.debug('debug message')
      logger.info('info message')
      logger.warn('warn message')
      logger.error('error message')
      expect(console.debug).toHaveBeenCalled()
      expect(console.info).toHaveBeenCalled()
      expect(console.warn).toHaveBeenCalled()
      expect(console.error).toHaveBeenCalled()
    })
    it('should only log ERROR when minLevel is ERROR', () => {
      logger.configure({ minLevel: LogLevel.ERROR })
      logger.debug('debug message')
      logger.info('info message')
      logger.warn('warn message')
      logger.error('error message')
      expect(console.debug).not.toHaveBeenCalled()
      expect(console.info).not.toHaveBeenCalled()
      expect(console.warn).not.toHaveBeenCalled()
      expect(console.error).toHaveBeenCalled()
    })
  })
  describe('Message Formatting', () => {
    it('should include timestamp when enabled', () => {
      logger.configure({ timestamp: true })
      logger.info('test message')
      const call = (console.info as jest.Mock).mock.calls[0][0]
      expect(call).toMatch(/\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\]/)
    })
    it('should not include timestamp when disabled', () => {
      logger.configure({ timestamp: false })
      logger.info('test message')
      const call = (console.info as jest.Mock).mock.calls[0][0]
      expect(call).not.toMatch(/\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\]/)
    })
    it('should include prefix when set', () => {
      const prefix = 'TEST'
      logger.configure({ prefix })
      logger.info('test message')
      const call = (console.info as jest.Mock).mock.calls[0][0]
      expect(call).toContain(`[${prefix}]`)
    })
    it('should handle additional arguments', () => {
      const additionalArg = { key: 'value' }
      logger.info('test message', additionalArg)
      expect(console.info).toHaveBeenCalledWith(
        expect.any(String),
        additionalArg
      )
    })
  })
  describe('Configuration', () => {
    it('should use default configuration when none provided', () => {
      const defaultLogger = new Logger()
      defaultLogger.debug('test')
      const call = (console.debug as jest.Mock).mock.calls[0][0]
      expect(call).toMatch(/\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\]/)
    })
    it('should update configuration with configure method', () => {
      logger.configure({
        minLevel: LogLevel.WARN,
        timestamp: false,
        prefix: 'NEW'
      })
      logger.warn('test message')
      const call = (console.warn as jest.Mock).mock.calls[0][0]
      expect(call).not.toMatch(/\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\]/)
      expect(call).toContain('[NEW]')
    })
  })
}) 