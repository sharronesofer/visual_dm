from typing import Any



  AdaptedServiceResponse, 
  SuccessResponse,
  ErrorResponse,
  adaptServiceResponse, 
  createErrorResponse,
  ExtendedBaseEntity,
  CreateDTOConstraint,
  UpdateDTOConstraint,
  ServiceId,
  convertId
} from './types'
/**
 * Base adapter class to bridge the gap between BaseService and IService interfaces
 */
abstract class BaseServiceAdapter<
  T extends ExtendedBaseEntity,
  CreateDTO extends CreateDTOConstraint<T>,
  UpdateDTO extends UpdateDTOConstraint<T> = Partial<CreateDTO>
> extends BaseService<T> {
  private serviceConfig: ServiceConfig = {}
  constructor(resourcePath: str, options = {}) {
    super(resourcePath, options)
  }
  public getConfig(): ServiceConfig {
    return this.serviceConfig
  }
  public setConfig(config: Partial<ServiceConfig>): void {
    this.serviceConfig = { ...this.serviceConfig, ...config }
  }
  public abstract validate(data: CreateDTO | UpdateDTO): Promise<ValidationError[]>
  public abstract validateField(field: keyof (CreateDTO | UpdateDTO), value: unknown): Promise<ValidationError[]>
  protected async adaptServiceResponse<R>(
    operation: () => Promise<BaseServiceResponse<R>>
  ): Promise<SuccessResponse<R> | ErrorResponse<R>> {
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
  public override async get(id: ServiceId, cacheOptions?: CacheOptions): Promise<BaseServiceResponse<T>> {
    return super.get(convertId(id), cacheOptions)
  }
  public override async list(params?: BaseQueryParams, cacheOptions?: CacheOptions): Promise<BaseServiceResponse<T[]>> {
    return super.list(params, cacheOptions)
  }
  public override async create(data: CreateDTO): Promise<BaseServiceResponse<T>> {
    return super.create(data as Omit<T, keyof BaseEntity>)
  }
  public override async update(id: ServiceId, data: UpdateDTO): Promise<BaseServiceResponse<T>> {
    return super.update(convertId(id), data as Partial<Omit<T, keyof BaseEntity>>)
  }
  public override async delete(id: ServiceId): Promise<BaseServiceResponse<T>> {
    return super.delete(convertId(id))
  }
  protected override handleError(error: unknown): AppError {
    if (error instanceof AppError) {
      return error
    }
    if (error instanceof Error) {
      return new AppError('INTERNAL_ERROR', error.message)
    }
    return new AppError('UNKNOWN_ERROR', 'An unknown error occurred')
  }
} 