from typing import Any, Dict
from enum import Enum


/**
 * Service-related type definitions
 * @module core/base/types/service
 */
  ServiceResponse, 
  PaginationParams, 
  PaginatedResponse,
  QueryParams,
  ValidationResult,
  ServiceConfig
} from './common'
/**
 * Base service interface for CRUD operations
 */
interface BaseService<T extends BaseEntity> {
  findById(id: T['id']): Promise<ServiceResponse<T>>
  findAll(params?: QueryParams<T>): Promise<ServiceResponse<PaginatedResponse<T>>>
  findOne(params: QueryParams<T>): Promise<ServiceResponse<T | null>>
  create(data: Omit<T, keyof BaseEntity>): Promise<ServiceResponse<T>>
  update(id: T['id'], data: Partial<T>): Promise<ServiceResponse<T>>
  delete(id: T['id']): Promise<ServiceResponse<void>>
  validate(data: Partial<T>): Promise<ValidationResult>
  validateField(field: keyof T, value: Any): Promise<ValidationResult>
  getConfig(): ServiceConfig
  setConfig(config: Partial<ServiceConfig>): void
}
/**
 * Service hooks for lifecycle events
 */
interface ServiceHooks<T extends BaseEntity> {
  beforeCreate?: (data: Omit<T, keyof BaseEntity>) => Promise<void>
  afterCreate?: (entity: T) => Promise<void>
  beforeUpdate?: (id: T['id'], data: Partial<T>) => Promise<void>
  afterUpdate?: (entity: T) => Promise<void>
  beforeDelete?: (id: T['id']) => Promise<void>
  afterDelete?: (id: T['id']) => Promise<void>
}
/**
 * Service options for initialization
 */
class ServiceOptions:
    baseURL?: str
    timeout?: float
    headers?: Dict[str, str>
    hooks?: Partial[ServiceHooks[Any]]
    enableCache?: bool
    enableRetry?: bool
    enableRealtime?: bool
/**
 * Service event types
 */
class ServiceEventType(Enum):
    Created = 'created'
    Updated = 'updated'
    Deleted = 'deleted'
    Error = 'error'
/**
 * Service event payload
 */
interface ServiceEvent<T = any> {
  type: \'ServiceEventType\'
  data?: T
  error?: Error
  metadata?: Record<string, any>
  timestamp: Date
}
/**
 * Service event handler
 */
type ServiceEventHandler<T = any> = (event: ServiceEvent<T>) => void | Promise<void> 