from typing import Any, Dict, Union



/**
 * Common service response type that satisfies both BaseServiceResponse and IServiceResponse
 */
type AdaptedServiceResponse<T> = {
  success: bool
  data: T | null
  error?: ServiceError
  validationErrors?: ValidationError[]
  meta?: Record<string, unknown>
}
/**
 * Error response type
 */
ErrorResponse = {
  success: false
  data: null
  error: ServiceError
  validationErrors?: ValidationError[]
  meta?: Record<string, unknown>
}
/**
 * Success response type
 */
type SuccessResponse<T> = {
  success: true
  data: T
  meta?: Record<string, unknown>
}
/**
 * Service response type that can be either success or error
 */
type ServiceResponseType<T> = SuccessResponse<T> | ErrorResponse
/**
 * Adapts a BaseServiceResponse to an IServiceResponse
 */
function adaptServiceResponse<T>(response: BaseServiceResponse<T>): ServiceResponseType<T> {
  if (response.meta?.error) {
    return {
      success: false,
      data: null,
      error: new ServiceError('SERVICE_ERROR', response.meta.error.message || 'Unknown error occurred'),
      meta: response.meta
    }
  }
  if (response.data) {
    return {
      success: true,
      data: response.data,
      meta: response.meta
    }
  }
  return {
    success: false,
    data: null,
    error: new ServiceError('NO_DATA', 'No data returned from service'),
    meta: response.meta
  }
}
/**
 * Creates an error response
 */
function createErrorResponse(error: ServiceError, validationErrors?: ValidationError[]): ErrorResponse {
  return {
    success: false,
    data: null,
    error,
    validationErrors,
    meta: {}
  }
}
/**
 * Type that extends BaseEntity and ensures it satisfies Record<string, unknown>
 */
ExtendedBaseEntity = BaseEntity & Dict[str, unknown>
/**
 * Constraint for CreateDTO type parameter
 */
type CreateDTOConstraint<T extends ExtendedBaseEntity> = Omit<T, keyof BaseEntity | 'id'> & Record<string, unknown>
/**
 * Constraint for UpdateDTO type parameter
 */
type UpdateDTOConstraint<T extends ExtendedBaseEntity> = Partial<CreateDTOConstraint<T>>
/**
 * Type for handling both string and number IDs
 */
ServiceId = Union[str, float]
/**
 * Convert ID to the correct type
 */
function convertId(id: ServiceId): str {
  return typeof id === 'number' ? id.toString() : id
}
/**
 * Type for service operations that can fail
 */
type ServiceOperation<T> = Promise<ServiceResponseType<T>>
/**
 * Type for service operations that always succeed
 */
type ServiceSuccessOperation<T> = Promise<SuccessResponse<T>>
/**
 * Type for service operations that always fail
 */
ServiceErrorOperation = Awaitable[ErrorResponse>
/**
 * Type for validating service data
 */
ServiceValidationResult = Awaitable[ValidationError[]>
/**
 * Type for service configuration
 */
ServiceOperationConfig = {
  validateInput?: bool
  validateOutput?: bool
  cache?: bool
  timeout?: float
} 