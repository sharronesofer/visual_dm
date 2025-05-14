/**
 * Error handling system for the media management application
 * @module errors
 */

/**
 * Base error class for application-specific errors
 */
export class AppError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 500,
    public details?: unknown,
    public isOperational: boolean = true
  ) {
    super(message);
    this.name = this.constructor.name;
    Error.captureStackTrace(this, this.constructor);
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
    };
  }
}

/**
 * Error thrown when request validation fails
 */
export class ValidationError extends AppError {
  constructor(
    message: string = 'Validation failed',
    public errors: Record<string, string[]>
  ) {
    super(message, 'VALIDATION_ERROR', 400, errors);
    this.name = 'ValidationError';
  }
}

/**
 * Error thrown when a requested resource is not found
 */
export class NotFoundError extends AppError {
  constructor(
    public resourceType: string,
    public resourceId: string | number,
    message?: string
  ) {
    super(message || `${resourceType} with ID ${resourceId} not found`, 'NOT_FOUND', 404);
    this.name = 'NotFoundError';
  }
}

/**
 * Error thrown when user is not authenticated
 */
export class AuthenticationError extends AppError {
  constructor(message: string = 'Authentication required', details?: unknown) {
    super(message, 'UNAUTHENTICATED', 401, details);
    this.name = 'AuthenticationError';
  }
}

/**
 * Error thrown when user lacks required permissions
 */
export class ForbiddenError extends AppError {
  constructor(message: string = 'Permission denied', details?: unknown) {
    super(message, 'FORBIDDEN', 403, details);
    this.name = 'ForbiddenError';
  }
}

/**
 * Error thrown when a conflict occurs (e.g., duplicate resource)
 */
export class ConflictError extends AppError {
  constructor(
    message: string,
    public conflictingResource?: { type: string; id: string | number }
  ) {
    super(message, 'CONFLICT', 409, conflictingResource);
    this.name = 'ConflictError';
  }
}

/**
 * Error thrown when rate limit is exceeded
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
 * Error thrown when service is temporarily unavailable
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
 * Error thrown for invalid request parameters
 */
export class BadRequestError extends AppError {
  constructor(message: string, details?: unknown) {
    super(message, 'BAD_REQUEST', 400, details);
    this.name = 'BadRequestError';
  }
}

/**
 * Error thrown for database operation failures
 */
export class DatabaseError extends AppError {
  constructor(
    message: string,
    public operation: string,
    public entity: string,
    details?: Record<string, unknown>
  ) {
    super(message, 'DATABASE_ERROR', 500, { operation, entity, ...(details || {}) });
    this.name = 'DatabaseError';
    this.isOperational = false;
  }
}

/**
 * Error thrown for external service failures
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
 * Error thrown for file system operation failures
 */
export class FileSystemError extends AppError {
  constructor(
    message: string,
    public operation: string,
    public path: string,
    details?: Record<string, unknown>
  ) {
    super(message, 'FILE_SYSTEM_ERROR', 500, { operation, path, ...(details || {}) });
    this.name = 'FileSystemError';
    this.isOperational = false;
  }
}

/**
 * Error thrown for media processing failures
 */
export class MediaProcessingError extends AppError {
  constructor(
    message: string,
    public mediaType: string,
    public operation: string,
    details?: unknown
  ) {
    super(message, 'MEDIA_PROCESSING_ERROR', 500, { mediaType, operation, ...details });
    this.name = 'MediaProcessingError';
  }
}

// Type Guards
export const isAppError = (error: unknown): error is AppError => {
  return error instanceof AppError;
};

export const isValidationError = (error: unknown): error is ValidationError => {
  return error instanceof ValidationError;
};

export const isNotFoundError = (error: unknown): error is NotFoundError => {
  return error instanceof NotFoundError;
};

export const isDatabaseError = (error: unknown): error is DatabaseError => {
  return error instanceof DatabaseError;
};

export const isExternalServiceError = (error: unknown): error is ExternalServiceError => {
  return error instanceof ExternalServiceError;
};

// Error Response Type
export interface ErrorResponse {
  code: string;
  message: string;
  statusCode: number;
  details?: unknown;
}

/**
 * Convert any error to a standardized error response
 */
export function toErrorResponse(error: unknown): ErrorResponse {
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
      message: error.message,
      statusCode: 500,
      details: {
        name: error.name,
        stack: error.stack,
      },
    };
  }

  return {
    code: 'UNKNOWN_ERROR',
    message: String(error),
    statusCode: 500,
  };
}

/**
 * Extract error message from various error types
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  if (typeof error === 'string') {
    return error;
  }

  if (error && typeof error === 'object') {
    const errorObj = error as Record<string, any>;
    return errorObj.message || errorObj.reason || errorObj.description || JSON.stringify(error);
  }

  return 'Unknown error occurred';
}

/**
 * Process error stack trace for logging
 */
export function processErrorStack(error: Error): {
  message: string;
  name: string;
  stackTrace: string[];
  isOperational: boolean;
  statusCode: number;
  firstFrame?: string;
} {
  const stackLines = error.stack?.split('\n').map(line => line.trim()) || [];
  const firstFrame = stackLines[1] || 'Unknown location';

  return {
    message: error.message,
    name: error.name,
    stackTrace: stackLines,
    isOperational: isAppError(error) ? error.isOperational : false,
    statusCode: isAppError(error) ? error.statusCode : 500,
    firstFrame,
  };
}
