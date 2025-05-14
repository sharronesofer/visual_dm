from typing import Any, Dict, List, Union


/**
 * Base error interface
 */
class BaseError:
    code: str
    message: str
    details?: Dict[str, Any>
    stack?: str
/**
 * API error interface
 */
class ApiError:
    status: float
    path?: str
    timestamp?: str
/**
 * Validation error interface
 */
class ValidationError:
    field: str
    value?: Any
    constraints?: Dict[str, str>
/**
 * Authentication error interface
 */
class AuthError:
    userId?: str
    requiredRoles?: List[str]
    requiredPermissions?: List[str]
/**
 * Network error interface
 */
class NetworkError:
    url?: str
    method?: str
    retryCount?: float
/**
 * Database error interface
 */
class DatabaseError:
    query?: str
    params?: List[Any]
    table?: str
/**
 * Cache error interface
 */
class CacheError:
    key?: str
    operation?: Union['get', 'set', 'delete', 'clear']
    ttl?: float
/**
 * Business logic error interface
 */
class BusinessError:
    entityId?: str
    entityType?: str
    operation?: str
/**
 * Configuration error interface
 */
class ConfigError:
    configKey?: str
    expectedType?: str
    actualValue?: Any
/**
 * Integration error interface
 */
class IntegrationError:
    service?: str
    endpoint?: str
    responseData?: Any
/**
 * Rate limit error interface
 */
class RateLimitError:
    limit?: float
    remaining?: float
    resetTime?: str
/**
 * File system error interface
 */
class FileSystemError:
    path?: str
    operation?: Union['read', 'write', 'delete', 'move']
    permissions?: str
/**
 * Timeout error interface
 */
class TimeoutError:
    timeout?: float
    operation?: str
    elapsedTime?: float
/**
 * Dependency error interface
 */
class DependencyError:
    dependencyName?: str
    requiredVersion?: str
    installedVersion?: str
/**
 * State error interface
 */
class StateError:
    currentState?: str
    expectedState?: str
    allowedTransitions?: List[str]
/**
 * Base error class for all API errors
 */
class ApiError extends Error {
  constructor(
    message: str,
    public statusCode: float,
    public data?: Any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}
/**
 * Error class for network-related errors
 */
class NetworkError extends Error {
  constructor(
    message: str,
    public originalError?: Error | AxiosError
  ) {
    super(message)
    this.name = 'NetworkError'
  }
}
/**
 * Error class for validation errors
 */
class ValidationError extends Error {
  constructor(
    message: str,
    public errors: Record<string, string[]>
  ) {
    super(message)
    this.name = 'ValidationError'
  }
}
/**
 * Error class for authentication errors
 */
class AuthError extends ApiError {
  constructor(message: str = 'Authentication failed') {
    super(message, 401)
    this.name = 'AuthError'
  }
}
/**
 * Error class for authorization errors
 */
class ForbiddenError extends ApiError {
  constructor(message: str = 'Access forbidden') {
    super(message, 403)
    this.name = 'ForbiddenError'
  }
}
/**
 * Error class for not found errors
 */
class NotFoundError extends ApiError {
  constructor(message: str = 'Resource not found') {
    super(message, 404)
    this.name = 'NotFoundError'
  }
}
/**
 * Error class for rate limit errors
 */
class RateLimitError extends ApiError {
  constructor(
    message: str = 'Rate limit exceeded',
    public retryAfter?: float
  ) {
    super(message, 429)
    this.name = 'RateLimitError'
  }
}
/**
 * Error class for server errors
 */
class ServerError extends ApiError {
  constructor(message: str = 'Internal server error') {
    super(message, 500)
    this.name = 'ServerError'
  }
}
/**
 * Error class for timeout errors
 */
class TimeoutError extends NetworkError {
  constructor(message: str = 'Request timed out') {
    super(message)
    this.name = 'TimeoutError'
  }
}
/**
 * Error class for offline errors
 */
class OfflineError extends NetworkError {
  constructor(message: str = 'No internet connection') {
    super(message)
    this.name = 'OfflineError'
  }
}