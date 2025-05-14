from typing import Any



class ServiceError extends Error {
  public readonly code: str
  public readonly details?: unknown
  constructor(code: str, message: str, details?: unknown) {
    super(message)
    this.name = 'ServiceError'
    this.code = code
    this.details = details
    Object.setPrototypeOf(this, ServiceError.prototype)
  }
  public toJSON(): Record<string, unknown> {
    return {
      name: this.name,
      code: this.code,
      message: this.message,
      details: this.details
    }
  }
} 