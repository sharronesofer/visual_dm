/**
 * Error handling system for the media management application
 * @module errors
 */

import { getRequestContext } from '../middleware/requestContext';

/**
 * Environment detection
 */
const isDevelopment = process.env.NODE_ENV === 'development';

/**
 * Error category types for better error classification
 */
export enum ErrorCategory {
  CLIENT_ERROR = 'CLIENT_ERROR',
  SERVER_ERROR = 'SERVER_ERROR',
  NETWORK_ERROR = 'NETWORK_ERROR',
  SECURITY_ERROR = 'SECURITY_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  RESOURCE_ERROR = 'RESOURCE_ERROR',
  DATA_ERROR = 'DATA_ERROR',
  OPERATIONAL_ERROR = 'OPERATIONAL_ERROR',
  PROGRAMMING_ERROR = 'PROGRAMMING_ERROR',
}

/**
 * Error severity levels
 */
export enum ErrorSeverity {
  CRITICAL = 'CRITICAL',
  HIGH = 'HIGH',
  MEDIUM = 'MEDIUM',
  LOW = 'LOW',
}

/**
 * Error context interface to enhance errors with additional information
 */
export interface ErrorContext {
  /** Request ID for correlation */
  requestId?: string;
  /** User ID if available */
  userId?: string | number;
  /** Resource information */
  resource?: { type: string; id?: string | number };
  /** Additional contextual data */
  data?: Record<string, unknown>;
  /** Error location (file, function, etc.) */
  location?: string;
  /** Timestamp when error occurred */
  timestamp?: string;
  /** Original error if this wraps another error */
  originalError?: Error;
}

/**
 * Base error class for application-specific errors with enhanced contextual capabilities
 * Supports error chaining, context merging, and serialization.
 */
export class AppError extends Error {
  /** Unique error code */
  public code: string;
  /** HTTP status code */
  public statusCode: number;
  /** Additional error details */
  public details?: unknown;
  /** Indicates if the error is expected as part of normal operation */
  public isOperational: boolean;
  /** Error category for classification */
  public category: ErrorCategory;
  /** Error severity level */
  public severity: ErrorSeverity;
  /** Error context with additional information */
  public context: ErrorContext;
  /** Optional error cause for chaining */
  public cause?: Error;

  constructor(
    message: string,
    code: string,
    statusCode: number = 500,
    details?: unknown,
    isOperational: boolean = true,
    category: ErrorCategory = ErrorCategory.SERVER_ERROR,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    context: ErrorContext = {},
    cause?: Error
  ) {
    super(message);
    this.name = this.constructor.name;
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;
    this.isOperational = isOperational;
    this.category = category;
    this.severity = severity;
    this.context = {
      ...context,
      timestamp: context.timestamp || new Date().toISOString(),
    };
    if (cause) this.cause = cause;
    // Try to get request ID from request context if available
    try {
      const requestContext = getRequestContext();
      if (requestContext?.requestId && !this.context.requestId) {
        this.context.requestId = requestContext.requestId;
      }
    } catch (e) { }
    // Capture stack trace
    Error.captureStackTrace(this, this.constructor);
  }

  /**
   * Adds additional context to the error
   */
  addContext(context: Partial<ErrorContext>): this {
    this.context = {
      ...this.context,
      ...context,
    };
    return this;
  }

  /**
   * Converts error to JSON representation, handling nested errors and circular references
   */
  toJSON() {
    const seen = new WeakSet();
    const serialize = (obj: any): any => {
      if (obj && typeof obj === 'object') {
        if (seen.has(obj)) return '[Circular]';
        seen.add(obj);
        const out: any = {};
        for (const key of Object.keys(obj)) {
          if (key === 'stack' && !isDevelopment) continue;
          out[key] = serialize(obj[key]);
        }
        return out;
      }
      return obj;
    };
    return serialize({
      name: this.name,
      code: this.code,
      message: this.message,
      statusCode: this.statusCode,
      details: this.details,
      isOperational: this.isOperational,
      category: this.category,
      severity: this.severity,
      context: this.context,
      stack: isDevelopment ? this.stack : undefined,
      cause: this.cause ? (typeof (this.cause as any).toJSON === 'function' ? (this.cause as any).toJSON() : {
        name: this.cause.name,
        message: this.cause.message,
        stack: isDevelopment ? this.cause.stack : undefined,
      }) : undefined,
    });
  }

