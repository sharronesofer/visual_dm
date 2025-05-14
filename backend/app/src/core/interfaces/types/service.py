from typing import Any, Dict, List, Union
from enum import Enum


/**
 * Base response type for all service operations
 */
interface ServiceResponse<T = void> {
  success: bool
  data?: T
  error?: {
    code: str
    message: str
    details?: Any
  }
  metadata?: {
    timestamp: float
    requestId?: str
    [key: string]: Any
  }
}
/**
 * Base configuration type for service operations
 */
class ServiceConfig:
    timeout?: float
    retryAttempts?: float
    bypassCache?: bool
    validateInput?: bool
    [key: str]: Any
/**
 * Base entity type that all domain entities must extend
 */
class BaseEntity:
    id: Union[str, float]
    createdAt: Date
    updatedAt: Date
    version?: float
    [key: str]: Any
/**
 * Generic type for creation DTOs
 */
type CreateDTO<T> = Omit<T, 'id' | 'createdAt' | 'updatedAt' | 'version'>
/**
 * Generic type for update DTOs
 */
type UpdateDTO<T> = Partial<CreateDTO<T>>
/**
 * Generic type for query parameters
 */
class QueryParams:
    filter?: Dict[str, Any>
    sort?: {
    field: str
    order: Union['asc', 'desc'][]
  include?: string[]
  [key: string]: Any
}
/**
 * Pagination parameters
 */
class PaginationParams:
    page: float
    limit: float
/**
 * Paginated response type
 */
interface PaginatedResponse<T> {
  items: List[T]
  total: float
  page: float
  limit: float
  hasMore: bool
}
/**
 * Cache configuration type
 */
class CacheConfig:
    ttl?: float
    policy?: Union['memory', 'session', 'none']
    bypassCache?: bool
    tags?: List[str]
/**
 * Rate limit configuration type
 */
class RateLimitConfig:
    windowMs: float
    maxRequests: float
    errorMessage?: str
/**
 * Hook function types
 */
type BeforeHook<T> = (data: Partial<T>) => Promise<void>
type AfterHook<T> = (entity: T) => Promise<void>
DeleteHook = Union[(id: str, float) => Awaitable[None>]
/**
 * Transaction callback type
 */
type TransactionCallback<R> = () => Promise<R>
/**
 * Service error types
 */
class ServiceErrorType(Enum):
    VALIDATION = 'VALIDATION_ERROR'
    NOT_FOUND = 'NOT_FOUND'
    UNAUTHORIZED = 'UNAUTHORIZED'
    FORBIDDEN = 'FORBIDDEN'
    CONFLICT = 'CONFLICT'
    INTERNAL = 'INTERNAL_ERROR'
    RATE_LIMIT = 'RATE_LIMIT_EXCEEDED'
    BAD_REQUEST = 'BAD_REQUEST'
/**
 * Service error class
 */
class ServiceError extends Error {
  constructor(
    public type: \'ServiceErrorType\',
    message: str,
    public details?: Any
  ) {
    super(message)
    this.name = 'ServiceError'
  }
} 