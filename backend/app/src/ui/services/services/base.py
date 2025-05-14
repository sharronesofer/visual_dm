from typing import Any, List


  ApiResponse,
  ValidationResult,
  ServiceConfig,
  ValidationError,
} from '../types/common'
/**
 * Abstract base service class that implements IBaseService interface
 * Provides common functionality for all services
 */
abstract class BaseService<
  T = any,
  CreateDTO extends Record<string, any> = any,
  UpdateDTO extends Partial<CreateDTO> = Partial<CreateDTO>,
> implements IBaseService<T, CreateDTO, UpdateDTO>
{
  protected config: ServiceConfig
  protected hooks: ServiceHooks<T, CreateDTO, UpdateDTO>
  protected cancellationToken: CancelTokenSource
  constructor(
    config?: Partial<ServiceConfig>,
    hooks?: Partial<ServiceHooks<T, CreateDTO, UpdateDTO>>
  ) {
    this.config = {
      baseURL: config?.baseURL || 'http:
      timeout: config?.timeout || 5000,
      headers: config?.headers || {},
      ...config,
    }
    this.hooks = hooks || {}
    this.cancellationToken = createCancellationToken()
  }
  /**
   * Create a new entity
   * @param data The data to create the entity with
   */
  async create(data: CreateDTO): Promise<ApiResponse<T>> {
    try {
      const validationResult = await this.validate(data)
      if (!validationResult.isValid) {
        const errors: Record<string, string[]> = {}
        validationResult.errors.forEach(error => {
          errors[error.field] = [error.message]
        })
        return this.createErrorResponse(new Error('Validation failed'))
      }
      const processedData = this.hooks.beforeCreate
        ? await this.hooks.beforeCreate(data)
        : data
      const response = await this.executeCreate(processedData)
      if (response.success && this.hooks.afterCreate) {
        response.data = await this.hooks.afterCreate(response.data)
      }
      return response
    } catch (error) {
      logger.error('Create operation failed', error as Error, { data })
      return this.createErrorResponse(error)
    }
  }
  /**
   * Update an existing entity
   * @param id The ID of the entity to update
   * @param data The data to update the entity with
   */
  async update(id: str, data: UpdateDTO): Promise<ApiResponse<T>> {
    try {
      const validationResult = await this.validate(data)
      if (!validationResult.isValid) {
        const errors: Record<string, string[]> = {}
        validationResult.errors.forEach(error => {
          errors[error.field] = [error.message]
        })
        return this.createErrorResponse(new Error('Validation failed'))
      }
      const processedData = this.hooks.beforeUpdate
        ? await this.hooks.beforeUpdate(id, data)
        : data
      const response = await this.executeUpdate(id, processedData)
      if (response.success && this.hooks.afterUpdate) {
        response.data = await this.hooks.afterUpdate(response.data)
      }
      return response
    } catch (error) {
      logger.error('Update operation failed', error as Error, { id, data })
      return this.createErrorResponse(error)
    }
  }
  /**
   * Delete an entity
   * @param id The ID of the entity to delete
   */
  async delete(id: str): Promise<ApiResponse<void>> {
    try {
      if (this.hooks.beforeDelete) {
        await this.hooks.beforeDelete(id)
      }
      const response = await this.executeDelete(id)
      if (response.success && this.hooks.afterDelete) {
        await this.hooks.afterDelete(id)
      }
      return response
    } catch (error) {
      logger.error('Delete operation failed', error as Error, { id })
      return this.createErrorResponse(error)
    }
  }
  /**
   * Get an entity by ID
   * @param id The ID of the entity to get
   */
  abstract getById(id: str): Promise<ApiResponse<T>>
  /**
   * Get all entities
   */
  abstract getAll(): Promise<ApiResponse<T[]>>
  /**
   * List entities with optional filtering and pagination
   */
  abstract list(): Promise<ApiResponse<T[]>>
  /**
   * Execute the actual create operation
   * @param data The processed data to create the entity with
   */
  protected abstract executeCreate(data: CreateDTO): Promise<ApiResponse<T>>
  /**
   * Execute the actual update operation
   * @param id The ID of the entity to update
   * @param data The processed data to update the entity with
   */
  protected abstract executeUpdate(
    id: str,
    data: UpdateDTO
  ): Promise<ApiResponse<T>>
  /**
   * Execute the actual delete operation
   * @param id The ID of the entity to delete
   */
  protected abstract executeDelete(id: str): Promise<ApiResponse<void>>
  /**
   * Validate entity data
   * @param data The data to validate
   */
  async validate(data: CreateDTO | UpdateDTO): Promise<ValidationResult> {
    const errors: List[ValidationError] = []
    const fields = Object.keys(data)
    for (const field of fields) {
      const result = await this.validateField(field, (data as any)[field])
      if (!result.isValid) {
        errors.push(...result.errors)
      }
    }
    return {
      isValid: errors.length === 0,
      errors,
    }
  }
  /**
   * Validate a specific field
   * @param field The field to validate
   * @param value The value to validate
   */
  async validateField(field: str, value: Any): Promise<ValidationResult> {
    return {
      isValid: true,
      errors: [],
    }
  }
  /**
   * Get the current service configuration
   */
  getConfig(): ServiceConfig {
    return { ...this.config }
  }
  /**
   * Update the service configuration
   * @param config The new configuration
   */
  async setConfig(config: Partial<ServiceConfig>): Promise<ApiResponse<void>> {
    this.config = {
      ...this.config,
      ...config,
    }
    return {
      success: true,
      data: undefined,
    }
  }
  /**
   * Get the current hooks configuration
   */
  getHooks(): ServiceHooks<T, CreateDTO, UpdateDTO> {
    return { ...this.hooks }
  }
  /**
   * Update the hooks configuration
   * @param hooks The new hooks
   */
  setHooks(hooks: Partial<ServiceHooks<T, CreateDTO, UpdateDTO>>): void {
    this.hooks = {
      ...this.hooks,
      ...hooks,
    }
  }
  /**
   * Cancel any ongoing requests
   */
  cancelRequests(): void {
    this.cancellationToken.cancel()
    this.cancellationToken = createCancellationToken()
  }
  /**
   * Helper method to create a successful API response
   * @param data The response data
   */
  protected createSuccessResponse<R>(data: R): ApiResponse<R> {
    return {
      success: true,
      data,
    }
  }
  /**
   * Helper method to create an error API response
   * @param error The error that occurred
   */
  protected createErrorResponse<R>(error: Error | any): ApiResponse<R> {
    const isAppError = error instanceof ApplicationError
    const errorObj = {
      message: error.message || 'An unknown error occurred',
      code: isAppError ? error.code : 'UNKNOWN_ERROR',
      details: isAppError ? error.details : undefined,
    }
    return {
      success: false,
      data: undefined as unknown as R,
      error: errorObj,
    }
  }
}