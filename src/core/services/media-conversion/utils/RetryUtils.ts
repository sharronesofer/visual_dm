import { ConversionError, ProcessError, RetryError } from './ErrorUtils';
import { Logger } from './LogUtils';
import { ConversionStage } from '../types';

/**
 * Configuration for retry behavior
 */
export interface RetryConfig {
  maxAttempts?: number;
  initialDelay?: number;
  maxDelay?: number;
  backoffFactor?: number;
  retryableErrors?: Array<string | RegExp>;
}

interface RequiredRetryConfig {
  maxAttempts: number;
  initialDelay: number;
  maxDelay: number;
  backoffFactor: number;
  retryableErrors: Array<string | RegExp>;
}

/**
 * Default retry configuration
 */
const DEFAULT_RETRY_CONFIG: RequiredRetryConfig = {
  maxAttempts: 3,
  initialDelay: 1000,
  maxDelay: 10000,
  backoffFactor: 2,
  retryableErrors: [/.*temporary failure.*/, /.*timeout.*/, /.*connection reset.*/]
};

/**
 * Utility class for handling retries and recovery strategies
 */
export class RetryHandler {
  private readonly config: RequiredRetryConfig;
  private readonly logger?: Logger;

  constructor(config: RetryConfig = {}, logger?: Logger) {
    this.config = {
      ...DEFAULT_RETRY_CONFIG,
      ...config
    };
    this.logger = logger;
  }

  /**
   * Execute an operation with retry logic
   */
  public async execute<T>(
    operation: () => Promise<T>,
    stage: ConversionStage = ConversionStage.RETRYING
  ): Promise<T> {
    let lastError: Error | null = null;
    let delay = this.config.initialDelay;

    for (let attempt = 1; attempt <= this.config.maxAttempts; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
        
        if (attempt === this.config.maxAttempts) {
          break;
        }

        this.logger?.warn(
          `Operation failed (attempt ${attempt}/${this.config.maxAttempts}), retrying...`,
          { error: lastError, stage, nextAttemptDelay: delay }
        );

        await this.sleep(delay);
        delay = Math.min(delay * this.config.backoffFactor, this.config.maxDelay);
      }
    }

    const errorDetails = {
      stage,
      maxAttempts: this.config.maxAttempts,
      lastError: lastError?.message || 'Unknown error'
    };

    throw new RetryError(
      `Operation failed after ${this.config.maxAttempts} attempts`,
      errorDetails
    );
  }

  /**
   * Check if an error is retryable based on configuration
   */
  private isRetryable(error: Error): boolean {
    // Always retry ProcessErrors (they're typically transient)
    if (error instanceof ProcessError) {
      return true;
    }

    // Don't retry validation errors
    if (error instanceof ConversionError && error.code === 'VALIDATION_ERROR') {
      return false;
    }

    // Check against configured retryable errors
    if (this.config.retryableErrors) {
      const errorString = error.message + (error.stack || '');
      return this.config.retryableErrors.some(pattern => {
        if (pattern instanceof RegExp) {
          return pattern.test(errorString);
        }
        return errorString.includes(pattern);
      });
    }

    return false;
  }

  /**
   * Calculate delay for next retry attempt using exponential backoff
   */
  private calculateDelay(attempt: number): number {
    const delay = Math.min(
      this.config.initialDelay * Math.pow(this.config.backoffFactor, attempt - 1),
      this.config.maxDelay
    );
    
    // Add jitter to prevent thundering herd
    const jitter = Math.random() * 0.1 * delay;
    return Math.floor(delay + jitter);
  }

  /**
   * Promise-based delay
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
} 