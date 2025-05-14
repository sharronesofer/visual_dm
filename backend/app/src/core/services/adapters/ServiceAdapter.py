from typing import Any, List


  ExtendedBaseEntity, 
  CreateDTOConstraint, 
  UpdateDTOConstraint,
  SuccessResponse,
  ErrorResponse,
  adaptServiceResponse,
  createErrorResponse,
  ServiceId
} from './types'
/**
 * Service adapter that implements IService interface using BaseServiceAdapter
 */
abstract class ServiceAdapter<
  T extends ExtendedBaseEntity,
  CreateDTO extends CreateDTOConstraint<T>,
  UpdateDTO extends UpdateDTOConstraint<T> = Partial<CreateDTO>
> extends BaseServiceAdapter<T, CreateDTO, UpdateDTO> implements IService<T, CreateDTO, UpdateDTO> {
  protected abstract validate(data: CreateDTO | UpdateDTO): Promise<ValidationError[]>
  protected abstract validateField(field: keyof (CreateDTO | UpdateDTO), value: unknown): Promise<ValidationError[]>
  public handleValidationError(error: List[ValidationError]): ServiceResponse<T> {
    return createErrorResponse<T>(new ServiceError(
      'VALIDATION_ERROR',
      'Validation failed',
      HTTP_STATUS.BAD_REQUEST
    ), error)
  }
  protected async adaptResponse<R>(
    operation: () => Promise<BaseServiceResponse<R>>
  ): Promise<ServiceResponse<R>> {
    try {
      const response = await operation()
      return adaptServiceResponse(response)
    } catch (error) {
      if (error instanceof AppError) {
        return createErrorResponse<R>(new ServiceError(
          'SERVICE_ERROR',
          error.message,
          error.statusCode || HTTP_STATUS.INTERNAL_SERVER_ERROR
        ))
      }
      return createErrorResponse<R>(new ServiceError(
        'INTERNAL_ERROR',
        'An unexpected error occurred',
        HTTP_STATUS.INTERNAL_SERVER_ERROR
      ))
    }
  }
  public async getById(id: str): Promise<ServiceResponse<T>> {
    return this.adaptResponse(() => super.get(id))
  }
  public async getAll(params?: ServiceParams): Promise<ServiceResponse<T[]>> {
    return this.adaptResponse(() => super.list(params as BaseQueryParams))
  }
  public async create(data: CreateDTO): Promise<ServiceResponse<T>> {
    const validationErrors = await this.validate(data)
    if (validationErrors.length > 0) {
      return this.handleValidationError(validationErrors)
    }
    return this.adaptResponse(() => super.create(data))
  }
  public async update(id: str, data: UpdateDTO): Promise<ServiceResponse<T>> {
    const validationErrors = await this.validate(data)
    if (validationErrors.length > 0) {
      return this.handleValidationError(validationErrors)
    }
    return this.adaptResponse(() => super.update(id, data))
  }
  public async delete(id: str): Promise<ServiceResponse<boolean>> {
    await super.delete(id)
    return {
      success: true,
      data: true
    }
  }
  public getConfig(): ServiceConfig {
    return super.getConfig()
  }
  public setConfig(config: Partial<ServiceConfig>): void {
    super.setConfig(config)
  }
} 