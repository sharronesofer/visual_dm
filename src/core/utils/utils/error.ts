import {
  ERROR_CODES,
  ERROR_MESSAGES,
  ERROR_HTTP_STATUS,
  ERROR_CATEGORIES,
} from '../constants/errors';
import {
  BaseError,
  ApiError,
  ValidationError,
  NetworkError,
  DatabaseError,
  CacheError,
} from '../types/errors';
import { logger } from './logger';

/**
 * Create a base error
 */
export function createError(
  category: keyof typeof ERROR_CATEGORIES,
  code: string,
  message?: string,
  details?: Record<string, any>
): BaseError {
  const error: BaseError = {
    code,
    message: message || getErrorMessage(category, code),
    category: ERROR_CATEGORIES[category],
    details,
  };

  logger.error('Error created:', { error });
  return error;
}

/**
 * Create an API error
 */
export function createApiError(
  code: keyof typeof ERROR_CODES.API,
  message?: string,
  details?: Record<string, any>
): ApiError {
  const errorCode = ERROR_CODES.API[code];
  const status = ERROR_HTTP_STATUS.API[errorCode];

  const error: ApiError = {
    code: errorCode,
    message: message || getErrorMessage('API', errorCode),
    category: ERROR_CATEGORIES.API,
    status,
    details,
  };

  logger.error('API error:', { error });
  return error;
}

/**
 * Create a validation error
 */
export function createValidationError(
  code: keyof typeof ERROR_CODES.VALIDATION,
  field: string,
  value?: any,
  message?: string,
  details?: Record<string, any>
): ValidationError {
  const errorCode = ERROR_CODES.VALIDATION[code];
  const status = ERROR_HTTP_STATUS.VALIDATION[errorCode];

  const error: ValidationError = {
    code: errorCode,
    message: message || getErrorMessage('VALIDATION', errorCode),
    category: ERROR_CATEGORIES.VALIDATION,
    status,
    field,
    value,
    details,
  };

  logger.error('Validation error:', { error });
  return error;
}

/**
 * Create a network error
 */
export function createNetworkError(
  code: keyof typeof ERROR_CODES.NETWORK,
  url?: string,
  method?: string,
  message?: string,
  details?: Record<string, any>
): NetworkError {
  const errorCode = ERROR_CODES.NETWORK[code];
  const status = ERROR_HTTP_STATUS.NETWORK[errorCode];

  const error: NetworkError = {
    code: errorCode,
    message: message || getErrorMessage('NETWORK', errorCode),
    category: ERROR_CATEGORIES.NETWORK,
    status,
    url,
    method,
    details,
  };

  logger.error('Network error:', { error });
  return error;
}

/**
 * Create a database error
 */
export function createDatabaseError(
  code: keyof typeof ERROR_CODES.DATABASE,
  operation?: string,
  message?: string,
  details?: Record<string, any>
): DatabaseError {
  const errorCode = ERROR_CODES.DATABASE[code];
  const status = ERROR_HTTP_STATUS.DATABASE[errorCode];

  const error: DatabaseError = {
    code: errorCode,
    message: message || getErrorMessage('DATABASE', errorCode),
    category: ERROR_CATEGORIES.DATABASE,
    status,
    operation,
    details,
  };

  logger.error('Database error:', { error });
  return error;
}

/**
 * Create a cache error
 */
export function createCacheError(
  code: keyof typeof ERROR_CODES.CACHE,
  key?: string,
  operation?: string,
  message?: string,
  details?: Record<string, any>
): CacheError {
  const errorCode = ERROR_CODES.CACHE[code];
  const status = ERROR_HTTP_STATUS.CACHE[errorCode];

  const error: CacheError = {
    code: errorCode,
    message: message || getErrorMessage('CACHE', errorCode),
    category: ERROR_CATEGORIES.CACHE,
    status,
    key,
    operation,
    details,
  };

  logger.error('Cache error:', { error });
  return error;
}

/**
 * Get error message for error code
 */
function getErrorMessage(
  category: keyof typeof ERROR_MESSAGES,
  code: string
): string {
  return ERROR_MESSAGES[category]?.[code] || 'An unknown error occurred';
}

/**
 * Check if error is an instance of BaseError
 */
export function isBaseError(error: any): error is BaseError {
  return (
    error && typeof error === 'object' && 'code' in error && 'message' in error
  );
}

/**
 * Check if error is an instance of ApiError
 */
export function isApiError(error: any): error is ApiError {
  return isBaseError(error) && error.category === ERROR_CATEGORIES.API;
}

/**
 * Check if error is an instance of ValidationError
 */
export function isValidationError(error: any): error is ValidationError {
  return isBaseError(error) && error.category === ERROR_CATEGORIES.VALIDATION;
}

/**
 * Check if error is an instance of NetworkError
 */
export function isNetworkError(error: any): error is NetworkError {
  return isBaseError(error) && error.category === ERROR_CATEGORIES.NETWORK;
}

/**
 * Check if error is an instance of DatabaseError
 */
export function isDatabaseError(error: any): error is DatabaseError {
  return isBaseError(error) && error.category === ERROR_CATEGORIES.DATABASE;
}

/**
 * Check if error is an instance of CacheError
 */
export function isCacheError(error: any): error is CacheError {
  return isBaseError(error) && error.category === ERROR_CATEGORIES.CACHE;
}

/**
 * Error boundary decorator factory
 */
export function ErrorBoundary(
  options: {
    fallback?: (error: Error) => any;
    rethrow?: boolean;
    logger?: (error: Error) => void;
  } = {}
) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      try {
        return await originalMethod.apply(this, args);
      } catch (error: any) {
        // Log the error
        if (options.logger) {
          options.logger(error);
        } else {
          logger.error('Error in method:', {
            method: propertyKey,
            error,
            args,
          });
        }

        // Handle the error
        if (options.fallback) {
          return options.fallback(error);
        }

        // Rethrow if specified
        if (options.rethrow) {
          throw error;
        }

        // Return null by default
        return null;
      }
    };

    return descriptor;
  };
}

/**
 * Retry decorator factory
 */
export function Retry(
  options: {
    maxAttempts?: number;
    delay?: number;
    backoff?: number;
    retryIf?: (error: any) => boolean;
  } = {}
) {
  const {
    maxAttempts = 3,
    delay = 1000,
    backoff = 2,
    retryIf = error => true,
  } = options;

  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      let lastError: any;
      let attempt = 1;
      let currentDelay = delay;

      while (attempt <= maxAttempts) {
        try {
          return await originalMethod.apply(this, args);
        } catch (error: any) {
          lastError = error;

          if (!retryIf(error) || attempt === maxAttempts) {
            throw error;
          }

          logger.warn('Retry attempt:', {
            method: propertyKey,
            attempt,
            maxAttempts,
            delay: currentDelay,
            error,
          });

          await new Promise(resolve => setTimeout(resolve, currentDelay));
          currentDelay *= backoff;
          attempt++;
        }
      }

      throw lastError;
    };

    return descriptor;
  };
}

/**
 * Timeout decorator factory
 */
export function Timeout(ms: number) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => {
          reject(
            createError(
              'API',
              ERROR_CODES.API.TIMEOUT,
              `Method ${propertyKey} timed out after ${ms}ms`
            )
          );
        }, ms);
      });

      return Promise.race([originalMethod.apply(this, args), timeoutPromise]);
    };

    return descriptor;
  };
}
