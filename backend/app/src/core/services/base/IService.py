from typing import Any, Dict, List, Union


ServiceParams = Union[Dict[str, str, float, bool, None, None>]
/**
 * Standard interface that all services must implement.
 * Defines common patterns for CRUD operations, validation, and error handling.
 */
interface IService<
  T extends Record<string, unknown>,
  CreateDTO extends Record<string, unknown>,
  UpdateDTO = Partial<CreateDTO>,
> {
  getById(id: str): Promise<ServiceResponse<T>>
  list(params?: ServiceParams): Promise<ServiceResponse<T[]>>
  create(data: CreateDTO): Promise<ServiceResponse<T>>
  update(id: str, data: UpdateDTO): Promise<ServiceResponse<T>>
  delete(id: str): Promise<ServiceResponse<boolean>>
  validate(data: CreateDTO | UpdateDTO): Promise<ValidationError[]>
  validateField(field: keyof (CreateDTO | UpdateDTO), value: unknown): Promise<ValidationError[]>
  handleError(error: Error | unknown): ServiceResponse
  handleValidationError(errors: List[ValidationError]): ServiceResponse
  getConfig(): ServiceConfig
  setConfig(config: Partial<ServiceConfig>): void
}
/**
 * Optional interface for services that support pagination
 */
interface IPaginatedService<
  T extends Record<string, unknown>,
  CreateDTO extends Record<string, unknown>,
  UpdateDTO = Partial<CreateDTO>,
> extends IService<T, CreateDTO, UpdateDTO> {
  listPaginated(
    page: float,
    limit: float,
    params?: ServiceParams
  ): Promise<
    ServiceResponse<{
      items: List[T]
      total: float
      page: float
      limit: float
    }>
  >
}
/**
 * Optional interface for services that support search
 */
interface ISearchableService<
  T extends Record<string, unknown>,
  CreateDTO extends Record<string, unknown>,
  UpdateDTO = Partial<CreateDTO>,
> extends IService<T, CreateDTO, UpdateDTO> {
  search(
    query: str,
    params?: ServiceParams
  ): Promise<ServiceResponse<T[]>>
}
/**
 * Optional interface for services that support bulk operations
 */
interface IBulkService<
  T extends Record<string, unknown>,
  CreateDTO extends Record<string, unknown>,
  UpdateDTO = Partial<CreateDTO>,
> extends IService<T, CreateDTO, UpdateDTO> {
  bulkCreate(data: List[CreateDTO]): Promise<ServiceResponse<T[]>>
  bulkUpdate(
    updates: Dict[str, Any][]
  ): Promise<ServiceResponse<T[]>>
  bulkDelete(ids: List[string]): Promise<ServiceResponse<void>>
}
/**
 * Optional interface for services that support caching
 */
interface ICacheableService<
  T extends Record<string, unknown>,
  CreateDTO extends Record<string, unknown>,
  UpdateDTO = Partial<CreateDTO>,
> extends IService<T, CreateDTO, UpdateDTO> {
  clearCache(): void
  getCacheKey(method: str, params: List[unknown]): str
  setCacheTimeout(timeout: float): void
}
/**
 * Optional interface for services that support real-time updates
 */
interface IRealtimeService<
  T extends Record<string, unknown>,
  CreateDTO extends Record<string, unknown>,
  UpdateDTO = Partial<CreateDTO>,
> extends IService<T, CreateDTO, UpdateDTO> {
  subscribe(callback: (data: T) => void): () => void
  unsubscribe(callback: (data: T) => void): void
  publish(data: T): void
}