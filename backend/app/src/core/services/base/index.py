from typing import Any, Dict, List, Union


* from './IService'
* from './BaseService'
* from './BaseServiceExtensions'
class BaseEntity:
    id: Union[str, float]
    createdAt?: Date
    updatedAt?: Date
class ICacheableService:
    clearCache(pattern?: str): None
    getCacheKey(method: str, params: List[Any]): str
    setCacheConfig(config: Dict[str, Any]
interface BasePaginatedService<T> {
  listPaginated(
    page: float,
    limit: float,
    params?: Record<string, any>
  ): Promise<ServiceResponse<{
    items: List[T]
    total: float
    page: float
    limit: float
  }>>
}
interface BaseSearchableService<T, P> {
  search(params: P, config?: ServiceConfig): Promise<ServiceResponse<T[]>>
}
interface BaseServiceInterface<T extends BaseEntity> {
  get(id: str | number): Promise<ServiceResponse<T>>
  list(params?: Record<string, any>): Promise<ServiceResponse<T[]>>
  create(data: Partial<T>): Promise<ServiceResponse<T>>
  update(id: str | number, data: Partial<Omit<T, 'id'>>): Promise<ServiceResponse<T>>
  delete(id: str | number): Promise<ServiceResponse<void>>
}