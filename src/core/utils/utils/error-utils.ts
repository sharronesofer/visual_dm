import {
  BaseError,
  ApiError,
  ValidationError,
  DatabaseError,
} from '../types/errors';

/**
 * Standard error format
 */
interface FormattedError {
  message: string;
  code?: string;
  stack?: string;
  details?: Record<string, any>;
}

/**
 * WeakMap to track visited objects during serialization
 */
const visitedObjects = new WeakMap<object, boolean>();

/**
 * Format any error into a standardized structure
 */
export function formatError(error: unknown): FormattedError {
  if (error instanceof Error && 'code' in error && 'details' in error) {
    const baseError = error as BaseError & Error;
    return {
      message: baseError.message,
      code: baseError.code,
      stack:
        process.env.NODE_ENV === 'development' ? baseError.stack : undefined,
      details: baseError.details,
    };
  }

  if (error instanceof Error) {
    return {
      message: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined,
    };
  }

  if (typeof error === 'string') {
    return { message: error };
  }

  return {
    message: 'Unknown error occurred',
    details: error ? { originalError: error } : undefined,
  };
}

/**
 * Safely serialize an error object handling circular references
 */
export function serializeError(error: unknown): Record<string, any> {
  visitedObjects.set({}, false); // Initialize with dummy object to avoid clear

  function serialize(obj: any): any {
    if (obj === null || typeof obj !== 'object') {
      return obj;
    }

    if (visitedObjects.has(obj)) {
      return '[Circular Reference]';
    }

    visitedObjects.set(obj, true);

    if (obj instanceof Error) {
      const serialized: Record<string, any> = {
        name: obj.name,
        message: obj.message,
        stack: process.env.NODE_ENV === 'development' ? obj.stack : undefined,
      };

      // Get all enumerable properties
      const errorProps = Object.getOwnPropertyNames(obj);
      errorProps.forEach(key => {
        if (key !== 'stack') {
          // Skip stack as we handled it above
          const value = (obj as any)[key];
          serialized[key] = serialize(value);
        }
      });

      return serialized;
    }

    if (Array.isArray(obj)) {
      return obj.map(item => serialize(item));
    }

    const result: Record<string, any> = {};
    Object.keys(obj).forEach(key => {
      result[key] = serialize(obj[key]);
    });

    return result;
  }

  return serialize(error);
}

/**
 * Parse error to extract useful information based on error type
 */
export function parseError(error: unknown): Record<string, any> {
  if (error instanceof Error) {
    if ('statusCode' in error && 'data' in error) {
      const apiError = error as ApiError;
      return {
        type: 'API_ERROR',
        status: apiError.statusCode,
        message: apiError.message,
        data: apiError.data,
      };
    }

    if ('errors' in error) {
      const validationError = error as ValidationError;
      return {
        type: 'VALIDATION_ERROR',
        message: validationError.message,
        errors: validationError.errors,
      };
    }

    if ('query' in error && 'params' in error && 'code' in error) {
      const dbError = error as unknown as DatabaseError;
      return {
        type: 'DATABASE_ERROR',
        message: dbError.message,
        query: dbError.query,
        params: dbError.params,
      };
    }

    return {
      type: 'ERROR',
      name: error.name,
      message: error.message,
    };
  }

  return {
    type: 'UNKNOWN_ERROR',
    message: getErrorMessage(error),
  };
}

/**
 * Extract consistent error message from various error objects
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
    return (
      errorObj.message ||
      errorObj.reason ||
      errorObj.description ||
      JSON.stringify(error)
    );
  }

  return 'Unknown error occurred';
}

/**
 * Sanitize error object for client response by removing sensitive information
 */
export function sanitizeErrorForClient(error: unknown): Record<string, any> {
  const sanitized = serializeError(error);

  // Remove sensitive information
  const sensitiveKeys = [
    'password',
    'token',
    'secret',
    'key',
    'connection',
    'auth',
    'credentials',
  ];

  function sanitizeObject(obj: Record<string, any>): void {
    Object.keys(obj).forEach(key => {
      // Check for sensitive keys
      if (
        sensitiveKeys.some(sensitive => key.toLowerCase().includes(sensitive))
      ) {
        obj[key] = '[REDACTED]';
        return;
      }

      // Recursively sanitize nested objects
      if (obj[key] && typeof obj[key] === 'object') {
        sanitizeObject(obj[key]);
      }
    });
  }

  sanitizeObject(sanitized);

  // Remove stack traces in production
  if (process.env.NODE_ENV === 'production') {
    delete sanitized.stack;
    if (sanitized.details) {
      delete sanitized.details.stack;
    }
  }

  return sanitized;
}
