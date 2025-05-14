from typing import Any, Dict



  AppError,
  ValidationError,
  NotFoundError,
  AuthorizationError,
  AuthenticationError,
  ForbiddenError,
  ConflictError,
  RateLimitError,
  ServiceUnavailableError,
  BadRequestError,
  DatabaseError,
  ExternalServiceError,
  isAppError,
  isValidationError,
  isNotFoundError,
  toErrorResponse,
} from '../../types/errors'
describe('Error Types', () => {
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
    })
  })
  describe('ValidationError', () => {
    it('should create validation error with correct properties', () => {
      const errors = { email: ['Invalid email'] }
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
      expect(error.message).toBe('User with id 123 not found')
      expect(error.code).toBe('NOT_FOUND')
      expect(error.statusCode).toBe(404)
      expect(error.details).toEqual({ resource: 'User', id: '123' })
      expect(error.name).toBe('NotFoundError')
    })
  })
  describe('AuthorizationError', () => {
    it('should create authorization error with correct properties', () => {
      const error = new AuthorizationError('Custom auth error', { role: 'user' })
      expect(error).toBeInstanceOf(AppError)
      expect(error.message).toBe('Custom auth error')
      expect(error.code).toBe('UNAUTHORIZED')
      expect(error.statusCode).toBe(401)
      expect(error.details).toEqual({ role: 'user' })
      expect(error.name).toBe('AuthorizationError')
    })
    it('should use default message if none provided', () => {
      const error = new AuthorizationError()
      expect(error.message).toBe('Unauthorized access')
    })
  })
  describe('AuthenticationError', () => {
    it('should create authentication error with correct properties', () => {
      const error = new AuthenticationError('Custom auth error', { token: 'invalid' })
      expect(error).toBeInstanceOf(AppError)
      expect(error.message).toBe('Custom auth error')
      expect(error.code).toBe('UNAUTHENTICATED')
      expect(error.statusCode).toBe(401)
      expect(error.details).toEqual({ token: 'invalid' })
      expect(error.name).toBe('AuthenticationError')
    })
    it('should use default message if none provided', () => {
      const error = new AuthenticationError()
      expect(error.message).toBe('Authentication failed')
    })
  })
  describe('ForbiddenError', () => {
    it('should create forbidden error with correct properties', () => {
      const error = new ForbiddenError('Custom forbidden error', { resource: 'document' })
      expect(error).toBeInstanceOf(AppError)
      expect(error.message).toBe('Custom forbidden error')
      expect(error.code).toBe('FORBIDDEN')
      expect(error.statusCode).toBe(403)
      expect(error.details).toEqual({ resource: 'document' })
      expect(error.name).toBe('ForbiddenError')
    })
    it('should use default message if none provided', () => {
      const error = new ForbiddenError()
      expect(error.message).toBe('Permission denied')
    })
  })
  describe('ConflictError', () => {
    it('should create conflict error with correct properties', () => {
      const error = new ConflictError('Resource already exists', { id: '123' })
      expect(error).toBeInstanceOf(AppError)
      expect(error.message).toBe('Resource already exists')
      expect(error.code).toBe('CONFLICT')
      expect(error.statusCode).toBe(409)
      expect(error.details).toEqual({ id: '123' })
      expect(error.name).toBe('ConflictError')
    })
  })
  describe('RateLimitError', () => {
    it('should create rate limit error with correct properties', () => {
      const error = new RateLimitError('Too many requests', 60)
      expect(error).toBeInstanceOf(AppError)
      expect(error.message).toBe('Too many requests')
      expect(error.code).toBe('RATE_LIMIT')
      expect(error.statusCode).toBe(429)
      expect(error.retryAfter).toBe(60)
      expect(error.details).toEqual({ retryAfter: 60 })
      expect(error.name).toBe('RateLimitError')
    })
    it('should use default message if none provided', () => {
      const error = new RateLimitError()
      expect(error.message).toBe('Rate limit exceeded')
    })
  })
  describe('ServiceUnavailableError', () => {
    it('should create service unavailable error with correct properties', () => {
      const error = new ServiceUnavailableError('Maintenance in progress', 300)
      expect(error).toBeInstanceOf(AppError)
      expect(error.message).toBe('Maintenance in progress')
      expect(error.code).toBe('SERVICE_UNAVAILABLE')
      expect(error.statusCode).toBe(503)
      expect(error.retryAfter).toBe(300)
      expect(error.details).toEqual({ retryAfter: 300 })
      expect(error.name).toBe('ServiceUnavailableError')
    })
    it('should use default message if none provided', () => {
      const error = new ServiceUnavailableError()
      expect(error.message).toBe('Service temporarily unavailable')
    })
  })
  describe('BadRequestError', () => {
    it('should create bad request error with correct properties', () => {
      const error = new BadRequestError('Invalid input', { field: 'email' })
      expect(error).toBeInstanceOf(AppError)
      expect(error.message).toBe('Invalid input')
      expect(error.code).toBe('BAD_REQUEST')
      expect(error.statusCode).toBe(400)
      expect(error.details).toEqual({ field: 'email' })
      expect(error.name).toBe('BadRequestError')
    })
  })
  describe('DatabaseError', () => {
    it('should create database error with correct properties', () => {
      const error = new DatabaseError('Connection failed', { table: 'users' })
      expect(error).toBeInstanceOf(AppError)
      expect(error.message).toBe('Connection failed')
      expect(error.code).toBe('DATABASE_ERROR')
      expect(error.statusCode).toBe(500)
      expect(error.details).toEqual({ table: 'users' })
      expect(error.name).toBe('DatabaseError')
    })
  })
  describe('ExternalServiceError', () => {
    it('should create external service error with correct properties', () => {
      const error = new ExternalServiceError(
        'API request failed',
        'payment-service',
        { statusCode: 500 }
      )
      expect(error).toBeInstanceOf(AppError)
      expect(error.message).toBe('API request failed')
      expect(error.code).toBe('EXTERNAL_SERVICE_ERROR')
      expect(error.statusCode).toBe(502)
      expect(error.service).toBe('payment-service')
      expect(error.details).toEqual({ service: 'payment-service', statusCode: 500 })
      expect(error.name).toBe('ExternalServiceError')
    })
  })
  describe('Type Guards', () => {
    it('should correctly identify AppError instances', () => {
      const appError = new AppError('Test', 'TEST')
      const validationError = new ValidationError('Test', {})
      const regularError = new Error('Test')
      expect(isAppError(appError)).toBe(true)
      expect(isAppError(validationError)).toBe(true)
      expect(isAppError(regularError)).toBe(false)
      expect(isAppError(null)).toBe(false)
      expect(isAppError(undefined)).toBe(false)
      expect(isAppError({ message: 'Test' })).toBe(false)
    })
    it('should correctly identify ValidationError instances', () => {
      const validationError = new ValidationError('Test', {})
      const appError = new AppError('Test', 'TEST')
      expect(isValidationError(validationError)).toBe(true)
      expect(isValidationError(appError)).toBe(false)
      expect(isValidationError(new Error('Test'))).toBe(false)
    })
    it('should correctly identify NotFoundError instances', () => {
      const notFoundError = new NotFoundError('User', '123')
      const appError = new AppError('Test', 'TEST')
      expect(isNotFoundError(notFoundError)).toBe(true)
      expect(isNotFoundError(appError)).toBe(false)
      expect(isNotFoundError(new Error('Test'))).toBe(false)
    })
  })
  describe('toErrorResponse', () => {
    it('should convert AppError to error response', () => {
      const error = new AppError('Test error', 'TEST_ERROR', 400, { foo: 'bar' })
      const response = toErrorResponse(error)
      expect(response).toEqual({
        code: 'TEST_ERROR',
        message: 'Test error',
        statusCode: 400,
        details: Dict[str, Any],
      })
    })
    it('should convert regular Error to error response', () => {
      const error = new Error('Test error')
      const response = toErrorResponse(error)
      expect(response).toEqual({
        code: 'INTERNAL_ERROR',
        message: 'Test error',
        statusCode: 500,
        details: Dict[str, Any],
      })
    })
    it('should convert unknown error to error response', () => {
      const response = toErrorResponse('Something went wrong')
      expect(response).toEqual({
        code: 'UNKNOWN_ERROR',
        message: 'Something went wrong',
        statusCode: 500,
      })
    })
    it('should handle null/undefined errors', () => {
      expect(toErrorResponse(null)).toEqual({
        code: 'UNKNOWN_ERROR',
        message: 'null',
        statusCode: 500,
      })
      expect(toErrorResponse(undefined)).toEqual({
        code: 'UNKNOWN_ERROR',
        message: 'undefined',
        statusCode: 500,
      })
    })
  })
}) 