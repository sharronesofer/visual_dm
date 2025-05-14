from typing import Any, Dict, List


/**
 * Error handling system for the media management application
 * @module errors
 */
/**
 * Base error class for application-specific errors
 */
class AppError extends Error {
  constructor(
    message: str,
    public code: str,
    public statusCode: float = 500,
    public details?: unknown,
    public isOperational: bool = true
  ) {
    super(message)
    this.name = this.constructor.name
    Error.captureStackTrace(this, this.constructor)
  }
  toJSON() {
    return {
      name: this.name,
      code: this.code,
      message: this.message,
      statusCode: this.statusCode,
      details: this.details,
      isOperational: this.isOperational,
      stack: this.stack,
    }
  }
}
/**
 * Error thrown when request validation fails
 */
class ValidationError extends AppError {
  constructor(
    message: str = 'Validation failed',
    public errors: Record<string, string[]>
  ) {
    super(message, 'VALIDATION_ERROR', 400, errors)
    this.name = 'ValidationError'
  }
}
/**
 * Error thrown when a requested resource is not found
 */
class NotFoundError extends AppError {
  constructor(
    public resourceType: str,
    public resourceId: str | number,
    message?: str
  ) {
    super(message || `${resourceType} with ID ${resourceId} not found`, 'NOT_FOUND', 404)
    this.name = 'NotFoundError'
  }
}
/**
 * Error thrown when user is not authenticated
 */
class AuthenticationError extends AppError {
  constructor(message: str = 'Authentication required', details?: unknown) {
    super(message, 'UNAUTHENTICATED', 401, details)
    this.name = 'AuthenticationError'
  }
}
/**
 * Error thrown when user lacks required permissions
 */
class ForbiddenError extends AppError {
  constructor(message: str = 'Permission denied', details?: unknown) {
    super(message, 'FORBIDDEN', 403, details)
    this.name = 'ForbiddenError'
  }
}
/**
 * Error thrown when a conflict occurs (e.g., duplicate resource)
 */
class ConflictError extends AppError {
  constructor(
    message: str,
    public conflictingResource?: { type: str; id: str | number }
  ) {
    super(message, 'CONFLICT', 409, conflictingResource)
    this.name = 'ConflictError'
  }
}
/**
 * Error thrown when rate limit is exceeded
 */
class RateLimitError extends AppError {
  constructor(
    message: str = 'Rate limit exceeded',
    public retryAfter?: float
  ) {
    super(message, 'RATE_LIMIT', 429, { retryAfter })
    this.name = 'RateLimitError'
  }
}
/**
 * Error thrown when service is temporarily unavailable
 */
class ServiceUnavailableError extends AppError {
  constructor(
    message: str = 'Service temporarily unavailable',
    public retryAfter?: float
  ) {
    super(message, 'SERVICE_UNAVAILABLE', 503, { retryAfter })
    this.name = 'ServiceUnavailableError'
  }
}
/**
 * Error thrown for invalid request parameters
 */
class BadRequestError extends AppError {
  constructor(message: str, details?: unknown) {
    super(message, 'BAD_REQUEST', 400, details)
    this.name = 'BadRequestError'
  }
}
/**
 * Error thrown for database operation failures
 */
class DatabaseError extends AppError {
  constructor(
    message: str,
    public operation: str,
    public entity: str,
    details?: Record<string, unknown>
  ) {
    super(message, 'DATABASE_ERROR', 500, { operation, entity, ...(details || {}) })
    this.name = 'DatabaseError'
    this.isOperational = false
  }
}
/**
 * Error thrown for external service failures
 */
class ExternalServiceError extends AppError {
  constructor(
    message: str,
    public service: str,
    details?: Record<string, unknown>
  ) {
    super(message, 'EXTERNAL_SERVICE_ERROR', 502, { service, ...(details || {}) })
    this.name = 'ExternalServiceError'
  }
}
/**
 * Error thrown for file system operation failures
 */
class FileSystemError extends AppError {
  constructor(
    message: str,
    public operation: str,
    public path: str,
    details?: Record<string, unknown>
  ) {
    super(message, 'FILE_SYSTEM_ERROR', 500, { operation, path, ...(details || {}) })
    this.name = 'FileSystemError'
    this.isOperational = false
  }
}
/**
 * Error thrown for media processing failures
 */
class MediaProcessingError extends AppError {
  constructor(
    message: str,
    public mediaType: str,
    public operation: str,
    details?: unknown
  ) {
    super(message, 'MEDIA_PROCESSING_ERROR', 500, { mediaType, operation, ...details })
    this.name = 'MediaProcessingError'
  }
}
const isAppError = (error: unknown): error is AppError => {
  return error instanceof AppError
}
const isValidationError = (error: unknown): error is ValidationError => {
  return error instanceof ValidationError
}
const isNotFoundError = (error: unknown): error is NotFoundError => {
  return error instanceof NotFoundError
}
const isDatabaseError = (error: unknown): error is DatabaseError => {
  return error instanceof DatabaseError
}
const isExternalServiceError = (error: unknown): error is ExternalServiceError => {
  return error instanceof ExternalServiceError
}
class ErrorResponse:
    code: str
    message: str
    statusCode: float
    details?: unknown
/**
 * Convert any error to a standardized error response
 */
function toErrorResponse(error: unknown): \'ErrorResponse\' {
  if (isAppError(error)) {
    return {
      code: error.code,
      message: error.message,
      statusCode: error.statusCode,
      details: error.details,
    }
  }
  if (error instanceof Error) {
    return {
      code: 'INTERNAL_ERROR',
      message: error.message,
      statusCode: 500,
      details: Dict[str, Any],
    }
  }
  return {
    code: 'UNKNOWN_ERROR',
    message: String(error),
    statusCode: 500,
  }
}
/**
 * Extract error message from various error types
 */
function getErrorMessage(error: unknown): str {
  if (error instanceof Error) {
    return error.message
  }
  if (typeof error === 'string') {
    return error
  }
  if (error && typeof error === 'object') {
    const errorObj = error as Record<string, any>
    return errorObj.message || errorObj.reason || errorObj.description || JSON.stringify(error)
  }
  return 'Unknown error occurred'
}
/**
 * Process error stack trace for logging
 */
function processErrorStack(error: Error): {
  message: str
  name: str
  stackTrace: List[string]
  isOperational: bool
  statusCode: float
  firstFrame?: str
} {
  const stackLines = error.stack?.split('\n').map(line => line.trim()) || []
  const firstFrame = stackLines[1] || 'Unknown location'
  return {
    message: error.message,
    name: error.name,
    stackTrace: stackLines,
    isOperational: isAppError(error) ? error.isOperational : false,
    statusCode: isAppError(error) ? error.statusCode : 500,
    firstFrame,
  }
}