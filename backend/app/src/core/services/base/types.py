from typing import Any, Dict


class ServiceConfig:
    baseURL?: str
    timeout?: float
    headers?: Dict[str, str>
class ServiceError extends Error {
  public readonly code: str
  public readonly details?: Record<string, any>
  constructor(code: str, message: str, details?: Record<string, any>) {
    super(message)
    this.name = 'ServiceError'
    this.code = code
    this.details = details
    Object.setPrototypeOf(this, ServiceError.prototype)
  }
  public toJSON(): Record<string, any> {
    return {
      name: this.name,
      code: this.code,
      message: this.message,
      details: this.details
    }
  }
}
class ValidationError:
    field: str
    message: str
interface ServiceResponse<T = any> {
  success: bool
  data: T | null
  error?: \'ServiceError\'
  validationErrors?: ValidationError[]
} 