  /**
   * Converts error to API error response format
   */
  toErrorResponse(includeDetails: boolean = isDevelopment): ErrorResponse {
    return {
      error: {
        code: this.code,
        message: this.message, // TODO: i18n/message template support
        statusCode: this.statusCode,
        details: includeDetails ? this.details : undefined,
        requestId: this.context.requestId,
        timestamp: this.context.timestamp || new Date().toISOString(),
      },
    };
  }

  /**
   * Creates a localized error message (placeholder for i18n integration)
   */
  localizeMessage(locale: string = 'en'): string {
    // TODO: Integrate with i18n/message template system
    return this.message;
  }

  /**
   * Static: Convert unknown error to AppError
   */
  static fromUnknown(error: unknown, context: ErrorContext = {}): AppError {
    if (error instanceof AppError) return error;
    if (error instanceof Error) {
      return new AppError(error.message, 'UNKNOWN_ERROR', 500, undefined, false, ErrorCategory.SERVER_ERROR, ErrorSeverity.MEDIUM, context, error);
    }
    return new AppError('Unknown error', 'UNKNOWN_ERROR', 500, error, false, ErrorCategory.SERVER_ERROR, ErrorSeverity.MEDIUM, context);
  }
}

/**
 * Error thrown when request validation fails
 */
export class ValidationError extends AppError {
  constructor(
    message: string = 'Validation failed',
    public errors: Record<string, string[]>,
    context: ErrorContext = {}
  ) {
    super(
      message,
      'VALIDATION_ERROR',
      400,
      errors,
      true,
      ErrorCategory.VALIDATION_ERROR,
      ErrorSeverity.MEDIUM,
      context
    );
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
    message?: string,
    context: ErrorContext = {}
  ) {
    super(
      message || `${resourceType} with ID ${resourceId} not found`,
      'NOT_FOUND',
      404,
      undefined,
      true,
      ErrorCategory.RESOURCE_ERROR,
      ErrorSeverity.LOW,
      {
        ...context,
        resource: { type: resourceType, id: resourceId }
      }
    );
    this.name = 'NotFoundError';
  }
}

/**
 * Error thrown when user is not authenticated
 */
export class AuthenticationError extends AppError {
  constructor(message: string = 'Authentication required', details?: unknown, context: ErrorContext = {}) {
    super(
      message,
      'UNAUTHENTICATED',
      401,
      details,
      true,
      ErrorCategory.SECURITY_ERROR,
      ErrorSeverity.MEDIUM,
      context
    );
    this.name = 'AuthenticationError';
  }
}

/**
 * Error thrown when user lacks required permissions
 */
export class ForbiddenError extends AppError {
  constructor(message: string = 'Permission denied', details?: unknown, context: ErrorContext = {}) {
    super(
      message,
      'FORBIDDEN',
      403,
      details,
      true,
      ErrorCategory.SECURITY_ERROR,
      ErrorSeverity.MEDIUM,
      context
    );
    this.name = 'ForbiddenError';
  }
}

/**
 * Error thrown when a conflict occurs (e.g., duplicate resource)
 */
export class ConflictError extends AppError {
  constructor(
    message: string,
    public conflictingResource?: { type: string; id: string | number },
    context: ErrorContext = {}
  ) {
    super(
      message,
      'CONFLICT',
      409,
      conflictingResource,
      true,
      ErrorCategory.DATA_ERROR,
      ErrorSeverity.MEDIUM,
      {
        ...context,
        resource: conflictingResource ? { type: conflictingResource.type, id: conflictingResource.id } : undefined
      }
    );
    this.name = 'ConflictError';
  }
}

/**
 * Error thrown when rate limit is exceeded
 */
