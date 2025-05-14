import { BaseEntity, ServiceResponse as BaseServiceResponse } from '../base.service';
import { ServiceResponse as IServiceResponse, ServiceError, ValidationError } from '../base/types';

/**
 * Common service response type that satisfies both BaseServiceResponse and IServiceResponse
 */
export type AdaptedServiceResponse<T> = {
  success: boolean;
  data: T | null;
  error?: ServiceError;
  validationErrors?: ValidationError[];
  meta?: Record<string, unknown>;
};

/**
 * Error response type
 */
export type ErrorResponse = {
  success: false;
  data: null;
  error: ServiceError;
  validationErrors?: ValidationError[];
  meta?: Record<string, unknown>;
};

/**
 * Success response type
 */
export type SuccessResponse<T> = {
  success: true;
  data: T;
  meta?: Record<string, unknown>;
};

/**
 * Service response type that can be either success or error
 */
export type ServiceResponseType<T> = SuccessResponse<T> | ErrorResponse;

/**
 * Adapts a BaseServiceResponse to an IServiceResponse
 */
export function adaptServiceResponse<T>(response: BaseServiceResponse<T>): ServiceResponseType<T> {
  // Check if there's an error in the metadata
  if (response.meta?.error) {
    return {
      success: false,
      data: null,
      error: new ServiceError('SERVICE_ERROR', response.meta.error.message || 'Unknown error occurred'),
      meta: response.meta
    };
  }

  // If we have data, return a success response
  if (response.data) {
    return {
      success: true,
      data: response.data,
      meta: response.meta
    };
  }

  // If we have no data, return an error response
  return {
    success: false,
    data: null,
    error: new ServiceError('NO_DATA', 'No data returned from service'),
    meta: response.meta
  };
}

/**
 * Creates an error response
 */
export function createErrorResponse(error: ServiceError, validationErrors?: ValidationError[]): ErrorResponse {
  return {
    success: false,
    data: null,
    error,
    validationErrors,
    meta: {}
  };
}

/**
 * Type that extends BaseEntity and ensures it satisfies Record<string, unknown>
 */
export type ExtendedBaseEntity = BaseEntity & Record<string, unknown>;

/**
 * Constraint for CreateDTO type parameter
 */
export type CreateDTOConstraint<T extends ExtendedBaseEntity> = Omit<T, keyof BaseEntity | 'id'> & Record<string, unknown>;

/**
 * Constraint for UpdateDTO type parameter
 */
export type UpdateDTOConstraint<T extends ExtendedBaseEntity> = Partial<CreateDTOConstraint<T>>;

/**
 * Type for handling both string and number IDs
 */
export type ServiceId = string | number;

/**
 * Convert ID to the correct type
 */
export function convertId(id: ServiceId): string {
  return typeof id === 'number' ? id.toString() : id;
}

/**
 * Type for service operations that can fail
 */
export type ServiceOperation<T> = Promise<ServiceResponseType<T>>;

/**
 * Type for service operations that always succeed
 */
export type ServiceSuccessOperation<T> = Promise<SuccessResponse<T>>;

/**
 * Type for service operations that always fail
 */
export type ServiceErrorOperation = Promise<ErrorResponse>;

/**
 * Type for validating service data
 */
export type ServiceValidationResult = Promise<ValidationError[]>;

/**
 * Type for service configuration
 */
export type ServiceOperationConfig = {
  validateInput?: boolean;
  validateOutput?: boolean;
  cache?: boolean;
  timeout?: number;
}; 