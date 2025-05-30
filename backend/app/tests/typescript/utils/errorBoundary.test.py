from typing import Any


  createErrorBoundary,
  createExpressErrorBoundary,
  withErrorLogging,
  processErrorStack
} from '../../../src/utils/errorBoundary'
describe('Error Boundary Utilities', () => {
  let mockLogger: Logger
  let consoleSpy: jest.SpyInstance
  beforeEach(() => {
    mockLogger = new Logger({ prefix: 'TestLogger' })
    consoleSpy = jest.spyOn(console, 'error').mockImplementation()
  })
  afterEach(() => {
    jest.restoreAllMocks()
  })
  describe('createErrorBoundary', () => {
    it('should pass through successful function execution', async () => {
      const successFn = async () => 'success'
      const boundFn = createErrorBoundary(successFn)
      const result = await boundFn()
      expect(result).toBe('success')
      expect(consoleSpy).not.toHaveBeenCalled()
    })
    it('should handle and log errors', async () => {
      const errorFn = async () => {
        throw new Error('Test error')
      }
      const boundFn = createErrorBoundary(errorFn, { rethrow: false })
      const result = await boundFn()
      expect(result).toBeUndefined()
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Error caught in boundary: Test error')
      )
    })
    it('should rethrow errors as AppError when configured', async () => {
      const errorFn = async () => {
        throw new Error('Test error')
      }
      const boundFn = createErrorBoundary(errorFn, { rethrow: true })
      await expect(boundFn()).rejects.toThrow(AppError)
      expect(consoleSpy).toHaveBeenCalled()
    })
    it('should preserve AppError instances when rethrowing', async () => {
      const appError = new AppError('Test AppError', 400)
      const errorFn = async () => {
        throw appError
      }
      const boundFn = createErrorBoundary(errorFn)
      await expect(boundFn()).rejects.toBe(appError)
    })
  })
  describe('createExpressErrorBoundary', () => {
    let mockReq: Partial<Request>
    let mockRes: Partial<Response>
    let mockNext: jest.Mock
    beforeEach(() => {
      mockReq = {}
      mockRes = {}
      mockNext = jest.fn()
    })
    it('should pass through successful handler execution', async () => {
      const successHandler = async () => 'success'
      const boundHandler = createExpressErrorBoundary()(successHandler)
      await boundHandler(
        mockReq as Request,
        mockRes as Response,
        mockNext
      )
      expect(mockNext).not.toHaveBeenCalled()
    })
    it('should pass errors to next middleware', async () => {
      const error = new Error('Test error')
      const errorHandler = async () => {
        throw error
      }
      const boundHandler = createExpressErrorBoundary()(errorHandler)
      await boundHandler(
        mockReq as Request,
        mockRes as Response,
        mockNext
      )
      expect(mockNext).toHaveBeenCalledWith(error)
    })
  })
  describe('withErrorLogging', () => {
    it('should log errors with enriched context', async () => {
      const error = new AppError('Test error', 400)
      const errorFn = async () => {
        throw error
      }
      const loggedFn = withErrorLogging(errorFn, mockLogger)
      await expect(loggedFn()).rejects.toBe(error)
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Error caught in boundary: Test error'),
        expect.objectContaining({
          name: error.name,
          message: error.message,
          isOperational: true,
          statusCode: 400
        })
      )
    })
    it('should use custom logger if provided', async () => {
      const customLogger = new Logger({ prefix: 'CustomLogger' })
      const loggerSpy = jest.spyOn(customLogger, 'error')
      const errorFn = async () => {
        throw new Error('Test error')
      }
      const loggedFn = withErrorLogging(errorFn, customLogger)
      await expect(loggedFn()).rejects.toThrow()
      expect(loggerSpy).toHaveBeenCalled()
    })
  })
  describe('processErrorStack', () => {
    it('should format error stack information', () => {
      const error = new Error('Test error')
      const stackInfo = processErrorStack(error)
      expect(stackInfo).toEqual(
        expect.objectContaining({
          message: 'Test error',
          name: 'Error',
          stackTrace: expect.any(Array),
          isOperational: false,
          statusCode: 500
        })
      )
    })
    it('should handle AppError instances correctly', () => {
      const error = new AppError('Test error', 400, true)
      const stackInfo = processErrorStack(error)
      expect(stackInfo).toEqual(
        expect.objectContaining({
          message: 'Test error',
          name: 'AppError',
          isOperational: true,
          statusCode: 400
        })
      )
    })
    it('should handle errors without stack traces', () => {
      const error = new Error('Test error')
      error.stack = undefined
      const stackInfo = processErrorStack(error)
      expect(stackInfo.stackTrace).toEqual([])
      expect(stackInfo.firstFrame).toBe('Unknown location')
    })
  })
}) 