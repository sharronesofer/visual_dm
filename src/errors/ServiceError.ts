/**
 * Base class for service-related errors
 */
export class ServiceError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ServiceError';
  }
}

/**
 * Error thrown when an entity is not found
 */
export class NotFoundError extends ServiceError {
  constructor(message: string) {
    super(message);
    this.name = 'NotFoundError';
  }
}

/**
 * Error thrown when validation fails
 */
export class ValidationError extends ServiceError {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

/**
 * Error thrown when a database operation fails
 */
export class DatabaseError extends ServiceError {
  constructor(message: string) {
    super(message);
    this.name = 'DatabaseError';
  }
}

/**
 * Error thrown when a duplicate entity is detected
 */
export class DuplicateError extends ServiceError {
  constructor(message: string) {
    super(message);
    this.name = 'DuplicateError';
  }
}

/**
 * Error thrown when an operation is not permitted
 */
export class ForbiddenError extends ServiceError {
  constructor(message: string) {
    super(message);
    this.name = 'ForbiddenError';
  }
} 