export class RateLimitError extends AppError {
  constructor(
    message: string = 'Rate limit exceeded',
    public retryAfter?: number,
    context: ErrorContext = {}
  ) {
    super(
      message,
      'RATE_LIMIT',
      429,
      { retryAfter },
      true,
      ErrorCategory.CLIENT_ERROR,
      ErrorSeverity.LOW,
      context
    );
    this.name = 'RateLimitError';
  }
}

/**
 * Error thrown when service is temporarily unavailable
 */
export class ServiceUnavailableError extends AppError {
  constructor(
    message: string = 'Service temporarily unavailable',
    public retryAfter?: number,
    context: ErrorContext = {}
  ) {
    super(
      message,
      'SERVICE_UNAVAILABLE',
      503,
      { retryAfter },
      true,
      ErrorCategory.SERVER_ERROR,
      ErrorSeverity.HIGH,
      context
    );
    this.name = 'ServiceUnavailableError';
  }
}

/**
 * Error thrown for invalid request parameters
 */
export class BadRequestError extends AppError {
  constructor(message: string, details?: unknown, context: ErrorContext = {}) {
    super(
      message,
      'BAD_REQUEST',
      400,
      details,
      true,
      ErrorCategory.CLIENT_ERROR,
      ErrorSeverity.LOW,
      context
    );
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
    details?: Record<string, unknown>,
    context: ErrorContext = {}
  ) {
    super(
      message,
      'DATABASE_ERROR',
      500,
      { operation, entity, ...(details || {}) },
      false,
      ErrorCategory.DATA_ERROR,
      ErrorSeverity.HIGH,
      context
    );
    this.name = 'DatabaseError';
  }
}

/**
 * Error thrown for external service failures
 */
export class ExternalServiceError extends AppError {
  constructor(
    message: string,
    public service: string,
    details?: Record<string, unknown>,
    context: ErrorContext = {}
  ) {
    super(
      message,
      'EXTERNAL_SERVICE_ERROR',
      502,
      { service, ...(details || {}) },
      true,
      ErrorCategory.NETWORK_ERROR,
      ErrorSeverity.HIGH,
      context
    );
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
    details?: Record<string, unknown>,
    context: ErrorContext = {}
  ) {
    super(
      message,
      'FILE_SYSTEM_ERROR',
      500,
      { operation, path, ...(details || {}) },
      false,
      ErrorCategory.SERVER_ERROR,
      ErrorSeverity.HIGH,
      context
    );
    this.name = 'FileSystemError';
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
    details?: unknown,
    context: ErrorContext = {}
  ) {
    super(
      message,
      'MEDIA_PROCESSING_ERROR',
      500,
      { mediaType, operation, ...(typeof details === 'object' && details ? details : {}) },
      true,
      ErrorCategory.RESOURCE_ERROR,
      ErrorSeverity.MEDIUM,
      context
    );
    this.name = 'MediaProcessingError';
  }
}

/**
 * New error class for configuration errors
 */
export class ConfigurationError extends AppError {
  constructor(
    message: string,
    public configKey?: string,
    details?: unknown,
    context: ErrorContext = {}
  ) {
    super(
      message,
      'CONFIGURATION_ERROR',
      500,
      { configKey, ...(typeof details === 'object' && details ? details : {}) },
      false,
      ErrorCategory.PROGRAMMING_ERROR,
      ErrorSeverity.CRITICAL,
      context
    );
    this.name = 'ConfigurationError';
  }
}

/**
 * New error class for timeout errors
 */
