from typing import Any, Dict



  ErrorReporter,
  ConsoleReporterBackend,
  ErrorReport,
  ErrorReporterBackend,
} from '../error-reporter'
jest.mock('../logger', () => ({
  logger: Dict[str, Any],
}))
describe('ErrorReporter', () => {
  let errorReporter: ErrorReporter
  let mockBackend: jest.Mocked<ErrorReporterBackend>
  beforeEach(() => {
    jest.clearAllMocks()
    jest.useFakeTimers()
    mockBackend = {
      name: 'mock',
      report: jest.fn().mockResolvedValue(undefined),
      flush: jest.fn().mockResolvedValue(undefined),
    }
    (ErrorReporter as any).instance = undefined
    errorReporter = ErrorReporter.getInstance({
      backends: [mockBackend],
      sampleRate: 1.0,
      maxBatchSize: 2,
      batchTimeout: 1000,
    })
  })
  afterEach(() => {
    jest.useRealTimers()
  })
  describe('Initialization', () => {
    it('should create singleton instance', () => {
      const instance1 = ErrorReporter.getInstance()
      const instance2 = ErrorReporter.getInstance()
      expect(instance1).toBe(instance2)
    })
    it('should use default options when not provided', () => {
      const reporter = ErrorReporter.getInstance()
      expect(reporter).toBeDefined()
      expect(reporter['backends'][0]).toBeInstanceOf(ConsoleReporterBackend)
    })
  })
  describe('Backend Management', () => {
    it('should add new backend', () => {
      const newBackend = { name: 'new', report: jest.fn() }
      errorReporter.addBackend(newBackend)
      expect(errorReporter['backends']).toContainEqual(newBackend)
    })
    it('should not add duplicate backend', () => {
      const backend = { name: 'test', report: jest.fn() }
      errorReporter.addBackend(backend)
      errorReporter.addBackend(backend)
      expect(
        errorReporter['backends'].filter(b => b.name === 'test')
      ).toHaveLength(1)
    })
    it('should remove backend', () => {
      errorReporter.removeBackend('mock')
      expect(errorReporter['backends']).not.toContainEqual(mockBackend)
    })
  })
  describe('Error Reporting', () => {
    it('should capture and report error', () => {
      const error = new Error('Test error')
      errorReporter.captureException(error)
      expect(errorReporter['batchQueue']).toHaveLength(1)
      expect(mockBackend.report).not.toHaveBeenCalled()
      jest.advanceTimersByTime(1000)
      expect(mockBackend.report).toHaveBeenCalled()
    })
    it('should respect sample rate', () => {
      errorReporter = ErrorReporter.getInstance({
        backends: [mockBackend],
        sampleRate: 0,
      })
      errorReporter.captureException(new Error('Test'))
      expect(errorReporter['batchQueue']).toHaveLength(0)
    })
    it('should respect filter function', () => {
      errorReporter = ErrorReporter.getInstance({
        backends: [mockBackend],
        filterFn: error => error.message.includes('report'),
      })
      errorReporter.captureException(new Error('do not report'))
      errorReporter.captureException(new Error('please report'))
      expect(errorReporter['batchQueue']).toHaveLength(1)
      expect(errorReporter['batchQueue'][0].error.message).toBe(
        'please report'
      )
    })
    it('should process batch immediately when full', () => {
      errorReporter.captureException(new Error('Error 1'))
      errorReporter.captureException(new Error('Error 2'))
      expect(mockBackend.report).toHaveBeenCalledTimes(2)
      expect(errorReporter['batchQueue']).toHaveLength(0)
    })
    it('should include context when provided', () => {
      const contextProvider = () => ({ app: 'test', env: 'testing' })
      errorReporter = ErrorReporter.getInstance({
        backends: [mockBackend],
        contextProvider,
      })
      errorReporter.captureException(new Error('Test'))
      jest.advanceTimersByTime(1000)
      expect(mockBackend.report).toHaveBeenCalledWith(
        expect.objectContaining({
          context: expect.objectContaining({
            app: 'test',
            env: 'testing',
          }),
        })
      )
    })
    it('should include user data when allowed', () => {
      const userProvider = () => ({ id: '123', email: 'test@example.com' })
      errorReporter = ErrorReporter.getInstance({
        backends: [mockBackend],
        userProvider,
        includePrivateData: true,
      })
      errorReporter.captureException(new Error('Test'))
      jest.advanceTimersByTime(1000)
      expect(mockBackend.report).toHaveBeenCalledWith(
        expect.objectContaining({
          user: expect.objectContaining({
            id: '123',
            email: 'test@example.com',
          }),
        })
      )
    })
    it('should exclude user data when private data disabled', () => {
      const userProvider = () => ({ id: '123', email: 'test@example.com' })
      errorReporter = ErrorReporter.getInstance({
        backends: [mockBackend],
        userProvider,
        includePrivateData: false,
      })
      errorReporter.captureException(new Error('Test'))
      jest.advanceTimersByTime(1000)
      expect(mockBackend.report).toHaveBeenCalledWith(
        expect.not.objectContaining({
          user: expect.anything(),
        })
      )
    })
  })
  describe('Error Frequency Tracking', () => {
    it('should track error frequency', () => {
      const error = new Error('Frequent error')
      errorReporter.captureException(error)
      errorReporter.captureException(error)
      errorReporter.captureException(error)
      const stats = errorReporter.getErrorStats()
      const key = `Error:${error.message}`
      expect(stats[key]).toBeDefined()
      expect(stats[key].count).toBe(3)
      expect(new Date(stats[key].firstSeen)).toBeInstanceOf(Date)
      expect(new Date(stats[key].lastSeen)).toBeInstanceOf(Date)
    })
    it('should track different errors separately', () => {
      errorReporter.captureException(new Error('Error 1'))
      errorReporter.captureException(new Error('Error 2'))
      errorReporter.captureException(new Error('Error 1'))
      const stats = errorReporter.getErrorStats()
      expect(Object.keys(stats)).toHaveLength(2)
      expect(stats['Error:Error 1'].count).toBe(2)
      expect(stats['Error:Error 2'].count).toBe(1)
    })
  })
  describe('Batch Processing', () => {
    it('should flush pending reports', async () => {
      errorReporter.captureException(new Error('Test 1'))
      errorReporter.captureException(new Error('Test 2'))
      jest.clearAllTimers()
      await errorReporter.flush()
      expect(mockBackend.report).toHaveBeenCalledTimes(2)
      expect(errorReporter['batchQueue']).toHaveLength(0)
      expect(mockBackend.flush).toHaveBeenCalled()
    })
    it('should handle backend errors gracefully', async () => {
      mockBackend.report.mockRejectedValueOnce(new Error('Backend error'))
      errorReporter.captureException(new Error('Test'))
      jest.advanceTimersByTime(1000)
      expect(logger.error).toHaveBeenCalledWith(
        'Error processing error report batch:',
        expect.any(Error)
      )
    })
  })
  describe('ConsoleReporterBackend', () => {
    it('should log errors to console', async () => {
      const consoleBackend = new ConsoleReporterBackend()
      const report: ErrorReport = {
        error: new Error('Console test'),
        timestamp: new Date().toISOString(),
        tags: Dict[str, Any],
        extra: Dict[str, Any],
      }
      await consoleBackend.report(report)
      expect(logger.error).toHaveBeenCalledWith(
        'Error Report:',
        report.error,
        expect.objectContaining({
          tags: report.tags,
          extra: report.extra,
        })
      )
    })
  })
})