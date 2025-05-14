/**
 * Service layer interfaces and types
 * @module types/services
 */

import type {
  ID,
  PaginationParams,
  PaginatedResponse,
  QueryParams,
  SuccessResponse,
  ErrorResponse,
  CacheOptions,
  RetryOptions,
  BaseEntity,
} from './common';

/**
 * Base service interface for CRUD operations
 */
export interface BaseService<T extends BaseEntity> {
  // Read operations
  findById(id: ID, options?: CacheOptions): Promise<T>;
  findAll(params?: QueryParams<T>): Promise<PaginatedResponse<T>>;
  findOne(params: QueryParams<T>): Promise<T | null>;

  // Write operations
  create(data: Omit<T, keyof BaseEntity>): Promise<T>;
  update(id: ID, data: Partial<T>): Promise<T>;
  delete(id: ID): Promise<void>;

  // Bulk operations
  bulkCreate(data: Array<Omit<T, keyof BaseEntity>>): Promise<T[]>;
  bulkUpdate(data: Array<{ id: ID; data: Partial<T> }>): Promise<T[]>;
  bulkDelete(ids: ID[]): Promise<void>;
}

/**
 * Service configuration options
 */
export interface ServiceConfig {
  baseURL: string;
  timeout?: number;
  retryOptions?: RetryOptions;
  cacheOptions?: CacheOptions;
}

/**
 * Service factory function type
 */
export type ServiceFactory<T extends BaseEntity> = (config: ServiceConfig) => BaseService<T>;

/**
 * Service event types
 */
export type ServiceEventType = 'create' | 'update' | 'delete' | 'error';

/**
 * Service event payload
 */
export interface ServiceEvent<T = unknown> {
  type: ServiceEventType;
  data: T;
  timestamp: number;
}

/**
 * Service event handler
 */
export type ServiceEventHandler<T = unknown> = (event: ServiceEvent<T>) => void | Promise<void>;

/**
 * Service event subscription
 */
export interface ServiceEventSubscription {
  unsubscribe(): void;
}

/**
 * Service event emitter interface
 */
export interface ServiceEventEmitter<T = unknown> {
  on(type: ServiceEventType, handler: ServiceEventHandler<T>): ServiceEventSubscription;
  off(type: ServiceEventType, handler: ServiceEventHandler<T>): void;
  emit(event: ServiceEvent<T>): void;
}

/**
 * Service with event handling capabilities
 */
export interface EventedService<T extends BaseEntity>
  extends BaseService<T>,
    ServiceEventEmitter<T> {}

/**
 * Service with caching capabilities
 */
export interface CachedService<T extends BaseEntity> extends BaseService<T> {
  clearCache(): void;
  invalidateCache(id: ID): void;
  setCacheOptions(options: CacheOptions): void;
}

/**
 * Service with retry capabilities
 */
export interface RetryableService<T extends BaseEntity> extends BaseService<T> {
  setRetryOptions(options: RetryOptions): void;
}

/**
 * Service with real-time update capabilities
 */
export interface RealtimeService<T extends BaseEntity> extends EventedService<T> {
  subscribe(id: ID): Promise<ServiceEventSubscription>;
  unsubscribe(id: ID): Promise<void>;
}

/**
 * Service response type
 */
export type ServiceResponse<T> = Promise<SuccessResponse<T> | ErrorResponse>;

/**
 * Service method decorator type
 */
export type ServiceDecorator = <T extends object>(
  target: T,
  propertyKey: string | symbol,
  descriptor: PropertyDescriptor
) => PropertyDescriptor;

/**
 * Service method parameter decorator type
 */
export type ServiceParameterDecorator = (
  target: object,
  propertyKey: string | symbol,
  parameterIndex: number
) => void;

/**
 * Service class decorator type
 */
export type ServiceClassDecorator = <T extends new (...args: any[]) => {}>(constructor: T) => T;
