from typing import Any, Dict



  ApplicationError,
  ApiErrorImpl,
  ValidationErrorImpl,
  AuthErrorImpl,
  NetworkErrorImpl,
  DatabaseErrorImpl,
  CacheErrorImpl,
  BusinessErrorImpl,
  ConfigErrorImpl,
  IntegrationErrorImpl,
  RateLimitErrorImpl,
  FileSystemErrorImpl,
  TimeoutErrorImpl,
  DependencyErrorImpl,
  StateErrorImpl,
} from '../index'
describe('Error Classes', () => {
  describe('ApplicationError', () => {
    it('should create base error with correct properties', () => {
      const error = new ApplicationError('TEST_ERROR', 'Test message', {
        foo: 'bar',
      })
      expect(error).toBeInstanceOf(Error)
      expect(error.code).toBe('TEST_ERROR')
      expect(error.message).toBe('Test message')
      expect(error.details).toEqual({ foo: 'bar' })
      expect(error.stack).toBeDefined()
    })
    it('should serialize to JSON correctly', () => {
      const error = new ApplicationError('TEST_ERROR', 'Test message', {
        foo: 'bar',
      })
      const json = error.toJSON()
      expect(json).toEqual({
        code: 'TEST_ERROR',
        message: 'Test message',
        details: Dict[str, Any],
        stack: error.stack,
      })
    })
  })
  describe('ApiErrorImpl', () => {
    it('should create API error with correct properties', () => {
      const error = new ApiErrorImpl('API_ERROR', 'API error', 404, '/test', {
        detail: 'Not found',
      })
      expect(error).toBeInstanceOf(ApplicationError)
      expect(error.code).toBe('API_ERROR')
      expect(error.message).toBe('API error')
      expect(error.status).toBe(404)
      expect(error.path).toBe('/test')
      expect(error.details).toEqual({ detail: 'Not found' })
      expect(error.timestamp).toBeDefined()
    })
  })
  describe('ValidationErrorImpl', () => {
    it('should create validation error with correct properties', () => {
      const constraints = { required: 'Field is required' }
      const error = new ValidationErrorImpl(
        'email',
        'Invalid email',
        'test',
        constraints
      )
      expect(error).toBeInstanceOf(ApplicationError)
      expect(error.code).toBe('VALIDATION_ERROR')
      expect(error.message).toBe('Invalid email')
      expect(error.field).toBe('email')
      expect(error.value).toBe('test')
      expect(error.constraints).toEqual(constraints)
    })
  })
  describe('AuthErrorImpl', () => {
    it('should create auth error with correct properties', () => {
      const error = new AuthErrorImpl(
        'Unauthorized',
        'user123',
        ['admin'],
        ['read', 'write']
      )
      expect(error).toBeInstanceOf(ApplicationError)
      expect(error.code).toBe('AUTH_ERROR')
      expect(error.message).toBe('Unauthorized')
      expect(error.userId).toBe('user123')
      expect(error.requiredRoles).toEqual(['admin'])
      expect(error.requiredPermissions).toEqual(['read', 'write'])
    })
  })
  describe('NetworkErrorImpl', () => {
    it('should create network error with correct properties', () => {
      const error = new NetworkErrorImpl(
        'Network failure',
        'https:
        'GET',
        3
      )
      expect(error).toBeInstanceOf(ApplicationError)
      expect(error.code).toBe('NETWORK_ERROR')
      expect(error.message).toBe('Network failure')
      expect(error.url).toBe('https:
      expect(error.method).toBe('GET')
      expect(error.retryCount).toBe(3)
    })
  })
  describe('DatabaseErrorImpl', () => {
    it('should create database error with correct properties', () => {
      const error = new DatabaseErrorImpl(
        'Query failed',
        'SELECT * FROM users',
        ['param1'],
        'users'
      )
      expect(error).toBeInstanceOf(ApplicationError)
      expect(error.code).toBe('DATABASE_ERROR')
      expect(error.message).toBe('Query failed')
      expect(error.query).toBe('SELECT * FROM users')
      expect(error.params).toEqual(['param1'])
      expect(error.table).toBe('users')
    })
  })
  describe('CacheErrorImpl', () => {
    it('should create cache error with correct properties', () => {
      const error = new CacheErrorImpl(
        'Cache operation failed',
        'test-key',
        'get',
        300000
      )
      expect(error).toBeInstanceOf(ApplicationError)
      expect(error.code).toBe('CACHE_ERROR')
      expect(error.message).toBe('Cache operation failed')
      expect(error.key).toBe('test-key')
      expect(error.operation).toBe('get')
      expect(error.ttl).toBe(300000)
    })
  })
  describe('BusinessErrorImpl', () => {
    it('should create business error with correct properties', () => {
      const error = new BusinessErrorImpl(
        'Invalid operation',
        'user123',
        'User',
        'delete'
      )
      expect(error).toBeInstanceOf(ApplicationError)
      expect(error.code).toBe('BUSINESS_ERROR')
      expect(error.message).toBe('Invalid operation')
      expect(error.entityId).toBe('user123')
      expect(error.entityType).toBe('User')
      expect(error.operation).toBe('delete')
    })
  })
  describe('ConfigErrorImpl', () => {
    it('should create config error with correct properties', () => {
      const error = new ConfigErrorImpl(
        'Invalid config',
        'API_KEY',
        'string',
        123
      )
      expect(error).toBeInstanceOf(ApplicationError)
      expect(error.code).toBe('CONFIG_ERROR')
      expect(error.message).toBe('Invalid config')
      expect(error.configKey).toBe('API_KEY')
      expect(error.expectedType).toBe('string')
      expect(error.actualValue).toBe(123)
    })
  })
  describe('IntegrationErrorImpl', () => {
    it('should create integration error with correct properties', () => {
      const error = new IntegrationErrorImpl(
        'Integration failed',
        'payment-service',
        '/process',
        { error: 'Invalid card' }
      )
      expect(error).toBeInstanceOf(ApplicationError)
      expect(error.code).toBe('INTEGRATION_ERROR')
      expect(error.message).toBe('Integration failed')
      expect(error.service).toBe('payment-service')
      expect(error.endpoint).toBe('/process')
      expect(error.responseData).toEqual({ error: 'Invalid card' })
    })
  })
  describe('RateLimitErrorImpl', () => {
    it('should create rate limit error with correct properties', () => {
      const error = new RateLimitErrorImpl(
        'Rate limit exceeded',
        100,
        0,
        '2024-03-20T10:00:00Z'
      )
      expect(error).toBeInstanceOf(ApplicationError)
      expect(error.code).toBe('RATE_LIMIT_ERROR')
      expect(error.message).toBe('Rate limit exceeded')
      expect(error.limit).toBe(100)
      expect(error.remaining).toBe(0)
      expect(error.resetTime).toBe('2024-03-20T10:00:00Z')
    })
  })
  describe('FileSystemErrorImpl', () => {
    it('should create file system error with correct properties', () => {
      const error = new FileSystemErrorImpl(
        'File operation failed',
        '/path/to/file',
        'read',
        '644'
      )
      expect(error).toBeInstanceOf(ApplicationError)
      expect(error.code).toBe('FILE_SYSTEM_ERROR')
      expect(error.message).toBe('File operation failed')
      expect(error.path).toBe('/path/to/file')
      expect(error.operation).toBe('read')
      expect(error.permissions).toBe('644')
    })
  })
  describe('TimeoutErrorImpl', () => {
    it('should create timeout error with correct properties', () => {
      const error = new TimeoutErrorImpl(
        'Operation timed out',
        5000,
        'database-query',
        6000
      )
      expect(error).toBeInstanceOf(ApplicationError)
      expect(error.code).toBe('TIMEOUT_ERROR')
      expect(error.message).toBe('Operation timed out')
      expect(error.timeout).toBe(5000)
      expect(error.operation).toBe('database-query')
      expect(error.elapsedTime).toBe(6000)
    })
  })
  describe('DependencyErrorImpl', () => {
    it('should create dependency error with correct properties', () => {
      const error = new DependencyErrorImpl(
        'Incompatible version',
        'react',
        '^18.0.0',
        '17.0.2'
      )
      expect(error).toBeInstanceOf(ApplicationError)
      expect(error.code).toBe('DEPENDENCY_ERROR')
      expect(error.message).toBe('Incompatible version')
      expect(error.dependencyName).toBe('react')
      expect(error.requiredVersion).toBe('^18.0.0')
      expect(error.installedVersion).toBe('17.0.2')
    })
  })
  describe('StateErrorImpl', () => {
    it('should create state error with correct properties', () => {
      const error = new StateErrorImpl(
        'Invalid state transition',
        'draft',
        'published',
        ['review', 'published']
      )
      expect(error).toBeInstanceOf(ApplicationError)
      expect(error.code).toBe('STATE_ERROR')
      expect(error.message).toBe('Invalid state transition')
      expect(error.currentState).toBe('draft')
      expect(error.expectedState).toBe('published')
      expect(error.allowedTransitions).toEqual(['review', 'published'])
    })
  })
})