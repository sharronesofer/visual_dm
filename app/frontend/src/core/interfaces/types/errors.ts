/**
 * Error type definitions and error handling utilities
 * @module types/errors
 */

/**
 * Base error class for application-specific errors
 */
export class AppError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 500,
    public details?: unknown
  ) {
    super(message);
    this.name = this.constructor.name;
    Error.captureStackTrace(this, this.constructor);
  }
}

/**
 * Validation error class for handling validation failures
 */
export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

/**
 * Not found error class for handling 404 cases
 */
export class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(`${resource} with id ${id} not found`, 'NOT_FOUND', 404, { resource, id });
    this.name = 'NotFoundError';
  }
}

/**
 * Authorization error class for handling permission issues
 */
export class AuthorizationError extends AppError {
  constructor(message: string = 'Unauthorized access', details?: unknown) {
    super(message, 'UNAUTHORIZED', 401, details);
    this.name = 'AuthorizationError';
  }
}

/**
 * Authentication error class for handling auth failures
 */
export class AuthenticationError extends AppError {
  constructor(message: string = 'Authentication failed', details?: unknown) {
    super(message, 'UNAUTHENTICATED', 401, details);
    this.name = 'AuthenticationError';
  }
}

/**
 * Forbidden error class for handling permission denied cases
 */
export class ForbiddenError extends AppError {
  constructor(message: string = 'Permission denied', details?: unknown) {
    super(message, 'FORBIDDEN', 403, details);
    this.name = 'ForbiddenError';
  }
}

/**
 * Conflict error class for handling resource conflicts
 */
export class ConflictError extends AppError {
  constructor(message: string, details?: unknown) {
    super(message, 'CONFLICT', 409, details);
    this.name = 'ConflictError';
  }
}

/**
 * Rate limit error class for handling rate limiting
 */
export class RateLimitError extends AppError {
  constructor(
    message: string = 'Rate limit exceeded',
    public retryAfter?: number
  ) {
    super(message, 'RATE_LIMIT', 429, { retryAfter });
    this.name = 'RateLimitError';
  }
}

/**
 * Service unavailable error class for handling service outages
 */
export class ServiceUnavailableError extends AppError {
  constructor(
    message: string = 'Service temporarily unavailable',
    public retryAfter?: number
  ) {
    super(message, 'SERVICE_UNAVAILABLE', 503, { retryAfter });
    this.name = 'ServiceUnavailableError';
  }
}

/**
 * Bad request error class for handling invalid requests
 */
export class BadRequestError extends AppError {
  constructor(message: string, details?: unknown) {
    super(message, 'BAD_REQUEST', 400, details);
    this.name = 'BadRequestError';
  }
}

/**
 * Database error class for handling database-related errors
 */
export class DatabaseError extends AppError {
  constructor(message: string, details?: unknown) {
    super(message, 'DATABASE_ERROR', 500, details);
    this.name = 'DatabaseError';
  }
}

/**
 * External service error class for handling third-party service errors
 */
export class ExternalServiceError extends AppError {
  constructor(
    message: string,
    public service: string,
    details?: Record<string, unknown>
  ) {
    super(message, 'EXTERNAL_SERVICE_ERROR', 502, { service, ...(details || {}) });
    this.name = 'ExternalServiceError';
  }
}

/**
 * Type guard to check if an error is an instance of AppError
 */
export function isAppError(error: unknown): error is AppError {
  return error instanceof AppError;
}

/**
 * Type guard to check if an error is a validation error
 */
export function isValidationError(error: unknown): error is ValidationError {
  return error instanceof ValidationError;
}

/**
 * Type guard to check if an error is a not found error
 */
export function isNotFoundError(error: unknown): error is NotFoundError {
  return error instanceof NotFoundError;
}

/**
 * Error response type for API errors
 */
export interface ErrorResponseData {
  code: string;
  message: string;
  statusCode: number;
  details?: unknown;
}

/**
 * Convert any error to a standardized error response
 */
export function toErrorResponse(error: unknown): ErrorResponseData {
  if (isAppError(error)) {
    return {
      code: error.code,
      message: error.message,
      statusCode: error.statusCode,
      details: error.details,
    };
  }

  if (error instanceof Error) {
    return {
      code: 'INTERNAL_ERROR',
      message: error.message || 'An unexpected error occurred',
      statusCode: 500,
      details: {
        name: error.name,
        stack: process.env.NODE_ENV === 'development' ? error.stack : undefined,
      },
    };
  }

  return {
    code: 'UNKNOWN_ERROR',
    message: String(error) || 'An unknown error occurred',
    statusCode: 500,
  };
}

export interface ServiceError {
  message: string;
  code?: string;
  details?: Record<string, unknown>;
}
