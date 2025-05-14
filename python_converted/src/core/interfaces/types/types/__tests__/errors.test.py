from typing import Any


  ApiError,
  NetworkError,
  ValidationError,
  AuthError,
  ForbiddenError,
  NotFoundError,
  RateLimitError,
  ServerError,
  TimeoutError,
  OfflineError,
} from '../errors'
describe('Error Types', () => {
  describe('ApiError', () => {
    it('should create ApiError with message and status code', () => {
      const error = new ApiError('Test error', 400)
      expect(error.message).toBe('Test error')
      expect(error.statusCode).toBe(400)
      expect(error.name).toBe('ApiError')
    })
    it('should include optional data', () => {
      const data = { field: 'test' }
      const error = new ApiError('Test error', 400, data)
      expect(error.data).toEqual(data)
    })
  })
  describe('NetworkError', () => {
    it('should create NetworkError with message', () => {
      const error = new NetworkError('Network error')
      expect(error.message).toBe('Network error')
      expect(error.name).toBe('NetworkError')
    })
    it('should include original error', () => {
      const originalError = new Error('Original error')
      const error = new NetworkError('Network error', originalError)
      expect(error.originalError).toBe(originalError)
    })
  })
  describe('ValidationError', () => {
    it('should create ValidationError with message and errors', () => {
      const errors = { field: ['Invalid value'] }
      const error = new ValidationError('Validation failed', errors)
      expect(error.message).toBe('Validation failed')
      expect(error.errors).toEqual(errors)
      expect(error.name).toBe('ValidationError')
    })
  })
  describe('AuthError', () => {
    it('should create AuthError with default message', () => {
      const error = new AuthError()
      expect(error.message).toBe('Authentication failed')
      expect(error.statusCode).toBe(401)
      expect(error.name).toBe('AuthError')
    })
    it('should create AuthError with custom message', () => {
      const error = new AuthError('Custom auth error')
      expect(error.message).toBe('Custom auth error')
      expect(error.statusCode).toBe(401)
    })
  })
  describe('ForbiddenError', () => {
    it('should create ForbiddenError with default message', () => {
      const error = new ForbiddenError()
      expect(error.message).toBe('Access forbidden')
      expect(error.statusCode).toBe(403)
      expect(error.name).toBe('ForbiddenError')
    })
    it('should create ForbiddenError with custom message', () => {
      const error = new ForbiddenError('Custom forbidden error')
      expect(error.message).toBe('Custom forbidden error')
      expect(error.statusCode).toBe(403)
    })
  })
  describe('NotFoundError', () => {
    it('should create NotFoundError with default message', () => {
      const error = new NotFoundError()
      expect(error.message).toBe('Resource not found')
      expect(error.statusCode).toBe(404)
      expect(error.name).toBe('NotFoundError')
    })
    it('should create NotFoundError with custom message', () => {
      const error = new NotFoundError('Custom not found error')
      expect(error.message).toBe('Custom not found error')
      expect(error.statusCode).toBe(404)
    })
  })
  describe('RateLimitError', () => {
    it('should create RateLimitError with default message', () => {
      const error = new RateLimitError()
      expect(error.message).toBe('Rate limit exceeded')
      expect(error.statusCode).toBe(429)
      expect(error.name).toBe('RateLimitError')
    })
    it('should create RateLimitError with retry after', () => {
      const error = new RateLimitError('Rate limit exceeded', 60)
      expect(error.retryAfter).toBe(60)
      expect(error.statusCode).toBe(429)
    })
  })
  describe('ServerError', () => {
    it('should create ServerError with default message', () => {
      const error = new ServerError()
      expect(error.message).toBe('Internal server error')
      expect(error.statusCode).toBe(500)
      expect(error.name).toBe('ServerError')
    })
    it('should create ServerError with custom message', () => {
      const error = new ServerError('Custom server error')
      expect(error.message).toBe('Custom server error')
      expect(error.statusCode).toBe(500)
    })
  })
  describe('TimeoutError', () => {
    it('should create TimeoutError with default message', () => {
      const error = new TimeoutError()
      expect(error.message).toBe('Request timed out')
      expect(error.name).toBe('TimeoutError')
    })
    it('should create TimeoutError with custom message', () => {
      const error = new TimeoutError('Custom timeout error')
      expect(error.message).toBe('Custom timeout error')
    })
  })
  describe('OfflineError', () => {
    it('should create OfflineError with default message', () => {
      const error = new OfflineError()
      expect(error.message).toBe('No internet connection')
      expect(error.name).toBe('OfflineError')
    })
    it('should create OfflineError with custom message', () => {
      const error = new OfflineError('Custom offline error')
      expect(error.message).toBe('Custom offline error')
    })
  })
})