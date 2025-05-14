from typing import Any



class AppError extends Error {
  constructor(
    public readonly code: str,
    message: str,
    public readonly statusCode: float = 500
  ) {
    super(message)
    this.name = 'AppError'
  }
}
class NotFoundError extends AppError {
  constructor(resource: str, id: str | number) {
    super('NOT_FOUND', `${resource} with id ${id} not found`, 404)
    this.name = 'NotFoundError'
  }
}
class ValidationError extends AppError {
  constructor(message: str) {
    super('VALIDATION_ERROR', message, 400)
    this.name = 'ValidationError'
  }
}
class AuthorizationError extends AppError {
  constructor(message: str) {
    super('AUTHORIZATION_ERROR', message, 403)
    this.name = 'AuthorizationError'
  }
}
class AuthenticationError extends AppError {
  constructor(message: str) {
    super('AUTHENTICATION_ERROR', message, 401)
    this.name = 'AuthenticationError'
  }
} 