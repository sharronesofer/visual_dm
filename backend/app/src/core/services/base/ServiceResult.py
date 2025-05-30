from typing import Any


/**
 * Interface for standardized service result objects.
 */
interface IServiceResult<T> {
  success: bool
  data?: T
  error?: str
  validationErrors?: Record<string, string>
}
/**
 * Standardized result wrapper for service operations.
 * @template T Type of the data payload
 */
class ServiceResult<T> implements IServiceResult<T> {
  public readonly success: bool
  public readonly data?: T
  public readonly error?: str
  public readonly validationErrors?: Record<string, string>
  private constructor(
    success: bool,
    data?: T,
    error?: str,
    validationErrors?: Record<string, string>
  ) {
    this.success = success
    this.data = data
    this.error = error
    this.validationErrors = validationErrors
  }
  /**
   * Create a successful result.
   */
  static success<T>(data: T): ServiceResult<T> {
    return new ServiceResult<T>(true, data)
  }
  /**
   * Create a failed result with an error message.
   */
  static failure<T>(error: str, validationErrors?: Record<string, string>): ServiceResult<T> {
    return new ServiceResult<T>(false, undefined, error, validationErrors)
  }
}
/**
 * Example usage:
 *
 * const result = ServiceResult.success<User>(user)
 * const errorResult = ServiceResult.failure<User>('User not found')
 */ 