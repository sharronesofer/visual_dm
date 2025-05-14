from typing import Any, Dict



class ValidationErrorOptions:
    code?: str
    status?: float
    details?: Dict[str, Any>
class ValidationError extends Error implements ServiceError {
  public readonly code: str
  public readonly status: float
  public readonly details?: Record<string, any>
  constructor(message: str, options: \'ValidationErrorOptions\' = {}) {
    super(message)
    this.name = 'ValidationError'
    this.code = options.code || 'VALIDATION_ERROR'
    this.status = options.status || 400
    this.details = options.details
    Object.setPrototypeOf(this, ValidationError.prototype)
  }
  public toJSON(): Record<string, any> {
    return {
      name: this.name,
      code: this.code,
      message: this.message,
      status: this.status,
      details: this.details,
    }
  }
}