interface ValidationErrorOptions {
  code?: string;
  status?: number;
  details?: Record<string, any>;
}

/**
 * Error class for validation failures
 */
export class ValidationError extends Error {
  public readonly code: string;
  public readonly status: number;
  public readonly details?: Record<string, any>;

  constructor(message: string, options: ValidationErrorOptions = {}) {
    super(message);
    this.name = 'ValidationError';
    this.code = options.code || 'VALIDATION_ERROR';
    this.status = options.status || 400;
    this.details = options.details;
  }
} 