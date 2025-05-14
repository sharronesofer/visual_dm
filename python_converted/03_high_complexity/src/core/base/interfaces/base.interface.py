from typing import Any



/**
 * Base service interface definitions
 * @module core/base/interfaces/base
 */
  ServiceResponse, 
  PaginatedResponse, 
  QueryParams,
  ValidationResult,
  ServiceConfig,
  ServiceEvent,
  ServiceEventHandler
} from '../types/common'
/**
 * Base service interface for CRUD, validation, config, and event handling
 */
interface IBaseService<T extends BaseEntity> {
  /** Find entity by ID */
  findById(id: T['id']): Promise<ServiceResponse<T>>
  /** Find all entities with optional query params */
  findAll(params?: QueryParams<T>): Promise<ServiceResponse<PaginatedResponse<T>>>
  /** Find one entity matching query params */
  findOne(params: QueryParams<T>): Promise<ServiceResponse<T | null>>
  /** Create a new entity */
  create(data: Omit<T, keyof BaseEntity>): Promise<ServiceResponse<T>>
  /** Update an entity by ID */
  update(id: T['id'], data: Partial<T>): Promise<ServiceResponse<T>>
  /** Delete an entity by ID */
  delete(id: T['id']): Promise<ServiceResponse<void>>
  /** Validate entity data */
  validate(data: Partial<T>): Promise<ValidationResult>
  /** Validate a single field */
  validateField(field: keyof T, value: Any): Promise<ValidationResult>
  /** Get service config */
  getConfig(): ServiceConfig
  /** Set service config */
  setConfig(config: Partial<ServiceConfig>): void
  /** Subscribe to service events */
  on(event: str, handler: ServiceEventHandler<T>): void
  /** Unsubscribe from service events */
  off(event: str, handler: ServiceEventHandler<T>): void
  /** Emit a service event */
  emit(event: ServiceEvent<T>): void
} 