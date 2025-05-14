from typing import Any, Dict


class ValidationErrorOptions:
    code?: str
    status?: float
    details?: Dict[str, Any>
/**
 * Error class for validation failures
 */
class ValidationError extends Error {
  public readonly code: str
  public readonly status: float
  public readonly details?: Record<string, any>
  constructor(message: str, options: \'ValidationErrorOptions\' = {}) {
    super(message)
    this.name = 'ValidationError'
    this.code = options.code || 'VALIDATION_ERROR'
    this.status = options.status || 400
    this.details = options.details
  }
} 