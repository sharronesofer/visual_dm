/**
 * Service-related type definitions
 * @module core/base/types/service
 */

import { BaseEntity } from './entity';
import { 
  ServiceResponse, 
  PaginationParams, 
  PaginatedResponse,
  QueryParams,
  ValidationResult,
  ServiceConfig
} from './common';

/**
 * Base service interface for CRUD operations
 */
export interface BaseService<T extends BaseEntity> {
  // Read operations
  findById(id: T['id']): Promise<ServiceResponse<T>>;
  findAll(params?: QueryParams<T>): Promise<ServiceResponse<PaginatedResponse<T>>>;
  findOne(params: QueryParams<T>): Promise<ServiceResponse<T | null>>;
  
  // Write operations
  create(data: Omit<T, keyof BaseEntity>): Promise<ServiceResponse<T>>;
  update(id: T['id'], data: Partial<T>): Promise<ServiceResponse<T>>;
  delete(id: T['id']): Promise<ServiceResponse<void>>;
  
  // Validation
  validate(data: Partial<T>): Promise<ValidationResult>;
  validateField(field: keyof T, value: any): Promise<ValidationResult>;
  
  // Configuration
  getConfig(): ServiceConfig;
  setConfig(config: Partial<ServiceConfig>): void;
}

/**
 * Service hooks for lifecycle events
 */
export interface ServiceHooks<T extends BaseEntity> {
  beforeCreate?: (data: Omit<T, keyof BaseEntity>) => Promise<void>;
  afterCreate?: (entity: T) => Promise<void>;
  beforeUpdate?: (id: T['id'], data: Partial<T>) => Promise<void>;
  afterUpdate?: (entity: T) => Promise<void>;
  beforeDelete?: (id: T['id']) => Promise<void>;
  afterDelete?: (id: T['id']) => Promise<void>;
}

/**
 * Service options for initialization
 */
export interface ServiceOptions {
  baseURL?: string;
  timeout?: number;
  headers?: Record<string, string>;
  hooks?: Partial<ServiceHooks<any>>;
  enableCache?: boolean;
  enableRetry?: boolean;
  enableRealtime?: boolean;
}

/**
 * Service event types
 */
export enum ServiceEventType {
  Created = 'created',
  Updated = 'updated',
  Deleted = 'deleted',
  Error = 'error'
}

/**
 * Service event payload
 */
export interface ServiceEvent<T = any> {
  type: ServiceEventType;
  data?: T;
  error?: Error;
  metadata?: Record<string, any>;
  timestamp: Date;
}

/**
 * Service event handler
 */
export type ServiceEventHandler<T = any> = (event: ServiceEvent<T>) => void | Promise<void>; 