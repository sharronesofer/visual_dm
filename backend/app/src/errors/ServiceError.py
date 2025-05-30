from typing import Any


/**
 * Base class for service-related errors
 */
class ServiceError extends Error {
  constructor(message: str) {
    super(message)
    this.name = 'ServiceError'
  }
}
/**
 * Error thrown when an entity is not found
 */
class NotFoundError extends ServiceError {
  constructor(message: str) {
    super(message)
    this.name = 'NotFoundError'
  }
}
/**
 * Error thrown when validation fails
 */
class ValidationError extends ServiceError {
  constructor(message: str) {
    super(message)
    this.name = 'ValidationError'
  }
}
/**
 * Error thrown when a database operation fails
 */
class DatabaseError extends ServiceError {
  constructor(message: str) {
    super(message)
    this.name = 'DatabaseError'
  }
}
/**
 * Error thrown when a duplicate entity is detected
 */
class DuplicateError extends ServiceError {
  constructor(message: str) {
    super(message)
    this.name = 'DuplicateError'
  }
}
/**
 * Error thrown when an operation is not permitted
 */
class ForbiddenError extends ServiceError {
  constructor(message: str) {
    super(message)
    this.name = 'ForbiddenError'
  }
} 