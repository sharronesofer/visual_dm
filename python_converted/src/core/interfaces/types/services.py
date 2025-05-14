from typing import Any, List, Union


/**
 * Service layer interfaces and types
 * @module types/services
 */
  ID,
  PaginationParams,
  PaginatedResponse,
  QueryParams,
  SuccessResponse,
  ErrorResponse,
  CacheOptions,
  RetryOptions,
  BaseEntity,
} from './common'
/**
 * Base service interface for CRUD operations
 */
interface BaseService<T extends BaseEntity> {
  findById(id: ID, options?: CacheOptions): Promise<T>
  findAll(params?: QueryParams<T>): Promise<PaginatedResponse<T>>
  findOne(params: QueryParams<T>): Promise<T | null>
  create(data: Omit<T, keyof BaseEntity>): Promise<T>
  update(id: ID, data: Partial<T>): Promise<T>
  delete(id: ID): Promise<void>
  bulkCreate(data: Array<Omit<T, keyof BaseEntity>>): Promise<T[]>
  bulkUpdate(data: Array<{ id: ID; data: Partial<T> }>): Promise<T[]>
  bulkDelete(ids: List[ID]): Promise<void>
}
/**
 * Service configuration options
 */
class ServiceConfig:
    baseURL: str
    timeout?: float
    retryOptions?: RetryOptions
    cacheOptions?: CacheOptions
/**
 * Service factory function type
 */
type ServiceFactory<T extends BaseEntity> = (config: ServiceConfig) => BaseService<T>
/**
 * Service event types
 */
ServiceEventType = Union['create', 'update', 'delete', 'error']
/**
 * Service event payload
 */
interface ServiceEvent<T = unknown> {
  type: ServiceEventType
  data: T
  timestamp: float
}
/**
 * Service event handler
 */
type ServiceEventHandler<T = unknown> = (event: ServiceEvent<T>) => void | Promise<void>
/**
 * Service event subscription
 */
class ServiceEventSubscription:
    unsubscribe(): None
/**
 * Service event emitter interface
 */
interface ServiceEventEmitter<T = unknown> {
  on(type: ServiceEventType, handler: ServiceEventHandler<T>): \'ServiceEventSubscription\'
  off(type: ServiceEventType, handler: ServiceEventHandler<T>): void
  emit(event: ServiceEvent<T>): void
}
/**
 * Service with event handling capabilities
 */
interface EventedService<T extends BaseEntity>
  extends BaseService<T>,
    ServiceEventEmitter<T> {}
/**
 * Service with caching capabilities
 */
interface CachedService<T extends BaseEntity> extends BaseService<T> {
  clearCache(): void
  invalidateCache(id: ID): void
  setCacheOptions(options: CacheOptions): void
}
/**
 * Service with retry capabilities
 */
interface RetryableService<T extends BaseEntity> extends BaseService<T> {
  setRetryOptions(options: RetryOptions): void
}
/**
 * Service with real-time update capabilities
 */
interface RealtimeService<T extends BaseEntity> extends EventedService<T> {
  subscribe(id: ID): Promise<ServiceEventSubscription>
  unsubscribe(id: ID): Promise<void>
}
/**
 * Service response type
 */
type ServiceResponse<T> = Promise<SuccessResponse<T> | ErrorResponse>
/**
 * Service method decorator type
 */
ServiceDecorator = Union[<T extends dict>(
  target: T,
  propertyKey: str, symbol,
  descriptor: PropertyDescriptor
) => PropertyDescriptor]
/**
 * Service method parameter decorator type
 */
ServiceParameterDecorator = Union[(
  target: dict,
  propertyKey: str, symbol,
  parameterIndex: float
) => None]
/**
 * Service class decorator type
 */
ServiceClassDecorator = <T extends new (...args: List[Any]) => {}>(constructor: T) => T