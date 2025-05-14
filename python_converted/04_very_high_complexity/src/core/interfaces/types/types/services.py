from typing import Any, List



  ApiResponse,
  ValidationResult,
  SearchParams,
  BulkOperation,
  ServiceConfig,
} from './common'
/**
 * Base interface for all services
 */
interface IBaseService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> {
  getById(id: str): Promise<ApiResponse<T>>
  list(params?: Record<string, any>): Promise<ApiResponse<T[]>>
  create(data: CreateDTO): Promise<ApiResponse<T>>
  update(id: str, data: UpdateDTO): Promise<ApiResponse<T>>
  delete(id: str): Promise<ApiResponse<void>>
  validate(data: CreateDTO | UpdateDTO): Promise<ValidationResult>
  validateField(field: str, value: Any): Promise<ValidationResult>
  getConfig(): ServiceConfig
  setConfig(config: Partial<ServiceConfig>): void
}
/**
 * Interface for services that support pagination
 */
interface IPaginatedService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> extends IBaseService<T, CreateDTO, UpdateDTO> {
  listPaginated(
    page: float,
    limit: float,
    params?: Record<string, any>
  ): Promise<
    ApiResponse<{
      items: List[T]
      total: float
      page: float
      limit: float
      hasMore: bool
    }>
  >
}
/**
 * Interface for services that support search operations
 */
interface ISearchableService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> extends IBaseService<T, CreateDTO, UpdateDTO> {
  search(params: SearchParams): Promise<ApiResponse<T[]>>
}
/**
 * Interface for services that support bulk operations
 */
interface IBulkService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> extends IBaseService<T, CreateDTO, UpdateDTO> {
  bulkCreate(operation: BulkOperation<CreateDTO>): Promise<ApiResponse<T[]>>
  bulkUpdate(
    operation: BulkOperation<{ id: str; data: UpdateDTO }>
  ): Promise<ApiResponse<T[]>>
  bulkDelete(ids: List[string]): Promise<ApiResponse<void>>
}
/**
 * Interface for services that support caching
 */
interface ICacheableService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> extends IBaseService<T, CreateDTO, UpdateDTO> {
  clearCache(): void
  getCacheKey(method: str, params: List[any]): str
  setCacheTimeout(timeout: float): void
}
/**
 * Interface for services that support real-time updates
 */
interface IRealtimeService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> extends IBaseService<T, CreateDTO, UpdateDTO> {
  subscribe(callback: (data: T) => void): () => void
  unsubscribe(callback: (data: T) => void): void
  publish(data: T): void
}
/**
 * Interface for services that support validation rules
 */
interface IValidatableService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> extends IBaseService<T, CreateDTO, UpdateDTO> {
  getValidationRules(): Record<string, any>
  setValidationRules(rules: Record<string, any>): void
}
/**
 * Interface for services that support custom actions
 */
interface IActionableService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> extends IBaseService<T, CreateDTO, UpdateDTO> {
  executeAction<R = any>(
    action: str,
    params?: Record<string, any>
  ): Promise<ApiResponse<R>>
  getAvailableActions(): string[]
}
/**
 * Interface for services that support entity relationships
 */
interface IRelationalService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> extends IBaseService<T, CreateDTO, UpdateDTO> {
  getRelated(id: str, relation: str): Promise<ApiResponse<any>>
  updateRelation(
    id: str,
    relation: str,
    relatedId: str
  ): Promise<ApiResponse<void>>
  removeRelation(
    id: str,
    relation: str,
    relatedId: str
  ): Promise<ApiResponse<void>>
}
/**
 * Interface for services that support versioning
 */
interface IVersionedService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> extends IBaseService<T, CreateDTO, UpdateDTO> {
  getVersion(id: str, version: float): Promise<ApiResponse<T>>
  getVersions(id: str): Promise<ApiResponse<number[]>>
  revertToVersion(id: str, version: float): Promise<ApiResponse<T>>
}
/**
 * Utility type to extract the entity type from a service interface
 */
type ServiceEntity<T> =
  T extends IBaseService<infer E, any, any> ? E : never
/**
 * Utility type to extract the create DTO type from a service interface
 */
type ServiceCreateDTO<T> =
  T extends IBaseService<any, infer C, any> ? C : never
/**
 * Utility type to extract the update DTO type from a service interface
 */
type ServiceUpdateDTO<T> =
  T extends IBaseService<any, any, infer U> ? U : never
/**
 * Utility type to create a fully featured service interface
 */
type FullService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> = IBaseService<T, CreateDTO, UpdateDTO> &
  IPaginatedService<T, CreateDTO, UpdateDTO> &
  ISearchableService<T, CreateDTO, UpdateDTO> &
  IBulkService<T, CreateDTO, UpdateDTO> &
  ICacheableService<T, CreateDTO, UpdateDTO> &
  IRealtimeService<T, CreateDTO, UpdateDTO> &
  IValidatableService<T, CreateDTO, UpdateDTO> &
  IActionableService<T, CreateDTO, UpdateDTO> &
  IRelationalService<T, CreateDTO, UpdateDTO> &
  IVersionedService<T, CreateDTO, UpdateDTO>
/**
 * Type for service factory functions
 */
type ServiceFactory<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> = {
  create(
    config?: Partial<ServiceConfig>
  ): IBaseService<T, CreateDTO, UpdateDTO>
}
/**
 * Type for service decorator functions
 */
type ServiceDecorator<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> = {
  (
    service: IBaseService<T, CreateDTO, UpdateDTO>
  ): IBaseService<T, CreateDTO, UpdateDTO>
}
/**
 * Type for service event handlers
 */
type ServiceEventHandler<T = any> = {
  onCreated?: (entity: T) => void | Promise<void>
  onUpdated?: (entity: T) => void | Promise<void>
  onDeleted?: (id: str) => void | Promise<void>
  onError?: (error: Error) => void | Promise<void>
}
/**
 * Type for service middleware
 */
type ServiceMiddleware<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> = {
  before?: (method: keyof IBaseService, args: List[any]) => void | Promise<void>
  after?: (method: keyof IBaseService, result: Any) => void | Promise<void>
  error?: (method: keyof IBaseService, error: Error) => void | Promise<void>
}
/**
 * Type for service query builders
 */
type ServiceQueryBuilder<T = any> = {
  where(conditions: Partial<T>): ServiceQueryBuilder<T>
  orderBy(field: keyof T, direction: 'asc' | 'desc'): ServiceQueryBuilder<T>
  limit(count: float): ServiceQueryBuilder<T>
  offset(count: float): ServiceQueryBuilder<T>
  include(relations: List[string]): ServiceQueryBuilder<T>
  build(): Record<string, any>
}
/**
 * Type for service hooks
 */
type ServiceHooks<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> = {
  beforeCreate?: (data: CreateDTO) => CreateDTO | Promise<CreateDTO>
  afterCreate?: (entity: T) => T | Promise<T>
  beforeUpdate?: (
    id: str,
    data: UpdateDTO
  ) => UpdateDTO | Promise<UpdateDTO>
  afterUpdate?: (entity: T) => T | Promise<T>
  beforeDelete?: (id: str) => void | Promise<void>
  afterDelete?: (id: str) => void | Promise<void>
}