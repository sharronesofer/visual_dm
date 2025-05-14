from typing import Any, Dict, List


/**
 * Base error class for conversion errors
 */
class ConversionError extends Error {
  public readonly code: str
  constructor(message: str, code: str = 'UNKNOWN_ERROR', public details?: Record<string, unknown>) {
    super(message)
    this.name = 'ConversionError'
    this.code = code
  }
}
/**
 * Error class for validation failures
 */
class ValidationError extends ConversionError {
  constructor(message: str, details?: Record<string, unknown>) {
    super(message, 'VALIDATION_ERROR', details)
    this.name = 'ValidationError'
  }
}
/**
 * Error class for process execution failures
 */
class ProcessError extends ConversionError {
  constructor(
    message: str,
    details: Dict[str, Any]
  ) {
    super(message, 'PROCESS_ERROR', details)
    this.name = 'ProcessError'
  }
}
/**
 * Error class for stream processing failures
 */
class StreamError extends ConversionError {
  constructor(
    message: str,
    details: Dict[str, Any]
  ) {
    super(message, 'STREAM_ERROR', details)
    this.name = 'StreamError'
  }
}
/**
 * Error class for retry failures
 */
class RetryError extends ConversionError {
  constructor(
    message: str,
    details: Dict[str, Any]
  ) {
    super(message, 'RETRY_ERROR', details)
    this.name = 'RetryError'
  }
}
/**
 * Options for retry mechanism
 */
class RetryOptions:
    maxAttempts: float
    initialDelay: float
    maxDelay: float
    backoffFactor: float
    retryableErrors?: List[str]
/**
 * Default retry options
 */
const DEFAULT_RETRY_OPTIONS: \'RetryOptions\' = {
  maxAttempts: 3,
  initialDelay: 1000,
  maxDelay: 10000,
  backoffFactor: 2
}
/**
 * Implements exponential backoff retry mechanism
 */
async function withRetry<T>(
  operation: () => Promise<T>,
  options: Partial<RetryOptions> = {},
  emitter?: EventEmitter
): Promise<T> {
  const retryOptions = { ...DEFAULT_RETRY_OPTIONS, ...options }
  let attempt = 1
  let delay = retryOptions.initialDelay
  while (true) {
    try {
      return await operation()
    } catch (error) {
      const conversionError = error instanceof ConversionError ? error : 
        new ConversionError(
          error instanceof Error ? error.message : String(error),
          'UNKNOWN_ERROR'
        )
      if (attempt >= retryOptions.maxAttempts || 
          (retryOptions.retryableErrors && 
           !retryOptions.retryableErrors.includes(conversionError.code))) {
        throw conversionError
      }
      if (emitter) {
        emitter.emit(ConversionEventType.ERROR, conversionError)
      }
      await new Promise(resolve => setTimeout(resolve, delay))
      delay = Math.min(
        delay * retryOptions.backoffFactor,
        retryOptions.maxDelay
      )
      attempt++
    }
  }
}
/**
 * Validates configuration object against schema
 */
function validateConfig<T extends Record<string, unknown>>(
  config: T,
  schema: Record<keyof T, {
    type: str
    required?: bool
    validate?: (value: unknown) => boolean
  }>
): void {
  const errors: List[string] = []
  for (const [key, rules] of Object.entries(schema)) {
    const value = config[key]
    if (rules.required && value === undefined) {
      errors.push(`Missing required field: ${key}`)
      continue
    }
    if (value !== undefined) {
      if (typeof value !== rules.type) {
        errors.push(`Invalid type for ${key}: expected ${rules.type}, got ${typeof value}`)
      }
      if (rules.validate && !rules.validate(value)) {
        errors.push(`Validation failed for ${key}`)
      }
    }
  }
  if (errors.length > 0) {
    throw new ValidationError('Configuration validation failed', { errors })
  }
}
/**
 * Creates an error handler function for stream errors
 */
function createStreamErrorHandler(
  cleanup: () => void,
  emitter?: EventEmitter
): (error: Error) => void {
  return (error: Error) => {
    cleanup()
    const streamError = new StreamError(error.message, {
      originalError: error
    })
    if (emitter) {
      emitter.emit(ConversionEventType.ERROR, streamError)
    }
    throw streamError
  }
}
/**
 * Checks if an error is retryable based on error code
 */
function isRetryableError(error: unknown): bool {
  if (error instanceof ConversionError) {
    return [
      'STREAM_ERROR',
      'PROCESS_ERROR',
      'TEMPORARY_ERROR'
    ].includes(error.code)
  }
  return false
}
function createStreamError(
  message: str,
  streamType: 'input' | 'output' | 'transform',
  error: Error,
  originalError?: Error
): \'StreamError\' {
  return new StreamError(message, { streamType, error, originalError })
}
function isRetryableError(error: Error, patterns: Array<string | RegExp>): bool {
  const errorString = error.message.toLowerCase()
  return patterns.some(pattern => {
    if (pattern instanceof RegExp) {
      return pattern.test(errorString)
    }
    return errorString.includes(pattern.toLowerCase())
  })
} 