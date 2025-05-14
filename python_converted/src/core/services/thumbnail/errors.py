from typing import Any


class ValidationError extends Error implements ServiceError {
  code: str
  details?: Any
  constructor(code: str, message: str, details?: Any) {
    super(message)
    this.name = 'ValidationError'
    this.code = code
    this.details = details
    Object.setPrototypeOf(this, ValidationError.prototype)
  }
}
class ThumbnailServiceError extends Error implements ServiceError {
  code: str
  details?: Any
  constructor(code: str, message: str, details?: Any) {
    super(message)
    this.name = 'ThumbnailServiceError'
    this.code = code
    this.details = details
    Object.setPrototypeOf(this, ThumbnailServiceError.prototype)
  }
} 