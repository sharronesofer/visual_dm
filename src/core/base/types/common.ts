/**
 * Common type definitions
 * @module core/base/types/common
 */

/**
 * Generic ID type that can be string or number
 */
export type ID = string | number;

/**
 * Timestamp type alias for Date
 */
export type Timestamp = Date;

/**
 * Generic response type for service operations
 */
export interface ServiceResponse<T = any> {
  success: boolean;
  data?: T;
  error?: Error;
  metadata?: Record<string, any>;
}

/**
 * Pagination parameters
 */
export interface PaginationParams {
  page?: number;
  limit?: number;
  offset?: number;
}

/**
 * Paginated response
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

/**
 * Query parameters for filtering and sorting
 */
export interface QueryParams<T = any> {
  filter?: Partial<T>;
  sort?: {
    [K in keyof T]?: 'asc' | 'desc';
  };
  search?: string;
  include?: string[];
}

/**
 * Cache options
 */
export interface CacheOptions {
  ttl?: number;
  key?: string;
  namespace?: string;
  version?: string;
}

/**
 * Retry options
 */
export interface RetryOptions {
  maxRetries?: number;
  retryDelay?: number;
  retryableStatuses?: number[];
}

/**
 * Service configuration
 */
export interface ServiceConfig {
  baseURL?: string;
  timeout?: number;
  headers?: Record<string, string>;
  cache?: CacheOptions;
  retry?: RetryOptions;
}

/**
 * Validation error
 */
export interface ValidationError {
  field: string;
  message: string;
  code?: string;
  value?: any;
}

/**
 * Validation result
 */
export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
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