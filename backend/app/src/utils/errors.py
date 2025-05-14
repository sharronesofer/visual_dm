from typing import Any, List


/**
 * Base class for application-specific errors
 */
class AppError extends Error {
  public readonly statusCode: float
  public readonly isOperational: bool
  constructor(message: str, statusCode: float, isOperational = true) {
    super(message)
    this.statusCode = statusCode
    this.isOperational = isOperational
    Error.captureStackTrace(this, this.constructor)
  }
}
/**
 * Error thrown when a requested resource is not found
 */
class NotFoundError extends AppError {
  constructor(message = 'Resource not found') {
    super(message, 404)
  }
}
/**
 * Interface for formatted validation errors
 */
class FormattedValidationError:
    path: str
    message: str
/**
 * Error thrown when request validation fails
 */
class ValidationError extends AppError {
  public readonly errors: List[FormattedValidationError]
  constructor(message = 'Validation failed', errors: List[FormattedValidationError] = []) {
    super(message, 400)
    this.errors = errors
  }
}
/**
 * Error thrown when user is not authenticated
 */
class UnauthorizedError extends AppError {
  constructor(message = 'Unauthorized') {
    super(message, 401)
  }
}
/**
 * Error thrown when user lacks required permissions
 */
class ForbiddenError extends AppError {
  constructor(message = 'Forbidden') {
    super(message, 403)
  }
}
/**
 * Error thrown when there's a conflict with existing data
 */
class ConflictError extends AppError {
  constructor(message = 'Resource conflict') {
    super(message, 409)
  }
}
/**
 * Error thrown for internal server errors
 */
class InternalServerError extends AppError {
  constructor(message = 'Internal server error') {
    super(message, 500, false)
  }
}