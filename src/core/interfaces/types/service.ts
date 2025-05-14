/**
 * Base response type for all service operations
 */
export interface ServiceResponse<T = void> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  metadata?: {
    timestamp: number;
    requestId?: string;
    [key: string]: any;
  };
}

/**
 * Base configuration type for service operations
 */
export interface ServiceConfig {
  timeout?: number;
  retryAttempts?: number;
  bypassCache?: boolean;
  validateInput?: boolean;
  [key: string]: any;
}

/**
 * Base entity type that all domain entities must extend
 */
export interface BaseEntity {
  id: string | number;
  createdAt: Date;
  updatedAt: Date;
  version?: number;
  [key: string]: any;
}

/**
 * Generic type for creation DTOs
 */
export type CreateDTO<T> = Omit<T, 'id' | 'createdAt' | 'updatedAt' | 'version'>;

/**
 * Generic type for update DTOs
 */
export type UpdateDTO<T> = Partial<CreateDTO<T>>;

/**
 * Generic type for query parameters
 */
export interface QueryParams {
  filter?: Record<string, any>;
  sort?: {
    field: string;
    order: 'asc' | 'desc';
  }[];
  include?: string[];
  [key: string]: any;
}

/**
 * Pagination parameters
 */
export interface PaginationParams {
  page: number;
  limit: number;
}

/**
 * Paginated response type
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

/**
 * Cache configuration type
 */
export interface CacheConfig {
  ttl?: number;
  policy?: 'memory' | 'session' | 'none';
  bypassCache?: boolean;
  tags?: string[];
}

/**
 * Rate limit configuration type
 */
export interface RateLimitConfig {
  windowMs: number;
  maxRequests: number;
  errorMessage?: string;
}

/**
 * Hook function types
 */
export type BeforeHook<T> = (data: Partial<T>) => Promise<void>;
export type AfterHook<T> = (entity: T) => Promise<void>;
export type DeleteHook = (id: string | number) => Promise<void>;

/**
 * Transaction callback type
 */
export type TransactionCallback<R> = () => Promise<R>;

/**
 * Service error types
 */
export enum ServiceErrorType {
  VALIDATION = 'VALIDATION_ERROR',
  NOT_FOUND = 'NOT_FOUND',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  CONFLICT = 'CONFLICT',
  INTERNAL = 'INTERNAL_ERROR',
  RATE_LIMIT = 'RATE_LIMIT_EXCEEDED',
  BAD_REQUEST = 'BAD_REQUEST'
}

/**
 * Service error class
 */
export class ServiceError extends Error {
  constructor(
    public type: ServiceErrorType,
    message: string,
    public details?: any
  ) {
    super(message);
    this.name = 'ServiceError';
  }
} 