export class TimeoutError extends AppError {
  constructor(
    message: string = 'Operation timed out',
    public timeoutMs?: number,
    details?: unknown,
    context: ErrorContext = {}
  ) {
    super(
      message,
      'TIMEOUT_ERROR',
      504,
      { timeoutMs, ...(typeof details === 'object' && details ? details : {}) },
      true,
      ErrorCategory.NETWORK_ERROR,
      ErrorSeverity.MEDIUM,
      context
    );
    this.name = 'TimeoutError';
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

// Additional type guards for error categories
export const isClientError = (error: unknown): boolean => {
  return isAppError(error) && error.category === ErrorCategory.CLIENT_ERROR;
};

export const isServerError = (error: unknown): boolean => {
  return isAppError(error) && error.category === ErrorCategory.SERVER_ERROR;
};

export const isSecurityError = (error: unknown): boolean => {
  return isAppError(error) && error.category === ErrorCategory.SECURITY_ERROR;
};

export const isDataError = (error: unknown): boolean => {
  return isAppError(error) && error.category === ErrorCategory.DATA_ERROR;
};

export const isOperationalError = (error: unknown): boolean => {
  return isAppError(error) && error.isOperational;
};

export const isProgrammingError = (error: unknown): boolean => {
  return isAppError(error) && !error.isOperational;
};

// Error Response Type
export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    statusCode: number;
    details?: unknown;
    requestId?: string;
    timestamp: string;
  }
}

/**
 * Convert any error to a standardized error response
 */
export function toErrorResponse(error: unknown, includeDetails: boolean = isDevelopment): ErrorResponse {
  const timestamp = new Date().toISOString();
  let requestId: string | undefined;

  try {
    const requestContext = getRequestContext();
    requestId = requestContext?.requestId;
  } catch (e) {
    // If request context isn't available, continue without requestId
  }

  if (isAppError(error)) {
    return {
      error: {
        code: error.code,
        message: error.message,
        statusCode: error.statusCode,
        details: includeDetails ? error.details : undefined,
        requestId: error.context.requestId || requestId,
        timestamp: error.context.timestamp || timestamp,
      }
    };
  }

  if (error instanceof Error) {
    return {
      error: {
        code: 'INTERNAL_ERROR',
        message: isDevelopment ? error.message : 'An internal error occurred',
        statusCode: 500,
        details: includeDetails ? {
          name: error.name,
          stack: error.stack,
        } : undefined,
        requestId,
        timestamp,
      }
    };
  }

  return {
    error: {
      code: 'UNKNOWN_ERROR',
      message: isDevelopment ? String(error) : 'An unknown error occurred',
      statusCode: 500,
      requestId,
      timestamp,
    }
  };
}

/**
 * Safe serialization of error objects to prevent circular references
 */
export function safeStringify(obj: unknown, space?: number): string {
  const cache = new Set();
  return JSON.stringify(obj, (key, value) => {
    if (typeof value === 'object' && value !== null) {
      if (cache.has(value)) {
        return '[Circular Reference]';
      }
      cache.add(value);
    }
    return value;
  }, space);
}

/**
 * Extract error message from any error object
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return String(error);
}

/**
 * Process error stack to extract useful debugging information
 */
export function processErrorStack(error: Error): {
  message: string;
  name: string;
  stackTrace: string[];
  isOperational: boolean;
  statusCode: number;
  firstFrame?: string;
} {
  const stackTrace = error.stack?.split('\n').map(line => line.trim()) || [];

  return {
    message: error.message,
    name: error.name,
    stackTrace: stackTrace.slice(1),
    isOperational: isAppError(error) ? error.isOperational : false,
    statusCode: isAppError(error) ? error.statusCode : 500,
    firstFrame: stackTrace.length > 1 ? stackTrace[1] : undefined,
  };
}

/**
 * POI Error Categories
 */
export enum POIErrorCategory {
  DATA_VALIDATION = 'DATA_VALIDATION',
  INTEGRATION = 'INTEGRATION',
  PERSISTENCE = 'PERSISTENCE',
  CONCURRENCY = 'CONCURRENCY',
  AUTHORIZATION = 'AUTHORIZATION',
  UNKNOWN = 'UNKNOWN',
}

/**
 * POI Error Severity Levels
 */
export enum POISeverityLevel {
  CRITICAL = 'CRITICAL',
  HIGH = 'HIGH',
  MEDIUM = 'MEDIUM',
  LOW = 'LOW',
}

/**
 * POI Error Codes
 * (Extend as needed for new error scenarios)
 */
