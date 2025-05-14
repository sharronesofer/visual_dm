from typing import Any, Dict, List



  ERROR_CODES,
  ERROR_MESSAGES,
  ERROR_HTTP_STATUS,
  ERROR_CATEGORIES,
} from '../constants/errors'
  BaseError,
  ApiError,
  ValidationError,
  NetworkError,
  DatabaseError,
  CacheError,
} from '../types/errors'
/**
 * Create a base error
 */
function createError(
  category: keyof typeof ERROR_CATEGORIES,
  code: str,
  message?: str,
  details?: Record<string, any>
): BaseError {
  const error: BaseError = {
    code,
    message: message || getErrorMessage(category, code),
    category: ERROR_CATEGORIES[category],
    details,
  }
  logger.error('Error created:', { error })
  return error
}
/**
 * Create an API error
 */
function createApiError(
  code: keyof typeof ERROR_CODES.API,
  message?: str,
  details?: Record<string, any>
): ApiError {
  const errorCode = ERROR_CODES.API[code]
  const status = ERROR_HTTP_STATUS.API[errorCode]
  const error: ApiError = {
    code: errorCode,
    message: message || getErrorMessage('API', errorCode),
    category: ERROR_CATEGORIES.API,
    status,
    details,
  }
  logger.error('API error:', { error })
  return error
}
/**
 * Create a validation error
 */
function createValidationError(
  code: keyof typeof ERROR_CODES.VALIDATION,
  field: str,
  value?: Any,
  message?: str,
  details?: Record<string, any>
): ValidationError {
  const errorCode = ERROR_CODES.VALIDATION[code]
  const status = ERROR_HTTP_STATUS.VALIDATION[errorCode]
  const error: ValidationError = {
    code: errorCode,
    message: message || getErrorMessage('VALIDATION', errorCode),
    category: ERROR_CATEGORIES.VALIDATION,
    status,
    field,
    value,
    details,
  }
  logger.error('Validation error:', { error })
  return error
}
/**
 * Create a network error
 */
function createNetworkError(
  code: keyof typeof ERROR_CODES.NETWORK,
  url?: str,
  method?: str,
  message?: str,
  details?: Record<string, any>
): NetworkError {
  const errorCode = ERROR_CODES.NETWORK[code]
  const status = ERROR_HTTP_STATUS.NETWORK[errorCode]
  const error: NetworkError = {
    code: errorCode,
    message: message || getErrorMessage('NETWORK', errorCode),
    category: ERROR_CATEGORIES.NETWORK,
    status,
    url,
    method,
    details,
  }
  logger.error('Network error:', { error })
  return error
}
/**
 * Create a database error
 */
function createDatabaseError(
  code: keyof typeof ERROR_CODES.DATABASE,
  operation?: str,
  message?: str,
  details?: Record<string, any>
): DatabaseError {
  const errorCode = ERROR_CODES.DATABASE[code]
  const status = ERROR_HTTP_STATUS.DATABASE[errorCode]
  const error: DatabaseError = {
    code: errorCode,
    message: message || getErrorMessage('DATABASE', errorCode),
    category: ERROR_CATEGORIES.DATABASE,
    status,
    operation,
    details,
  }
  logger.error('Database error:', { error })
  return error
}
/**
 * Create a cache error
 */
function createCacheError(
  code: keyof typeof ERROR_CODES.CACHE,
  key?: str,
  operation?: str,
  message?: str,
  details?: Record<string, any>
): CacheError {
  const errorCode = ERROR_CODES.CACHE[code]
  const status = ERROR_HTTP_STATUS.CACHE[errorCode]
  const error: CacheError = {
    code: errorCode,
    message: message || getErrorMessage('CACHE', errorCode),
    category: ERROR_CATEGORIES.CACHE,
    status,
    key,
    operation,
    details,
  }
  logger.error('Cache error:', { error })
  return error
}
/**
 * Get error message for error code
 */
function getErrorMessage(
  category: keyof typeof ERROR_MESSAGES,
  code: str
): str {
  return ERROR_MESSAGES[category]?.[code] || 'An unknown error occurred'
}
/**
 * Check if error is an instance of BaseError
 */
function isBaseError(error: Any): error is BaseError {
  return (
    error && typeof error === 'object' && 'code' in error && 'message' in error
  )
}
/**
 * Check if error is an instance of ApiError
 */
function isApiError(error: Any): error is ApiError {
  return isBaseError(error) && error.category === ERROR_CATEGORIES.API
}
/**
 * Check if error is an instance of ValidationError
 */
function isValidationError(error: Any): error is ValidationError {
  return isBaseError(error) && error.category === ERROR_CATEGORIES.VALIDATION
}
/**
 * Check if error is an instance of NetworkError
 */
function isNetworkError(error: Any): error is NetworkError {
  return isBaseError(error) && error.category === ERROR_CATEGORIES.NETWORK
}
/**
 * Check if error is an instance of DatabaseError
 */
function isDatabaseError(error: Any): error is DatabaseError {
  return isBaseError(error) && error.category === ERROR_CATEGORIES.DATABASE
}
/**
 * Check if error is an instance of CacheError
 */
function isCacheError(error: Any): error is CacheError {
  return isBaseError(error) && error.category === ERROR_CATEGORIES.CACHE
}
/**
 * Error boundary decorator factory
 */
function ErrorBoundary(
  options: Dict[str, Any] = {}
) {
  return function (
    target: Any,
    propertyKey: str,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value
    descriptor.value = async function (...args: List[any]) {
      try {
        return await originalMethod.apply(this, args)
      } catch (error: Any) {
        if (options.logger) {
          options.logger(error)
        } else {
          logger.error('Error in method:', {
            method: propertyKey,
            error,
            args,
          })
        }
        if (options.fallback) {
          return options.fallback(error)
        }
        if (options.rethrow) {
          throw error
        }
        return null
      }
    }
    return descriptor
  }
}
/**
 * Retry decorator factory
 */
function Retry(
  options: Dict[str, Any] = {}
) {
  const {
    maxAttempts = 3,
    delay = 1000,
    backoff = 2,
    retryIf = error => true,
  } = options
  return function (
    target: Any,
    propertyKey: str,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value
    descriptor.value = async function (...args: List[any]) {
      let lastError: Any
      let attempt = 1
      let currentDelay = delay
      while (attempt <= maxAttempts) {
        try {
          return await originalMethod.apply(this, args)
        } catch (error: Any) {
          lastError = error
          if (!retryIf(error) || attempt === maxAttempts) {
            throw error
          }
          logger.warn('Retry attempt:', {
            method: propertyKey,
            attempt,
            maxAttempts,
            delay: currentDelay,
            error,
          })
          await new Promise(resolve => setTimeout(resolve, currentDelay))
          currentDelay *= backoff
          attempt++
        }
      }
      throw lastError
    }
    return descriptor
  }
}
/**
 * Timeout decorator factory
 */
function Timeout(ms: float) {
  return function (
    target: Any,
    propertyKey: str,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value
    descriptor.value = async function (...args: List[any]) {
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => {
          reject(
            createError(
              'API',
              ERROR_CODES.API.TIMEOUT,
              `Method ${propertyKey} timed out after ${ms}ms`
            )
          )
        }, ms)
      })
      return Promise.race([originalMethod.apply(this, args), timeoutPromise])
    }
    return descriptor
  }
}