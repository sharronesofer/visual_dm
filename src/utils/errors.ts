/**
 * Base class for application-specific errors
 */
export class AppError extends Error {
  public readonly statusCode: number;
  public readonly isOperational: boolean;

  constructor(message: string, statusCode: number, isOperational = true) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = isOperational;
    Error.captureStackTrace(this, this.constructor);
  }
}

/**
 * Error thrown when a requested resource is not found
 */
export class NotFoundError extends AppError {
  constructor(message = 'Resource not found') {
    super(message, 404);
  }
}

/**
 * Interface for formatted validation errors
 */
export interface FormattedValidationError {
  path: string;
  message: string;
}

/**
 * Error thrown when request validation fails
 */
export class ValidationError extends AppError {
  public readonly errors: FormattedValidationError[];

  constructor(message = 'Validation failed', errors: FormattedValidationError[] = []) {
    super(message, 400);
    this.errors = errors;
  }
}

/**
 * Error thrown when user is not authenticated
 */
export class UnauthorizedError extends AppError {
  constructor(message = 'Unauthorized') {
    super(message, 401);
  }
}

/**
 * Error thrown when user lacks required permissions
 */
export class ForbiddenError extends AppError {
  constructor(message = 'Forbidden') {
    super(message, 403);
  }
}

/**
 * Error thrown when there's a conflict with existing data
 */
export class ConflictError extends AppError {
  constructor(message = 'Resource conflict') {
    super(message, 409);
  }
}

/**
 * Error thrown for internal server errors
 */
export class InternalServerError extends AppError {
  constructor(message = 'Internal server error') {
    super(message, 500, false);
  }
}
