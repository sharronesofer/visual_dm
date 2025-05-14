import { EventEmitter } from 'events';
import { ConversionEventType, ConversionStage } from '../types';

/**
 * Base error class for conversion errors
 */
export class ConversionError extends Error {
  public readonly code: string;

  constructor(message: string, code: string = 'UNKNOWN_ERROR', public details?: Record<string, unknown>) {
    super(message);
    this.name = 'ConversionError';
    this.code = code;
  }
}

/**
 * Error class for validation failures
 */
export class ValidationError extends ConversionError {
  constructor(message: string, details?: Record<string, unknown>) {
    super(message, 'VALIDATION_ERROR', details);
    this.name = 'ValidationError';
  }
}

/**
 * Error class for process execution failures
 */
export class ProcessError extends ConversionError {
  constructor(
    message: string,
    details: {
      command: string;
      args: string[];
      error?: string;
      exitCode?: number;
    }
  ) {
    super(message, 'PROCESS_ERROR', details);
    this.name = 'ProcessError';
  }
}

/**
 * Error class for stream processing failures
 */
export class StreamError extends ConversionError {
  constructor(
    message: string,
    details: {
      streamType: 'input' | 'output' | 'transform';
      error: Error;
      originalError?: Error;
    }
  ) {
    super(message, 'STREAM_ERROR', details);
    this.name = 'StreamError';
  }
}

/**
 * Error class for retry failures
 */
export class RetryError extends ConversionError {
  constructor(
    message: string,
    details: {
      stage: ConversionStage;
      maxAttempts: number;
      lastError: string;
    }
  ) {
    super(message, 'RETRY_ERROR', details);
    this.name = 'RetryError';
  }
}

/**
 * Options for retry mechanism
 */
export interface RetryOptions {
  maxAttempts: number;
  initialDelay: number;
  maxDelay: number;
  backoffFactor: number;
  retryableErrors?: string[];
}

/**
 * Default retry options
 */
export const DEFAULT_RETRY_OPTIONS: RetryOptions = {
  maxAttempts: 3,
  initialDelay: 1000,
  maxDelay: 10000,
  backoffFactor: 2
};

/**
 * Implements exponential backoff retry mechanism
 */
export async function withRetry<T>(
  operation: () => Promise<T>,
  options: Partial<RetryOptions> = {},
  emitter?: EventEmitter
): Promise<T> {
  const retryOptions = { ...DEFAULT_RETRY_OPTIONS, ...options };
  let attempt = 1;
  let delay = retryOptions.initialDelay;

  while (true) {
    try {
      return await operation();
    } catch (error) {
      const conversionError = error instanceof ConversionError ? error : 
        new ConversionError(
          error instanceof Error ? error.message : String(error),
          'UNKNOWN_ERROR'
        );

      if (attempt >= retryOptions.maxAttempts || 
          (retryOptions.retryableErrors && 
           !retryOptions.retryableErrors.includes(conversionError.code))) {
        throw conversionError;
      }

      // Emit error event if emitter is provided
      if (emitter) {
        emitter.emit(ConversionEventType.ERROR, conversionError);
      }

      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, delay));

      // Increase delay with exponential backoff
      delay = Math.min(
        delay * retryOptions.backoffFactor,
        retryOptions.maxDelay
      );
      attempt++;
    }
  }
}

/**
 * Validates configuration object against schema
 */
export function validateConfig<T extends Record<string, unknown>>(
  config: T,
  schema: Record<keyof T, {
    type: string;
    required?: boolean;
    validate?: (value: unknown) => boolean;
  }>
): void {
  const errors: string[] = [];

  for (const [key, rules] of Object.entries(schema)) {
    const value = config[key];

    if (rules.required && value === undefined) {
      errors.push(`Missing required field: ${key}`);
      continue;
    }

    if (value !== undefined) {
      if (typeof value !== rules.type) {
        errors.push(`Invalid type for ${key}: expected ${rules.type}, got ${typeof value}`);
      }

      if (rules.validate && !rules.validate(value)) {
        errors.push(`Validation failed for ${key}`);
      }
    }
  }

  if (errors.length > 0) {
    throw new ValidationError('Configuration validation failed', { errors });
  }
}

/**
 * Creates an error handler function for stream errors
 */
export function createStreamErrorHandler(
  cleanup: () => void,
  emitter?: EventEmitter
): (error: Error) => void {
  return (error: Error) => {
    cleanup();
    const streamError = new StreamError(error.message, {
      originalError: error
    });
    
    if (emitter) {
      emitter.emit(ConversionEventType.ERROR, streamError);
    }
    
    throw streamError;
  };
}

/**
 * Checks if an error is retryable based on error code
 */
export function isRetryableError(error: unknown): boolean {
  if (error instanceof ConversionError) {
    return [
      'STREAM_ERROR',
      'PROCESS_ERROR',
      'TEMPORARY_ERROR'
    ].includes(error.code);
  }
  return false;
}

// Helper function to create a StreamError with proper type checking
export function createStreamError(
  message: string,
  streamType: 'input' | 'output' | 'transform',
  error: Error,
  originalError?: Error
): StreamError {
  return new StreamError(message, { streamType, error, originalError });
}

// Helper function to check if an error is retryable
export function isRetryableError(error: Error, patterns: Array<string | RegExp>): boolean {
  const errorString = error.message.toLowerCase();
  return patterns.some(pattern => {
    if (pattern instanceof RegExp) {
      return pattern.test(errorString);
    }
    return errorString.includes(pattern.toLowerCase());
  });
} 