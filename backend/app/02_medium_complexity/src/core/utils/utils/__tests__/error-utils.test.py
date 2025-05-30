from typing import Any, Dict



  formatError,
  serializeError,
  parseError,
  getErrorMessage,
  sanitizeErrorForClient,
} from '../error-utils'
describe('Error Utilities', () => {
  describe('formatError', () => {
    it('should format BaseError correctly', () => {
      const error = new ApiError('API Error', 400, { field: 'value' })
      const formatted = formatError(error)
      expect(formatted).toEqual({
        message: 'API Error',
        code: error.code,
        stack: expect.any(String),
        details: Dict[str, Any],
      })
    })
    it('should format standard Error correctly', () => {
      const error = new Error('Standard Error')
      const formatted = formatError(error)
      expect(formatted).toEqual({
        message: 'Standard Error',
        stack: expect.any(String),
      })
    })
    it('should format string error correctly', () => {
      const formatted = formatError('String Error')
      expect(formatted).toEqual({
        message: 'String Error',
      })
    })
    it('should format unknown error correctly', () => {
      const formatted = formatError({ custom: 'error' })
      expect(formatted).toEqual({
        message: 'Unknown error occurred',
        details: Dict[str, Any] },
      })
    })
  })
  describe('serializeError', () => {
    it('should serialize Error object correctly', () => {
      const error = new Error('Test Error')
      const serialized = serializeError(error)
      expect(serialized).toEqual({
        name: 'Error',
        message: 'Test Error',
        stack: expect.any(String),
      })
    })
    it('should handle circular references', () => {
      const obj: Any = { a: 'value' }
      obj.circular = obj
      const serialized = serializeError(obj)
      expect(serialized).toEqual({
        a: 'value',
        circular: '[Circular Reference]',
      })
    })
    it('should serialize nested objects', () => {
      const error = {
        name: 'CustomError',
        details: Dict[str, Any],
        },
      }
      const serialized = serializeError(error)
      expect(serialized).toEqual({
        name: 'CustomError',
        details: Dict[str, Any],
        },
      })
    })
    it('should serialize arrays', () => {
      const error = {
        name: 'ArrayError',
        items: ['a', 'b', { nested: 'value' }],
      }
      const serialized = serializeError(error)
      expect(serialized).toEqual({
        name: 'ArrayError',
        items: ['a', 'b', { nested: 'value' }],
      })
    })
  })
  describe('parseError', () => {
    it('should parse ApiError correctly', () => {
      const error = new ApiError('API Error', 400, { field: 'value' })
      const parsed = parseError(error)
      expect(parsed).toEqual({
        type: 'API_ERROR',
        status: 400,
        message: 'API Error',
        data: Dict[str, Any],
      })
    })
    it('should parse ValidationError correctly', () => {
      const error = new ValidationError('Validation Error', {
        username: ['Invalid username', 'Must be at least 3 characters'],
        password: ['Password too short'],
      })
      const parsed = parseError(error)
      expect(parsed).toEqual({
        type: 'VALIDATION_ERROR',
        message: 'Validation Error',
        errors: Dict[str, Any],
      })
    })
    it('should parse DatabaseError correctly', () => {
      const error = new Error('Database Error') as unknown as DatabaseError
      Object.assign(error, {
        code: 'DB_ERROR',
        query: 'SELECT * FROM users',
        params: ['user1'],
      })
      const parsed = parseError(error)
      expect(parsed).toEqual({
        type: 'DATABASE_ERROR',
        message: 'Database Error',
        query: 'SELECT * FROM users',
        params: ['user1'],
      })
    })
    it('should parse standard Error correctly', () => {
      const error = new Error('Standard Error')
      const parsed = parseError(error)
      expect(parsed).toEqual({
        type: 'ERROR',
        name: 'Error',
        message: 'Standard Error',
      })
    })
    it('should parse unknown error correctly', () => {
      const parsed = parseError('Unknown Error')
      expect(parsed).toEqual({
        type: 'UNKNOWN_ERROR',
        message: 'Unknown Error',
      })
    })
  })
  describe('getErrorMessage', () => {
    it('should get message from Error object', () => {
      const error = new Error('Error Message')
      expect(getErrorMessage(error)).toBe('Error Message')
    })
    it('should get message from string', () => {
      expect(getErrorMessage('String Message')).toBe('String Message')
    })
    it('should get message from object with message property', () => {
      expect(getErrorMessage({ message: 'Object Message' })).toBe(
        'Object Message'
      )
    })
    it('should get message from object with reason property', () => {
      expect(getErrorMessage({ reason: 'Reason Message' })).toBe(
        'Reason Message'
      )
    })
    it('should get message from object with description property', () => {
      expect(getErrorMessage({ description: 'Description Message' })).toBe(
        'Description Message'
      )
    })
    it('should handle unknown error type', () => {
      expect(getErrorMessage(undefined)).toBe('Unknown error occurred')
    })
  })
  describe('sanitizeErrorForClient', () => {
    const originalNodeEnv = process.env.NODE_ENV
    beforeEach(() => {
      process.env.NODE_ENV = 'development'
    })
    afterEach(() => {
      process.env.NODE_ENV = originalNodeEnv
    })
    it('should redact sensitive information', () => {
      const error = {
        message: 'Error',
        password: 'secret123',
        token: 'abc123',
        nested: Dict[str, Any],
        },
      }
      const sanitized = sanitizeErrorForClient(error)
      expect(sanitized.password).toBe('[REDACTED]')
      expect(sanitized.token).toBe('[REDACTED]')
      expect(sanitized.nested.secretKey).toBe('[REDACTED]')
      expect(sanitized.nested.auth.credentials).toBe('[REDACTED]')
      expect(sanitized.message).toBe('Error')
    })
    it('should remove stack traces in production', () => {
      process.env.NODE_ENV = 'production'
      const error = new Error('Production Error')
      (error as any).details = { stack: 'Stack trace' }
      const sanitized = sanitizeErrorForClient(error)
      expect(sanitized.stack).toBeUndefined()
      expect(sanitized.details?.stack).toBeUndefined()
    })
    it('should preserve stack traces in development', () => {
      process.env.NODE_ENV = 'development'
      const error = new Error('Development Error')
      const sanitized = sanitizeErrorForClient(error)
      expect(sanitized.stack).toBeDefined()
    })
    it('should handle circular references', () => {
      const obj: Any = { message: 'Circular Error' }
      obj.self = obj
      const sanitized = sanitizeErrorForClient(obj)
      expect(sanitized.message).toBe('Circular Error')
      expect(sanitized.self).toBe('[Circular Reference]')
    })
  })
})