export enum POIErrorCode {
  POI_VALIDATION = 'POI_001',
  POI_INTEGRATION = 'POI_002',
  POI_PERSISTENCE = 'POI_003',
  POI_CONCURRENCY = 'POI_004',
  POI_AUTHORIZATION = 'POI_005',
  POI_UNKNOWN = 'POI_999',
}

/**
 * Context information for POI errors
 */
export interface POIErrorContext {
  poiId?: string | number;
  operationType?: string;
  timestamp?: string;
  userId?: string | number;
  additionalData?: Record<string, unknown>;
}

/**
 * Base class for POI-specific exceptions
 */
export class POIException extends AppError {
  public errorCategory: POIErrorCategory;
  public severityLevel: POISeverityLevel;
  public errorCode: POIErrorCode;
  public context: POIErrorContext;

  constructor(
    message: string,
    errorCategory: POIErrorCategory,
    severityLevel: POISeverityLevel,
    errorCode: POIErrorCode,
    context: POIErrorContext = {},
    statusCode: number = 500,
    details?: unknown
  ) {
    super(message, errorCode, statusCode, details);
    this.name = this.constructor.name;
    this.errorCategory = errorCategory;
    this.severityLevel = severityLevel;
    this.errorCode = errorCode;
    this.context = context;
  }

  toJSON() {
    return {
      ...super.toJSON(),
      errorCategory: this.errorCategory,
      severityLevel: this.severityLevel,
      errorCode: this.errorCode,
      context: this.context,
    };
  }
}

/**
 * POI Validation Exception
 */
export class POIValidationException extends POIException {
  constructor(
    message: string,
    context: POIErrorContext = {},
    details?: unknown
  ) {
    super(
      message,
      POIErrorCategory.DATA_VALIDATION,
      POISeverityLevel.HIGH,
      POIErrorCode.POI_VALIDATION,
      context,
      400,
      details
    );
    this.name = 'POIValidationException';
  }
}

/**
 * POI Integration Exception
 */
export class POIIntegrationException extends POIException {
  constructor(
    message: string,
    context: POIErrorContext = {},
    details?: unknown
  ) {
    super(
      message,
      POIErrorCategory.INTEGRATION,
      POISeverityLevel.CRITICAL,
      POIErrorCode.POI_INTEGRATION,
      context,
      502,
      details
    );
    this.name = 'POIIntegrationException';
  }
}

/**
 * POI Persistence Exception
 */
export class POIPersistenceException extends POIException {
  constructor(
    message: string,
    context: POIErrorContext = {},
    details?: unknown
  ) {
    super(
      message,
      POIErrorCategory.PERSISTENCE,
      POISeverityLevel.CRITICAL,
      POIErrorCode.POI_PERSISTENCE,
      context,
      500,
      details
    );
    this.name = 'POIPersistenceException';
  }
}

/**
 * POI Concurrency Exception
 */
export class POIConcurrencyException extends POIException {
  constructor(
    message: string,
    context: POIErrorContext = {},
    details?: unknown
  ) {
    super(
      message,
      POIErrorCategory.CONCURRENCY,
      POISeverityLevel.HIGH,
      POIErrorCode.POI_CONCURRENCY,
      context,
      409,
      details
    );
    this.name = 'POIConcurrencyException';
  }
}

/**
 * POI Authorization Exception
 */
export class POIAuthorizationException extends POIException {
  constructor(
    message: string,
    context: POIErrorContext = {},
    details?: unknown
  ) {
    super(
      message,
      POIErrorCategory.AUTHORIZATION,
      POISeverityLevel.HIGH,
      POIErrorCode.POI_AUTHORIZATION,
      context,
      403,
      details
    );
    this.name = 'POIAuthorizationException';
  }
}

/**
 * POI Unknown Exception
 */
export class POIUnknownException extends POIException {
  constructor(
    message: string,
    context: POIErrorContext = {},
    details?: unknown
  ) {
    super(
      message,
      POIErrorCategory.UNKNOWN,
      POISeverityLevel.MEDIUM,
      POIErrorCode.POI_UNKNOWN,
      context,
      500,
      details
    );
    this.name = 'POIUnknownException';
  }
}
