from typing import Any, Dict


  AppError,
  ValidationError,
  NotFoundError,
  AuthenticationError,
  ForbiddenError,
  ConflictError,
  RateLimitError,
  ServiceUnavailableError,
  BadRequestError,
  DatabaseError,
  ExternalServiceError,
  FileSystemError,
  MediaProcessingError,
  isAppError,
  isValidationError,
  isNotFoundError,
  isDatabaseError,
  isExternalServiceError,
  toErrorResponse,
  getErrorMessage,
  processErrorStack
} from '../index'
describe('Error Classes', () => {
  describe('AppError', () => {
    it('should create base error with correct properties', () => {
      const error = new AppError('Test error', 'TEST_ERROR', 500, { foo: 'bar' })
      expect(error).toBeInstanceOf(Error)
      expect(error).toBeInstanceOf(AppError)
      expect(error.message).toBe('Test error')
      expect(error.code).toBe('TEST_ERROR')
      expect(error.statusCode).toBe(500)
      expect(error.details).toEqual({ foo: 'bar' })
      expect(error.name).toBe('AppError')
      expect(error.stack).toBeDefined()
      expect(error.isOperational).toBe(true)
    })
    it('should serialize to JSON correctly', () => {
      const error = new AppError('Test error', 'TEST_ERROR', 500, { foo: 'bar' })
      const json = error.toJSON()
      expect(json).toEqual({
        name: 'AppError',
        code: 'TEST_ERROR',
        message: 'Test error',
        statusCode: 500,
        details: Dict[str, Any],
        isOperational: true,
        stack: error.stack
      })
    })
  })
  describe('ValidationError', () => {
    it('should create validation error with correct properties', () => {
      const errors = { email: ['Invalid email format'] }
      const error = new ValidationError('Validation failed', errors)
      expect(error).toBeInstanceOf(AppError)
      expect(error.message).toBe('Validation failed')
      expect(error.code).toBe('VALIDATION_ERROR')
      expect(error.statusCode).toBe(400)
      expect(error.errors).toEqual(errors)
      expect(error.name).toBe('ValidationError')
    })
  })
  describe('NotFoundError', () => {
    it('should create not found error with correct properties', () => {
      const error = new NotFoundError('User', '123')
      expect(error).toBeInstanceOf(AppError)
      expect(error.message).toBe('User with ID 123 not found')
      expect(error.code).toBe('NOT_FOUND')
      expect(error.statusCode).toBe(404)
      expect(error.resourceType).toBe('User')
      expect(error.resourceId).toBe('123')
      expect(error.name).toBe('NotFoundError')
    })
    it('should use custom message if provided', () => {
      const error = new NotFoundError('User', '123', 'Custom not found message')
      expect(error.message).toBe('Custom not found message')
    })
  })
  describe('AuthenticationError', () => {
    it('should create authentication error with correct properties', () => {
      const error = new AuthenticationError()
      expect(error).toBeInstanceOf(AppError)
      expect(error.message).toBe('Authentication required')
      expect(error.code).toBe('UNAUTHENTICATED')
      expect(error.statusCode).toBe(401)
      expect(error.name).toBe('AuthenticationError')
    })
    it('should use custom message and details if provided', () => {
      const details = { reason: 'Token expired' }
      const error = new AuthenticationError('Custom auth error', details)
      expect(error.message).toBe('Custom auth error')
      expect(error.details).toEqual(details)
    })
  })
  describe('DatabaseError', () => {
    it('should create database error with correct properties', () => {
      const details = { query: 'SELECT * FROM users' }
      const error = new DatabaseError(
        'Database query failed',
        'SELECT',
        'users',
        details
      )
      expect(error).toBeInstanceOf(AppError)
      expect(error.message).toBe('Database query failed')
      expect(error.code).toBe('DATABASE_ERROR')
      expect(error.statusCode).toBe(500)
      expect(error.operation).toBe('SELECT')
      expect(error.entity).toBe('users')
      expect(error.details).toEqual({
        operation: 'SELECT',
        entity: 'users',
        query: 'SELECT * FROM users'
      })
      expect(error.name).toBe('DatabaseError')
      expect(error.isOperational).toBe(false)
    })
  })
  describe('MediaProcessingError', () => {
    it('should create media processing error with correct properties', () => {
      const details = { format: 'webp' }
      const error = new MediaProcessingError(
        'Image conversion failed',
        'image/jpeg',
        'convert',
        details
      )
      expect(error).toBeInstanceOf(AppError)
      expect(error.message).toBe('Image conversion failed')
      expect(error.code).toBe('MEDIA_PROCESSING_ERROR')
      expect(error.statusCode).toBe(500)
      expect(error.mediaType).toBe('image/jpeg')
      expect(error.operation).toBe('convert')
      expect(error.details).toEqual({
        mediaType: 'image/jpeg',
        operation: 'convert',
        format: 'webp'
      })
      expect(error.name).toBe('MediaProcessingError')
    })
  })
})
describe('Type Guards', () => {
  it('should correctly identify AppError instances', () => {
    const appError = new AppError('Test', 'TEST')
    const error = new Error('Test')
    expect(isAppError(appError)).toBe(true)
    expect(isAppError(error)).toBe(false)
    expect(isAppError(null)).toBe(false)
    expect(isAppError(undefined)).toBe(false)
  })
  it('should correctly identify ValidationError instances', () => {
    const validationError = new ValidationError('Test', {})
    const appError = new AppError('Test', 'TEST')
    expect(isValidationError(validationError)).toBe(true)
    expect(isValidationError(appError)).toBe(false)
  })
  it('should correctly identify NotFoundError instances', () => {
    const notFoundError = new NotFoundError('User', '123')
    const appError = new AppError('Test', 'TEST')
    expect(isNotFoundError(notFoundError)).toBe(true)
    expect(isNotFoundError(appError)).toBe(false)
  })
  it('should correctly identify DatabaseError instances', () => {
    const dbError = new DatabaseError('Test', 'SELECT', 'users')
    const appError = new AppError('Test', 'TEST')
    expect(isDatabaseError(dbError)).toBe(true)
    expect(isDatabaseError(appError)).toBe(false)
  })
})
describe('Error Utilities', () => {
  describe('toErrorResponse', () => {
    it('should convert AppError to error response', () => {
      const error = new AppError('Test error', 'TEST_ERROR', 400, { foo: 'bar' })
      const response = toErrorResponse(error)
      expect(response).toEqual({
        code: 'TEST_ERROR',
        message: 'Test error',
        statusCode: 400,
        details: Dict[str, Any]
      })
    })
    it('should convert Error to error response', () => {
      const error = new Error('Test error')
      const response = toErrorResponse(error)
      expect(response).toEqual({
        code: 'INTERNAL_ERROR',
        message: 'Test error',
        statusCode: 500,
        details: Dict[str, Any]
      })
    })
    it('should convert unknown error to error response', () => {
      const response = toErrorResponse('Something went wrong')
      expect(response).toEqual({
        code: 'UNKNOWN_ERROR',
        message: 'Something went wrong',
        statusCode: 500
      })
    })
  })
  describe('getErrorMessage', () => {
    it('should get message from Error object', () => {
      const error = new Error('Error message')
      expect(getErrorMessage(error)).toBe('Error message')
    })
    it('should get message from string', () => {
      expect(getErrorMessage('String message')).toBe('String message')
    })
    it('should get message from object with message property', () => {
      expect(getErrorMessage({ message: 'Object message' })).toBe('Object message')
    })
    it('should handle unknown error type', () => {
      expect(getErrorMessage(undefined)).toBe('Unknown error occurred')
    })
  })
  describe('processErrorStack', () => {
    it('should process error stack information', () => {
      const error = new AppError('Test error', 'TEST_ERROR', 400)
      const stackInfo = processErrorStack(error)
      expect(stackInfo).toEqual({
        message: 'Test error',
        name: 'AppError',
        stackTrace: expect.any(Array),
        isOperational: true,
        statusCode: 400,
        firstFrame: expect.any(String)
      })
    })
    it('should handle errors without stack trace', () => {
      const error = new Error('Test error')
      error.stack = undefined
      const stackInfo = processErrorStack(error)
      expect(stackInfo.stackTrace).toEqual([])
      expect(stackInfo.firstFrame).toBe('Unknown location')
    })
  })
}) 